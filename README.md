# DAS Trader Pro - Automated Trading System

A 5-minute chart long-only trading strategy that automates trades on one stock at a time.

## Features
- One trade at a time per ticker
- State awareness (IDLE, LONG, PAUSED, EXITED)
- Risk management profiles
- Comprehensive logging
- Paper and Live trading modes

## Quick Start
1. Install dependencies: `pip install -r requirements.txt`
2. Run the application: `python app/app.py`
3. Access API at: `http://localhost:8000`

## API Endpoints
- `GET /state` - Get current trading state
- `POST /start` - Start strategy with ticker
- `POST /pause` - Pause strategy
- `POST /emergency-exit` - Emergency exit all positions
- `GET /logs` - Get trading logs
