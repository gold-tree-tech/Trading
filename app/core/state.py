import json
import os
from datetime import datetime
from typing import Dict, Any, Optional
from core.logger import TradeLogger
from core.profiles import ProfileManager

class TradingState:
    def __init__(self, logger: TradeLogger, profile_manager: ProfileManager):
        self.logger = logger
        self.profile_manager = profile_manager
        self.state_file = "trading_state.json"
        self.load_state()
    
    def load_state(self):
        """Load state from file or initialize default state"""
        default_state = {
            "current_state": "IDLE",  # IDLE, LONG, PAUSED, EXITED
            "ticker": None,
            "profile": "safe_mode",
            "equity": 100000.0,
            "position": None,
            "strategy_active": False,
            "last_updated": datetime.now().isoformat()
        }
        
        if os.path.exists(self.state_file):
            try:
                with open(self.state_file, 'r') as f:
                    self.state = json.load(f)
                # Validate loaded state
                if not all(key in self.state for key in default_state.keys()):
                    self.state = default_state
            except:
                self.state = default_state
        else:
            self.state = default_state
        
        # Log state recovery
        if self.state['current_state'] != 'IDLE':
            self.logger.log({
                "timestamp": datetime.now().isoformat(),
                "event": "STATE_RECOVERY",
                "message": f"Recovered state: {self.state['current_state']}",
                "state": self.state.copy()
            })
    
    def save_state(self):
        """Save current state to file"""
        self.state['last_updated'] = datetime.now().isoformat()
        with open(self.state_file, 'w') as f:
            json.dump(self.state, f, indent=2)
    
    def get_state(self) -> Dict[str, Any]:
        """Get current state"""
        return self.state.copy()
    
    def update_state(self, updates: Dict[str, Any]):
        """Update state with new values"""
        before_state = self.state.copy()
        self.state.update(updates)
        self.save_state()
        
        # Log state change if significant
        if any(key in updates for key in ['current_state', 'position', 'equity']):
            self.logger.log({
                "timestamp": datetime.now().isoformat(),
                "event": "STATE_CHANGE",
                "before_state": before_state,
                "after_state": self.state.copy()
            })
    
    def enter_trade(self, ticker: str, entry_price: float, quantity: int):
        """Enter a new trade with detailed logging"""
        profile = self.profile_manager.get_profile(self.state['profile'])
        stop_loss = entry_price * (1 - profile['stop_loss_pct'] / 100)
        take_profit = entry_price * (1 + profile['take_profit_pct'] / 100)
        
        position = {
            "ticker": ticker,
            "entry_price": entry_price,
            "quantity": quantity,
            "stop_loss": stop_loss,
            "take_profit": take_profit,
            "entry_time": datetime.now().isoformat()
        }
        
        self.update_state({
            "current_state": "LONG",
            "ticker": ticker,
            "position": position
        })
        
        # Detailed trade log
        position_value = entry_price * quantity
        self.logger.log({
            "timestamp": datetime.now().isoformat(),
            "event": "ENTRY",
            "ticker": ticker,
            "profile": self.state['profile'],
            "action": "BUY",
            "quantity": quantity,
            "entry_price": entry_price,
            "position_value": position_value,
            "stop_loss": stop_loss,
            "take_profit": take_profit,
            "message": f"BUY {quantity} shares of {ticker} at ${entry_price:.2f}",
            "before_state": {
                "equity": self.state['equity'],
                "position": "IDLE"
            },
            "after_state": {
                "equity": self.state['equity'],
                "position": "LONG",
                "qty": quantity,
                "entry_price": entry_price
            }
        })
    
    def exit_trade(self, exit_price: float, reason: str):
        """Exit current trade"""
        if not self.state['position']:
            return
        
        position = self.state['position']
        pnl = (exit_price - position['entry_price']) * position['quantity']
        new_equity = self.state['equity'] + pnl
        
        before_state = self.state.copy()
        
        self.update_state({
            "current_state": "IDLE",
            "equity": new_equity,
            "position": None
        })
        
        # Log trade exit
        self.logger.log({
            "timestamp": datetime.now().isoformat(),
            "event": "EXIT",
            "ticker": position['ticker'],
            "exit_reason": reason,
            "exit_price": exit_price,
            "pnl": pnl,
            "before_state": before_state,
            "after_state": self.state.copy()
        })