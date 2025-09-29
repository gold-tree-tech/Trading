from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, Dict, Any
import uvicorn
import yaml
import os
from core.state import TradingState
from core.controller import TradingController
from core.logger import TradeLogger
from core.profiles import ProfileManager
from core.strategy import StrategyEngine

# Load configuration
with open('config.yaml', 'r') as f:
    config = yaml.safe_load(f)

app = FastAPI(title="DAS Trader Pro API", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize core components
logger = TradeLogger(config['log_file'])
profile_manager = ProfileManager(config['profiles_db'])
state = TradingState(logger, profile_manager)
controller = TradingController(state, config)

# Pydantic models for request/response
class TickerRequest(BaseModel):
    ticker: str

class ProfileRequest(BaseModel):
    profile: str

class TradeResponse(BaseModel):
    success: bool
    message: str
    state: Dict[str, Any]

@app.get("/")
async def root():
    return {"message": "DAS Trader Pro API", "version": "1.0.0"}

@app.get("/state")
async def get_state():
    """Get current trading state"""
    return state.get_state()

@app.post("/start")
async def start_strategy(request: TickerRequest):
    """Start trading strategy for a ticker"""
    try:
        success, message = controller.start_strategy(request.ticker)
        return TradeResponse(success=success, message=message, state=state.get_state())
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/pause")
async def pause_strategy():
    """Pause the trading strategy"""
    try:
        success, message = controller.pause_strategy()
        return TradeResponse(success=success, message=message, state=state.get_state())
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/resume")
async def resume_strategy():
    """Resume the trading strategy"""
    try:
        success, message = controller.resume_strategy()
        return TradeResponse(success=success, message=message, state=state.get_state())
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/emergency-exit")
async def emergency_exit():
    """Emergency exit - close all positions"""
    try:
        success, message = controller.emergency_exit()
        return TradeResponse(success=success, message=message, state=state.get_state())
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/set-profile")
async def set_profile(request: ProfileRequest):
    """Set trading profile"""
    try:
        success, message = controller.set_profile(request.profile)
        return TradeResponse(success=success, message=message, state=state.get_state())
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/logs")
async def get_logs(limit: int = 100):
    """Get recent trading logs"""
    return logger.get_recent_logs(limit)

@app.get("/profiles")
async def get_profiles():
    """Get available trading profiles"""
    return profile_manager.get_all_profiles()

@app.get("/strategies")
async def get_strategies():
    """Get all available trading strategies"""
    try:
        strategies = controller.get_strategies()
        return {"success": True, "strategies": strategies}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/set-strategy")
async def set_strategy(request: dict):
    """Set active trading strategy"""
    try:
        strategy_name = request.get('strategy')
        if not strategy_name:
            raise HTTPException(status_code=400, detail="Strategy name required")
        
        success, message = controller.set_strategy(strategy_name)
        return TradeResponse(success=success, message=message, state=state.get_state())
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/create-strategy")
async def create_strategy(request: dict):
    """Create a new trading strategy"""
    try:
        strategy_name = request.get('name')
        strategy_config = request.get('config')
        
        if not strategy_name or not strategy_config:
            raise HTTPException(status_code=400, detail="Strategy name and config required")
        
        success, message = controller.create_strategy(strategy_name, strategy_config)
        return {"success": success, "message": message}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/strategy/{strategy_name}")
async def get_strategy(strategy_name: str):
    """Get specific strategy configuration"""
    try:
        strategy = controller.strategy_engine.get_strategy(strategy_name)
        if not strategy:
            raise HTTPException(status_code=404, detail="Strategy not found")
        return {"success": True, "strategy": strategy}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=config['api_port'])