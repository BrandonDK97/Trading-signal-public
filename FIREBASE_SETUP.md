# Firebase Setup Guide

This guide walks you through setting up Firebase Firestore for the Trading Signal System.

---

## Step 1: Create Firebase Project

### 1.1 Go to Firebase Console
Visit: https://console.firebase.google.com/

### 1.2 Create New Project
1. Click **"Add project"** or **"Create a project"**
2. Enter project name: `trading-signal-system` (or your preferred name)
3. Click **Continue**
4. **Google Analytics**: Optional (you can disable it for simplicity)
5. Click **Create project**
6. Wait for project creation (takes ~30 seconds)
7. Click **Continue** when ready

---

## Step 2: Set Up Firestore Database

### 2.1 Create Firestore Database
1. In the Firebase Console, click **"Firestore Database"** in the left sidebar
2. Click **"Create database"**

### 2.2 Choose Security Mode
Select **"Start in test mode"** (for development)
- This allows read/write access for testing
- You'll secure it later for production

### 2.3 Select Location
Choose a location closest to your users:
- `us-central1` (USA)
- `europe-west1` (Europe)
- `asia-northeast1` (Asia)

Click **Enable**

---

## Step 3: Get Service Account Credentials

### 3.1 Access Project Settings
1. Click the **⚙️ gear icon** (Settings) in the left sidebar
2. Select **"Project settings"**

### 3.2 Navigate to Service Accounts
1. Click the **"Service accounts"** tab at the top
2. You should see: **"Firebase Admin SDK"**

### 3.3 Generate Private Key
1. Click **"Generate new private key"**
2. A popup appears: **"Generate new private key?"**
3. Click **"Generate key"**
4. A JSON file downloads automatically (keep it safe!)

**⚠️ IMPORTANT:**
- This JSON file contains sensitive credentials
- **Never commit it to git**
- **Never share it publicly**
- Store it securely

---

## Step 4: Configure Environment Variables

### 4.1 Open the Downloaded JSON File
Open the downloaded file (e.g., `trading-signal-system-abc123-firebase-adminsdk-xyz.json`)

It looks like this:
```json
{
  "type": "service_account",
  "project_id": "trading-signal-system-abc123",
  "private_key_id": "abc123def456...",
  "private_key": "-----BEGIN PRIVATE KEY-----\nMIIEvQIBA...\n-----END PRIVATE KEY-----\n",
  "client_email": "firebase-adminsdk-xyz@trading-signal-system-abc123.iam.gserviceaccount.com",
  "client_id": "123456789012345678901",
  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
  "token_uri": "https://oauth2.googleapis.com/token",
  "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
  "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/firebase-adminsdk-xyz%40trading-signal-system-abc123.iam.gserviceaccount.com"
}
```

### 4.2 Create .env File
In your project root directory, create a `.env` file:

```bash
# Copy from .env.example
cp .env.example .env
```

### 4.3 Add Firebase Credentials to .env

**Option A: Single-line JSON (Recommended for .env)**
1. Copy the entire JSON content
2. Remove all newlines and spaces (make it a single line)
3. Add to `.env`:

```bash
# .env file
FIREBASE_SERVICE_ACCOUNT_JSON='{"type":"service_account","project_id":"trading-signal-system-abc123","private_key_id":"abc123...","private_key":"-----BEGIN PRIVATE KEY-----\\nMIIEvQIBA...\\n-----END PRIVATE KEY-----\\n","client_email":"firebase-adminsdk-xyz@...","client_id":"123456789012345678901","auth_uri":"https://accounts.google.com/o/oauth2/auth","token_uri":"https://oauth2.googleapis.com/token","auth_provider_x509_cert_url":"https://www.googleapis.com/oauth2/v1/certs","client_x509_cert_url":"https://www.googleapis.com/robot/v1/metadata/..."}'

# Add your API keys
ANTHROPIC_API_KEY=your_anthropic_api_key_here
TELEGRAM_BOT_TOKEN=your_telegram_bot_token_here
```

**⚠️ Important:**
- Replace `\n` in the private_key with `\\n` (double backslash)
- Use single quotes around the JSON string
- No spaces after `=`

**Option B: Using a separate file**
1. Save the JSON file as `firebase-credentials.json` in your project root
2. Add to `.env`:
```bash
FIREBASE_CREDENTIALS_PATH=./firebase-credentials.json
```
3. Update `config.py` to read from file path (requires code modification)

---

## Step 5: Initialize Firestore Collections

### 5.1 Install Dependencies
```bash
pip install -r requirements.txt
```

### 5.2 Initialize Default Leverages

Run this Python script to set up the leverage map:

```bash
python -c "
from config import get_config_manager

manager = get_config_manager()
result = manager.initialize_default_leverages()

if result:
    print('✅ Default leverages initialized!')
    leverages = manager.get_all_leverages()
    for symbol, lev in leverages.items():
        print(f'  {symbol}: {lev}x')
else:
    print('❌ Failed to initialize leverages')
"
```

This creates the `system_configs/leverage_map` document with:
- BTC: 100x
- ETH: 75x
- SOL: 50x
- HYPE: 25x
- AVAX: 50x
- MATIC: 50x
- DOT: 50x
- LINK: 50x
- UNI: 50x
- AAVE: 50x

### 5.3 Create Test Users

Run this to create test users:

