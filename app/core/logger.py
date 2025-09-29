import json
import os
from typing import List, Dict, Any
from datetime import datetime

class TradeLogger:
    def __init__(self, log_file: str):
        self.log_file = log_file
        os.makedirs(os.path.dirname(log_file), exist_ok=True)
    
    def log(self, log_entry: Dict[str, Any]):
        """Add a new log entry"""
        if 'timestamp' not in log_entry:
            log_entry['timestamp'] = datetime.now().isoformat()
        
        with open(self.log_file, 'a') as f:
            f.write(json.dumps(log_entry) + '\n')
    
    def get_recent_logs(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get recent log entries"""
        logs = []
        if not os.path.exists(self.log_file):
            return logs
        
        with open(self.log_file, 'r') as f:
            lines = f.readlines()
        
        # Get last 'limit' lines
        for line in lines[-limit:]:
            try:
                logs.append(json.loads(line.strip()))
            except:
                continue
        
        return logs
    
    def get_last_trade_state(self) -> Dict[str, Any]:
        """Get the last trade state from logs for recovery"""
        logs = self.get_recent_logs(500)  # Check last 500 logs
        
        for log in reversed(logs):
            if log.get('event') in ['ENTRY', 'EXIT', 'STATE_CHANGE']:
                if 'after_state' in log:
                    return log['after_state']
        
        return None