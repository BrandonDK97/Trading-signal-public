"""
Quick Firebase setup script
Initializes leverages and creates test users
"""

from config import get_config_manager
import sys


def setup():
    """Initialize Firebase with default data"""
    print("\n" + "="*70)
    print("🔥 FIREBASE SETUP")
    print("="*70 + "\n")

    try:
        manager = get_config_manager()
    except Exception as e:
        print(f"❌ Failed to connect to Firebase: {e}")
        print("\nMake sure:")
        print("  1. .env file exists with FIREBASE_SERVICE_ACCOUNT_JSON")
        print("  2. Firebase credentials are valid")
        print("  3. Firestore is enabled in your Firebase project")
        return False

    # Initialize leverages
    print("1. Initializing default leverages...")
    try:
        if manager.initialize_default_leverages():
            leverages = manager.get_all_leverages()
            print(f"   ✅ Created {len(leverages)} leverage mappings:")
            for symbol, lev in sorted(leverages.items()):
                print(f"      {symbol}: {lev}x")
        else:
            print("   ❌ Failed to initialize leverages")
            return False
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False

    # Create test users
    print("\n2. Creating test users...")
    users = [
        ('john_trader', 10000, 3.0),
        ('alice_crypto', 25000, 2.0),
        ('bob_degen', 5000, 5.0)
    ]

    created = 0
    existing = 0
    for handle, balance, risk in users:
        try:
            if manager.create_user_config(handle, balance, risk):
                print(f"   ✅ Created: @{handle} (Balance: ${balance:,.2f}, Risk: {risk}%)")
                created += 1
            else:
                print(f"   ⚠️  Already exists: @{handle}")
                existing += 1
        except Exception as e:
            print(f"   ❌ Error creating @{handle}: {e}")

    print(f"\n" + "="*70)
    print(f"✅ SETUP COMPLETE!")
    print("="*70)
    print(f"\nSummary:")
    print(f"  📊 Leverages: {len(leverages)} symbols configured")
    print(f"  👥 Users: {created} created, {existing} already existed")
    print(f"\nFirestore Collections Created:")
    print(f"  - user_configs/ ({created + existing} documents)")
    print(f"  - system_configs/leverage_map (1 document)")
    print(f"\nNext Steps:")
    print(f"  1. Verify in Firebase Console: https://console.firebase.google.com")
    print(f"  2. Test with: python test_controller.py")
    print(f"  3. Run tests: python test_examples.py")
    print("\n" + "="*70 + "\n")

    return True


if __name__ == "__main__":
    success = setup()
    sys.exit(0 if success else 1)
