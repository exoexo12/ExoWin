import random
import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from src.database import get_user, update_user_balance, record_transaction, record_game
from src.utils.formatting import format_money

# Active basketball competitions
active_basketball_games = {}

# Basketball scoring system (Telegram basketball returns 1-5)
BASKETBALL_SCORING = {
    1: {"name": "Miss", "multiplier": 0, "emoji": "❌"},
    2: {"name": "Rim Shot", "multiplier": 1, "emoji": "🔴"},
    3: {"name": "Good Shot", "multiplier": 2, "emoji": "🟡"},
    4: {"name": "Great Shot", "multiplier": 4, "emoji": "🟢"},
    5: {"name": "Perfect Shot", "multiplier": 8, "emoji": "🏀"}
}

async def basketball_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle the /basketball command"""
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
            InlineKeyboardButton("🏀 Solo Shooting", callback_data="basketball_solo"),
            InlineKeyboardButton("⚔️ Shootout", callback_data="basketball_challenge")
        ],
        [
            InlineKeyboardButton("🏆 Tournament", callback_data="basketball_tournament"),
            InlineKeyboardButton("📊 Scoring", callback_data="basketball_scoring")
        ],
        [
            InlineKeyboardButton("🏆 Leaderboard", callback_data="leaderboard_basketball_all_time")
        ],
        [
            InlineKeyboardButton("🔙 Back to Games", callback_data="menu_games")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    message_text = (
        "🏀 **BASKETBALL GAME** 🏀\n\n"
        f"💰 Balance: {format_money(user['balance'])}\n\n"
        "Take your shot and score big!\n\n"
        "**Scoring:**\n"
        "🏀 Perfect Shot: 8x your bet\n"
        "🟢 Great Shot: 4x your bet\n"
        "🟡 Good Shot: 2x your bet\n"
        "🔴 Rim Shot: 1x your bet\n"
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

async def basketball_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle basketball game callbacks"""
    query = update.callback_query
    await query.answer()
    
    data = query.data.split('_')
    action = data[1]
    
    if action == "solo":
        # Show bet amount selection
        keyboard = [
            [
                InlineKeyboardButton("💰 $1", callback_data="basketball_solo_bet_1"),
                InlineKeyboardButton("💰 $5", callback_data="basketball_solo_bet_5"),
                InlineKeyboardButton("💰 $10", callback_data="basketball_solo_bet_10")
            ],
            [
                InlineKeyboardButton("💰 $25", callback_data="basketball_solo_bet_25"),
                InlineKeyboardButton("💰 $50", callback_data="basketball_solo_bet_50"),
                InlineKeyboardButton("💰 $100", callback_data="basketball_solo_bet_100")
            ],
            [
                InlineKeyboardButton("🔙 Back", callback_data="basketball_back")
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            "🏀 **SOLO BASKETBALL**\n\n"
            "Choose your bet amount:\n"
            "Perfect shots pay 8x!",
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
    
    elif action == "solo" and data[2] == "bet":
        # Execute solo basketball game
        bet_amount = float(data[3])
        await execute_solo_basketball_game(query, bet_amount)
    
    elif action == "scoring":
        # Show scoring system
        scoring_text = (
            "🏀 **BASKETBALL SCORING**\n\n"
            "Based on your shot accuracy:\n\n"
            "🏀 **Perfect Shot**: 8x multiplier\n"
            "🟢 **Great Shot**: 4x multiplier\n"
            "🟡 **Good Shot**: 2x multiplier\n"
            "🔴 **Rim Shot**: 1x multiplier\n"
            "❌ **Miss**: 0x (lose bet)\n\n"
            "💡 **Tip**: Practice makes perfect!"
        )
        
        keyboard = [[InlineKeyboardButton("🔙 Back", callback_data="basketball_back")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(scoring_text, reply_markup=reply_markup, parse_mode='Markdown')

async def execute_solo_basketball_game(query, bet_amount: float):
    """Execute a solo basketball game with animation"""
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
    await record_transaction(user["user_id"], -bet_amount, "basketball bet", "Solo basketball game")
    
    # Show shooting animation
    await query.edit_message_text(
        f"🏀 **TAKING SHOT...**\n\n"
        f"💰 Bet: {format_money(bet_amount)}\n\n"
        f"🏀 Shooting... 🏀",
        parse_mode='Markdown'
    )
    
    # Send animated basketball using Telegram's built-in animation
    basketball_message = await query.message.reply_dice(emoji="🏀")
    
    # Wait for animation
    await asyncio.sleep(3)
    
    # Get result (1-5)
    result = basketball_message.dice.value
    scoring = BASKETBALL_SCORING[result]
    winnings = bet_amount * scoring['multiplier']
    
    # Record game
    game_id = await record_game(
        user["user_id"], 
        "basketball", 
        bet_amount, 
        "win" if winnings > 0 else "loss", 
        winnings
    )
    
    if winnings > 0:
        await update_user_balance(user["user_id"], winnings)
        await record_transaction(user["user_id"], winnings, "basketball win", f"Game ID: {game_id}")
    
    # Get updated balance
    user = await get_user(user["user_id"])
    
    # Show result
    if winnings > 0:
        result_text = (
            f"🎉 **GREAT SHOT!** 🎉\n\n"
            f"🏀 **RESULT:** {scoring['emoji']} **{scoring['name']}**\n"
            f"🎯 Multiplier: **{scoring['multiplier']}x**\n\n"
            f"💰 Bet: {format_money(bet_amount)}\n"
            f"🏆 Won: **{format_money(winnings)}**\n"
            f"📈 Profit: **{format_money(winnings - bet_amount)}**\n"
            f"💳 Balance: {format_money(user['balance'])}"
        )
    else:
        result_text = (
            f"😢 **MISSED!**\n\n"
            f"🏀 **RESULT:** {scoring['emoji']} **{scoring['name']}**\n\n"
            f"💸 Lost: {format_money(bet_amount)}\n"
            f"💳 Balance: {format_money(user['balance'])}\n\n"
            f"🏀 Keep practicing your shot!"
        )
    
    keyboard = [
        [
            InlineKeyboardButton("🏀 Shoot Again", callback_data=f"basketball_solo_bet_{bet_amount}"),
            InlineKeyboardButton("💰 Double Bet", callback_data=f"basketball_solo_bet_{bet_amount*2}")
        ],
        [
            InlineKeyboardButton("⚔️ Challenge Player", callback_data="basketball_challenge"),
            InlineKeyboardButton("🏠 Main Menu", callback_data="main_menu")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.message.reply_text(result_text, reply_markup=reply_markup, parse_mode='Markdown')

# Export the callback handler
basketball_callback_handler = basketball_callback