"""
Configuration Manager with Firebase Integration

Manages user configurations stored in Firebase Firestore.
Stores: telegram_handle, account_balance, risk_appetite, and future bybit_api_key.

TODO: SECURITY ENHANCEMENT - RSA Public/Private Key Authentication
================================================================

Current Status: ⚠️ No authentication required to fetch configs from Firebase
Security Risk: Anyone with Firebase access can read all user configurations

Proposed Implementation:
------------------------

1. RSA Key Pair Generation:
   - Generate RSA public/private key pair
   - Private key: Store securely on local system (environment variable or file)
   - Public key: Store in Firebase Firestore (in separate 'api_keys' collection)

2. Authentication Flow:
   a) Client signs request with private key
   b) Include signature in request header/payload
   c) Server fetches public key from Firebase
   d) Server verifies signature using public key
   e) If valid, allow config fetch; otherwise, reject

3. Implementation Steps:

   Step 1: Key Generation & Storage
   ---------------------------------
   - Use cryptography library: `from cryptography.hazmat.primitives.asymmetric import rsa`
   - Generate 2048-bit RSA key pair
   - Store private key in .env as PEM format: FIREBASE_PRIVATE_KEY
   - Store public key in Firebase collection:
     {
       "api_keys": {
         "main_api": {
           "public_key": "-----BEGIN PUBLIC KEY-----...",
           "created_at": "2025-01-04",
           "enabled": true
         }
       }
     }

   Step 2: Request Signing
   -----------------------
   - Create request payload: {"timestamp": <unix_time>, "action": "get_config"}
   - Sign payload with private key using PKCS#1 v1.5 or PSS padding
   - Include signature in API request

   Step 3: Signature Verification
   ------------------------------
   - Add verify_signature() method to ConfigManager
   - Fetch public key from Firebase
   - Verify signature matches payload
   - Check timestamp (prevent replay attacks - max 60 seconds old)

   Step 4: Update All Methods
   --------------------------
   - Add signature parameter to: get_user_config(), get_all_users(), etc.
   - Verify signature before allowing data access
   - Return 401 Unauthorized if signature invalid

4. Example Code Structure:

   from cryptography.hazmat.primitives import hashes, serialization
   from cryptography.hazmat.primitives.asymmetric import padding, rsa

   class SecureConfigManager(ConfigManager):
       def verify_signature(self, payload: str, signature: bytes) -> bool:
           # Fetch public key from Firebase
           # Verify signature
           # Check timestamp
           pass

       def get_user_config(self, telegram_handle: str, signature: bytes, timestamp: int):
           if not self.verify_signature(f"{telegram_handle}:{timestamp}", signature):
               raise PermissionError("Invalid signature")
           # ... existing logic

5. Environment Variables Required:
   FIREBASE_PRIVATE_KEY=-----BEGIN RSA PRIVATE KEY-----...
   FIREBASE_KEY_ID=main_api

6. Benefits:
   ✅ Prevents unauthorized config access
   ✅ No shared secrets (asymmetric encryption)
   ✅ Public key can be safely stored in Firebase
   ✅ Rotate keys without changing all clients (just update Firebase public key)
   ✅ Can track which API key accessed what data

7. Additional Considerations:
   - Implement key rotation mechanism (monthly/quarterly)
   - Add rate limiting per API key
   - Log all access attempts with signature verification results
   - Support multiple API keys for different services
   - Add API key enable/disable toggle in Firebase

Priority: HIGH (before production deployment)
Estimated Effort: 4-6 hours
Dependencies: cryptography library (pip install cryptography)

"""

import os
import json
from typing import Dict, Optional, List
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

try:
    import firebase_admin
    from firebase_admin import credentials, firestore
    FIREBASE_AVAILABLE = True
except ImportError:
    FIREBASE_AVAILABLE = False
    print("Warning: Firebase dependencies not installed. Run: pip install firebase-admin")


