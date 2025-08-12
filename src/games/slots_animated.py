# Modified to handle callback queries
# Modified to handle callback queries
# Modified to handle callback queries
# Modified to handle callback queries
# Modified to handle callback queries
# Modified to handle callback queries
import random
import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from src.database import get_user, update_user_balance, record_transaction, record_game
from src.utils.formatting import format_money

# Active slots tournaments
active_slots_tournaments = {}

# Slot machine payouts (based on Telegram's slot machine values)
SLOT_PAYOUTS = {
    (1, 1, 1): {"multiplier": 10, "name": "🍋 Triple Lemons"},
    (2, 2, 2): {"multiplier": 15, "name": "🍊 Triple Oranges"},
    (3, 3, 3): {"multiplier": 20, "name": "🍇 Triple Grapes"},
    (4, 4, 4): {"multiplier": 30, "name": "🍒 Triple Cherries"},
    (5, 5, 5): {"multiplier": 50, "name": "🔔 Triple Bells"},
    (6, 6, 6): {"multiplier": 100, "name": "💎 Triple Diamonds"},
    (7, 7, 7): {"multiplier": 777, "name": "🎰 JACKPOT!"},
    # Two of a kind
    "two_kind": {"multiplier": 2, "name": "Two of a Kind"},
    # Special combinations
    (1, 2, 3): {"multiplier": 5, "name": "🍋🍊🍇 Fruit Mix"},
    (4, 5, 6): {"multiplier": 8, "name": "🍒🔔💎 Premium Mix"}
}

