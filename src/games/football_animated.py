# Modified to handle callback queries
import random
import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from src.database import get_user, update_user_balance, record_transaction, record_game
from src.utils.formatting import format_money

# Active football competitions
active_football_games = {}

# Football scoring system (Telegram football returns 1-5)
FOOTBALL_SCORING = {
    1: {"name": "Miss", "multiplier": 0, "emoji": "❌"},
    2: {"name": "Saved", "multiplier": 1, "emoji": "🔴"},
    3: {"name": "Close", "multiplier": 2, "emoji": "🟡"},
    4: {"name": "Good Goal", "multiplier": 4, "emoji": "🟢"},
    5: {"name": "Perfect Goal", "multiplier": 8, "emoji": "⚽"}
}

async def football_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle the /football command - Telegram animated football game"""
    # Handle both direct commands and callback queries
    if update.message:
        pass
    elif update.callback_query:
        update.message = update.callback_query.message
        
    keyboard = [
        [
            InlineKeyboardButton("⚽ Solo Football", callback_data="football_solo"),
            InlineKeyboardButton("👥 Multiplayer", callback_data="football_multiplayer")
        ],
        [
            InlineKeyboardButton("⚔️ Football Duel", callback_data="football_duel"),
            InlineKeyboardButton("📊 How to Play", callback_data="football_help")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    message_text = (
        "⚽ **ANIMATED FOOTBALL GAME**\n\n"
        "Real Telegram football animation!\n\n"
        "**Game Modes:**\n"
        "⚽ **Solo**: Guess the outcome (Miss, Saved, Close, Good, Perfect)\n"
        "👥 **Multiplayer**: Everyone bets, winner takes pot\n"
        "⚔️ **Duel**: Challenge another player\n\n"
        "Choose your game mode:"
    )

    await update.message.reply_text(message_text, reply_markup=reply_markup, parse_mode='Markdown')

async def football_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle football game callbacks"""
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    data = query.data.split("_")
    
    if len(data) < 2:
        return
    
    action = data[1]
    
    if action == "solo":
        await query.message.reply_text("Solo football game coming soon!")
    elif action == "multiplayer":
        await query.message.reply_text("Multiplayer football game coming soon!")
    elif action == "duel":
        await query.message.reply_text("Football duel game coming soon!")
    elif action == "help":
        await query.message.reply_text("Football game help coming soon!")