class ConfigManager:
    """Manages user configurations in Firebase Firestore"""

    def __init__(self):
        """Initialize Firebase connection"""
        if not FIREBASE_AVAILABLE:
            raise ImportError("Firebase Admin SDK not installed. Install with: pip install firebase-admin")

        # Check if Firebase is already initialized
        if not firebase_admin._apps:
            # Get credentials from environment variable
            firebase_creds_json = os.getenv('FIREBASE_SERVICE_ACCOUNT_JSON')
            if not firebase_creds_json:
                raise ValueError("FIREBASE_SERVICE_ACCOUNT_JSON environment variable is required")

            # Parse credentials
            creds_dict = json.loads(firebase_creds_json)
            cred = credentials.Certificate(creds_dict)

            # Initialize Firebase
            firebase_admin.initialize_app(cred)

        # Get Firestore client
        self.db = firestore.client()
        self.collection_name = 'user_configs'
        self.system_config_collection = 'system_configs'

    def get_user_config(self, telegram_handle: str) -> Optional[Dict]:
        """
        Get user configuration by Telegram handle

        Args:
            telegram_handle: User's Telegram username (with or without @)

        Returns:
            User configuration dictionary or None if not found

        Example:
            >>> config = manager.get_user_config("@john_trader")
            >>> print(config['account_balance'])
            10000
        """
        # Normalize handle (remove @ if present)
        handle = telegram_handle.lstrip('@')

        try:
            doc_ref = self.db.collection(self.collection_name).document(handle)
            doc = doc_ref.get()

            if doc.exists:
                return doc.to_dict()
            return None
        except Exception as e:
            print(f"Error getting user config: {e}")
            return None

    def create_user_config(
        self,
        telegram_handle: str,
        account_balance: float = 0.0,
        risk_appetite: float = 3.0,
        bybit_api_key: Optional[str] = None,
        bybit_api_secret: Optional[str] = None
    ) -> bool:
        """
        Create a new user configuration

        Args:
            telegram_handle: User's Telegram username
            account_balance: Account balance in USDT (default: 0)
            risk_appetite: Risk percentage per trade (default: 3%)
            bybit_api_key: Optional Bybit API key
            bybit_api_secret: Optional Bybit API secret

        Returns:
            True if created successfully, False otherwise

        Example:
            >>> manager.create_user_config(
            ...     telegram_handle="@john_trader",
            ...     account_balance=10000,
            ...     risk_appetite=3.0
            ... )
            True
        """
        # Normalize handle
        handle = telegram_handle.lstrip('@')

        try:
            doc_ref = self.db.collection(self.collection_name).document(handle)

            # Check if user already exists
            if doc_ref.get().exists:
                print(f"User {handle} already exists")
                return False

            # Create user config
            config = {
                'telegram_handle': handle,
                'account_balance': account_balance,
                'risk_appetite': risk_appetite,
                'bybit_api_key': bybit_api_key,
                'bybit_api_secret': bybit_api_secret,
                'created_at': datetime.utcnow().isoformat(),
                'updated_at': datetime.utcnow().isoformat()
            }

            doc_ref.set(config)
            print(f"Created user config for {handle}")
            return True

        except Exception as e:
            print(f"Error creating user config: {e}")
            return False

    def update_user_config(
        self,
        telegram_handle: str,
        account_balance: Optional[float] = None,
        risk_appetite: Optional[float] = None,
        bybit_api_key: Optional[str] = None,
        bybit_api_secret: Optional[str] = None
    ) -> bool:
        """
        Update user configuration (only updates provided fields)

        Args:
            telegram_handle: User's Telegram username
            account_balance: New account balance (optional)
            risk_appetite: New risk appetite (optional)
            bybit_api_key: New Bybit API key (optional)
            bybit_api_secret: New Bybit API secret (optional)

        Returns:
            True if updated successfully, False otherwise

        Example:
            >>> manager.update_user_config(
            ...     telegram_handle="@john_trader",
            ...     account_balance=15000
            ... )
            True
        """
        # Normalize handle
        handle = telegram_handle.lstrip('@')

        try:
            doc_ref = self.db.collection(self.collection_name).document(handle)

            # Check if user exists
            if not doc_ref.get().exists:
                print(f"User {handle} not found")
                return False

            # Build update dictionary
            updates = {'updated_at': datetime.utcnow().isoformat()}

            if account_balance is not None:
                updates['account_balance'] = account_balance
            if risk_appetite is not None:
                updates['risk_appetite'] = risk_appetite
            if bybit_api_key is not None:
                updates['bybit_api_key'] = bybit_api_key
            if bybit_api_secret is not None:
                updates['bybit_api_secret'] = bybit_api_secret

            doc_ref.update(updates)
            print(f"Updated user config for {handle}")
            return True

        except Exception as e:
            print(f"Error updating user config: {e}")
            return False

    def delete_user_config(self, telegram_handle: str) -> bool:
        """
        Delete user configuration

        Args:
            telegram_handle: User's Telegram username

        Returns:
            True if deleted successfully, False otherwise
        """
        # Normalize handle
        handle = telegram_handle.lstrip('@')

        try:
            doc_ref = self.db.collection(self.collection_name).document(handle)
            doc_ref.delete()
            print(f"Deleted user config for {handle}")
            return True
        except Exception as e:
            print(f"Error deleting user config: {e}")
            return False

    def get_all_users(self) -> List[Dict]:
        """
        Get all user configurations

        Returns:
            List of user configuration dictionaries

        Example:
            >>> users = manager.get_all_users()
            >>> for user in users:
            ...     print(f"{user['telegram_handle']}: ${user['account_balance']}")
        """
        try:
            docs = self.db.collection(self.collection_name).stream()
            return [doc.to_dict() for doc in docs]
        except Exception as e:
            print(f"Error getting all users: {e}")
            return []

    def user_exists(self, telegram_handle: str) -> bool:
        """
        Check if user exists

        Args:
            telegram_handle: User's Telegram username

        Returns:
            True if user exists, False otherwise
        """
        handle = telegram_handle.lstrip('@')
        try:
            doc_ref = self.db.collection(self.collection_name).document(handle)
            return doc_ref.get().exists
        except Exception as e:
            print(f"Error checking user existence: {e}")
            return False

    # System-level configuration methods

    def get_leverage_for_symbol(self, symbol: str) -> int:
        """
        Get leverage for a specific trading symbol

        Args:
            symbol: Trading symbol (e.g., "BTC", "ETH", "HYPE")

        Returns:
            Leverage value (default: 10 if not found)

        Example:
            >>> manager = get_config_manager()
            >>> leverage = manager.get_leverage_for_symbol("BTC")
            >>> print(leverage)
            100
        """
        try:
            # Normalize symbol to uppercase
            symbol = symbol.upper()

            # Get leverage map document
            doc_ref = self.db.collection(self.system_config_collection).document('leverage_map')
            doc = doc_ref.get()

            if doc.exists:
                leverage_map = doc.to_dict()
                return leverage_map.get(symbol, 10)  # Default to 10x if not found
            else:
                # If leverage map doesn't exist, return default
                print(f"Leverage map not found in Firebase, using default leverage: 10x")
                return 10

        except Exception as e:
            print(f"Error getting leverage for {symbol}: {e}")
            return 10  # Default to 10x on error

    def set_leverage_for_symbol(self, symbol: str, leverage: int) -> bool:
        """
        Set leverage for a specific trading symbol

        Args:
            symbol: Trading symbol (e.g., "BTC", "ETH")
            leverage: Leverage value (e.g., 100, 25, 10)

        Returns:
            True if updated successfully, False otherwise

        Example:
            >>> manager = get_config_manager()
            >>> manager.set_leverage_for_symbol("BTC", 100)
            >>> manager.set_leverage_for_symbol("HYPE", 25)
        """
        try:
            # Normalize symbol to uppercase
            symbol = symbol.upper()

            # Get or create leverage map document
            doc_ref = self.db.collection(self.system_config_collection).document('leverage_map')

            # Update the specific symbol's leverage
            doc_ref.set({symbol: leverage}, merge=True)
            print(f"Set leverage for {symbol}: {leverage}x")
            return True

        except Exception as e:
            print(f"Error setting leverage for {symbol}: {e}")
            return False

    def get_all_leverages(self) -> Dict[str, int]:
        """
        Get all symbol leverage mappings

        Returns:
            Dictionary mapping symbols to leverage values

        Example:
            >>> manager = get_config_manager()
            >>> leverages = manager.get_all_leverages()
            >>> print(leverages)
            {'BTC': 100, 'ETH': 50, 'HYPE': 25}
        """
        try:
            doc_ref = self.db.collection(self.system_config_collection).document('leverage_map')
            doc = doc_ref.get()

            if doc.exists:
                return doc.to_dict()
            return {}

        except Exception as e:
            print(f"Error getting all leverages: {e}")
            return {}

    def initialize_default_leverages(self) -> bool:
        """
        Initialize leverage map with common default values

        Returns:
            True if initialized successfully, False otherwise
        """
        default_leverages = {
            'BTC': 100,
            'ETH': 75,
            'SOL': 50,
            'HYPE': 25,
            'AVAX': 50,
            'MATIC': 50,
            'DOT': 50,
            'LINK': 50,
            'UNI': 50,
            'AAVE': 50
        }

        try:
            doc_ref = self.db.collection(self.system_config_collection).document('leverage_map')
            doc_ref.set(default_leverages)
            print(f"Initialized leverage map with {len(default_leverages)} symbols")
            return True

        except Exception as e:
            print(f"Error initializing leverages: {e}")
            return False


