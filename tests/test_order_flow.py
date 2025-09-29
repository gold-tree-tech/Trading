import requests
import time
from datetime import datetime

def monitor_backend(url: str = "http://localhost:8000", interval: int = 5):
    """Monitor backend status continuously"""
    print(f"🔍 Monitoring backend at {url} (Ctrl+C to stop)")
    
    while True:
        try:
            # Check health
            health_response = requests.get(f"{url}/", timeout=5)
            health_status = "✅ ONLINE" if health_response.status_code == 200 else "❌ OFFLINE"
            
            # Check state
            state_response = requests.get(f"{url}/state", timeout=5)
            state_data = state_response.json() if state_response.status_code == 200 else {}
            
            # Check logs
            logs_response = requests.get(f"{url}/logs?limit=1", timeout=5)
            logs_count = len(logs_response.json()) if logs_response.status_code == 200 else 0
            
            timestamp = datetime.now().strftime("%H:%M:%S")
            print(f"[{timestamp}] {health_status} | State: {state_data.get('current_state', 'UNKNOWN')} | Logs: {logs_count}")
            
        except requests.exceptions.ConnectionError:
            print(f"[{datetime.now().strftime('%H:%M:%S')}] ❌ CANNOT CONNECT")
        except Exception as e:
            print(f"[{datetime.now().strftime('%H:%M:%S')}] ⚠️  ERROR: {e}")
        
        time.sleep(interval)

def stress_test_endpoint(url: str, endpoint: str, method: str = "GET", requests_count: int = 10):
    """Stress test a specific endpoint"""
    print(f"⚡ Stress testing {method} {endpoint} with {requests_count} requests")
    
    successes = 0
    failures = 0
    total_time = 0
    
    for i in range(requests_count):
        try:
            start_time = time.time()
            response = requests.request(method, f"{url}{endpoint}", timeout=5)
            duration = time.time() - start_time
            total_time += duration
            
            if response.status_code == 200:
                successes += 1
                print(f"  Request {i+1}: ✅ {duration:.3f}s")
            else:
                failures += 1
                print(f"  Request {i+1}: ❌ {response.status_code}")
                
        except Exception as e:
            failures += 1
            print(f"  Request {i+1}: 💥 {e}")
    
    avg_time = total_time / requests_count if requests_count > 0 else 0
    print(f"\n📊 Results: {successes}/{requests_count} successful")
    print(f"⏱️  Average response time: {avg_time:.3f}s")
    print(f"🚀 Requests per second: {successes/total_time:.1f}" if total_time > 0 else "N/A")

if __name__ == "__main__":
    # Example usage
    monitor_backend()