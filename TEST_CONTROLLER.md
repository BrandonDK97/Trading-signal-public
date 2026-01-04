# Test Controller Documentation

The test controller provides API endpoints to test all functionality of the Trading Signal System without needing external integrations.

## Quick Start

### 1. Start the Test Controller

```bash
python test_controller.py
```

Server runs on: `http://localhost:8001`

### 2. Run Automated Tests

**Option A: Python Script (Recommended)**
```bash
python test_examples.py
```

**Option B: Bash Script**
```bash
./test_examples.sh
```

**Option C: Manual Testing with curl**
See examples below.

---

## API Endpoints

### Setup Endpoints

#### Initialize Default Leverages
```bash
POST /test/setup/leverages
```

Creates default leverage mappings:
- BTC: 100x
- ETH: 75x
- SOL: 50x
- HYPE: 25x
- etc.

**Example:**
```bash
curl -X POST http://localhost:8001/test/setup/leverages
```

#### Create Test User
```bash
POST /test/setup/user?telegram_handle=@john&balance=10000&risk_appetite=3
```

**Example:**
```bash
curl -X POST "http://localhost:8001/test/setup/user?telegram_handle=@john_trader&balance=10000&risk_appetite=3"
```

---

### Test Endpoints

#### 1. Get User Config

```bash
GET /test/user/{telegram_handle}
```

**Example:**
```bash
curl http://localhost:8001/test/user/@john_trader | jq '.'
```

**Response:**
```json
{
  "success": true,
  "data": {
    "telegram_handle": "john_trader",
    "account_balance": 10000.0,
    "risk_appetite": 3.0,
    "bybit_api_key": null,
    "created_at": "2025-01-04T10:30:00",
    "updated_at": "2025-01-04T10:30:00"
  }
}
```

---

#### 2. Update User Balance (Persistent)

```bash
PUT /test/user/{telegram_handle}/balance
```

**Example:**
```bash
curl -X PUT http://localhost:8001/test/user/@john_trader/balance \
  -H "Content-Type: application/json" \
  -d '{"balance": 15000}' | jq '.'
```

**Response:**
```json
{
  "success": true,
  "message": "Balance updated to $15,000.00",
  "data": {
    "telegram_handle": "john_trader",
    "account_balance": 15000.0,
    "risk_appetite": 3.0,
    ...
  }
}
```

**Verification:**
The balance is updated in Firebase and persists across server restarts.

---

#### 3. Change/Create Coin Leverage (Persistent)

```bash
PUT /test/leverage/{symbol}
```

**Example: Update existing leverage**
```bash
curl -X PUT http://localhost:8001/test/leverage/BTC \
  -H "Content-Type: application/json" \
  -d '{"leverage": 125}' | jq '.'
```

**Example: Create new coin leverage**
```bash
curl -X PUT http://localhost:8001/test/leverage/NEWCOIN \
  -H "Content-Type: application/json" \
  -d '{"leverage": 20}' | jq '.'
```

**Response:**
```json
{
  "success": true,
  "message": "Leverage for BTC set to 125x",
  "data": {
    "symbol": "BTC",
    "leverage": 125
  }
}
```

**Get leverage for symbol:**
```bash
curl http://localhost:8001/test/leverage/BTC | jq '.'
```

**Get all leverages:**
```bash
curl http://localhost:8001/test/leverages | jq '.'
```

---

#### 4. Test End-to-End Trade Message Flow

```bash
POST /test/trade
```

**Example 1: Single Entry Trade**
```bash
curl -X POST http://localhost:8001/test/trade \
  -H "Content-Type: application/json" \
  -d '{
    "message": "@SpaghettiRavioli longed BTC at 50000 sl: 49000"
  }' | jq '.'
```

**Example 2: Range Entry Trade**
```bash
curl -X POST http://localhost:8001/test/trade \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Tradoor long ETH 3000-2900 sl: 2850"
  }' | jq '.'
```

**Example 3: Short Trade**
```bash
curl -X POST http://localhost:8001/test/trade \
  -H "Content-Type: application/json" \
  -d '{
    "message": "@crypto_king shorted HYPE at 25.50 sl: 26.00"
  }' | jq '.'
```

