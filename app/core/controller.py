import time
from typing import Tuple, Dict, Any, List  # ADDED List import
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from core.state import TradingState
from core.execution_adapter import PaperTradingAdapter, LiveTradingAdapter
from core.utils import calculate_position_size

class TradingController:
    def __init__(self, state: TradingState, config: Dict[str, Any]):
        self.state = state
        self.config = config
        self.scheduler = BackgroundScheduler()
        
        # Initialize execution adapter based on mode
        if config['mode'] == 'paper':
            self.execution = PaperTradingAdapter()
        else:
            self.execution = LiveTradingAdapter(config.get('das_api_config', {}))
        
        # Start monitoring job
        self._start_monitoring()
    
    def _start_monitoring(self):
        """Start the background monitoring job"""
        trigger = IntervalTrigger(minutes=1)  # Check every minute
        self.scheduler.add_job(
            self._monitor_trading,
            trigger,
            id='trading_monitor'
        )
        self.scheduler.start()
    
    def _monitor_trading(self):
        """Main trading monitoring logic"""
        current_state = self.state.get_state()
        
        if not current_state['strategy_active']:
            return
        
        if current_state['current_state'] == 'LONG':
            self._monitor_exit_conditions()
        elif current_state['current_state'] == 'IDLE':
            self._check_entry_conditions()
    
    def _monitor_exit_conditions(self):
        """Check if exit conditions are met for current position"""
        position = self.state.state['position']
        if not position:
            return
        
        # Get current price (simulated)
        current_price = self._get_current_price(position['ticker'])
        
        # Check stop loss
        if current_price <= position['stop_loss']:
            self._exit_trade(current_price, "STOP_LOSS")
        # Check take profit
        elif current_price >= position['take_profit']:
            self._exit_trade(current_price, "TAKE_PROFIT")
    
    def _check_entry_conditions(self):
        """Check if entry conditions are met"""
        current_state = self.state.get_state()
        if not current_state['ticker']:
            return
        
        # Simple entry logic based on random chance for demo
        import random
        if random.random() < 0.1:  # 10% chance to enter
            current_price = self._get_current_price(current_state['ticker'])
            self._enter_trade(current_state['ticker'], current_price)
    
    def _enter_trade(self, ticker: str, price: float):
        """Enter a new trade"""
        current_state = self.state.get_state()
        profile_config = self.state.profile_manager.get_profile(current_state['profile'])
        quantity = calculate_position_size(
            current_state['equity'],
            price,
            profile_config['capital_allocation_pct']
        )
        
        # Place order
        order_result = self.execution.place_order(ticker, quantity, "MARKET", price)
        
        if order_result['status'] == 'FILLED':
            self.state.enter_trade(ticker, order_result['executed_price'], quantity)
    
    def _exit_trade(self, price: float, reason: str):
        """Exit current trade"""
        position = self.state.state['position']
        if not position:
            return
        
        # Place exit order
        order_result = self.execution.place_order(
            position['ticker'], 
            -position['quantity'],
            "MARKET", 
            price
        )
        
        if order_result['status'] == 'FILLED':
            self.state.exit_trade(order_result['executed_price'], reason)
    
    def _get_current_price(self, ticker: str) -> float:
        """Get current price for ticker (simulated)"""
        base_prices = {
            'SPY': 450.0,
            'AAPL': 175.0,
            'QQQ': 380.0,
            'TSLA': 240.0,
            'MSFT': 370.0
        }
        base_price = base_prices.get(ticker, 100.0)
        
        import random
        variation = (random.random() - 0.5) * 10
        return base_price + variation
    
    def start_strategy(self, ticker: str) -> Tuple[bool, str]:
        """Start trading strategy for a ticker"""
        current_state = self.state.get_state()
        
        if current_state['strategy_active']:
            return False, "Strategy already active"
        
        self.state.update_state({
            "strategy_active": True,
            "ticker": ticker,
            "current_state": "IDLE"
        })
        
        return True, f"Strategy started for {ticker}"
    
    def pause_strategy(self) -> Tuple[bool, str]:
        """Pause the trading strategy"""
        current_state = self.state.get_state()
        
        if not current_state['strategy_active']:
            return False, "Strategy not active"
        
        self.state.update_state({"strategy_active": False})
        
        if current_state['current_state'] == 'LONG':
            return True, "Strategy paused (holding position)"
        else:
            return True, "Strategy paused"
    
    def resume_strategy(self) -> Tuple[bool, str]:
        """Resume the trading strategy"""
        current_state = self.state.get_state()
        
        if current_state['strategy_active']:
            return False, "Strategy already active"
        
        self.state.update_state({"strategy_active": True})
        return True, "Strategy resumed"
    
    def emergency_exit(self) -> Tuple[bool, str]:
        """Emergency exit - close all positions"""
        current_state = self.state.get_state()
        
        if current_state['current_state'] == 'LONG':
            position = current_state['position']
            current_price = self._get_current_price(position['ticker'])
            self._exit_trade(current_price, "EMERGENCY_EXIT")
        
        self.state.update_state({
            "strategy_active": False,
            "current_state": "IDLE"
        })
        
        return True, "Emergency exit completed"
    
    def set_profile(self, profile: str) -> Tuple[bool, str]:
        """Set trading profile"""
        try:
            self.state.profile_manager.get_profile(profile)
            self.state.update_state({"profile": profile})
            return True, f"Profile set to {profile}"
        except ValueError as e:
            return False, str(e)
    
    # Strategy management methods (for custom strategies)
    def set_strategy(self, strategy: str) -> Tuple[bool, str]:
        """Set trading strategy"""
        try:
            self.state.update_state({"strategy": strategy})
            return True, f"Strategy set to {strategy}"
        except Exception as e:
            return False, str(e)
    
    def create_strategy(self, name: str, config: Dict[str, Any]) -> Tuple[bool, str]:
        """Create a new trading strategy"""
        try:
            # This would save to strategies.yaml in a real implementation
            return True, f"Strategy '{name}' created successfully"
        except Exception as e:
            return False, str(e)
    
    def get_strategies(self) -> List[str]:
        """Get all available strategies"""
        return ["default", "mean_reversion", "momentum", "scalping"]
    
    def start_strategy(self, ticker: str) -> Tuple[bool, str]:
        """Start trading strategy for a ticker"""
        current_state = self.state.get_state()
        
        if current_state['strategy_active']:
            return False, "Strategy already active"
        
        self.state.update_state({
            "strategy_active": True,
            "ticker": ticker,
            "current_state": "IDLE"
        })
        
        return True, f"Strategy started for {ticker}"
    
    def pause_strategy(self) -> Tuple[bool, str]:
        """Pause the trading strategy"""
        current_state = self.state.get_state()
        
        if not current_state['strategy_active']:
            return False, "Strategy not active"
        
        self.state.update_state({"strategy_active": False})
        
        if current_state['current_state'] == 'LONG':
            return True, "Strategy paused (holding position)"
        else:
            return True, "Strategy paused"
    
    def resume_strategy(self) -> Tuple[bool, str]:
        """Resume the trading strategy"""
        current_state = self.state.get_state()
        
        if current_state['strategy_active']:
            return False, "Strategy already active"
        
        self.state.update_state({"strategy_active": True})
        return True, "Strategy resumed"
    
    def emergency_exit(self) -> Tuple[bool, str]:
        """Emergency exit - close all positions"""
        current_state = self.state.get_state()
        
        if current_state['current_state'] == 'LONG':
            position = current_state['position']
            current_price = self._get_current_price(position['ticker'])
            self._exit_trade(current_price, "EMERGENCY_EXIT")
        
        self.state.update_state({
            "strategy_active": False,
            "current_state": "IDLE"
        })
        
        return True, "Emergency exit completed"
    
    def set_profile(self, profile: str) -> Tuple[bool, str]:
        """Set trading profile"""
        try:
            # Validate profile exists
            self.state.profile_manager.get_profile(profile)
            self.state.update_state({"profile": profile})
            return True, f"Profile set to {profile}"
        except ValueError as e:
            return False, str(e)