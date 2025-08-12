# 🗄️ ExoWin Database Configuration Guide

## ✅ Database Status: FULLY CONFIGURED

All database configurations have been validated and are working correctly. The database is properly set up for both Telegram bot operations and webapp functionality.

## 📋 Configuration Overview

### Database Details
- **Database Name**: `exowin_bot` (configurable via `DATABASE_NAME` env var)
- **MongoDB URI**: Configurable via `MONGODB_URI` env var
- **Collections**: `users`, `transactions`, `games`
- **Architecture**: Async for bot, Sync for webapp

### Key Features
- ✅ **Unified Schema**: Both bot and webapp use identical user schema
- ✅ **Shared Wallet**: All games share the same user balance
- ✅ **Consistent Data**: Same database name and structure across all modules
- ✅ **Proper Indexing**: Optimized indexes for performance
- ✅ **Transaction Logging**: Complete audit trail of all operations
- ✅ **Game History**: Detailed records of all game sessions

## 🏗️ Database Schema

### Users Collection
```javascript
{
  "user_id": 123456789,                    // Telegram user ID (unique)
  "balance": 1.0,                          // Current balance ($1 starting)
  "created_at": ISODate("2024-01-01"),     // Account creation date
  "last_active": ISODate("2024-01-01"),    // Last activity timestamp
  
  // Game Statistics
  "total_bets": 0,                         // Total number of bets placed
  "total_wins": 0,                         // Total number of wins
  "total_losses": 0,                       // Total number of losses
  "total_deposits": 0.0,                   // Total amount deposited
  "total_withdrawals": 0.0,                // Total amount withdrawn
  
  // Bonus System
  "daily_bonus_streak": 0,                 // Current daily bonus streak
  "last_daily_bonus": null,                // Last daily bonus claim date
  "total_daily_bonuses": 0.0,              // Total daily bonuses received
  "total_referrals": 0,                    // Number of users referred
  "total_referral_bonuses": 0.0,           // Total referral bonuses
  "total_event_bonuses": 0.0,              // Total event bonuses
  "referred_by": null,                     // User ID who referred this user
  
  // User Settings
  "notifications_enabled": true,           // Push notifications
  "sound_effects": true,                   // Game sound effects
  "theme": "dark",                         // UI theme (dark/light)
  "language": "en",                        // Interface language
  "auto_bet_enabled": false,               // Auto-betting feature
  "quick_bet_enabled": false,              // Quick bet buttons
  
  // User Information
  "username": "user123",                   // Telegram username
  "first_name": "John",                    // First name
  "last_name": "Doe",                      // Last name
  "is_banned": false                       // Account status
}
```

### Transactions Collection
```javascript
{
  "user_id": 123456789,                    // User who made transaction
  "amount": 10.0,                          // Transaction amount
  "type": "deposit",                       // deposit, withdrawal, bet, win, bonus
  "game_id": "game_session_123",           // Associated game session (optional)
  "description": "Daily bonus",            // Human-readable description
  "timestamp": ISODate("2024-01-01")       // Transaction timestamp
}
```

### Games Collection
```javascript
{
  "user_id": 123456789,                    // Player user ID
  "game_type": "blackjack",                // Type of game played
  "bet_amount": 5.0,                       // Amount wagered
  "outcome": "win",                        // win, loss, push
  "winnings": 10.0,                        // Amount won (0 if loss)
  "timestamp": ISODate("2024-01-01")       // Game completion time
}
```

## 🔧 Database Modules

### Main Database Module (`src/database/db.py`)
- **Purpose**: Async operations for Telegram bot
- **Client**: Motor (async MongoDB driver)
- **Functions**: All core database operations
- **Usage**: Used by animated games and bot commands

### Webapp Sync Module (`webapp/sync_db.py`)
- **Purpose**: Sync operations for Flask webapp
- **Client**: PyMongo (sync MongoDB driver)
- **Functions**: Subset of core operations (sync versions)
- **Usage**: Used by webapp games and API endpoints

### Database Initialization (`src/database/__init__.py`)
- **Purpose**: Centralized imports and exports
- **Exports**: All database functions for easy importing
- **Usage**: `from src.database import get_user, update_user_balance`