**Response:**
```json
{
  "success": true,
  "data": {
    "signal_sender": "SpaghettiRavioli",
    "trade": {
      "symbol": "BTC",
      "direction": "long",
      "entry_type": "single",
      "entry": 50000,
      "stop_loss": 49000,
      "leverage": 100
    },
    "take_profits": {
      "tp1_price": 50500,
      "tp2_price": 51250,
      "tp1_percent": 35,
      "tp2_percent": 50,
      "manual_percent": 15,
      "direction": "long"
    },
    "users": [
      {
        "telegram_handle": "john_trader",
        "status": "calculated",
        "balance": 10000,
        "risk_tolerance": 3.0,
        "position_sizing": {
          "conservative": {
            "notional_value": 5000.00,
            "quantity": 10.0000,
            "margin_required": 50.00,
            "leverage": 100,
            "max_loss": 100.00,
            "risk_percent": 1.0
          },
          "normal": {
            "notional_value": 15000.00,
            "quantity": 30.0000,
            "margin_required": 150.00,
            "leverage": 100,
            "max_loss": 300.00,
            "risk_percent": 3.0
          },
          "aggressive": {
            "notional_value": 25000.00,
            "quantity": 50.0000,
            "margin_required": 250.00,
            "leverage": 100,
            "max_loss": 500.00,
            "risk_percent": 5.0
          }
        }
      }
    ],
    "summary": {
      "total_users": 3,
      "calculated_users": 3,
      "skipped_users": 0
    }
  }
}
```

---

### Additional Endpoints

#### Get All Users
```bash
GET /test/users
```

```bash
curl http://localhost:8001/test/users | jq '.'
```

#### Get All Leverages
```bash
GET /test/leverages
```

```bash
curl http://localhost:8001/test/leverages | jq '.'
```

---

## E2E Flow Explanation

When you call `POST /test/trade`, the system performs:

1. **Parse Message** (LLM Gateway)
   - Sends message to Claude API
   - Extracts symbol, direction, entry, stop loss

2. **Fetch Leverage** (System Config)
   - Looks up leverage for symbol in Firebase
   - Uses default 10x if not found

3. **Calculate Take Profits**
   - TP1: 0.5R (35% exit)
   - TP2: 1.25R (50% exit)
   - Manual: Remaining 15%

4. **Get All Users** (Firebase)
   - Fetches all user configurations
   - Skips users with zero balance

5. **Calculate Position Sizing** (Per User)
   - Conservative: risk - 2%
   - Normal: user's risk tolerance
   - Aggressive: risk + 2%
   - Applies leverage to quantity
   - Calculates margin required

6. **Return Results**
   - Trade details
   - Take profits
   - Position sizing for all users
   - Summary statistics

---

## Console Output

The test controller logs detailed information during trade processing:

```
======================================================================
🧪 TEST: Processing Trade Message
======================================================================
Message: @SpaghettiRavioli longed BTC at 50000 sl: 49000

✅ Step 1: Parsed trade data
   Symbol: BTC
   Direction: long
   Entry: 50000
   Stop Loss: 49000

✅ Step 2: Fetched leverage
   BTC: 100x

✅ Step 3: Calculated take profits
   TP1: 50500.0 (35%)
   TP2: 51250.0 (50%)

✅ Step 4: Fetched users
   Found 3 user(s)

   ✅ Calculated john_trader: 30.0 BTC
   ✅ Calculated alice_crypto: 75.0 BTC
   ✅ Calculated bob_degen: 15.0 BTC

✅ Step 5: Complete!
   Calculated: 3 users
   Skipped: 0 users
======================================================================
```

---

## Testing Workflow

### Typical Test Session

```bash
# 1. Start test controller
python test_controller.py

# 2. In another terminal, run tests
python test_examples.py

# OR test manually:

# Setup
curl -X POST http://localhost:8001/test/setup/leverages
curl -X POST "http://localhost:8001/test/setup/user?telegram_handle=@john&balance=10000&risk_appetite=3"

# Test operations
curl http://localhost:8001/test/user/@john | jq '.'
curl -X PUT http://localhost:8001/test/user/@john/balance -H "Content-Type: application/json" -d '{"balance": 15000}' | jq '.'
curl -X PUT http://localhost:8001/test/leverage/BTC -H "Content-Type: application/json" -d '{"leverage": 125}' | jq '.'

# Test E2E
curl -X POST http://localhost:8001/test/trade \
  -H "Content-Type: application/json" \
  -d '{"message": "@trader longed BTC at 50000 sl: 49000"}' | jq '.'
```

---

## Notes

- **Port**: Test controller runs on 8001 (production API on 8000)
- **Persistence**: All updates (balance, leverage) are saved to Firebase
- **Requirements**: Firebase credentials must be set in `.env`
- **Dependencies**: Requires ANTHROPIC_API_KEY for LLM parsing

---

## Troubleshooting

### Connection Refused
```
Error: Cannot connect to test controller
```
**Solution**: Start test controller with `python test_controller.py`

### Firebase Not Found
```
Error: FIREBASE_SERVICE_ACCOUNT_JSON environment variable is required
```
**Solution**: Set up `.env` file with Firebase credentials

### LLM Parsing Failed
```
Error: ANTHROPIC_API_KEY environment variable is required
```
**Solution**: Add ANTHROPIC_API_KEY to `.env` file

### User Not Found
```
Error: User @john_trader not found
```
**Solution**: Create user first with `POST /test/setup/user`

---

## API Documentation

For full API documentation, visit:
```
http://localhost:8001/docs
```

This opens the interactive Swagger UI with all endpoints documented.
