"""
Position Size Calculator for Trading

Calculates position sizing based on entry price, stop loss, account balance, and risk tolerance.
Provides three risk modes: Conservative, Normal, and Aggressive.
Includes Take Profit calculations based on Risk-Reward ratios.
"""

from typing import Dict, Literal


def calculate_take_profits(
    entry: float,
    stop_loss: float
) -> Dict[str, any]:
    """
    Calculate Take Profit levels based on Risk-Reward ratios.
    Direction is automatically inferred from entry and stop loss relationship.

    Standard TP strategy:
    - TP1 at 0.5R (35% position close)
    - TP2 at 1.25R (50% position close)
    - Remaining 15% for manual exit

    Args:
        entry: Entry price for the trade
        stop_loss: Stop loss price

    Returns:
        Dictionary containing:
            - tp1_price: First take profit price (0.5R)
            - tp2_price: Second take profit price (1.25R)
            - tp1_percent: Percentage to close at TP1 (35%)
            - tp2_percent: Percentage to close at TP2 (50%)
            - manual_percent: Percentage for manual exit (15%)
            - risk_distance: Distance from entry to SL
            - rr_ratio_tp1: Risk-Reward ratio for TP1 (0.5)
            - rr_ratio_tp2: Risk-Reward ratio for TP2 (1.25)
            - direction: Inferred trade direction ('long' or 'short')

    Example:
        >>> tps = calculate_take_profits(entry=50000, stop_loss=49000)
        >>> print(f"Direction: {tps['direction']}")
        Direction: long
        >>> print(f"TP1: ${tps['tp1_price']}, TP2: ${tps['tp2_price']}")
        TP1: $50500.0, TP2: $51250.0
    """
    # Calculate risk distance
    risk_distance = abs(entry - stop_loss)

    # TP ratios
    tp1_rr = 0.5
    tp2_rr = 1.25

    # Position sizing percentages
    tp1_percent = 35
    tp2_percent = 50
    manual_percent = 15

    # Infer direction from entry and stop loss relationship
    # If SL < Entry → LONG (risk is below entry)
    # If SL > Entry → SHORT (risk is above entry)
    is_long = stop_loss < entry

    # Calculate TP prices based on inferred direction
    if is_long:
        tp1_price = entry + (risk_distance * tp1_rr)
        tp2_price = entry + (risk_distance * tp2_rr)
        direction = 'long'
    else:  # short
        tp1_price = entry - (risk_distance * tp1_rr)
        tp2_price = entry - (risk_distance * tp2_rr)
        direction = 'short'

    return {
        'tp1_price': round(tp1_price, 2),
        'tp2_price': round(tp2_price, 2),
        'tp1_percent': tp1_percent,
        'tp2_percent': tp2_percent,
        'manual_percent': manual_percent,
        'risk_distance': round(risk_distance, 2),
        'rr_ratio_tp1': tp1_rr,
        'rr_ratio_tp2': tp2_rr,
        'direction': direction
    }


