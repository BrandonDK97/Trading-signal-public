# Firebase Data Import Guide

This directory contains JSON files for importing test data into Firebase Firestore.

---

## 📁 Files

- **`user_configs.json`** - User-level configurations (5 test users)
- **`system_configs.json`** - System-level configurations (leverage map with 44+ coins)

---

## 📊 Data Overview

### User Configs (5 users)
| User | Balance | Risk | Profile |
|------|---------|------|---------|
| john_trader | $10,000 | 3% | Average trader |
| alice_crypto | $25,000 | 2% | Conservative, higher capital |
| bob_degen | $5,000 | 5% | Aggressive, smaller capital |
| test_whale | $100,000 | 2.5% | Large capital |
| conservative_trader | $15,000 | 1% | Very conservative |

### System Configs (Leverage Map)
| Category | Leverage | Examples |
|----------|----------|----------|
| Major | 75-100x | BTC (100x), ETH (75x) |
| Large Cap | 50x | SOL, AVAX, MATIC, DOT, LINK |
| Mid Cap | 40x | APT, SUI, SEI, INJ, TIA |
| Meme Coins | 20-25x | DOGE, SHIB, PEPE, WIF, BONK |
| DeFi | 40x | AAVE, MKR, COMP, SUSHI, CRV |

---

## 🚀 Import Methods

### Method 1: Manual Import via Firebase Console (Easiest)

#### Step 1: Go to Firestore Database
1. Open Firebase Console: https://console.firebase.google.com
2. Select your project
3. Click "Firestore Database" in left sidebar

#### Step 2: Import User Configs
1. Click **"Start collection"** (or use existing `user_configs` collection)
2. Collection ID: `user_configs`
3. For each user in `user_configs.json`:
   - Click **"Add document"**
   - Document ID: Enter the username (e.g., `john_trader`)
   - Add fields manually:
     - `telegram_handle` (string): `john_trader`
     - `account_balance` (number): `10000`
     - `risk_appetite` (number): `3`
     - `bybit_api_key` (null)
     - `bybit_api_secret` (null)
     - `created_at` (string): `2025-01-04T10:00:00Z`
     - `updated_at` (string): `2025-01-04T10:00:00Z`
   - Click **"Save"**
   - Repeat for all 5 users

#### Step 3: Import System Configs
1. Create new collection: `system_configs`
2. Click **"Add document"**
3. Document ID: `leverage_map`
4. For each coin in `system_configs.json`:
   - Add field:
     - Field name: `BTC` (or coin symbol)
     - Field type: number
     - Value: `100` (or leverage value)
   - Click "+" to add next field
   - Repeat for all coins
5. Click **"Save"**

---

### Method 2: Import via Firebase CLI (Advanced)

#### Prerequisites
```bash
# Install Firebase CLI
npm install -g firebase-tools

# Login to Firebase
firebase login

# Initialize Firebase in your project
firebase init firestore
```

#### Import Process
Unfortunately, Firebase doesn't support direct JSON import for Firestore. You need to use the Firebase Admin SDK (which is what our Python scripts do).

**Recommended:** Use Method 3 instead.

---

### Method 3: Import via Python Script (Recommended)

This is the easiest automated method.

#### Step 1: Ensure .env is configured
Make sure your `.env` file has Firebase credentials:
```bash
FIREBASE_SERVICE_ACCOUNT_JSON='{"type":"service_account",...}'
```

#### Step 2: Run setup script
```bash
python setup_firebase.py
```

This automatically imports all data!

---

### Method 4: Import Individual Documents via curl

If you want to test the API:

```bash
# Create a user
curl -X POST "http://localhost:8001/test/setup/user?telegram_handle=john_trader&balance=10000&risk_appetite=3"

# Set leverage
curl -X PUT http://localhost:8001/test/leverage/BTC \
  -H "Content-Type: application/json" \
  -d '{"leverage": 100}'
```

---

## 🔍 Verify Import

### Via Firebase Console
1. Go to Firestore Database
2. Check collections exist:
   - `user_configs` (5 documents)
   - `system_configs` (1 document: leverage_map)

### Via API
```bash
# Start test controller
python test_controller.py

# Check users
curl http://localhost:8001/test/users | jq '.'

# Check leverages
curl http://localhost:8001/test/leverages | jq '.'

# Expected output:
# {
#   "success": true,
#   "count": 5,
#   "data": [...]
# }
```

### Via Python
```python
from config import get_config_manager

manager = get_config_manager()

# Check users
users = manager.get_all_users()
print(f"Users: {len(users)}")  # Should be 5

# Check leverages
leverages = manager.get_all_leverages()
print(f"Leverages: {len(leverages)}")  # Should be 44+
print(f"BTC: {leverages.get('BTC')}x")  # Should be 100
```

---

## 📝 Customization

### Add Your Own User
Edit `user_configs.json` and add:
```json
"your_username": {
  "telegram_handle": "your_username",
  "account_balance": 50000.0,
  "risk_appetite": 2.5,
  "bybit_api_key": null,
  "bybit_api_secret": null,
  "created_at": "2025-01-04T10:00:00Z",
  "updated_at": "2025-01-04T10:00:00Z"
}
```

### Add New Coin Leverage
Edit `system_configs.json` → `leverage_map` and add:
```json
"YOURCOIN": 50
```

Then re-import!

---

## 🎯 Quick Start

**Fastest way to get testing:**

```bash
# 1. Configure .env with Firebase credentials
# 2. Run setup script
python setup_firebase.py

# 3. Verify
python test_controller.py
# In another terminal:
curl http://localhost:8001/test/users | jq '.'

# 4. Test E2E
curl -X POST http://localhost:8001/test/trade \
  -H "Content-Type: application/json" \
  -d '{"message": "@trader longed BTC at 50000 sl: 49000"}' | jq '.'
```

---

## 💡 Notes

- **Document IDs:** Must match telegram_handle (without @)
- **Null values:** Use `null` not empty string
- **Numbers:** Don't use quotes (e.g., `10000` not `"10000"`)
- **Timestamps:** ISO 8601 format recommended
- **Case sensitive:** Symbol names are converted to uppercase in code

---

## 🔒 Production Data

For production:
1. Remove test users
2. Add real user data (with proper authentication)
3. Adjust leverage values based on your risk policy
4. Enable Firestore security rules
5. Add API key fields when ready

---

## Questions?

Check `FIREBASE_SETUP.md` for detailed Firebase configuration guide.
