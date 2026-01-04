"""
Test Examples for Trading Signal System

Run this script to test all endpoints of the test controller.
Make sure the test controller is running first: python test_controller.py
"""

import requests
import json
from typing import Dict, Any

BASE_URL = "http://localhost:8001"


def print_section(title: str):
    """Print a formatted section header"""
    print("\n" + "="*70)
    print(title)
    print("="*70 + "\n")


def print_response(response: requests.Response, title: str = ""):
    """Print formatted API response"""
    if title:
        print(f"\n{title}")
        print("-" * 70)

    print(f"Status: {response.status_code}")
    try:
        data = response.json()
        print(json.dumps(data, indent=2))
    except:
        print(response.text)


def setup_test_environment():
    """Setup: Create test users and initialize leverages"""
    print_section("📋 SETUP: Creating Test Environment")

    # Initialize default leverages
    print("1. Initializing default leverages...")
    response = requests.post(f"{BASE_URL}/test/setup/leverages")
    print_response(response)

    # Create test users
    users = [
        ("@john_trader", 10000, 3.0),
        ("@alice_crypto", 25000, 2.0),
        ("@bob_degen", 5000, 5.0)
    ]

    for i, (handle, balance, risk) in enumerate(users, 2):
        print(f"\n{i}. Creating user {handle}...")
        response = requests.post(
            f"{BASE_URL}/test/setup/user",
            params={
                "telegram_handle": handle,
                "balance": balance,
                "risk_appetite": risk
            }
        )
        print_response(response)


def test_get_user_config():
    """Test 1: Get user config"""
    print_section("TEST 1: Get User Config")

    response = requests.get(f"{BASE_URL}/test/user/@john_trader")
    print_response(response, "GET /test/user/@john_trader")


def test_update_balance():
    """Test 2: Update user balance (persistent)"""
    print_section("TEST 2: Update User Balance (Persistent)")

    # Update balance
    print("Updating @john_trader balance to $15,000...")
    response = requests.put(
        f"{BASE_URL}/test/user/@john_trader/balance",
        json={"balance": 15000}
    )
    print_response(response)

    # Verify update
    print("\nVerifying balance was updated...")
    response = requests.get(f"{BASE_URL}/test/user/@john_trader")
    data = response.json()
    balance = data['data']['account_balance']
    print(f"✅ New balance: ${balance:,.2f}")


def test_change_leverage():
    """Test 3: Change/create coin leverage (persistent)"""
    print_section("TEST 3: Change/Create Coin Leverage (Persistent)")

    # Update existing leverage
    print("Updating BTC leverage to 125x...")
    response = requests.put(
        f"{BASE_URL}/test/leverage/BTC",
        json={"leverage": 125}
    )
    print_response(response)

    # Create new leverage
    print("\nCreating new coin NEWCOIN with 20x leverage...")
    response = requests.put(
        f"{BASE_URL}/test/leverage/NEWCOIN",
        json={"leverage": 20}
    )
    print_response(response)

    # Verify
    print("\nVerifying BTC leverage...")
    response = requests.get(f"{BASE_URL}/test/leverage/BTC")
    print_response(response)

    # Get all leverages
    print("\nGetting all leverages...")
    response = requests.get(f"{BASE_URL}/test/leverages")
    data = response.json()
    print(f"Total leverages: {data['count']}")
    print(json.dumps(data['data'], indent=2))


def test_trade_message():
    """Test 4: End-to-end trade message processing"""
    print_section("TEST 4: End-to-End Trade Message Processing")

    test_messages = [
        {
            "name": "Single Entry BTC Trade",
            "message": "@SpaghettiRavioli longed BTC at 50000 sl: 49000"
        },
        {
            "name": "Range Entry ETH Trade",
            "message": "Tradoor long ETH 3000-2900 sl: 2850"
        },
        {
            "name": "HYPE Short Trade",
            "message": "@crypto_king shorted HYPE at 25.50 sl: 26.00"
        }
    ]

    for test in test_messages:
        print(f"\n{'─'*70}")
        print(f"Test: {test['name']}")
        print(f"Message: {test['message']}")
        print(f"{'─'*70}")

        response = requests.post(
            f"{BASE_URL}/test/trade",
            json={"message": test['message']}
        )

        if response.status_code == 200:
            data = response.json()['data']

            # Print summary
            print(f"\n📊 Trade Summary:")
            print(f"   Symbol: {data['trade']['symbol']}")
            print(f"   Direction: {data['trade']['direction']}")
            print(f"   Entry: {data['trade']['entry']}")
            print(f"   Stop Loss: {data['trade']['stop_loss']}")
            print(f"   Leverage: {data['trade']['leverage']}x")

            print(f"\n💰 Take Profits:")
            print(f"   TP1: {data['take_profits']['tp1_price']} ({data['take_profits']['tp1_percent']}%)")
            print(f"   TP2: {data['take_profits']['tp2_price']} ({data['take_profits']['tp2_percent']}%)")

            print(f"\n👥 Users Processed:")
            print(f"   Total: {data['summary']['total_users']}")
            print(f"   Calculated: {data['summary']['calculated_users']}")
            print(f"   Skipped: {data['summary']['skipped_users']}")

            # Print position sizing for each user
            for user in data['users']:
                if user['status'] == 'calculated':
                    normal = user['position_sizing']['normal']
                    print(f"\n   📈 {user['telegram_handle']}:")
                    print(f"      Balance: ${user['balance']:,.2f}")
                    print(f"      Risk: {user['risk_tolerance']}%")
                    print(f"      Quantity: {normal['quantity']} {data['trade']['symbol']}")
                    print(f"      Margin Required: ${normal['margin_required']:,.2f}")
                    print(f"      Max Loss: ${normal['max_loss']:,.2f}")
        else:
            print_response(response)


def test_get_all():
    """Additional: Get all users and leverages"""
    print_section("ADDITIONAL: Get All Users and Leverages")

    # Get all users
    print("Getting all users...")
    response = requests.get(f"{BASE_URL}/test/users")
    data = response.json()
    print(f"\nTotal users: {data['count']}")
    for user in data['data']:
        print(f"  - {user['telegram_handle']}: ${user['account_balance']:,.2f} (Risk: {user['risk_appetite']}%)")

    # Get all leverages
    print("\n\nGetting all leverages...")
    response = requests.get(f"{BASE_URL}/test/leverages")
    data = response.json()
    print(f"\nTotal symbols: {data['count']}")
    for symbol, leverage in sorted(data['data'].items()):
        print(f"  - {symbol}: {leverage}x")


def main():
    """Run all tests"""
    print("\n" + "="*70)
    print("🧪 TRADING SIGNAL SYSTEM - TEST EXAMPLES")
    print("="*70)
    print("\nMake sure test_controller.py is running on port 8001!")
    print("Start it with: python test_controller.py\n")

    try:
        # Check if server is running
        response = requests.get(f"{BASE_URL}/")
        if response.status_code != 200:
            print("❌ Test controller is not responding!")
            return
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to test controller!")
        print("Please start it first: python test_controller.py")
        return

    # Run all tests
    setup_test_environment()
    test_get_user_config()
    test_update_balance()
    test_change_leverage()
    test_trade_message()
    test_get_all()

    print("\n" + "="*70)
    print("✅ All tests complete!")
    print("="*70 + "\n")


if __name__ == "__main__":
    main()