# Handle both direct commands and callback queries from games menu
# Handle both direct commands and callback queries from games menuasync def slots_command_wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE):    if update.callback_query:        update.message = update.callback_query.message        await update.callback_query.answer()    return await slots_command(update, context)
# Handle both direct commands and callback queries from games menuasync def slots_command_wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE):    if update.callback_query:        update.message = update.callback_query.message        await update.callback_query.answer()    return await slots_command(update, context)
# Handle both direct commands and callback queries from games menuasync def slots_command_wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE):    if update.callback_query:        update.message = update.callback_query.message        await update.callback_query.answer()    return await slots_command(update, context)
# Handle both direct commands and callback queries from games menuasync def slots_command_wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE):    if update.callback_query:        update.message = update.callback_query.message        await update.callback_query.answer()    return await slots_command(update, context)
# Handle both direct commands and callback queries from games menuasync def slots_command_wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE):    if update.callback_query:        update.message = update.callback_query.message        await update.callback_query.answer()    return await slots_command(update, context)
# Handle both direct commands and callback queries from games menuasync def slots_command_wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE):    if update.callback_query:        update.message = update.callback_query.message        await update.callback_query.answer()    return await slots_command(update, context)
# Handle both direct commands and callback queries from games menuasync def slots_command_wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE):    if update.callback_query:        update.message = update.callback_query.message        await update.callback_query.answer()    return await slots_command(update, context)
# Handle both direct commands and callback queries from games menuasync def slots_command_wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE):    if update.callback_query:        update.message = update.callback_query.message        await update.callback_query.answer()    return await slots_command(update, context)
# Handle both direct commands and callback queries from games menuasync def slots_command_wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE):    if update.callback_query:        update.message = update.callback_query.message        await update.callback_query.answer()    return await slots_command(update, context)
# Handle both direct commands and callback queries from games menuasync def slots_command_wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE):    if update.callback_query:        update.message = update.callback_query.message        await update.callback_query.answer()    return await slots_command(update, context)
# Handle both direct commands and callback queries from games menuasync def slots_command_wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE):    if update.callback_query:        update.message = update.callback_query.message        await update.callback_query.answer()    return await slots_command(update, context)
# Handle both direct commands and callback queries from games menuasync def slots_command_wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE):    if update.callback_query:        update.message = update.callback_query.message        await update.callback_query.answer()    return await slots_command(update, context)
# Handle both direct commands and callback queries from games menuasync def slots_command_wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE):    if update.callback_query:        update.message = update.callback_query.message        await update.callback_query.answer()    return await slots_command(update, context)
# Handle both direct commands and callback queries from games menuasync def slots_command_wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE):    if update.callback_query:        update.message = update.callback_query.message        await update.callback_query.answer()    return await slots_command(update, context)
# Handle both direct commands and callback queries from games menuasync def slots_command_wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE):    if update.callback_query:        update.message = update.callback_query.message        await update.callback_query.answer()    return await slots_command(update, context)
# Handle both direct commands and callback queries from games menuasync def slots_command_wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE):    if update.callback_query:        update.message = update.callback_query.message        await update.callback_query.answer()    return await slots_command(update, context)
# Handle both direct commands and callback queries from games menuasync def slots_command_wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE):    if update.callback_query:        update.message = update.callback_query.message        await update.callback_query.answer()    return await slots_command(update, context)
# Handle both direct commands and callback queries from games menuasync def slots_command_wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE):    if update.callback_query:        update.message = update.callback_query.message        await update.callback_query.answer()    return await slots_command(update, context)
# Handle both direct commands and callback queries from games menuasync def slots_command_wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE):    if update.callback_query:        update.message = update.callback_query.message        await update.callback_query.answer()    return await slots_command(update, context)
# Handle both direct commands and callback queries from games menuasync def slots_command_wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE):    if update.callback_query:        update.message = update.callback_query.message        await update.callback_query.answer()    return await slots_command(update, context)
# Handle both direct commands and callback queries from games menuasync def slots_command_wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE):    if update.callback_query:        update.message = update.callback_query.message        await update.callback_query.answer()    return await slots_command(update, context)
# Handle both direct commands and callback queries from games menuasync def slots_command_wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE):    if update.callback_query:        update.message = update.callback_query.message        await update.callback_query.answer()    return await slots_command(update, context)
# Handle both direct commands and callback queries from games menuasync def slots_command_wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE):    if update.callback_query:        update.message = update.callback_query.message        await update.callback_query.answer()    return await slots_command(update, context)
# Handle both direct commands and callback queries from games menuasync def slots_command_wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE):    if update.callback_query:        update.message = update.callback_query.message        await update.callback_query.answer()    return await slots_command(update, context)
# Handle both direct commands and callback queries from games menuasync def slots_command_wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE):    if update.callback_query:        update.message = update.callback_query.message        await update.callback_query.answer()    return await slots_command(update, context)
# Handle both direct commands and callback queries from games menuasync def slots_command_wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE):    if update.callback_query:        update.message = update.callback_query.message        await update.callback_query.answer()    return await slots_command(update, context)
# Handle both direct commands and callback queries from games menuasync def slots_command_wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE):    if update.callback_query:        update.message = update.callback_query.message        await update.callback_query.answer()    return await slots_command(update, context)
# Handle both direct commands and callback queries from games menuasync def slots_command_wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE):    if update.callback_query:        update.message = update.callback_query.message        await update.callback_query.answer()    return await slots_command(update, context)
# Handle both direct commands and callback queries from games menuasync def slots_command_wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE):    if update.callback_query:        update.message = update.callback_query.message        await update.callback_query.answer()    return await slots_command(update, context)
# Handle both direct commands and callback queries from games menuasync def slots_command_wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE):    if update.callback_query:        update.message = update.callback_query.message        await update.callback_query.answer()    return await slots_command(update, context)
# Handle both direct commands and callback queries from games menuasync def slots_command_wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE):    if update.callback_query:        update.message = update.callback_query.message        await update.callback_query.answer()    return await slots_command(update, context)
async def slots_command_wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.callback_query:
        update.message = update.callback_query.message
        await update.callback_query.answer()
    return await slots_command(update, context)

