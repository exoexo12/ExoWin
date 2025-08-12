# 🎮 ExoWin Game Architecture - Final Consolidated State

## 📋 Overview
All games have been successfully consolidated into two distinct categories with proper routing and shared wallet integration.

## 🎯 Game Categories

### 🎪 Animated Games (Telegram Native)
These games use Telegram's native animation features and are handled directly by the bot:

- **coinflip_animated.py** - Coin flip with Telegram dice animation
- **dice_animated.py** - Dice roll with Telegram dice animation  
- **slots_animated.py** - Slot machine with Telegram slot animation
- **darts_animated.py** - Darts with Telegram darts animation
- **basketball_animated.py** - Basketball with Telegram basketball animation
- **football_animated.py** - Football with Telegram football animation
- **bowling_animated.py** - Bowling with Telegram bowling animation
- **wheel_animated.py** - Wheel of fortune with Telegram dice animation

### 🌐 Webapp Games (Complex Interfaces)
These games use rich web interfaces and are handled through the Flask webapp:

- **blackjack.py** - Card game with interactive interface
- **roulette.py** - Roulette table with betting options
- **mines.py** - Minesweeper-style game with grid
- **tower.py** - Tower climbing game with risk/reward
- **crash.py** - Multiplier crash game with real-time updates
- **plinko.py** - Plinko ball drop game with physics
- **poker.py** - 5-card poker against dealer
- **lottery.py** - Number selection lottery game

## 🔄 Routing System

### Games Menu Routing
The `games_menu.py` properly routes each game type:

```python
# Animated games → Telegram handlers
if game_type == "dice":
    from src.games.dice_animated import dice_command
    await dice_command(update, context)

# Webapp games → Mini app interfaces  
elif game_type == "blackjack":
    await show_blackjack_webapp(update, context)
```

### Menu Structure
- **Main Games Menu** → Choose between Animated or Webapp games
- **Animated Games Menu** → Direct Telegram game execution
- **Webapp Games Menu** → Launch mini app interfaces

## 💰 Shared Wallet Integration

All games (both animated and webapp) share the same wallet system:

### Database Integration
- **Balance Management**: All games deduct/add to same user balance
- **Transaction Recording**: All bets and winnings logged in same database
- **Game History**: All games recorded in unified game history

### Wallet Functions
```python
# Used by all games
get_user(user_id)                    # Get user balance
update_user_balance(user_id, amount) # Update balance  
record_transaction(user_id, ...)     # Log transaction
record_game(user_id, ...)           # Log game result
```

## 🌐 Webapp Architecture

### API Endpoints
Each webapp game has dedicated API endpoints:

- **Blackjack**: `/api/blackjack/deal`, `/api/blackjack/hit`, `/api/blackjack/stand`
- **Roulette**: `/api/roulette/start`, `/api/roulette/bet`, `/api/roulette/spin`
- **Crash**: `/api/crash/start`, `/api/crash/update`, `/api/crash/cashout`
- **Mines**: `/api/mines/start`, `/api/mines/reveal`, `/api/mines/cashout`
- **Tower**: `/api/tower/start`, `/api/tower/choose`, `/api/tower/cashout`
- **Plinko**: `/api/plinko/start`, `/api/plinko/drop`
- **Poker**: `/api/poker/start`, `/api/poker/finish`
- **Lottery**: `/api/lottery/start`, `/api/lottery/select`, `/api/lottery/draw`

### Frontend Files
- **Templates**: `webapp/templates/games/[game].html`
- **JavaScript**: `webapp/static/js/[game].js`
- **Styling**: Integrated CSS in templates

## 🎮 Game Mechanics

### In-Game Features (NOT Withdrawal)
Some games have "cash out" mechanics as part of gameplay strategy:
- **Crash**: Cash out before crash to secure winnings
- **Mines**: Cash out before hitting mine to secure multiplier
- **Tower**: Cash out before trap to secure level winnings

These are **risk vs reward decisions**, not platform withdrawals.

### Withdrawal System
- **Single Method**: Only through official menu system
- **No Game Withdrawals**: Individual games cannot withdraw from platform
- **Shared Balance**: All games update same wallet balance

## 📁 File Structure

```
src/games/
├── __init__.py                 # Only imports animated game callbacks
├── coinflip_animated.py       # ✅ Animated
├── dice_animated.py           # ✅ Animated  
├── slots_animated.py          # ✅ Animated
├── darts_animated.py          # ✅ Animated
├── basketball_animated.py     # ✅ Animated
├── football_animated.py       # ✅ Animated
├── bowling_animated.py        # ✅ Animated
├── wheel_animated.py          # ✅ Animated
├── blackjack.py              # 🌐 Webapp
├── roulette.py               # 🌐 Webapp
├── mines.py                  # 🌐 Webapp
├── tower.py                  # 🌐 Webapp
├── crash.py                  # 🌐 Webapp
├── plinko.py                 # 🌐 Webapp
├── poker.py                  # 🌐 Webapp
└── lottery.py                # 🌐 Webapp

webapp/
├── app.py                    # Flask server with all API endpoints
├── templates/games/          # HTML templates for webapp games
└── static/js/               # JavaScript for webapp games
```

## ✅ Verification Checklist

- [x] **All animated games** use Telegram native animations
- [x] **All webapp games** use rich web interfaces  
- [x] **Shared wallet** integration across all games
- [x] **Proper routing** in games menu
- [x] **Complete API endpoints** for all webapp games
- [x] **Frontend files** for all webapp games
- [x] **No import conflicts** between game types
- [x] **Single withdrawal method** through menus only
- [x] **Clean file structure** with proper separation
- [x] **Working webapp server** on port 12000

## 🚀 Status: FULLY CONSOLIDATED ✅

All games are properly set up with:
- Correct routing between animated and webapp games
- Shared wallet integration across all games  
- Complete API endpoints and frontend files
- Proper separation of concerns
- Single withdrawal system through menus
- No conflicts or missing dependencies

The system is ready for production use with both Telegram native animations and rich webapp interfaces working seamlessly together.