import random
import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from src.database import get_user, update_user_balance, record_transaction, record_game
from src.utils.formatting import format_money

# Active coinflip games for multiplayer
active_coinflip_games = {}

async def coinflip_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle the coinflip command - Telegram animated coin game"""
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
            InlineKeyboardButton("🪙 Solo Flip", callback_data="coinflip_solo"),
            InlineKeyboardButton("👥 Multiplayer", callback_data="coinflip_multiplayer")
        ],
        [
            InlineKeyboardButton("⚔️ Coin Duel", callback_data="coinflip_duel"),
            InlineKeyboardButton("📊 How to Play", callback_data="coinflip_help")
        ],
        [
            InlineKeyboardButton("🏆 Leaderboard", callback_data="leaderboard_coinflip_all_time")
        ],
        [
            InlineKeyboardButton("🔙 Back to Games", callback_data="menu_games")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    message_text = (
        "🪙 **COINFLIP GAME** 🪙\n\n"
        f"💰 Balance: {format_money(user['balance'])}\n\n"
        "Real Telegram coin animation!\n\n"
        "**Game Modes:**\n"
        "🪙 **Solo**: Choose heads or tails\n"
        "👥 **Multiplayer**: Everyone bets, winner takes pot\n"
        "⚔️ **Duel**: Challenge another player\n\n"
        "🏆 **Win 2x your bet** for correct guess!"
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

async def coinflip_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle coinflip game callbacks"""
    query = update.callback_query
    await query.answer()
    
    data = query.data.split('_')
    
    # Handle new betting format: coinflip_choice_amount
    if len(data) == 3 and data[0] == "coinflip" and data[1] in ["heads", "tails"]:
        choice = data[1]
        bet_amount = float(data[2])
        await handle_coinflip_bet(query, choice, bet_amount)
        return
    
    if data[0] == "coinflip":
        if data[1] == "solo":
            await show_solo_coinflip_menu(query)
        elif data[1] == "multiplayer":
            await show_multiplayer_coinflip_menu(query)
        elif data[1] == "duel":
            await show_coinflip_duel_menu(query)
        elif data[1] == "help":
            await show_coinflip_help(query)
        elif data[1] == "join":
            game_id = data[2]
            await join_coinflip_game(query, game_id)
        elif data[1] == "start":
            game_id = data[2]
            await start_coinflip_game(query, game_id)