# Handle both direct commands and callback queries from games menuasync def slots_command_wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE):    if update.callback_query:        update.message = update.callback_query.message        await update.callback_query.answer()    return await slots_command(update, context)
# Handle both direct commands and callback queries from games menuasync def slots_command_wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE):    if update.callback_query:        update.message = update.callback_query.message        await update.callback_query.answer()    return await slots_command(update, context)
# Handle both direct commands and callback queries from games menuasync def slots_command_wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE):    if update.callback_query:        update.message = update.callback_query.message        await update.callback_query.answer()    return await slots_command(update, context)
# Handle both direct commands and callback queries from games menuasync def slots_command_wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE):    if update.callback_query:        update.message = update.callback_query.message        await update.callback_query.answer()    return await slots_command(update, context)
# Handle both direct commands and callback queries from games menuasync def slots_command_wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE):    if update.callback_query:        update.message = update.callback_query.message        await update.callback_query.answer()    return await slots_command(update, context)
# Handle both direct commands and callback queries from games menuasync def slots_command_wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE):    if update.callback_query:        update.message = update.callback_query.message        await update.callback_query.answer()    return await slots_command(update, context)
# Handle both direct commands and callback queries from games menuasync def slots_command_wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE):    if update.callback_query:        update.message = update.callback_query.message        await update.callback_query.answer()    return await slots_command(update, context)
# Handle both direct commands and callback queries from games menuasync def slots_command_wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE):    if update.callback_query:        update.message = update.callback_query.message        await update.callback_query.answer()    return await slots_command(update, context)
# Handle both direct commands and callback queries from games menuasync def slots_command_wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE):    if update.callback_query:        update.message = update.callback_query.message        await update.callback_query.answer()    return await slots_command(update, context)
# Handle both direct commands and callback queries from games menuasync def slots_command_wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE):    if update.callback_query:        update.message = update.callback_query.message        await update.callback_query.answer()    return await slots_command(update, context)
# Handle both direct commands and callback queries from games menuasync def slots_command_wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE):    if update.callback_query:        update.message = update.callback_query.message        await update.callback_query.answer()    return await slots_command(update, context)
# Handle both direct commands and callback queries from games menuasync def slots_command_wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE):    if update.callback_query:        update.message = update.callback_query.message        await update.callback_query.answer()    return await slots_command(update, context)
# Handle both direct commands and callback queries from games menuasync def slots_command_wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE):    if update.callback_query:        update.message = update.callback_query.message        await update.callback_query.answer()    return await slots_command(update, context)
# Handle both direct commands and callback queries from games menuasync def slots_command_wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE):    if update.callback_query:        update.message = update.callback_query.message        await update.callback_query.answer()    return await slots_command(update, context)
# Handle both direct commands and callback queries from games menuasync def slots_command_wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE):    if update.callback_query:        update.message = update.callback_query.message        await update.callback_query.answer()    return await slots_command(update, context)
# Handle both direct commands and callback queries from games menuasync def slots_command_wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE):    if update.callback_query:        update.message = update.callback_query.message        await update.callback_query.answer()    return await slots_command(update, context)
# Handle both direct commands and callback queries from games menuasync def slots_command_wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE):    if update.callback_query:        update.message = update.callback_query.message        await update.callback_query.answer()    return await slots_command(update, context)
# Handle both direct commands and callback queries from games menuasync def slots_command_wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE):    if update.callback_query:        update.message = update.callback_query.message        await update.callback_query.answer()    return await slots_command(update, context)
# Handle both direct commands and callback queries from games menuasync def slots_command_wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE):    if update.callback_query:        update.message = update.callback_query.message        await update.callback_query.answer()    return await slots_command(update, context)
# Handle both direct commands and callback queries from games menuasync def slots_command_wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE):    if update.callback_query:        update.message = update.callback_query.message        await update.callback_query.answer()    return await slots_command(update, context)
# Handle both direct commands and callback queries from games menuasync def slots_command_wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE):    if update.callback_query:        update.message = update.callback_query.message        await update.callback_query.answer()    return await slots_command(update, context)
# Handle both direct commands and callback queries from games menuasync def slots_command_wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE):    if update.callback_query:        update.message = update.callback_query.message        await update.callback_query.answer()    return await slots_command(update, context)
# Handle both direct commands and callback queries from games menuasync def slots_command_wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE):    if update.callback_query:        update.message = update.callback_query.message        await update.callback_query.answer()    return await slots_command(update, context)
# Handle both direct commands and callback queries from games menuasync def slots_command_wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE):    if update.callback_query:        update.message = update.callback_query.message        await update.callback_query.answer()    return await slots_command(update, context)
# Handle both direct commands and callback queries from games menuasync def slots_command_wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE):    if update.callback_query:        update.message = update.callback_query.message        await update.callback_query.answer()    return await slots_command(update, context)
# Handle both direct commands and callback queries from games menuasync def slots_command_wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE):    if update.callback_query:        update.message = update.callback_query.message        await update.callback_query.answer()    return await slots_command(update, context)
# Handle both direct commands and callback queries from games menuasync def slots_command_wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE):    if update.callback_query:        update.message = update.callback_query.message        await update.callback_query.answer()    return await slots_command(update, context)
# Handle both direct commands and callback queries from games menuasync def slots_command_wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE):    if update.callback_query:        update.message = update.callback_query.message        await update.callback_query.answer()    return await slots_command(update, context)
# Handle both direct commands and callback queries from games menuasync def slots_command_wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE):    if update.callback_query:        update.message = update.callback_query.message        await update.callback_query.answer()    return await slots_command(update, context)
# Handle both direct commands and callback queries from games menuasync def slots_command_wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE):    if update.callback_query:        update.message = update.callback_query.message        await update.callback_query.answer()    return await slots_command(update, context)
# Handle both direct commands and callback queries from games menuasync def slots_command_wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE):    if update.callback_query:        update.message = update.callback_query.message        await update.callback_query.answer()    return await slots_command(update, context)
async def slots_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Handle both direct commands and callback queries
    if update.message:
        pass
    elif update.callback_query:
        update.message = update.callback_query.message
    """Handle the /slots command"""
    keyboard = [
        [
            InlineKeyboardButton("🎰 Solo Slots", callback_data="slots_solo"),
            InlineKeyboardButton("🏆 Tournament", callback_data="slots_tournament")
        ],
        [
            InlineKeyboardButton("📊 Paytable", callback_data="slots_paytable")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        "🎰 **SLOT MACHINE**\n\n"
        "Pull the lever and win big!\n\n"
        "**Game Modes:**\n"
        "🎰 **Solo**: Play against the house\n"
        "🏆 **Tournament**: Compete with others\n\n"
        "💎 **JACKPOT**: 777x multiplier!",
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

async def slots_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle slots game callbacks"""
    query = update.callback_query
    await query.answer()
    
    data = query.data.split('_')
    action = data[1]
    
    if action == "solo":
        # Show bet amount selection for solo slots
        keyboard = [
            [
                InlineKeyboardButton("💰 $1", callback_data="slots_solo_bet_1"),
                InlineKeyboardButton("💰 $5", callback_data="slots_solo_bet_5"),
                InlineKeyboardButton("💰 $10", callback_data="slots_solo_bet_10")
            ],
            [
                InlineKeyboardButton("💰 $25", callback_data="slots_solo_bet_25"),
                InlineKeyboardButton("💰 $50", callback_data="slots_solo_bet_50"),
                InlineKeyboardButton("💰 $100", callback_data="slots_solo_bet_100")
            ],
            [
                InlineKeyboardButton("🔙 Back", callback_data="slots_back")
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            "🎰 **SOLO SLOTS**\n\n"
            "Choose your bet amount:\n"
            "Higher bets = bigger wins!",
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
    
    elif action == "tournament":
        # Show tournament options
        keyboard = [
            [
                InlineKeyboardButton("🏆 Join Tournament ($10)", callback_data="slots_tournament_join_10"),
                InlineKeyboardButton("🏆 Join Tournament ($25)", callback_data="slots_tournament_join_25")
            ],
            [
                InlineKeyboardButton("🏆 Join Tournament ($50)", callback_data="slots_tournament_join_50"),
                InlineKeyboardButton("🏆 Create Tournament", callback_data="slots_tournament_create")
            ],
            [
                InlineKeyboardButton("🔙 Back", callback_data="slots_back")
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            "🏆 **SLOTS TOURNAMENT**\n\n"
            "Compete with other players!\n"
            "Everyone spins, highest multiplier wins the pot!",
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
    
    elif action == "solo" and data[2] == "bet":
        # Handle solo slots execution
        bet_amount = float(data[3])
        await execute_solo_slots_game(query, bet_amount)
    
    elif action == "paytable":
        # Show paytable
        paytable_text = (
            "🎰 **SLOT MACHINE PAYTABLE**\n\n"
            "**Triple Matches:**\n"
            "🍋🍋🍋 Triple Lemons: 10x\n"
            "🍊🍊🍊 Triple Oranges: 15x\n"
            "🍇🍇🍇 Triple Grapes: 20x\n"
            "🍒🍒🍒 Triple Cherries: 30x\n"
            "🔔🔔🔔 Triple Bells: 50x\n"
            "💎💎💎 Triple Diamonds: 100x\n"
            "🎰🎰🎰 **JACKPOT: 777x**\n\n"
            "**Special Combinations:**\n"
            "🍋🍊🍇 Fruit Mix: 5x\n"
            "🍒🔔💎 Premium Mix: 8x\n"
            "Any Two Match: 2x"
        )
        
        keyboard = [[InlineKeyboardButton("🔙 Back", callback_data="slots_back")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(paytable_text, reply_markup=reply_markup, parse_mode='Markdown')

async def execute_solo_slots_game(query, bet_amount: float):
    """Execute a solo slots game with animation"""
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
    await record_transaction(user["user_id"], -bet_amount, "slots bet", "Solo slots game")
    
    # Show spinning animation
    await query.edit_message_text(
        f"🎰 **SPINNING REELS...**\n\n"
        f"💰 Bet: {format_money(bet_amount)}\n\n"
        f"🎰 Pulling the lever... 🎰",
        parse_mode='Markdown'
    )
    
    # Send animated slot machine using Telegram's built-in animation
    slots_message = await query.message.reply_dice(emoji="🎰")
    
    # Wait for animation to complete
    await asyncio.sleep(3)
    
    # Get the slot machine result
    result = slots_message.dice.value
    
    # Calculate winnings based on result
    winnings = 0
    win_description = "No match"
    
    # Telegram slot machine returns values 1-64, we need to map this to our payout system
    if result == 64:  # Jackpot (777)
        winnings = bet_amount * 777
        win_description = "🎰 JACKPOT! 777x"
    elif result >= 60:  # Triple diamonds
        winnings = bet_amount * 100
        win_description = "💎💎💎 Triple Diamonds! 100x"
    elif result >= 55:  # Triple bells
        winnings = bet_amount * 50
        win_description = "🔔🔔🔔 Triple Bells! 50x"
    elif result >= 45:  # Triple cherries
        winnings = bet_amount * 30
        win_description = "🍒🍒🍒 Triple Cherries! 30x"
    elif result >= 35:  # Triple grapes
        winnings = bet_amount * 20
        win_description = "🍇🍇🍇 Triple Grapes! 20x"
    elif result >= 25:  # Triple oranges
        winnings = bet_amount * 15
        win_description = "🍊🍊🍊 Triple Oranges! 15x"
    elif result >= 15:  # Triple lemons
        winnings = bet_amount * 10
        win_description = "🍋🍋🍋 Triple Lemons! 10x"
    elif result >= 10:  # Premium mix
        winnings = bet_amount * 8
        win_description = "🍒🔔💎 Premium Mix! 8x"
    elif result >= 6:   # Fruit mix
        winnings = bet_amount * 5
        win_description = "🍋🍊🍇 Fruit Mix! 5x"
    elif result >= 3:   # Two of a kind
        winnings = bet_amount * 2
        win_description = "Two of a Kind! 2x"
    
    # Record game
    game_id = await record_game(
        user["user_id"], 
        "slots", 
        bet_amount, 
        "win" if winnings > 0 else "loss", 
        winnings
    )
    
    if winnings > 0:
        await update_user_balance(user["user_id"], winnings)
        await record_transaction(user["user_id"], winnings, "slots win", f"Game ID: {game_id}")
    
    # Get updated balance
    user = await get_user(user["user_id"])
    
    # Show result
    if winnings > 0:
        result_text = (
            f"🎉 **WINNER!** 🎉\n\n"
            f"🎰 **{win_description}**\n\n"
            f"💰 Bet: {format_money(bet_amount)}\n"
            f"🏆 Won: **{format_money(winnings)}**\n"
            f"📈 Profit: **{format_money(winnings - bet_amount)}**\n"
            f"💳 Balance: {format_money(user['balance'])}"
        )
    else:
        result_text = (
            f"😢 **NO MATCH!**\n\n"
            f"🎰 Better luck next time!\n\n"
            f"💸 Lost: {format_money(bet_amount)}\n"
            f"💳 Balance: {format_money(user['balance'])}"
        )
    
    keyboard = [
        [
            InlineKeyboardButton("🎰 Spin Again", callback_data=f"slots_solo_bet_{bet_amount}"),
            InlineKeyboardButton("💰 Double Bet", callback_data=f"slots_solo_bet_{bet_amount*2}")
        ],
        [
            InlineKeyboardButton("🏆 Tournament", callback_data="slots_tournament"),
            InlineKeyboardButton("🏠 Main Menu", callback_data="main_menu")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.message.reply_text(result_text, reply_markup=reply_markup, parse_mode='Markdown')

# Export the callback handler
slots_callback_handler = slots_callback