def calculate_all_position_sizing_modes(
    entry: float,
    stop_loss: float,
    balance: float,
    user_risk_tolerance: float
) -> Dict[str, Dict[str, float]]:
    """
    Calculate position sizing for all three risk modes.

    Args:
        entry: Entry price for the trade
        stop_loss: Stop loss price
        balance: Account balance in USDT
        user_risk_tolerance: User's normal risk tolerance percentage (e.g., 3 for 3%)

    Returns:
        Dictionary containing position sizing for conservative, normal, and aggressive modes.
        Each mode includes:
            - notional_value: Position size in USDT
            - quantity: Number of coins/tokens
            - max_loss: Maximum potential loss in USDT
            - risk_percent: Risk percentage used
            - mode: Mode name

    Example:
        >>> result = calculate_all_position_sizing_modes(
        ...     entry=50000,
        ...     stop_loss=49000,
        ...     balance=10000,
        ...     user_risk_tolerance=3
        ... )
        >>> print(result['normal'])
        {
            'notional_value': 15000.00,
            'quantity': 0.3000,
            'max_loss': 300.00,
            'risk_percent': 3.0,
            'mode': 'normal'
        }
    """
    # Calculate risk percentages based on user's normal risk
    conservative_risk = max(0.5, user_risk_tolerance - 2)  # Normal - 2%, minimum 0.5%
    normal_risk = user_risk_tolerance  # User's set risk
    aggressive_risk = min(10.0, user_risk_tolerance + 2)  # Normal + 2%, maximum 10%

    modes = {
        'conservative': conservative_risk,
        'normal': normal_risk,
        'aggressive': aggressive_risk
    }

    results = {}
    for mode_name, risk_percent in modes.items():
        # Calculate maximum loss allowed for this risk level
        max_loss = balance * (risk_percent / 100)

        # Calculate price difference between entry and stop loss
        price_difference = abs(entry - stop_loss)

        # Calculate risk per unit (percentage)
        risk_per_unit = price_difference / entry

        # Calculate notional value (position size in USDT)
        notional_value = max_loss / risk_per_unit

        # Calculate quantity (number of coins/tokens)
        quantity = notional_value / entry

        results[mode_name] = {
            'notional_value': round(notional_value, 2),
            'quantity': round(quantity, 4),
            'max_loss': round(max_loss, 2),
            'risk_percent': risk_percent,
            'mode': mode_name
        }

    return results


def calculate_position_size(
    entry: float,
    stop_loss: float,
    balance: float,
    risk_percent: float
) -> Dict[str, float]:
    """
    Calculate position sizing for a single risk percentage.

    Args:
        entry: Entry price for the trade
        stop_loss: Stop loss price
        balance: Account balance in USDT
        risk_percent: Risk tolerance percentage (e.g., 3 for 3%)

    Returns:
        Dictionary containing:
            - notional_value: Position size in USDT
            - quantity: Number of coins/tokens
            - max_loss: Maximum potential loss in USDT
            - risk_percent: Risk percentage used

    Example:
        >>> result = calculate_position_size(
        ...     entry=50000,
        ...     stop_loss=49000,
        ...     balance=10000,
        ...     risk_percent=3
        ... )
        >>> print(f"Position size: ${result['notional_value']}")
        Position size: $15000.00
    """
    # Calculate maximum loss allowed for this risk level
    max_loss = balance * (risk_percent / 100)

    # Calculate price difference between entry and stop loss
    price_difference = abs(entry - stop_loss)

    # Calculate risk per unit (percentage)
    risk_per_unit = price_difference / entry

    # Calculate notional value (position size in USDT)
    notional_value = max_loss / risk_per_unit

    # Calculate quantity (number of coins/tokens)
    quantity = notional_value / entry

    return {
        'notional_value': round(notional_value, 2),
        'quantity': round(quantity, 4),
        'max_loss': round(max_loss, 2),
        'risk_percent': risk_percent
    }


def format_position_sizing(results: Dict[str, Dict[str, float]], symbol: str = "BTC") -> str:
    """
    Format position sizing results for display.

    Args:
        results: Results from calculate_all_position_sizing_modes
        symbol: Trading symbol (e.g., "BTC", "ETH")

    Returns:
        Formatted string with all three risk modes
    """
    conservative = results['conservative']
    normal = results['normal']
    aggressive = results['aggressive']

    return f"""💼 Position Sizing Options for {symbol}:

🛡️ Conservative ({conservative['risk_percent']:.1f}%):
   Position: ${conservative['notional_value']:,.2f} USDT
   Quantity: {conservative['quantity']} {symbol}
   Max Loss: ${conservative['max_loss']:,.2f}

⚖️ Normal ({normal['risk_percent']:.1f}%):
   Position: ${normal['notional_value']:,.2f} USDT
   Quantity: {normal['quantity']} {symbol}
   Max Loss: ${normal['max_loss']:,.2f}

⚡ Aggressive ({aggressive['risk_percent']:.1f}%):
   Position: ${aggressive['notional_value']:,.2f} USDT
   Quantity: {aggressive['quantity']} {symbol}
   Max Loss: ${aggressive['max_loss']:,.2f}"""