```bash
python -c "
from config import get_config_manager

manager = get_config_manager()

# Create users
users = [
    ('john_trader', 10000, 3.0),
    ('alice_crypto', 25000, 2.0),
    ('bob_degen', 5000, 5.0)
]

for handle, balance, risk in users:
    success = manager.create_user_config(
        telegram_handle=handle,
        account_balance=balance,
        risk_appetite=risk
    )
    if success:
        print(f'✅ Created user: @{handle}')
    else:
        print(f'⚠️  User @{handle} already exists')
"
```

---

## Step 6: Verify Setup

### 6.1 Check Firestore Console
1. Go to Firebase Console → Firestore Database
2. You should see two collections:
   - `user_configs` (with documents: john_trader, alice_crypto, bob_degen)
   - `system_configs` (with document: leverage_map)

### 6.2 Test with Test Controller

Start the test controller:
```bash
python test_controller.py
```

Test the setup:
```bash
# Get all users
curl http://localhost:8001/test/users | jq '.'

# Get all leverages
curl http://localhost:8001/test/leverages | jq '.'

# Get specific user
curl http://localhost:8001/test/user/@john_trader | jq '.'
```

### 6.3 Test E2E Flow
```bash
curl -X POST http://localhost:8001/test/trade \
  -H "Content-Type: application/json" \
  -d '{
    "message": "@trader longed BTC at 50000 sl: 49000"
  }' | jq '.'
```

If you see position sizing results, Firebase is working! ✅

---

## Firestore Data Structure

### Collection: `user_configs`
```
user_configs/
├── john_trader/
│   ├── telegram_handle: "john_trader"
│   ├── account_balance: 10000.0
│   ├── risk_appetite: 3.0
│   ├── bybit_api_key: null
│   ├── bybit_api_secret: null
│   ├── created_at: "2025-01-04T10:30:00"
│   └── updated_at: "2025-01-04T10:30:00"
│
├── alice_crypto/
│   └── ...
│
└── bob_degen/
    └── ...
```

### Collection: `system_configs`
```
system_configs/
└── leverage_map/
    ├── BTC: 100
    ├── ETH: 75
    ├── SOL: 50
    ├── HYPE: 25
    └── ...
```

---

## Security Configuration (Production)

### For Production, Update Firestore Rules:

1. Go to **Firestore Database** → **Rules** tab
2. Replace with:

```javascript
rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {
    // User configs - authenticated read/write
    match /user_configs/{userId} {
      allow read, write: if request.auth != null;
    }

    // System configs - authenticated read only
    match /system_configs/{document} {
      allow read: if request.auth != null;
      allow write: if request.auth.token.admin == true;
    }
  }
}
```

3. Click **Publish**

---

## Troubleshooting

### Error: "FIREBASE_SERVICE_ACCOUNT_JSON environment variable is required"
**Solution:** Make sure `.env` file exists and contains the Firebase credentials

### Error: "Failed to initialize Firebase"
**Solution:**
- Check JSON formatting (especially `\n` → `\\n` in private_key)
- Ensure no extra spaces in `.env`
- Verify the JSON is wrapped in single quotes

### Error: "Permission denied"
**Solution:**
- Check Firestore security rules
- For development, use "test mode" rules
- Verify service account has proper permissions

### Error: "Module 'firebase_admin' not found"
**Solution:**
```bash
pip install firebase-admin
```

### Firestore Collections Not Created
**Solution:**
- Run the initialization scripts (Step 5.2 and 5.3)
- Check Firebase Console for any errors
- Verify `.env` credentials are correct

---

## Quick Setup Script

Save this as `setup_firebase.py`:

```python
"""
Quick Firebase setup script
Initializes leverages and creates test users
"""

from config import get_config_manager

def setup():
    print("\n" + "="*70)
    print("🔥 FIREBASE SETUP")
    print("="*70 + "\n")

    manager = get_config_manager()

    # Initialize leverages
    print("1. Initializing default leverages...")
    if manager.initialize_default_leverages():
        leverages = manager.get_all_leverages()
        print(f"   ✅ Created {len(leverages)} leverage mappings")
    else:
        print("   ❌ Failed to initialize leverages")
        return

    # Create test users
    print("\n2. Creating test users...")
    users = [
        ('john_trader', 10000, 3.0),
        ('alice_crypto', 25000, 2.0),
        ('bob_degen', 5000, 5.0)
    ]

    created = 0
    for handle, balance, risk in users:
        if manager.create_user_config(handle, balance, risk):
            print(f"   ✅ Created: @{handle}")
            created += 1
        else:
            print(f"   ⚠️  Exists: @{handle}")

    print(f"\n✅ Setup complete!")
    print(f"   Users: {created} created")
    print(f"   Leverages: {len(leverages)} symbols")
    print("\n" + "="*70 + "\n")

if __name__ == "__main__":
    setup()
```

Run it:
```bash
python setup_firebase.py
```

---

## Next Steps

After Firebase is set up:

1. ✅ Firebase configured
2. ✅ Collections initialized
3. ✅ Test users created
4. → Set up Anthropic API key (for LLM parsing)
5. → Set up Telegram Bot Token (for notifications)
6. → Test the complete system
7. → Deploy to production

---

## Summary

**What you need:**
1. Firebase project created
2. Firestore database enabled
3. Service account JSON downloaded
4. Credentials in `.env` file
5. Collections initialized (leverage_map + test users)

**Verify everything works:**
```bash
python test_controller.py
# In another terminal:
curl http://localhost:8001/test/users | jq '.'
```

If you see your test users, you're all set! 🚀
