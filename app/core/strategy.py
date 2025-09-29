import yaml
import json
from typing import Dict, Any, List, Optional
from datetime import datetime
import ta  # Technical analysis library

class StrategyEngine:
    def __init__(self, config_file: str = "strategies.yaml"):
        self.config_file = config_file
        self.strategies = self.load_strategies()
    
    def load_strategies(self) -> Dict[str, Any]:
        """Load strategies from YAML configuration"""
        try:
            with open(self.config_file, 'r') as f:
                return yaml.safe_load(f) or {}
        except FileNotFoundError:
            # Return default strategies
            return {
                "default": {
                    "name": "5-Minute Breakout",
                    "description": "Basic breakout strategy on 5-minute charts",
                    "conditions": {
                        "entry": [
                            "price > ema_20",
                            "rsi < 70",
                            "volume > volume_sma_20"
                        ],
                        "exit": [
                            "price < ema_10 OR rsi > 80"
                        ]
                    },
                    "timeframe": "5min"
                }
            }
    
    def save_strategies(self):
        """Save strategies to YAML file"""
        with open(self.config_file, 'w') as f:
            yaml.dump(self.strategies, f, default_flow_style=False)
    
    def create_strategy(self, name: str, config: Dict[str, Any]):
        """Create a new trading strategy"""
        self.strategies[name] = config
        self.save_strategies()
    
    def get_strategy(self, name: str) -> Optional[Dict[str, Any]]:
        """Get strategy configuration"""
        return self.strategies.get(name)
    
    def get_all_strategies(self) -> List[str]:
        """Get all available strategy names"""
        return list(self.strategies.keys())
    
    def evaluate_conditions(self, strategy_name: str, market_data: Dict[str, Any]) -> Dict[str, bool]:
        """Evaluate strategy conditions against market data"""
        strategy = self.get_strategy(strategy_name)
        if not strategy:
            return {"entry": False, "exit": False}
        
        results = {"entry": True, "exit": False}
        
        # Evaluate entry conditions
        for condition in strategy.get('conditions', {}).get('entry', []):
            if not self.evaluate_condition(condition, market_data):
                results["entry"] = False
                break
        
        # Evaluate exit conditions
        for condition in strategy.get('conditions', {}).get('exit', []):
            if self.evaluate_condition(condition, market_data):
                results["exit"] = True
                break
        
        return results
    
    def evaluate_condition(self, condition: str, market_data: Dict[str, Any]) -> bool:
        """Evaluate a single condition string"""
        try:
            # Replace variable names with actual values from market_data
            evaluated_condition = condition
            for key, value in market_data.items():
                if isinstance(value, (int, float)):
                    evaluated_condition = evaluated_condition.replace(key, str(value))
            
            # Safe evaluation of the condition
            return eval(evaluated_condition, {"__builtins__": {}}, {})
        except:
            return False
    
    def calculate_indicators(self, price_data: List[float], volume_data: List[float]) -> Dict[str, Any]:
        """Calculate technical indicators from price and volume data"""
        if len(price_data) < 20:
            return {}
        
        import pandas as pd
        
        # Convert to pandas Series for technical analysis
        prices = pd.Series(price_data)
        volumes = pd.Series(volume_data)
        
        indicators = {
            'price': price_data[-1],
            'volume': volume_data[-1] if volume_data else 0,
            
            # Moving averages
            'sma_5': ta.trend.sma_indicator(prices, window=5).iloc[-1],
            'sma_10': ta.trend.sma_indicator(prices, window=10).iloc[-1],
            'sma_20': ta.trend.sma_indicator(prices, window=20).iloc[-1],
            'ema_10': ta.trend.ema_indicator(prices, window=10).iloc[-1],
            'ema_20': ta.trend.ema_indicator(prices, window=20).iloc[-1],
            
            # RSI
            'rsi': ta.momentum.rsi(prices, window=14).iloc[-1],
            
            # MACD
            'macd': ta.trend.macd(prices).iloc[-1],
            'macd_signal': ta.trend.macd_signal(prices).iloc[-1],
            
            # Bollinger Bands
            'bb_upper': ta.volatility.bollinger_hband(prices).iloc[-1],
            'bb_lower': ta.volatility.bollinger_lband(prices).iloc[-1],
            'bb_middle': ta.volatility.bollinger_mavg(prices).iloc[-1],
            
            # Volume indicators
            'volume_sma_20': ta.trend.sma_indicator(volumes, window=20).iloc[-1] if len(volume_data) >= 20 else volume_data[-1],
            
            # Support/Resistance (simplified)
            'resistance': max(price_data[-20:]),
            'support': min(price_data[-20:])
        }
        
        return indicators