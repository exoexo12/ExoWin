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
    """Handle the /football command"""
    # Handle both direct commands and callback queries
    if update.message:
        message = update.message
        user_id = update.effective_user.id
    elif update.callback_query:
        message = update.callback_query.message
        user_id = update.callback_query.from_user.id
    else:
        return
    
    user = await get_user(user_id)
    
    keyboard = [
        [
            InlineKeyboardButton("⚽ Solo Penalty", callback_data="football_solo"),
            InlineKeyboardButton("⚔️ Penalty Shootout", callback_data="football_challenge")
        ],
        [
            InlineKeyboardButton("🏆 Tournament", callback_data="football_tournament"),
            InlineKeyboardButton("📊 Scoring", callback_data="football_scoring")
        ],
        [
            InlineKeyboardButton("🏆 Leaderboard", callback_data="leaderboard_football_all_time")
        ],
        [
            InlineKeyboardButton("🔙 Back to Games", callback_data="menu_games")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    message_text = (
        "⚽ **FOOTBALL PENALTY** ⚽\n\n"
        f"💰 Balance: {format_money(user['balance'])}\n\n"
        "Take your penalty kick!\n\n"
        "**Scoring:**\n"
        "⚽ Perfect Goal: 8x your bet\n"
        "🟢 Good Goal: 4x your bet\n"
        "🟡 Close: 2x your bet\n"
        "🔴 Saved: 1x your bet\n"
        "❌ Miss: Lose your bet"
    )
    
    if update.message:
        await message.reply_text(
            message_text,
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
    elif update.callback_query:
        await update.callback_query.edit_message_text(
            message_text,
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )

async def football_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle football game callbacks"""
    query = update.callback_query
    await query.answer()
    
    data = query.data.split('_')
    action = data[1]
    
    if action == "solo":
        # Show bet amount selection
        keyboard = [
            [
                InlineKeyboardButton("💰 $1", callback_data="football_solo_bet_1"),
                InlineKeyboardButton("💰 $5", callback_data="football_solo_bet_5"),
                InlineKeyboardButton("💰 $10", callback_data="football_solo_bet_10")
            ],
            [
                InlineKeyboardButton("💰 $25", callback_data="football_solo_bet_25"),
                InlineKeyboardButton("💰 $50", callback_data="football_solo_bet_50"),
                InlineKeyboardButton("💰 $100", callback_data="football_solo_bet_100")
            ],
            [
                InlineKeyboardButton("🔙 Back", callback_data="football_back")
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            "⚽ **SOLO PENALTY**\n\n"
            "Choose your bet amount:\n"
            "Perfect goals pay 8x!",
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
    
    elif action == "solo" and data[2] == "bet":
        # Execute solo football game
        bet_amount = float(data[3])
        await execute_solo_football_game(query, bet_amount)
    
    elif action == "scoring":
        # Show scoring system
        scoring_text = (
            "⚽ **FOOTBALL SCORING**\n\n"
            "Based on your penalty kick:\n\n"
            "⚽ **Perfect Goal**: 8x multiplier\n"
            "🟢 **Good Goal**: 4x multiplier\n"
            "🟡 **Close**: 2x multiplier\n"
            "🔴 **Saved**: 1x multiplier\n"
            "❌ **Miss**: 0x (lose bet)\n\n"
            "💡 **Tip**: Aim for the corners!"
        )
        
        keyboard = [[InlineKeyboardButton("🔙 Back", callback_data="football_back")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(scoring_text, reply_markup=reply_markup, parse_mode='Markdown')

async def execute_solo_football_game(query, bet_amount: float):
    """Execute a solo football game with animation"""
    user = await get_user(query.from_user.id)
    
    if user["balance"] < bet_amount:
        await query.edit_message_text(
            f"❌ Insufficient funds!\n"
            f"Balance: {format_money(user['balance'])}\n"
            f"Required: {format_money(bet_amount)}"
        )
        return
    
    # Deduct bet amount
    await update_user_balance(user["user_id"], -bet_amount)
    await record_transaction(user["user_id"], -bet_amount, "football bet", "Solo football game")
    
    # Show kicking animation
    await query.edit_message_text(
        f"⚽ **TAKING PENALTY...**\n\n"
        f"💰 Bet: {format_money(bet_amount)}\n\n"
        f"⚽ Kicking... ⚽",
        parse_mode='Markdown'
    )
    
    # Send animated football using Telegram's built-in animation
    football_message = await query.message.reply_dice(emoji="⚽")
    
    # Wait for animation
    await asyncio.sleep(3)
    
    # Get result (1-5)
    result = football_message.dice.value
    scoring = FOOTBALL_SCORING[result]
    winnings = bet_amount * scoring['multiplier']
    
    # Record game
    game_id = await record_game(
        user["user_id"], 
        "football", 
        bet_amount, 
        "win" if winnings > 0 else "loss", 
        winnings
    )
    
    if winnings > 0:
        await update_user_balance(user["user_id"], winnings)
        await record_transaction(user["user_id"], winnings, "football win", f"Game ID: {game_id}")
    
    # Get updated balance
    user = await get_user(user["user_id"])
    
    # Show result
    if winnings > 0:
        result_text = (
            f"🎉 **GOAL!** 🎉\n\n"
            f"⚽ **RESULT:** {scoring['emoji']} **{scoring['name']}**\n"
            f"🎯 Multiplier: **{scoring['multiplier']}x**\n\n"
            f"💰 Bet: {format_money(bet_amount)}\n"
            f"🏆 Won: **{format_money(winnings)}**\n"
            f"📈 Profit: **{format_money(winnings - bet_amount)}**\n"
            f"💳 Balance: {format_money(user['balance'])}"
        )
    else:
        result_text = (
            f"😢 **MISSED!**\n\n"
            f"⚽ **RESULT:** {scoring['emoji']} **{scoring['name']}**\n\n"
            f"💸 Lost: {format_money(bet_amount)}\n"
            f"💳 Balance: {format_money(user['balance'])}\n\n"
            f"⚽ Try again for the perfect goal!"
        )
    
    keyboard = [
        [
            InlineKeyboardButton("⚽ Kick Again", callback_data=f"football_solo_bet_{bet_amount}"),
            InlineKeyboardButton("💰 Double Bet", callback_data=f"football_solo_bet_{bet_amount*2}")
        ],
        [
            InlineKeyboardButton("⚔️ Challenge Player", callback_data="football_challenge"),
            InlineKeyboardButton("🏠 Main Menu", callback_data="main_menu")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.message.reply_text(result_text, reply_markup=reply_markup, parse_mode='Markdown')

# Export the callback handler
football_callback_handler = football_callback