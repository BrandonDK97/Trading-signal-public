"""
Examples of using Config Manager with Firebase

Shows how to integrate user configuration management into your trading system.
"""

from config import (
    ConfigManager,
    get_config_manager,
    get_user_balance,
    get_user_risk,
    update_user_balance,
    update_user_risk
)


def example_1_create_users():
    """Example 1: Create multiple users"""
    print("=== Example 1: Creating Users ===\n")

    manager = get_config_manager()

    # Create users with different configurations
    users = [
        {
            'handle': '@john_trader',
            'balance': 10000,
            'risk': 3.0
        },
        {
            'handle': '@alice_crypto',
            'balance': 25000,
            'risk': 2.0
        },
        {
            'handle': '@bob_degen',
            'balance': 5000,
            'risk': 5.0
        }
    ]

    for user in users:
        success = manager.create_user_config(
            telegram_handle=user['handle'],
            account_balance=user['balance'],
            risk_appetite=user['risk']
        )
        print(f"{'✅' if success else '❌'} Created {user['handle']}: ${user['balance']:,.2f} @ {user['risk']}% risk")

    print()


def example_2_get_user_for_trade():
    """Example 2: Get user config when processing trade signal"""
    print("=== Example 2: Get User Config for Trade ===\n")

    # Simulate receiving a trade signal with telegram handle
    incoming_signal = {
        'telegram_handle': '@john_trader',
        'message': 'longed BTC at 50000 sl: 49000'
    }

    # Get user configuration
    config = get_config_manager().get_user_config(incoming_signal['telegram_handle'])

    if config:
        print(f"User found: {config['telegram_handle']}")
        print(f"Account Balance: ${config['account_balance']:,.2f}")
        print(f"Risk Appetite: {config['risk_appetite']}%")
        print(f"\nReady to calculate position sizing...")
    else:
        print(f"❌ User {incoming_signal['telegram_handle']} not found in database")

    print()


def example_3_update_after_trade():
    """Example 3: Update user balance after trade profit/loss"""
    print("=== Example 3: Update Balance After Trade ===\n")

    telegram_handle = '@john_trader'

    # Get current balance
    current_balance = get_user_balance(telegram_handle)
    print(f"Current Balance: ${current_balance:,.2f}")

    # Simulate trade profit
    trade_profit = 500
    new_balance = current_balance + trade_profit

    # Update balance
    success = update_user_balance(telegram_handle, new_balance)

    if success:
        print(f"✅ Updated balance: ${new_balance:,.2f} (+${trade_profit:,.2f})")
    else:
        print("❌ Failed to update balance")

    print()


def example_4_integration_with_rest_api():
    """Example 4: How to integrate with REST API"""
    print("=== Example 4: REST API Integration Pattern ===\n")

    print("""
    # In rest_api.py, modify the /signal endpoint:

    from config import get_user_balance, get_user_risk

    @app.post("/signal")
    async def process_signal(request: SignalRequest):
        # Parse the trade signal
        trade_data = parse_trade_signal(request.message)

        # Get user config from Firebase (instead of using request.balance/risk)
        telegram_handle = request.telegram_handle  # Add this to SignalRequest

        balance = get_user_balance(telegram_handle)
        risk = get_user_risk(telegram_handle)

        if balance == 0:
            return SignalResponse(
                success=False,
                error=f"User {telegram_handle} not found or has no balance"
            )

        # Calculate position sizing using Firebase config
        position_sizing = calculate_all_position_sizing_modes(
            entry=trade_data['entry'],
            stop_loss=trade_data['stop_loss'],
            balance=balance,  # From Firebase
            user_risk_tolerance=risk  # From Firebase
        )

        # ... rest of processing
    """)

    print()


def example_5_list_all_users():
    """Example 5: Get all users for admin dashboard"""
    print("=== Example 5: List All Users ===\n")

    manager = get_config_manager()
    users = manager.get_all_users()

    print(f"Total Users: {len(users)}\n")

    for i, user in enumerate(users, 1):
        print(f"{i}. {user['telegram_handle']}")
        print(f"   Balance: ${user['account_balance']:,.2f}")
        print(f"   Risk: {user['risk_appetite']}%")
        print(f"   Created: {user.get('created_at', 'N/A')}")
        print()


def example_6_update_risk_tolerance():
    """Example 6: Update user's risk tolerance"""
    print("=== Example 6: Update Risk Tolerance ===\n")

    telegram_handle = '@alice_crypto'

    current_risk = get_user_risk(telegram_handle)
    print(f"Current Risk: {current_risk}%")

    # User wants to be more aggressive
    new_risk = 4.0
    success = update_user_risk(telegram_handle, new_risk)

    if success:
        print(f"✅ Updated risk tolerance: {new_risk}%")
    else:
        print("❌ Failed to update risk")

    print()


def example_7_add_bybit_credentials():
    """Example 7: Add Bybit API credentials (for future auto-trading)"""
    print("=== Example 7: Add Bybit API Credentials ===\n")

    manager = get_config_manager()

    success = manager.update_user_config(
        telegram_handle='@john_trader',
        bybit_api_key='your_api_key_here',
        bybit_api_secret='your_api_secret_here'
    )

    if success:
        print("✅ Bybit credentials added")
        print("   (These will be used for auto-trading in the future)")
    else:
        print("❌ Failed to add credentials")

    print()


# Modified SignalRequest model for REST API
def example_8_modified_api_models():
    """Example 8: Modified API models to work with Firebase"""
    print("=== Example 8: Modified API Models ===\n")

    print("""
    # Updated SignalRequest in rest_api.py:

    class SignalRequest(BaseModel):
        message: str
        telegram_handle: str  # NEW: Required for Firebase lookup
        # balance and risk_tolerance removed - get from Firebase instead

    # Example request:
    POST /signal
    {
        "message": "longed BTC at 50000 sl: 49000",
        "telegram_handle": "@john_trader"
    }

    # System will:
    # 1. Look up user in Firebase by telegram_handle
    # 2. Get their balance and risk appetite
    # 3. Calculate position sizing
    # 4. Return personalized result
    """)

    print()


if __name__ == "__main__":
    print("\n" + "="*60)
    print("FIREBASE CONFIG MANAGER - USAGE EXAMPLES")
    print("="*60 + "\n")

    try:
        # Run examples
        example_1_create_users()
        example_2_get_user_for_trade()
        example_3_update_after_trade()
        example_4_integration_with_rest_api()
        example_5_list_all_users()
        example_6_update_risk_tolerance()
        example_7_add_bybit_credentials()
        example_8_modified_api_models()

        print("="*60)
        print("✅ All examples completed!")
        print("="*60)

    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("\nMake sure you have:")
        print("1. Set FIREBASE_SERVICE_ACCOUNT_JSON in .env")
        print("2. Created a Firebase project")
        print("3. Installed firebase-admin: pip install firebase-admin")
