"""
Configuration Manager with Firebase Integration

Manages user configurations stored in Firebase Firestore.
Stores: telegram_handle, account_balance, risk_appetite, and future bybit_api_key.
"""

import os
import json
from typing import Dict, Optional, List
from datetime import datetime

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
