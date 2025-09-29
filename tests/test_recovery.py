import unittest
import os
import json
from core.state import TradingState
from core.logger import TradeLogger
from core.profiles import ProfileManager

class TestRecovery(unittest.TestCase):
    def setUp(self):
        self.log_file = "test_logs.jsonl"
        self.state_file = "test_state.json"
        self.db_file = "test_profiles.db"
        
        self.logger = TradeLogger(self.log_file)
        self.profile_manager = ProfileManager(self.db_file)
    
    def tearDown(self):
        # Clean up test files
        for file in [self.log_file, self.state_file, self.db_file]:
            if os.path.exists(file):
                os.remove(file)
    
    def test_state_recovery(self):
        # Create a state with active position
        test_state = {
            "current_state": "LONG",
            "ticker": "AAPL",
            "profile": "safe_mode",
            "equity": 100000.0,
            "position": {
                "ticker": "AAPL",
                "entry_price": 175.0,
                "quantity": 100,
                "stop_loss": 173.25,
                "take_profit": 178.5
            },
            "strategy_active": True
        }
        
        # Save state
        with open(self.state_file, 'w') as f:
            json.dump(test_state, f)
        
        # Try to load state
        state = TradingState(self.logger, self.profile_manager)
        state.state_file = self.state_file
        state.load_state()
        
        # Verify state was recovered
        self.assertEqual(state.state['current_state'], "LONG")
        self.assertEqual(state.state['ticker'], "AAPL")
        self.assertIsNotNone(state.state['position'])

if __name__ == '__main__':
    unittest.main()