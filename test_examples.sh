#!/bin/bash

# Test Examples for Trading Signal System
# Make sure the test controller is running: python test_controller.py

BASE_URL="http://localhost:8001"

echo "========================================================================"
echo "🧪 TRADING SIGNAL SYSTEM - TEST EXAMPLES"
echo "========================================================================"
echo ""

# ============================================================================
# Setup: Create test users and initialize leverages
# ============================================================================

echo "📋 SETUP: Creating test users and initializing leverages"
echo "------------------------------------------------------------------------"

echo ""
echo "1. Initialize default leverages..."
curl -X POST "$BASE_URL/test/setup/leverages" \
  -H "Content-Type: application/json" | jq '.'

echo ""
echo "2. Create test user: @john_trader..."
curl -X POST "$BASE_URL/test/setup/user?telegram_handle=@john_trader&balance=10000&risk_appetite=3" \
  -H "Content-Type: application/json" | jq '.'

echo ""
echo "3. Create test user: @alice_crypto..."
curl -X POST "$BASE_URL/test/setup/user?telegram_handle=@alice_crypto&balance=25000&risk_appetite=2" \
  -H "Content-Type: application/json" | jq '.'

echo ""
echo "4. Create test user: @bob_degen..."
curl -X POST "$BASE_URL/test/setup/user?telegram_handle=@bob_degen&balance=5000&risk_appetite=5" \
  -H "Content-Type: application/json" | jq '.'

# ============================================================================
# Test 1: Get user config
# ============================================================================

echo ""
echo ""
echo "========================================================================"
echo "TEST 1: Get User Config"
echo "========================================================================"

echo ""
echo "GET /test/user/@john_trader"
curl -X GET "$BASE_URL/test/user/@john_trader" \
  -H "Content-Type: application/json" | jq '.'

# ============================================================================
# Test 2: Update user balance (persistent)
# ============================================================================

echo ""
echo ""
echo "========================================================================"
echo "TEST 2: Update User Balance (Persistent)"
echo "========================================================================"

echo ""
echo "PUT /test/user/@john_trader/balance - Update to \$15,000"
curl -X PUT "$BASE_URL/test/user/@john_trader/balance" \
  -H "Content-Type: application/json" \
  -d '{"balance": 15000}' | jq '.'

echo ""
echo "Verify balance was updated..."
curl -X GET "$BASE_URL/test/user/@john_trader" \
  -H "Content-Type: application/json" | jq '.data.account_balance'

# ============================================================================
# Test 3: Change/create coin leverage (persistent)
# ============================================================================

echo ""
echo ""
echo "========================================================================"
echo "TEST 3: Change/Create Coin Leverage (Persistent)"
echo "========================================================================"

echo ""
echo "PUT /test/leverage/BTC - Update BTC to 125x"
curl -X PUT "$BASE_URL/test/leverage/BTC" \
  -H "Content-Type: application/json" \
  -d '{"leverage": 125}' | jq '.'

echo ""
echo "PUT /test/leverage/NEWCOIN - Create new coin with 20x leverage"
curl -X PUT "$BASE_URL/test/leverage/NEWCOIN" \
  -H "Content-Type: application/json" \
  -d '{"leverage": 20}' | jq '.'

echo ""
echo "GET /test/leverage/BTC - Verify BTC leverage"
curl -X GET "$BASE_URL/test/leverage/BTC" \
  -H "Content-Type: application/json" | jq '.'

echo ""
echo "GET /test/leverages - Get all leverages"
curl -X GET "$BASE_URL/test/leverages" \
  -H "Content-Type: application/json" | jq '.'

# ============================================================================
# Test 4: End-to-End Trade Message Processing
# ============================================================================

echo ""
echo ""
echo "========================================================================"
echo "TEST 4: End-to-End Trade Message Processing"
echo "========================================================================"

echo ""
echo "POST /test/trade - Single entry BTC trade"
curl -X POST "$BASE_URL/test/trade" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "@SpaghettiRavioli longed BTC at 50000 sl: 49000"
  }' | jq '.'

echo ""
echo ""
echo "POST /test/trade - Range entry ETH trade"
curl -X POST "$BASE_URL/test/trade" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Tradoor long ETH 3000-2900 sl: 2850"
  }' | jq '.'

echo ""
echo ""
echo "POST /test/trade - HYPE trade with lower leverage"
curl -X POST "$BASE_URL/test/trade" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "@crypto_king shorted HYPE at 25.50 sl: 26.00"
  }' | jq '.'

# ============================================================================
# Additional Tests
# ============================================================================

echo ""
echo ""
echo "========================================================================"
echo "ADDITIONAL: Get All Users and Leverages"
echo "========================================================================"

echo ""
echo "GET /test/users - Get all users"
curl -X GET "$BASE_URL/test/users" \
  -H "Content-Type: application/json" | jq '.'

echo ""
echo ""
echo "========================================================================"
echo "✅ All tests complete!"
echo "========================================================================"
echo ""
