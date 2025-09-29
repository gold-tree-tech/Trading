from abc import ABC, abstractmethod
from typing import Dict, Any

class ExecutionAdapter(ABC):
    @abstractmethod
    def place_order(self, ticker: str, quantity: int, order_type: str, price: float = None) -> Dict[str, Any]:
        pass
    
    @abstractmethod
    def cancel_order(self, order_id: str) -> bool:
        pass
    
    @abstractmethod
    def get_position(self, ticker: str) -> Dict[str, Any]:
        pass
    
    @abstractmethod
    def get_account_info(self) -> Dict[str, Any]:
        pass

class PaperTradingAdapter(ExecutionAdapter):
    def __init__(self, initial_equity: float = 100000.0):
        self.equity = initial_equity
        self.positions = {}
        self.orders = {}
        self.order_id_counter = 1
    
    def place_order(self, ticker: str, quantity: int, order_type: str, price: float = None) -> Dict[str, Any]:
        order_id = f"PAPER_{self.order_id_counter}"
        self.order_id_counter += 1
        
        # Simulate order execution
        if order_type == "MARKET":
            # Use current market price (simulated)
            executed_price = price if price else self._get_simulated_price(ticker)
        else:
            executed_price = price
        
        order_result = {
            "order_id": order_id,
            "ticker": ticker,
            "quantity": quantity,
            "executed_price": executed_price,
            "status": "FILLED",
            "order_type": order_type
        }
        
        # Update position
        if ticker in self.positions:
            self.positions[ticker]['quantity'] += quantity
            self.positions[ticker]['average_price'] = (
                (self.positions[ticker]['average_price'] * self.positions[ticker]['quantity'] + 
                 executed_price * quantity) / (self.positions[ticker]['quantity'] + quantity)
            )
        else:
            self.positions[ticker] = {
                'quantity': quantity,
                'average_price': executed_price
            }
        
        self.orders[order_id] = order_result
        return order_result
    
    def cancel_order(self, order_id: str) -> bool:
        if order_id in self.orders:
            self.orders[order_id]['status'] = 'CANCELLED'
            return True
        return False
    
    def get_position(self, ticker: str) -> Dict[str, Any]:
        return self.positions.get(ticker, {'quantity': 0, 'average_price': 0})
    
    def get_account_info(self) -> Dict[str, Any]:
        return {
            "equity": self.equity,
            "buying_power": self.equity,
            "positions": self.positions
        }
    
    def _get_simulated_price(self, ticker: str) -> float:
        # Simple price simulation - in real implementation, this would connect to market data
        base_prices = {
            'SPY': 450.0,
            'AAPL': 175.0,
            'QQQ': 380.0,
            'TSLA': 240.0,
            'MSFT': 370.0
        }
        return base_prices.get(ticker, 100.0)

class LiveTradingAdapter(ExecutionAdapter):
    def __init__(self, das_api_config: Dict[str, Any]):
        self.api_config = das_api_config
        # In a real implementation, this would initialize connection to DAS API
    
    def place_order(self, ticker: str, quantity: int, order_type: str, price: float = None) -> Dict[str, Any]:
        # This would make actual API calls to DAS Trader
        # For now, return simulated response
        return {
            "order_id": f"LIVE_{ticker}_{quantity}",
            "ticker": ticker,
            "quantity": quantity,
            "status": "SUBMITTED",
            "order_type": order_type
        }
    
    def cancel_order(self, order_id: str) -> bool:
        # Actual DAS API call to cancel order
        return True
    
    def get_position(self, ticker: str) -> Dict[str, Any]:
        # Actual DAS API call to get position
        return {"quantity": 0, "average_price": 0}
    
    def get_account_info(self) -> Dict[str, Any]:
        # Actual DAS API call to get account info
        return {
            "equity": 100000.0,
            "buying_power": 100000.0,
            "positions": {}
        }