# Modified to handle callback queries
import random
import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from src.database import get_user, update_user_balance, record_transaction, record_game
from src.utils.formatting import format_money

# Active basketball competitions
active_basketball_games = {}

async def basketball_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle the /basketball command - Telegram animated basketball game"""
    # Handle both direct commands and callback queries
    if update.message:
        pass
    elif update.callback_query:
        update.message = update.callback_query.message
        
    keyboard = [
        [
            InlineKeyboardButton("🏀 Solo Basketball", callback_data="basketball_solo"),
            InlineKeyboardButton("👥 Multiplayer", callback_data="basketball_multiplayer")
        ],
        [
            InlineKeyboardButton("⚔️ Basketball Duel", callback_data="basketball_duel"),
            InlineKeyboardButton("📊 How to Play", callback_data="basketball_help")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    message_text = (
        "🏀 **ANIMATED BASKETBALL GAME**\n\n"
        "Real Telegram basketball animation!\n\n"
        "**Game Modes:**\n"
        "🏀 **Solo**: Play against the bot\n"
        "👥 **Multiplayer**: Everyone bets, winner takes pot\n"
        "⚔️ **Duel**: Challenge another player\n\n"
        "Choose your game mode:"
    )

    await update.message.reply_text(message_text, reply_markup=reply_markup, parse_mode='Markdown')

async def basketball_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle basketball game callbacks"""
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    data = query.data.split("_")
    
    if len(data) < 2:
        return
    
    action = data[1]
    
    if action == "solo":
        await query.message.reply_text("Solo basketball game coming soon!")
    elif action == "multiplayer":
        await query.message.reply_text("Multiplayer basketball game coming soon!")
    elif action == "duel":
        await query.message.reply_text("Basketball duel game coming soon!")
    elif action == "help":
        await query.message.reply_text("Basketball game help coming soon!")
