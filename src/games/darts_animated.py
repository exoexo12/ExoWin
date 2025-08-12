import random
import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from src.database import get_user, update_user_balance, record_transaction, record_game
from src.utils.formatting import format_money

# Active darts competitions
active_darts_games = {}

# Darts scoring system (Telegram darts returns 1-6)
DARTS_SCORING = {
    1: {"name": "Miss", "multiplier": 0, "emoji": "❌"},
    2: {"name": "Outer Ring", "multiplier": 1, "emoji": "⚪"},
    3: {"name": "Inner Ring", "multiplier": 2, "emoji": "🔵"},
    4: {"name": "Double Ring", "multiplier": 3, "emoji": "🟡"},
    5: {"name": "Triple Ring", "multiplier": 5, "emoji": "🟠"},
    6: {"name": "Bullseye", "multiplier": 10, "emoji": "🎯"}
}

async def darts_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle the /darts command"""
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
            InlineKeyboardButton("🎯 Solo Darts", callback_data="darts_solo"),
            InlineKeyboardButton("⚔️ Challenge", callback_data="darts_challenge")
        ],
        [
            InlineKeyboardButton("🏆 Tournament", callback_data="darts_tournament"),
            InlineKeyboardButton("📊 Scoring", callback_data="darts_scoring")
        ],
        [
            InlineKeyboardButton("🏆 Leaderboard", callback_data="leaderboard_darts_all_time")
        ],
        [
            InlineKeyboardButton("🔙 Back to Games", callback_data="menu_games")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    message_text = (
        "🎯 **DARTS GAME** 🎯\n\n"
        f"💰 Balance: {format_money(user['balance'])}\n\n"
        "Aim for the bullseye!\n\n"
        "**Scoring:**\n"
        "🎯 Bullseye: 10x your bet\n"
        "🟠 Triple Ring: 5x your bet\n"
        "🟡 Double Ring: 3x your bet\n"
        "🔵 Inner Ring: 2x your bet\n"
        "⚪ Outer Ring: 1x your bet\n"
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
async def darts_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle darts game callbacks"""
    query = update.callback_query
    await query.answer()
    
    data = query.data.split('_')
    action = data[1]
    
    if action == "solo":
        # Show bet amount selection
        keyboard = [
            [
                InlineKeyboardButton("💰 $1", callback_data="darts_solo_bet_1"),
                InlineKeyboardButton("💰 $5", callback_data="darts_solo_bet_5"),
                InlineKeyboardButton("💰 $10", callback_data="darts_solo_bet_10")
            ],
            [
                InlineKeyboardButton("💰 $25", callback_data="darts_solo_bet_25"),
                InlineKeyboardButton("💰 $50", callback_data="darts_solo_bet_50"),
                InlineKeyboardButton("💰 $100", callback_data="darts_solo_bet_100")
            ],
            [
                InlineKeyboardButton("🔙 Back", callback_data="darts_back")
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            "🎯 **SOLO DARTS**\n\n"
            "Choose your bet amount:\n"
            "Aim for the bullseye for 10x!",
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
    
    elif action == "challenge":
        # Show challenge options
        keyboard = [
            [
                InlineKeyboardButton("⚔️ Create Challenge ($10)", callback_data="darts_challenge_create_10"),
                InlineKeyboardButton("⚔️ Create Challenge ($25)", callback_data="darts_challenge_create_25")
            ],
            [
                InlineKeyboardButton("⚔️ Create Challenge ($50)", callback_data="darts_challenge_create_50"),
                InlineKeyboardButton("⚔️ Create Challenge ($100)", callback_data="darts_challenge_create_100")
            ],
            [
                InlineKeyboardButton("🔙 Back", callback_data="darts_back")
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            "⚔️ **DARTS CHALLENGE**\n\n"
            "Challenge another player to a darts duel!\n"
            "Best throw wins the pot!",
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
    
    elif action == "solo" and data[2] == "bet":
        # Execute solo darts game
        bet_amount = float(data[3])
        await execute_solo_darts_game(query, bet_amount)
    
    elif action == "challenge" and data[2] == "create":
        # Create darts challenge
        bet_amount = float(data[3])
        await create_darts_challenge(query, bet_amount)
    
    elif action == "scoring":
        # Show scoring system
        scoring_text = (
            "🎯 **DARTS SCORING SYSTEM**\n\n"
            "Based on where your dart lands:\n\n"
            "🎯 **Bullseye**: 10x multiplier\n"
            "🟠 **Triple Ring**: 5x multiplier\n"
            "🟡 **Double Ring**: 3x multiplier\n"
            "🔵 **Inner Ring**: 2x multiplier\n"
            "⚪ **Outer Ring**: 1x multiplier\n"
            "❌ **Miss**: 0x (lose bet)\n\n"
            "💡 **Tip**: Higher risk = higher reward!"
        )
        
        keyboard = [[InlineKeyboardButton("🔙 Back", callback_data="darts_back")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(scoring_text, reply_markup=reply_markup, parse_mode='Markdown')

async def execute_solo_darts_game(query, bet_amount: float):
    """Execute a solo darts game with animation"""
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
    await record_transaction(user["user_id"], -bet_amount, "darts bet", "Solo darts game")
    
    # Show throwing animation
    await query.edit_message_text(
        f"🎯 **THROWING DART...**\n\n"
        f"💰 Bet: {format_money(bet_amount)}\n\n"
        f"🎯 Aiming... 🎯",
        parse_mode='Markdown'
    )
    
    # Send animated darts using Telegram's built-in animation
    darts_message = await query.message.reply_dice(emoji="🎯")
    
    # Wait for animation
    await asyncio.sleep(3)
    
    # Get result (1-6)
    result = darts_message.dice.value
    scoring = DARTS_SCORING[result]
    winnings = bet_amount * scoring['multiplier']
    
    # Record game
    game_id = await record_game(
        user["user_id"], 
        "darts", 
        bet_amount, 
        "win" if winnings > 0 else "loss", 
        winnings
    )
    
    if winnings > 0:
        await update_user_balance(user["user_id"], winnings)
        await record_transaction(user["user_id"], winnings, "darts win", f"Game ID: {game_id}")
    
    # Get updated balance
    user = await get_user(user["user_id"])
    
    # Show result
    if winnings > 0:
        result_text = (
            f"🎉 **GREAT THROW!** 🎉\n\n"
            f"🎯 **RESULT:** {scoring['emoji']} **{scoring['name']}**\n"
            f"🎯 Multiplier: **{scoring['multiplier']}x**\n\n"
            f"💰 Bet: {format_money(bet_amount)}\n"
            f"🏆 Won: **{format_money(winnings)}**\n"
            f"📈 Profit: **{format_money(winnings - bet_amount)}**\n"
            f"💳 Balance: {format_money(user['balance'])}"
        )
    else:
        result_text = (
            f"😢 **MISSED!**\n\n"
            f"🎯 **RESULT:** {scoring['emoji']} **{scoring['name']}**\n\n"
            f"💸 Lost: {format_money(bet_amount)}\n"
            f"💳 Balance: {format_money(user['balance'])}\n\n"
            f"🎯 Try again for the bullseye!"
        )
    
    keyboard = [
        [
            InlineKeyboardButton("🎯 Throw Again", callback_data=f"darts_solo_bet_{bet_amount}"),
            InlineKeyboardButton("💰 Double Bet", callback_data=f"darts_solo_bet_{bet_amount*2}")
        ],
        [
            InlineKeyboardButton("⚔️ Challenge Player", callback_data="darts_challenge"),
            InlineKeyboardButton("🏠 Main Menu", callback_data="main_menu")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.message.reply_text(result_text, reply_markup=reply_markup, parse_mode='Markdown')

async def create_darts_challenge(query, bet_amount: float):
    """Create a darts challenge for other players"""
    user = await get_user(query.from_user.id)
    
    if user["balance"] < bet_amount:
        await query.edit_message_text(
            f"❌ Insufficient funds!\n"
            f"Balance: {format_money(user['balance'])}\n"
            f"Required: {format_money(bet_amount)}"
        )
        return
    
    game_id = f"darts_{query.message.chat.id}_{random.randint(1000, 9999)}"
    
    # Create new challenge
    active_darts_games[game_id] = {
        'creator': query.from_user.id,
        'creator_name': query.from_user.first_name,
        'bet_amount': bet_amount,
        'challenger': None,
        'challenger_name': None,
        'creator_score': None,
        'challenger_score': None,
        'status': 'waiting',
        'chat_id': query.message.chat.id
    }
    
    keyboard = [
        [
            InlineKeyboardButton("⚔️ Accept Challenge", callback_data=f"darts_accept_{game_id}"),
        ],
        [
            InlineKeyboardButton("❌ Cancel", callback_data=f"darts_cancel_{game_id}")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        f"⚔️ **DARTS CHALLENGE**\n\n"
        f"🎯 **{query.from_user.first_name}** challenges you to darts!\n\n"
        f"💰 Bet Amount: {format_money(bet_amount)}\n"
        f"🏆 Winner takes: {format_money(bet_amount * 2)}\n\n"
        f"**Rules:**\n"
        f"• Both players throw one dart\n"
        f"• Highest score wins the pot\n"
        f"• Tie = money returned\n\n"
        f"⏰ Waiting for challenger...",
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

# Export the callback handler
darts_callback_handler = darts_callback