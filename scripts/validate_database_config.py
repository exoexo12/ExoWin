#!/usr/bin/env python3
"""
Database Configuration Validation Script for ExoWin Bot
This script validates database configuration and code consistency without requiring a live database connection.
"""

import os
import sys
import importlib.util
from datetime import datetime
from dotenv import load_dotenv

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def validate_imports():
    """Test that all database modules can be imported successfully"""
    try:
        print("📦 Testing database module imports...")
        
        # Test main database module
        from src.database.db import (
            get_user, update_user_balance, record_transaction, record_game,
            setup_database, users_collection, transactions_collection, games_collection
        )
        print("✅ Main database module imports successfully")
        
        # Test webapp sync module
        from webapp.sync_db import (
            get_user as webapp_get_user,
            update_user_balance as webapp_update_balance,
            record_transaction as webapp_record_transaction,
            record_game as webapp_record_game
        )
        print("✅ Webapp sync database module imports successfully")
        
        # Test database initialization
        from src.database import (
            get_user as db_get_user,
            update_user_balance as db_update_balance,
            record_transaction as db_record_transaction,
            record_game as db_record_game
        )
        print("✅ Database __init__ module imports successfully")
        
        return True
    except Exception as e:
        print(f"❌ Import validation failed: {e}")
        return False

def validate_configuration():
    """Validate environment configuration"""
    try:
        print("⚙️ Validating configuration...")
        
        from src.utils.config_validator import ConfigValidator
        is_valid, issues = ConfigValidator.validate_config()
        
        if is_valid:
            print("✅ Configuration is valid")
        else:
            print("⚠️ Configuration has issues:")
            for issue in issues:
                if "Optional variable" not in issue:
                    print(f"   ❌ {issue}")
                else:
                    print(f"   ⚠️ {issue}")
        
        return is_valid
    except Exception as e:
        print(f"❌ Configuration validation failed: {e}")
        return False

def validate_database_consistency():
    """Validate consistency between main db.py and webapp sync_db.py"""
    try:
        print("🔄 Validating database consistency...")
        
        # Check database names
        from src.database.db import DATABASE_NAME as main_db_name
        from webapp.sync_db import DATABASE_NAME as webapp_db_name
        
        if main_db_name == webapp_db_name:
            print(f"✅ Database names match: {main_db_name}")
        else:
            print(f"❌ Database name mismatch: main='{main_db_name}', webapp='{webapp_db_name}'")
            return False
        
        # Check MongoDB URIs
        from src.database.db import MONGODB_URI as main_uri
        from webapp.sync_db import MONGODB_URI as webapp_uri
        
        if main_uri == webapp_uri:
            print(f"✅ MongoDB URIs match")
        else:
            print(f"❌ MongoDB URI mismatch")
            return False
        
        print("✅ Database configuration is consistent")
        return True
    except Exception as e:
        print(f"❌ Database consistency validation failed: {e}")
        return False

def validate_function_signatures():
    """Validate that function signatures match between main and webapp modules"""
    try:
        print("🔍 Validating function signatures...")
        
        import inspect
        from src.database.db import get_user as main_get_user, update_user_balance as main_update_balance
        from webapp.sync_db import get_user as webapp_get_user, update_user_balance as webapp_update_balance
        
        # Check get_user signatures
        main_sig = inspect.signature(main_get_user)
        webapp_sig = inspect.signature(webapp_get_user)
        
        if len(main_sig.parameters) == len(webapp_sig.parameters):
            print("✅ get_user function signatures are compatible")
        else:
            print("⚠️ get_user function signatures differ (this may be intentional)")
        
        # Check update_user_balance signatures
        main_sig = inspect.signature(main_update_balance)
        webapp_sig = inspect.signature(webapp_update_balance)
        
        if len(main_sig.parameters) == len(webapp_sig.parameters):
            print("✅ update_user_balance function signatures match")
        else:
            print("❌ update_user_balance function signatures don't match")
            return False
        
        return True
    except Exception as e:
        print(f"❌ Function signature validation failed: {e}")
        return False

def validate_game_integrations():
    """Validate that all games can import database functions"""
    try:
        print("🎮 Validating game database integrations...")
        
        # Test animated games
        animated_games = [
            'coinflip_animated', 'dice_animated', 'slots_animated', 'darts_animated',
            'basketball_animated', 'football_animated', 'bowling_animated', 'wheel_animated'
        ]
        
        for game in animated_games:
            try:
                module = importlib.import_module(f'src.games.{game}')
                print(f"✅ {game} imports successfully")
            except Exception as e:
                print(f"❌ {game} import failed: {e}")
                return False
        
        # Test webapp games
        webapp_games = [
            'blackjack', 'roulette', 'mines', 'tower', 'crash', 'plinko', 'poker', 'lottery'
        ]
        
        for game in webapp_games:
            try:
                module = importlib.import_module(f'src.games.{game}')
                print(f"✅ {game} imports successfully")
            except Exception as e:
                print(f"❌ {game} import failed: {e}")
                return False
        
        return True
    except Exception as e:
        print(f"❌ Game integration validation failed: {e}")
        return False

def validate_webapp_integration():
    """Validate webapp database integration"""
    try:
        print("🌐 Validating webapp integration...")
        
        # Test webapp app imports
        from webapp.app import app
        print("✅ Webapp app imports successfully")
        
        # Check if webapp uses sync_db
        with open('/workspace/project/ExoWin/webapp/app.py', 'r') as f:
            content = f.read()
            if 'sync_db' in content:
                print("✅ Webapp uses sync_db module")
            else:
                print("⚠️ Webapp may not be using sync_db module")
        
        return True
    except Exception as e:
        print(f"❌ Webapp integration validation failed: {e}")
        return False

def generate_database_summary():
    """Generate a summary of the database configuration"""
    try:
        print("\n📋 Database Configuration Summary:")
        print("=" * 50)
        
        # Environment variables
        load_dotenv()
        print(f"Database Name: {os.getenv('DATABASE_NAME', 'Not set')}")
        print(f"MongoDB URI: {os.getenv('MONGODB_URI', 'Not set')}")
        print(f"Flask Port: {os.getenv('FLASK_PORT', '12000')}")
        
        # Collections
        print("\nCollections:")
        print("- users (user accounts and balances)")
        print("- transactions (deposits, withdrawals, bets, wins)")
        print("- games (game history and results)")
        
        # Game types
        print("\nGame Integration:")
        print("- Animated Games: Use async database functions")
        print("- Webapp Games: Use sync database functions")
        print("- Shared Wallet: All games use same user balance")
        
        return True
    except Exception as e:
        print(f"❌ Failed to generate summary: {e}")
        return False

def main():
    """Main validation function"""
    print("🔍 ExoWin Database Configuration Validation")
    print("=" * 50)
    
    # Load environment variables
    load_dotenv()
    
    all_passed = True
    
    # Run all validations
    validations = [
        ("Import Validation", validate_imports),
        ("Configuration Validation", validate_configuration),
        ("Database Consistency", validate_database_consistency),
        ("Function Signatures", validate_function_signatures),
        ("Game Integrations", validate_game_integrations),
        ("Webapp Integration", validate_webapp_integration)
    ]
    
    for name, validation_func in validations:
        print(f"\n{name}...")
        if not validation_func():
            all_passed = False
    
    # Generate summary
    generate_database_summary()
    
    print("\n" + "=" * 50)
    if all_passed:
        print("🎉 All database validations passed!")
        print("Your database configuration is ready for use.")
    else:
        print("❌ Some validations failed.")
        print("Please review the issues above before deploying.")
    
    return all_passed

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)