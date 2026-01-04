"""
Position Size Calculator for Trading

Calculates position sizing based on entry price, stop loss, account balance, and risk tolerance.
Provides three risk modes: Conservative, Normal, and Aggressive.
"""

from typing import Dict


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
    print("=== Position Size Calculator ===\n")

    # Example trade parameters
    entry_price = 50000  # BTC entry at $50,000
    stop_loss_price = 49000  # Stop loss at $49,000
    account_balance = 10000  # $10,000 account
    risk_tolerance = 3  # 3% risk per trade

    print(f"Trade Setup:")
    print(f"  Entry: ${entry_price:,.2f}")
    print(f"  Stop Loss: ${stop_loss_price:,.2f}")
    print(f"  Account Balance: ${account_balance:,.2f}")
    print(f"  User Risk Tolerance: {risk_tolerance}%")
    print(f"  Risk Amount: ${entry_price - stop_loss_price:,.2f} per coin\n")

    # Calculate all position sizing modes
    results = calculate_all_position_sizing_modes(
        entry=entry_price,
        stop_loss=stop_loss_price,
        balance=account_balance,
        user_risk_tolerance=risk_tolerance
    )

    # Display formatted results
    print(format_position_sizing(results, symbol="BTC"))

    print("\n" + "="*50 + "\n")

    # Example 2: ETH trade
    print("=== Example 2: ETH Long Trade ===\n")

    eth_entry = 3000
    eth_sl = 2900

    results_eth = calculate_all_position_sizing_modes(
        entry=eth_entry,
        stop_loss=eth_sl,
        balance=account_balance,
        user_risk_tolerance=risk_tolerance
    )

    print(f"Trade Setup:")
    print(f"  Entry: ${eth_entry:,.2f}")
    print(f"  Stop Loss: ${eth_sl:,.2f}")
    print(f"  Account Balance: ${account_balance:,.2f}\n")

    print(format_position_sizing(results_eth, symbol="ETH"))
