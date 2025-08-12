import random
import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from src.database import get_user, update_user_balance, record_transaction, record_game
from src.utils.formatting import format_money

# Active bowling competitions
active_bowling_games = {}

# Bowling scoring system (Telegram bowling returns 1-6)
BOWLING_SCORING = {
    1: {"name": "Gutter Ball", "multiplier": 0, "emoji": "❌"},
    2: {"name": "1-2 Pins", "multiplier": 1, "emoji": "🔴"},
    3: {"name": "3-5 Pins", "multiplier": 2, "emoji": "🟡"},
    4: {"name": "6-8 Pins", "multiplier": 3, "emoji": "🟢"},
    5: {"name": "9 Pins", "multiplier": 5, "emoji": "🔵"},
    6: {"name": "Strike!", "multiplier": 10, "emoji": "🎳"}
}

async def bowling_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle the /bowling command"""
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
            InlineKeyboardButton("🎳 Solo Bowling", callback_data="bowling_solo"),
            InlineKeyboardButton("⚔️ Bowling Duel", callback_data="bowling_challenge")
        ],
        [
            InlineKeyboardButton("🏆 Tournament", callback_data="bowling_tournament"),
            InlineKeyboardButton("📊 Scoring", callback_data="bowling_scoring")
        ],
        [
            InlineKeyboardButton("🏆 Leaderboard", callback_data="leaderboard_bowling_all_time")
        ],
        [
            InlineKeyboardButton("🔙 Back to Games", callback_data="menu_games")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    message_text = (
        "🎳 **BOWLING GAME** 🎳\n\n"
        f"💰 Balance: {format_money(user['balance'])}\n\n"
        "Roll for a strike!\n\n"
        "**Scoring:**\n"
        "🎳 Strike: 10x your bet\n"
        "🔵 9 Pins: 5x your bet\n"
        "🟢 6-8 Pins: 3x your bet\n"
        "🟡 3-5 Pins: 2x your bet\n"
        "🔴 1-2 Pins: 1x your bet\n"
        "❌ Gutter: Lose your bet"
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

async def bowling_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle bowling game callbacks"""
    query = update.callback_query
    await query.answer()
    
    data = query.data.split('_')
    action = data[1]
    
    if action == "solo":
        # Show bet amount selection
        keyboard = [
            [
                InlineKeyboardButton("💰 $1", callback_data="bowling_solo_bet_1"),
                InlineKeyboardButton("💰 $5", callback_data="bowling_solo_bet_5"),
                InlineKeyboardButton("💰 $10", callback_data="bowling_solo_bet_10")
            ],
            [
                InlineKeyboardButton("💰 $25", callback_data="bowling_solo_bet_25"),
                InlineKeyboardButton("💰 $50", callback_data="bowling_solo_bet_50"),
                InlineKeyboardButton("💰 $100", callback_data="bowling_solo_bet_100")
            ],
            [
                InlineKeyboardButton("🔙 Back", callback_data="bowling_back")
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            "🎳 **SOLO BOWLING**\n\n"
            "Choose your bet amount:\n"
            "Strikes pay 10x!",
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
    
    elif action == "solo" and data[2] == "bet":
        # Execute solo bowling game
        bet_amount = float(data[3])
        await execute_solo_bowling_game(query, bet_amount)
    
    elif action == "scoring":
        # Show scoring system
        scoring_text = (
            "🎳 **BOWLING SCORING**\n\n"
            "Based on pins knocked down:\n\n"
            "🎳 **Strike (10 pins)**: 10x multiplier\n"
            "🔵 **9 Pins**: 5x multiplier\n"
            "🟢 **6-8 Pins**: 3x multiplier\n"
            "🟡 **3-5 Pins**: 2x multiplier\n"
            "🔴 **1-2 Pins**: 1x multiplier\n"
            "❌ **Gutter Ball**: 0x (lose bet)\n\n"
            "💡 **Tip**: Aim for the center!"
        )
        
        keyboard = [[InlineKeyboardButton("🔙 Back", callback_data="bowling_back")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(scoring_text, reply_markup=reply_markup, parse_mode='Markdown')

async def execute_solo_bowling_game(query, bet_amount: float):
    """Execute a solo bowling game with animation"""
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
    await record_transaction(user["user_id"], -bet_amount, "bowling bet", "Solo bowling game")
    
    # Show bowling animation
    await query.edit_message_text(
        f"🎳 **ROLLING BALL...**\n\n"
        f"💰 Bet: {format_money(bet_amount)}\n\n"
        f"🎳 Rolling... 🎳",
        parse_mode='Markdown'
    )
    
    # Send animated bowling using Telegram's built-in animation
    bowling_message = await query.message.reply_dice(emoji="🎳")
    
    # Wait for animation
    await asyncio.sleep(3)
    
    # Get result (1-6)
    result = bowling_message.dice.value
    scoring = BOWLING_SCORING[result]
    winnings = bet_amount * scoring['multiplier']
    
    # Record game
    game_id = await record_game(
        user["user_id"], 
        "bowling", 
        bet_amount, 
        "win" if winnings > 0 else "loss", 
        winnings
    )
    
    if winnings > 0:
        await update_user_balance(user["user_id"], winnings)
        await record_transaction(user["user_id"], winnings, "bowling win", f"Game ID: {game_id}")
    
    # Get updated balance
    user = await get_user(user["user_id"])
    
    # Show result
    if winnings > 0:
        result_text = (
            f"🎉 **GREAT ROLL!** 🎉\n\n"
            f"🎳 **RESULT:** {scoring['emoji']} **{scoring['name']}**\n"
            f"🎯 Multiplier: **{scoring['multiplier']}x**\n\n"
            f"💰 Bet: {format_money(bet_amount)}\n"
            f"🏆 Won: **{format_money(winnings)}**\n"
            f"📈 Profit: **{format_money(winnings - bet_amount)}**\n"
            f"💳 Balance: {format_money(user['balance'])}"
        )
    else:
        result_text = (
            f"😢 **GUTTER BALL!**\n\n"
            f"🎳 **RESULT:** {scoring['emoji']} **{scoring['name']}**\n\n"
            f"💸 Lost: {format_money(bet_amount)}\n"
            f"💳 Balance: {format_money(user['balance'])}\n\n"
            f"🎳 Try again for a strike!"
        )
    
    keyboard = [
        [
            InlineKeyboardButton("🎳 Roll Again", callback_data=f"bowling_solo_bet_{bet_amount}"),
            InlineKeyboardButton("💰 Double Bet", callback_data=f"bowling_solo_bet_{bet_amount*2}")
        ],
        [
            InlineKeyboardButton("⚔️ Challenge Player", callback_data="bowling_challenge"),
            InlineKeyboardButton("🏠 Main Menu", callback_data="main_menu")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.message.reply_text(result_text, reply_markup=reply_markup, parse_mode='Markdown')

# Export the callback handler
bowling_callback_handler = bowling_callback