async def show_solo_coinflip_menu(query):
    """Show solo coinflip betting menu"""
    user = await get_user(query.from_user.id)
    
    message = (
        f"🪙 **SOLO COINFLIP** 🪙\n\n"
        f"💰 Balance: {format_money(user['balance'])}\n\n"
        f"Choose your side and bet amount:\n"
        f"• 50/50 chance to win\n"
        f"• Win 2x your bet amount\n"
        f"• Real coin animation!"
    )
    
    keyboard = [
        [
            InlineKeyboardButton("🪙 Heads - $1", callback_data="coinflip_heads_1.0"),
            InlineKeyboardButton("🪙 Tails - $1", callback_data="coinflip_tails_1.0")
        ],
        [
            InlineKeyboardButton("🪙 Heads - $5", callback_data="coinflip_heads_5.0"),
            InlineKeyboardButton("🪙 Tails - $5", callback_data="coinflip_tails_5.0")
        ],
        [
            InlineKeyboardButton("🪙 Heads - $10", callback_data="coinflip_heads_10.0"),
            InlineKeyboardButton("🪙 Tails - $10", callback_data="coinflip_tails_10.0")
        ],
        [
            InlineKeyboardButton("🪙 Heads - $25", callback_data="coinflip_heads_25.0"),
            InlineKeyboardButton("🪙 Tails - $25", callback_data="coinflip_tails_25.0")
        ],
        [
            InlineKeyboardButton("🔙 Back to Games", callback_data="menu_games")
        ]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(message, reply_markup=reply_markup, parse_mode='Markdown')

async def handle_coinflip_bet(query, choice, bet_amount):
    """Handle a coinflip bet"""
    user = await get_user(query.from_user.id)
    
    if user["balance"] < bet_amount:
        await query.edit_message_text(
            f"❌ **Insufficient Funds**\n\n"
            f"You need {format_money(bet_amount)} to play.\n"
            f"Your balance: {format_money(user['balance'])}\n\n"
            f"💰 Use /deposit to add funds!",
            parse_mode='Markdown'
        )
        return
    
    # Deduct bet amount
    await update_user_balance(user["user_id"], -bet_amount)
    await record_transaction(user["user_id"], -bet_amount, "bet")
    
    # Show betting message
    await query.edit_message_text(
        f"🪙 **COINFLIP GAME** 🪙\n\n"
        f"👤 Player: {query.from_user.first_name}\n"
        f"🎯 Choice: {choice.title()}\n"
        f"💰 Bet: {format_money(bet_amount)}\n\n"
        f"🎬 Flipping coin...",
        parse_mode='Markdown'
    )
    
    # Send the coin animation
    coin_message = await query.message.reply_dice(emoji="🪙")
    
    # Wait for animation to complete
    await asyncio.sleep(4)
    
    # Get the result (1 = heads, 0 = tails for coin emoji)
    coin_result = coin_message.dice.value
    result = "heads" if coin_result == 1 else "tails"
    won = choice == result
    
    # Calculate winnings
    winnings = bet_amount * 2 if won else 0
    
    # Record game result
    game_id = await record_game(
        user["user_id"], 
        "coinflip", 
        bet_amount, 
        "win" if won else "loss", 
        winnings
    )
    
    # Update balance if won
    if won:
        await update_user_balance(user["user_id"], winnings)
        await record_transaction(user["user_id"], winnings, "win", game_id)
    
    # Get updated user data
    user = await get_user(user["user_id"])
    
    # Create result message
    if won:
        result_message = (
            f"🎉 **WINNER!** 🎉\n\n"
            f"🪙 Coin landed on: **{result.title()}**\n"
            f"🎯 Your choice: **{choice.title()}**\n\n"
            f"💰 Bet: {format_money(bet_amount)}\n"
            f"🏆 Won: {format_money(winnings)}\n"
            f"💳 Balance: {format_money(user['balance'])}"
        )
    else:
        result_message = (
            f"😔 **BETTER LUCK NEXT TIME** 😔\n\n"
            f"🪙 Coin landed on: **{result.title()}**\n"
            f"🎯 Your choice: **{choice.title()}**\n\n"
            f"💰 Lost: {format_money(bet_amount)}\n"
            f"💳 Balance: {format_money(user['balance'])}"
        )
    
    # Create play again keyboard
    keyboard = [
        [
            InlineKeyboardButton("🔄 Same Bet", callback_data=f"coinflip_{choice}_{bet_amount}"),
            InlineKeyboardButton("💰 Double Bet", callback_data=f"coinflip_{choice}_{bet_amount*2}")
        ],
        [
            InlineKeyboardButton("🪙 Switch Side", callback_data=f"coinflip_{'tails' if choice == 'heads' else 'heads'}_{bet_amount}"),
            InlineKeyboardButton("🎮 New Game", callback_data="coinflip_solo")
        ],
        [
            InlineKeyboardButton("🔙 Back to Games", callback_data="menu_games")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(result_message, reply_markup=reply_markup, parse_mode='Markdown')

async def show_multiplayer_coinflip_menu(query):
    """Show multiplayer coinflip menu"""
    message = (
        f"👥 **MULTIPLAYER COINFLIP** 👥\n\n"
        f"Create or join a coinflip game!\n\n"
        f"🎮 **How it works:**\n"
        f"• Players choose heads or tails\n"
        f"• Everyone bets the same amount\n"
        f"• Winner takes the entire pot!\n"
        f"• Real coin animation for all"
    )
    
    keyboard = [
        [
            InlineKeyboardButton("🆕 Create Game ($5)", callback_data="coinflip_create_5"),
            InlineKeyboardButton("🆕 Create Game ($10)", callback_data="coinflip_create_10")
        ],
        [
            InlineKeyboardButton("🆕 Create Game ($25)", callback_data="coinflip_create_25"),
            InlineKeyboardButton("🆕 Create Game ($50)", callback_data="coinflip_create_50")
        ],
        [
            InlineKeyboardButton("🔍 Join Game", callback_data="coinflip_browse"),
            InlineKeyboardButton("📊 Active Games", callback_data="coinflip_active")
        ],
        [
            InlineKeyboardButton("🔙 Back", callback_data="coinflip_solo")
        ]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(message, reply_markup=reply_markup, parse_mode='Markdown')

async def show_coinflip_duel_menu(query):
    """Show coinflip duel menu"""
    message = (
        f"⚔️ **COINFLIP DUEL** ⚔️\n\n"
        f"Challenge another player to a coin duel!\n\n"
        f"🎯 **How it works:**\n"
        f"• Challenge a specific player\n"
        f"• Both choose heads or tails\n"
        f"• Winner takes all!\n"
        f"• Honor system - no backing out!"
    )
    
    keyboard = [
        [
            InlineKeyboardButton("⚔️ Challenge Player", callback_data="coinflip_challenge"),
            InlineKeyboardButton("🏆 Accept Challenge", callback_data="coinflip_accept")
        ],
        [
            InlineKeyboardButton("📋 Pending Duels", callback_data="coinflip_pending"),
            InlineKeyboardButton("🔙 Back", callback_data="coinflip_solo")
        ]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(message, reply_markup=reply_markup, parse_mode='Markdown')

async def show_coinflip_help(query):
    """Show coinflip help information"""
    message = (
        f"📊 **HOW TO PLAY COINFLIP** 📊\n\n"
        f"🪙 **Basic Rules:**\n"
        f"• Choose heads or tails\n"
        f"• Place your bet\n"
        f"• Watch the real coin animation\n"
        f"• Win 2x your bet if correct!\n\n"
        f"🎮 **Game Modes:**\n\n"
        f"🪙 **Solo Play:**\n"
        f"• Play against the house\n"
        f"• 50/50 odds\n"
        f"• Instant results\n\n"
        f"👥 **Multiplayer:**\n"
        f"• Multiple players, one coin flip\n"
        f"• Winner takes entire pot\n"
        f"• More players = bigger pot!\n\n"
        f"⚔️ **Duels:**\n"
        f"• 1v1 challenges\n"
        f"• Winner takes all\n"
        f"• Honor system\n\n"
        f"💡 **Tips:**\n"
        f"• Start with small bets\n"
        f"• Set a budget and stick to it\n"
        f"• Remember: it's 50/50 every time!"
    )
    
    keyboard = [
        [
            InlineKeyboardButton("🪙 Play Solo", callback_data="coinflip_solo"),
            InlineKeyboardButton("👥 Multiplayer", callback_data="coinflip_multiplayer")
        ],
        [
            InlineKeyboardButton("🔙 Back to Games", callback_data="menu_games")
        ]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(message, reply_markup=reply_markup, parse_mode='Markdown')

# Placeholder functions for multiplayer features (can be implemented later)
async def join_coinflip_game(query, game_id):
    """Join a multiplayer coinflip game"""
    await query.edit_message_text(
        "🚧 **Feature Coming Soon!** 🚧\n\n"
        "Multiplayer coinflip games are being developed.\n"
        "For now, enjoy solo play!",
        reply_markup=InlineKeyboardMarkup([[
            InlineKeyboardButton("🪙 Play Solo", callback_data="coinflip_solo")
        ]])
    )

async def start_coinflip_game(query, game_id):
    """Start a multiplayer coinflip game"""
    await query.edit_message_text(
        "🚧 **Feature Coming Soon!** 🚧\n\n"
        "Multiplayer coinflip games are being developed.\n"
        "For now, enjoy solo play!",
        reply_markup=InlineKeyboardMarkup([[
            InlineKeyboardButton("🪙 Play Solo", callback_data="coinflip_solo")
        ]])
    )