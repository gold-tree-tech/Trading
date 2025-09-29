import sqlite3
import json
from typing import Dict, Any, List

class ProfileManager:
    def __init__(self, db_file: str):
        self.db_file = db_file
        self.init_db()
    
    def init_db(self):
        """Initialize database with default profiles"""
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS profiles (
                name TEXT PRIMARY KEY,
                config TEXT NOT NULL
            )
        ''')
        
        # Insert default profiles
        default_profiles = {
            'safe_mode': {
                'stop_loss_pct': 1.0,
                'take_profit_pct': 2.0,
                'capital_allocation_pct': 1.0
            },
            'risky_business': {
                'stop_loss_pct': 3.0,
                'take_profit_pct': 6.0,
                'capital_allocation_pct': 5.0
            }
        }
        
        for name, config in default_profiles.items():
            cursor.execute(
                'INSERT OR REPLACE INTO profiles (name, config) VALUES (?, ?)',
                (name, json.dumps(config))
            )
        
        conn.commit()
        conn.close()
    
    def get_profile(self, profile_name: str) -> Dict[str, Any]:
        """Get profile configuration"""
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        
        cursor.execute('SELECT config FROM profiles WHERE name = ?', (profile_name,))
        result = cursor.fetchone()
        conn.close()
        
        if result:
            return json.loads(result[0])
        else:
            raise ValueError(f"Profile '{profile_name}' not found")
    
    def get_all_profiles(self) -> List[str]:
        """Get all available profile names"""
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        
        cursor.execute('SELECT name FROM profiles')
        results = cursor.fetchall()
        conn.close()
        
        return [result[0] for result in results]
    
    def create_profile(self, name: str, config: Dict[str, Any]):
        """Create a new trading profile"""
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        
        cursor.execute(
            'INSERT OR REPLACE INTO profiles (name, config) VALUES (?, ?)',
            (name, json.dumps(config))
        )
        
        conn.commit()
        conn.close()