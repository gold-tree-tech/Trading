def calculate_position_size(equity: float, price: float, allocation_pct: float) -> int:
    """Calculate position size based on equity and allocation percentage"""
    allocation_amount = equity * (allocation_pct / 100)
    quantity = int(allocation_amount / price)
    return max(1, quantity)  # Minimum 1 share

def round_price(price: float, tick_size: float = 0.01) -> float:
    """Round price to nearest tick size"""
    return round(price / tick_size) * tick_size

def format_currency(amount: float) -> str:
    """Format currency amount"""
    return f"${amount:,.2f}"