# Singleton instance
_config_manager_instance = None


def get_config_manager() -> ConfigManager:
    """
    Get or create singleton ConfigManager instance

    Returns:
        ConfigManager instance

    Example:
        >>> from config import get_config_manager
        >>> manager = get_config_manager()
        >>> user = manager.get_user_config("@john_trader")
    """
    global _config_manager_instance
    if _config_manager_instance is None:
        _config_manager_instance = ConfigManager()
    return _config_manager_instance


# Convenience functions
def get_user_balance(telegram_handle: str) -> float:
    """Get user's account balance"""
    manager = get_config_manager()
    config = manager.get_user_config(telegram_handle)
    return config['account_balance'] if config else 0.0


def get_user_risk(telegram_handle: str) -> float:
    """Get user's risk appetite"""
    manager = get_config_manager()
    config = manager.get_user_config(telegram_handle)
    return config['risk_appetite'] if config else 3.0


def update_user_balance(telegram_handle: str, new_balance: float) -> bool:
    """Update user's account balance"""
    manager = get_config_manager()
    return manager.update_user_config(telegram_handle, account_balance=new_balance)


def update_user_risk(telegram_handle: str, new_risk: float) -> bool:
    """Update user's risk appetite"""
    manager = get_config_manager()
    return manager.update_user_config(telegram_handle, risk_appetite=new_risk)


