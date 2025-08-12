# Modified to handle callback queries
import random
import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from src.database import get_user, update_user_balance, record_transaction, record_game
from src.utils.formatting import format_money

# Active darts competitions
active_darts_games = {}

async def darts_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle the /darts command - Telegram animated darts game"""
    # Handle both direct commands and callback queries
    if update.message:
        pass
    elif update.callback_query:
        update.message = update.callback_query.message
        
    keyboard = [
        [
            InlineKeyboardButton("🎯 Solo Darts", callback_data="darts_solo"),
            InlineKeyboardButton("👥 Multiplayer", callback_data="darts_multiplayer")
        ],
        [
            InlineKeyboardButton("⚔️ Darts Duel", callback_data="darts_duel"),
            InlineKeyboardButton("📊 How to Play", callback_data="darts_help")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    message_text = (
        "🎯 **ANIMATED DARTS GAME**\n\n"
        "Real Telegram darts animation!\n\n"
        "**Game Modes:**\n"
        "🎯 **Solo**: Play against the bot\n"
        "👥 **Multiplayer**: Everyone bets, winner takes pot\n"
        "⚔️ **Duel**: Challenge another player\n\n"
        "Choose your game mode:"
    )

    await update.message.reply_text(message_text, reply_markup=reply_markup, parse_mode='Markdown')

async def darts_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle darts game callbacks"""
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    data = query.data.split("_")
    
    if len(data) < 2:
        return
    
    action = data[1]
    
    if action == "solo":
        await query.message.reply_text("Solo darts game coming soon!")
    elif action == "multiplayer":
        await query.message.reply_text("Multiplayer darts game coming soon!")
    elif action == "duel":
        await query.message.reply_text("Darts duel game coming soon!")
    elif action == "help":
        await query.message.reply_text("Darts game help coming soon!")