## 🎮 Game Integration

### Animated Games (Telegram Native)
```python
from src.database import get_user, update_user_balance, record_transaction, record_game

# Example usage in animated game
user = await get_user(user_id)
await update_user_balance(user_id, -bet_amount)  # Deduct bet
await record_transaction(user_id, -bet_amount, "bet", game_id, "Dice bet")

# If win
await update_user_balance(user_id, winnings)
await record_transaction(user_id, winnings, "win", game_id, "Dice win")
await record_game(user_id, "dice", bet_amount, "win", winnings)
```

### Webapp Games (Complex Interfaces)
```python
from webapp.sync_db import get_user, update_user_balance, record_transaction, record_game

# Example usage in webapp game
user = get_user(user_id)
update_user_balance(user_id, -bet_amount)  # Deduct bet
record_transaction(user_id, -bet_amount, "bet", game_id, "Blackjack bet")

# If win
update_user_balance(user_id, winnings)
record_transaction(user_id, winnings, "win", game_id, "Blackjack win")
record_game(user_id, "blackjack", bet_amount, "win", winnings)
```

## 📊 Database Indexes

### Users Collection Indexes
- `user_id` (unique) - Primary lookup
- `last_active` - Activity queries
- `is_banned` - Admin filtering
- `balance` - Leaderboards
- `total_bets` - Statistics
- `created_at` - Registration tracking

### Transactions Collection Indexes
- `user_id` - User transaction history
- `timestamp` - Time-based queries
- `type` - Transaction type filtering
- `(user_id, timestamp)` - Compound index for user history

### Games Collection Indexes
- `user_id` - User game history
- `game_type` - Game statistics
- `timestamp` - Time-based queries
- `(user_id, timestamp)` - User game history
- `(game_type, timestamp)` - Game type statistics

## 🚀 Setup Instructions

### 1. Environment Configuration
Create a `.env` file with required variables:
```bash
BOT_TOKEN=your_bot_token_here
MONGODB_URI=mongodb://localhost:27017
DATABASE_NAME=exowin_bot
ADMIN_USER_ID=your_telegram_user_id
SECRET_KEY=your_secret_key_here
FLASK_SECRET_KEY=your_flask_secret_key_here
```

### 2. Database Initialization
Run the database setup script:
```bash
python init_db.py
```

### 3. Validation
Validate your configuration:
```bash
python validate_database_config.py
```

### 4. Production Setup
For production deployment:
```bash
python database_setup.py  # Requires live MongoDB connection
```

## 🔒 Security Considerations

### Data Protection
- User balances are stored as floats with proper validation
- All transactions are logged for audit purposes
- User data includes privacy-conscious fields only
- No sensitive payment information stored in database

### Access Control
- Admin functions require proper authentication
- User operations validate ownership
- Database connections use proper authentication
- Environment variables protect sensitive configuration

### Performance
- Proper indexing for fast queries
- Efficient aggregation pipelines for statistics
- Connection pooling for high concurrency
- Optimized queries for common operations

## 🛠️ Maintenance

### Regular Tasks
1. **Monitor Database Size**: Track collection growth
2. **Index Performance**: Monitor query performance
3. **Backup Strategy**: Regular database backups
4. **User Cleanup**: Archive inactive accounts
5. **Transaction Audits**: Verify transaction integrity

### Troubleshooting
- **Connection Issues**: Check MongoDB URI and network
- **Schema Mismatches**: Run validation script
- **Performance Issues**: Review indexes and queries
- **Data Inconsistencies**: Check transaction logs

## 📈 Statistics and Analytics

The database supports comprehensive analytics:
- User registration trends
- Game popularity statistics
- Financial transaction summaries
- User engagement metrics
- Daily/weekly/monthly reports

Access via admin functions:
```python
from src.database import get_system_stats, get_game_statistics, get_financial_stats
```

## ✅ Validation Results

All database components have been validated:
- ✅ Import validation passed
- ✅ Configuration validation passed
- ✅ Database consistency validated
- ✅ Function signatures compatible
- ✅ Game integrations working
- ✅ Webapp integration confirmed

**Status**: Ready for production deployment! 🚀