# Example usage and testing
if __name__ == "__main__":
    print("=== Firebase Config Manager ===\n")

    try:
        manager = ConfigManager()

        # Example 1: Create a user
        print("1. Creating user...")
        success = manager.create_user_config(
            telegram_handle="@john_trader",
            account_balance=10000,
            risk_appetite=3.0
        )
        print(f"   Result: {'✅ Success' if success else '❌ Failed'}\n")

        # Example 2: Get user config
        print("2. Getting user config...")
        config = manager.get_user_config("@john_trader")
        if config:
            print(f"   Handle: {config['telegram_handle']}")
            print(f"   Balance: ${config['account_balance']:,.2f}")
            print(f"   Risk: {config['risk_appetite']}%\n")
        else:
            print("   User not found\n")

        # Example 3: Update balance
        print("3. Updating balance to $15,000...")
        success = manager.update_user_config("@john_trader", account_balance=15000)
        print(f"   Result: {'✅ Success' if success else '❌ Failed'}\n")

        # Example 4: Get all users
        print("4. Getting all users...")
        users = manager.get_all_users()
        print(f"   Found {len(users)} user(s):")
        for user in users:
            print(f"   - {user['telegram_handle']}: ${user['account_balance']:,.2f} (Risk: {user['risk_appetite']}%)")
        print()

        # Example 5: Using convenience functions
        print("5. Using convenience functions...")
        balance = get_user_balance("@john_trader")
        risk = get_user_risk("@john_trader")
        print(f"   Balance: ${balance:,.2f}")
        print(f"   Risk: {risk}%\n")

    except Exception as e:
        print(f"❌ Error: {e}")
