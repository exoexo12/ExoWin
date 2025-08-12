#!/usr/bin/env python3
"""
Database Setup and Validation Script for ExoWin Bot
This script ensures the database is properly configured and all collections are set up correctly.
"""

import asyncio
import os
import sys
from datetime import datetime
from dotenv import load_dotenv

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.database.db import setup_database, client, db, users_collection, transactions_collection, games_collection
from src.utils.logger import db_logger
from src.utils.config_validator import ConfigValidator

async def validate_database_connection():
    """Test database connection"""
    try:
        # Test connection
        await client.admin.command('ping')
        db_logger.info("✅ Database connection successful")
        return True
    except Exception as e:
        db_logger.error(f"❌ Database connection failed: {e}")
        return False

async def validate_collections():
    """Validate that all required collections exist and have proper indexes"""
    try:
        # List all collections
        collections = await db.list_collection_names()
        required_collections = ["users", "transactions", "games"]
        
        for collection in required_collections:
            if collection in collections:
                db_logger.info(f"✅ Collection '{collection}' exists")
            else:
                db_logger.warning(f"⚠️ Collection '{collection}' does not exist (will be created on first use)")
        
        # Check indexes
        for collection_name, collection_obj in [
            ("users", users_collection),
            ("transactions", transactions_collection), 
            ("games", games_collection)
        ]:
            indexes = await collection_obj.list_indexes().to_list(length=None)
            index_names = [idx['name'] for idx in indexes]
            db_logger.info(f"📋 Collection '{collection_name}' indexes: {index_names}")
        
        return True
    except Exception as e:
        db_logger.error(f"❌ Collection validation failed: {e}")
        return False

async def test_database_operations():
    """Test basic database operations"""
    try:
        test_user_id = 999999999  # Test user ID
        
        # Test user creation
        from src.database.db import get_user, update_user_balance, record_transaction, record_game
        
        db_logger.info("🧪 Testing database operations...")
        
        # Test 1: Create user
        user = await get_user(test_user_id, {
            'username': 'test_user',
            'first_name': 'Test',
            'last_name': 'User'
        })
        if user:
            db_logger.info("✅ User creation/retrieval works")
        else:
            db_logger.error("❌ User creation failed")
            return False
        
        # Test 2: Update balance
        original_balance = user['balance']
        await update_user_balance(test_user_id, 10.0)
        updated_user = await get_user(test_user_id)
        if updated_user['balance'] == original_balance + 10.0:
            db_logger.info("✅ Balance update works")
        else:
            db_logger.error("❌ Balance update failed")
            return False
        
        # Test 3: Record transaction
        transaction_id = await record_transaction(
            test_user_id, 5.0, "deposit", description="Test deposit"
        )
        if transaction_id:
            db_logger.info("✅ Transaction recording works")
        else:
            db_logger.error("❌ Transaction recording failed")
            return False
        
        # Test 4: Record game
        game_id = await record_game(
            test_user_id, "test_game", 1.0, "win", 2.0
        )
        if game_id:
            db_logger.info("✅ Game recording works")
        else:
            db_logger.error("❌ Game recording failed")
            return False
        
        # Clean up test user
        await users_collection.delete_one({"user_id": test_user_id})
        await transactions_collection.delete_many({"user_id": test_user_id})
        await games_collection.delete_many({"user_id": test_user_id})
        db_logger.info("🧹 Test data cleaned up")
        
        return True
    except Exception as e:
        db_logger.error(f"❌ Database operations test failed: {e}")
        return False

async def test_webapp_database():
    """Test webapp database synchronization"""
    try:
        from webapp.sync_db import get_user as webapp_get_user, update_user_balance as webapp_update_balance
        
        test_user_id = 999999998  # Different test user for webapp
        
        db_logger.info("🌐 Testing webapp database operations...")
        
        # Test webapp user creation
        user = webapp_get_user(test_user_id, {
            'username': 'webapp_test',
            'first_name': 'Webapp',
            'last_name': 'Test'
        })
        if user:
            db_logger.info("✅ Webapp user creation works")
        else:
            db_logger.error("❌ Webapp user creation failed")
            return False
        
        # Test webapp balance update
        original_balance = user['balance']
        webapp_update_balance(test_user_id, 5.0)
        updated_user = webapp_get_user(test_user_id)
        if updated_user['balance'] == original_balance + 5.0:
            db_logger.info("✅ Webapp balance update works")
        else:
            db_logger.error("❌ Webapp balance update failed")
            return False
        
        # Clean up
        users_collection.delete_one({"user_id": test_user_id})
        db_logger.info("🧹 Webapp test data cleaned up")
        
        return True
    except Exception as e:
        db_logger.error(f"❌ Webapp database test failed: {e}")
        return False

async def get_database_stats():
    """Get current database statistics"""
    try:
        stats = {
            'users': await users_collection.count_documents({}),
            'transactions': await transactions_collection.count_documents({}),
            'games': await games_collection.count_documents({})
        }
        
        db_logger.info("📊 Database Statistics:")
        for collection, count in stats.items():
            db_logger.info(f"   {collection}: {count} documents")
        
        return stats
    except Exception as e:
        db_logger.error(f"❌ Failed to get database stats: {e}")
        return {}

async def main():
    """Main database setup and validation"""
    print("🚀 ExoWin Database Setup and Validation")
    print("=" * 50)
    
    # Load environment variables
    load_dotenv()
    
    # Validate configuration
    print("\n1. Validating Configuration...")
    is_valid, issues = ConfigValidator.validate_config()
    if not is_valid:
        print("❌ Configuration validation failed:")
        for issue in issues:
            print(f"   - {issue}")
        print("\nPlease fix configuration issues before proceeding.")
        return False
    else:
        print("✅ Configuration is valid")
    
    # Test database connection
    print("\n2. Testing Database Connection...")
    if not await validate_database_connection():
        print("❌ Database connection failed. Please check your MONGODB_URI.")
        return False
    
    # Setup database indexes
    print("\n3. Setting up Database Indexes...")
    if await setup_database():
        print("✅ Database indexes created successfully")
    else:
        print("❌ Database index creation failed")
        return False
    
    # Validate collections
    print("\n4. Validating Collections...")
    if not await validate_collections():
        print("❌ Collection validation failed")
        return False
    
    # Test database operations
    print("\n5. Testing Database Operations...")
    if not await test_database_operations():
        print("❌ Database operations test failed")
        return False
    
    # Test webapp database
    print("\n6. Testing Webapp Database Integration...")
    if not await test_webapp_database():
        print("❌ Webapp database test failed")
        return False
    
    # Get database statistics
    print("\n7. Database Statistics...")
    await get_database_stats()
    
    print("\n" + "=" * 50)
    print("🎉 Database setup and validation completed successfully!")
    print("Your ExoWin bot database is ready for production use.")
    
    return True

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)