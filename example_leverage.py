"""
Example demonstrating leverage configuration and position sizing

Shows how leverage affects position sizing calculations.
"""

from calculate_size import calculate_all_position_sizing_modes


def example_leverage_impact():
    """
    Demonstrate how leverage affects position sizing
    """
    print("\n" + "="*70)
    print("LEVERAGE IMPACT ON POSITION SIZING")
    print("="*70 + "\n")

    # Trade parameters
    entry = 50000
    stop_loss = 49000
    balance = 10000
    risk_tolerance = 3  # 3% risk

    print(f"Trade Setup:")
    print(f"  Entry: ${entry:,.2f}")
    print(f"  Stop Loss: ${stop_loss:,.2f}")
    print(f"  Account Balance: ${balance:,.2f}")
    print(f"  Risk Tolerance: {risk_tolerance}%")
    print()

    # Test different leverage levels
    leverage_levels = [1, 10, 25, 50, 100]

    for leverage in leverage_levels:
        print(f"\n{'─'*70}")
        print(f"Leverage: {leverage}x")
        print(f"{'─'*70}")

        result = calculate_all_position_sizing_modes(
            entry=entry,
            stop_loss=stop_loss,
            balance=balance,
            user_risk_tolerance=risk_tolerance,
            leverage=leverage
        )

        # Show normal mode only for clarity
        normal = result['normal']

        print(f"\nNormal Mode (3% risk):")
        print(f"  Notional Value: ${normal['notional_value']:,.2f}")
        print(f"  Quantity: {normal['quantity']:.4f} BTC")
        print(f"  Margin Required: ${normal['margin_required']:,.2f}")
        print(f"  Max Loss: ${normal['max_loss']:,.2f}")
        print()
        print(f"  💡 With {leverage}x leverage:")
        print(f"     - You control ${normal['notional_value']:,.2f} worth of BTC")
        print(f"     - But only need ${normal['margin_required']:,.2f} in margin")
        print(f"     - You can buy {normal['quantity']:.4f} BTC (${normal['quantity'] * entry:,.2f})")

    print("\n" + "="*70)
    print("KEY INSIGHTS:")
    print("="*70)
    print("""
1. Notional Value stays the same - this is the position size for your risk level
2. Margin Required decreases with higher leverage (capital efficiency)
3. Quantity increases proportionally with leverage
4. Max Loss stays the same - you're risking the same percentage regardless

Example: 100x leverage
- Notional: $15,000 (same as 1x)
- Margin: $150 (100x less capital needed)
- Quantity: 30 BTC (100x more coins)
- Risk: Still only $300 max loss (3% of $10,000)

⚠️  WARNING: Higher leverage = higher liquidation risk!
   While max loss per trade stays same, liquidation can occur faster.
""")


def example_symbol_leverage_config():
    """
    Example of how to configure leverage per symbol
    """
    print("\n" + "="*70)
    print("SYSTEM-LEVEL LEVERAGE CONFIGURATION")
    print("="*70 + "\n")

    print("""
Firebase Structure (system_configs collection):

Document: leverage_map
{
  "BTC": 100,
  "ETH": 75,
  "SOL": 50,
  "HYPE": 25,
  "DOGE": 20,
  "SHIB": 10
}

Usage in code:
-------------

from config import get_config_manager

# Get leverage for specific symbol
manager = get_config_manager()
btc_leverage = manager.get_leverage_for_symbol("BTC")  # Returns: 100
hype_leverage = manager.get_leverage_for_symbol("HYPE")  # Returns: 25
unknown_leverage = manager.get_leverage_for_symbol("NEWCOIN")  # Returns: 10 (default)

# Set leverage for new symbol
manager.set_leverage_for_symbol("AVAX", 50)

# Get all leverage mappings
all_leverages = manager.get_all_leverages()
# Returns: {'BTC': 100, 'ETH': 75, 'SOL': 50, ...}

# Initialize with defaults
manager.initialize_default_leverages()
""")

    print("\nLeverage Selection Guide:")
    print("-" * 70)
    print("  100x: Major coins (BTC) - high liquidity, stable")
    print("   75x: Large caps (ETH) - very liquid")
    print("   50x: Mid caps (SOL, AVAX) - good liquidity")
    print("   25x: Smaller caps (HYPE) - moderate liquidity")
    print("   10x: Micro caps / New tokens - default, safer")


if __name__ == "__main__":
    example_leverage_impact()
    example_symbol_leverage_config()
    print("\n" + "="*70)
    print("✅ Examples complete!")
    print("="*70 + "\n")