# Example usage
if __name__ == "__main__":
    print("=== Position Size Calculator with Take Profits ===\n")

    # Example trade parameters
    entry_price = 50000  # BTC entry at $50,000
    stop_loss_price = 49000  # Stop loss at $49,000
    account_balance = 10000  # $10,000 account
    risk_tolerance = 3  # 3% risk per trade

    print(f"Trade Setup:")
    print(f"  Entry: ${entry_price:,.2f}")
    print(f"  Stop Loss: ${stop_loss_price:,.2f}")
    print(f"  Account Balance: ${account_balance:,.2f}")
    print(f"  User Risk Tolerance: {risk_tolerance}%\n")

    # Calculate Take Profits
    tps = calculate_take_profits(entry=entry_price, stop_loss=stop_loss_price)

    print(f"📊 Direction: {tps['direction'].upper()}")
    print(f"📏 Risk Distance: ${tps['risk_distance']:,.2f}\n")

    print(f"🎯 Take Profit Levels:")
    print(f"  TP1 ({tps['rr_ratio_tp1']}R): ${tps['tp1_price']:,.2f} - Close {tps['tp1_percent']}%")
    print(f"  TP2 ({tps['rr_ratio_tp2']}R): ${tps['tp2_price']:,.2f} - Close {tps['tp2_percent']}%")
    print(f"  Manual Exit: {tps['manual_percent']}% remaining\n")

    # Calculate all position sizing modes
    results = calculate_all_position_sizing_modes(
        entry=entry_price,
        stop_loss=stop_loss_price,
        balance=account_balance,
        user_risk_tolerance=risk_tolerance
    )

    # Display formatted results
    print(format_position_sizing(results, symbol="BTC"))

    # Show TP exit quantities for normal mode
    normal_qty = results['normal']['quantity']
    print(f"\n💡 Exit Strategy (Normal Mode):")
    print(f"  At TP1 (${tps['tp1_price']:,.2f}): Close {normal_qty * 0.35:.4f} BTC ({tps['tp1_percent']}%)")
    print(f"  At TP2 (${tps['tp2_price']:,.2f}): Close {normal_qty * 0.50:.4f} BTC ({tps['tp2_percent']}%)")
    print(f"  Manual: Keep {normal_qty * 0.15:.4f} BTC ({tps['manual_percent']}%)")

    print("\n" + "="*50 + "\n")

    # Example 2: ETH SHORT trade
    print("=== Example 2: ETH Short Trade ===\n")

    eth_entry = 3000
    eth_sl = 3100  # SL above entry = SHORT

    print(f"Trade Setup:")
    print(f"  Entry: ${eth_entry:,.2f}")
    print(f"  Stop Loss: ${eth_sl:,.2f}")
    print(f"  Account Balance: ${account_balance:,.2f}\n")

    # Calculate TPs
    tps_eth = calculate_take_profits(entry=eth_entry, stop_loss=eth_sl)

    print(f"📊 Direction: {tps_eth['direction'].upper()}")
    print(f"📏 Risk Distance: ${tps_eth['risk_distance']:,.2f}\n")

    print(f"🎯 Take Profit Levels:")
    print(f"  TP1 ({tps_eth['rr_ratio_tp1']}R): ${tps_eth['tp1_price']:,.2f} - Close {tps_eth['tp1_percent']}%")
    print(f"  TP2 ({tps_eth['rr_ratio_tp2']}R): ${tps_eth['tp2_price']:,.2f} - Close {tps_eth['tp2_percent']}%")
    print(f"  Manual Exit: {tps_eth['manual_percent']}% remaining\n")

    results_eth = calculate_all_position_sizing_modes(
        entry=eth_entry,
        stop_loss=eth_sl,
        balance=account_balance,
        user_risk_tolerance=risk_tolerance
    )

    print(format_position_sizing(results_eth, symbol="ETH"))
