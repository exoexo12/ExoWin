"""
Leaderboard menu for ExoWin bot
"""
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from src.database import get_user
from src.database.leaderboard import get_game_leaderboard, get_overall_leaderboard, get_user_ranking
from src.utils.formatting import format_money

async def leaderboard_menu_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Display the leaderboard menu"""
    await show_leaderboard_menu(update, context)

async def show_leaderboard_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show the leaderboard selection menu"""
    user_id = update.effective_user.id if update.effective_user else update.callback_query.from_user.id
    user = await get_user(user_id)
    
    message = (
        f"🏆 **LEADERBOARDS** 🏆\n\n"
        f"Check out the top players in different games!\n\n"
        f"💰 Your Balance: {format_money(user['balance'])}\n\n"
        f"Select a leaderboard to view:"
    )
    
    keyboard = [
        [
            InlineKeyboardButton("🌟 Overall", callback_data="leaderboard_overall_all_time"),
            InlineKeyboardButton("🎲 Dice", callback_data="leaderboard_dice_all_time")
        ],
        [
            InlineKeyboardButton("🎯 Darts", callback_data="leaderboard_darts_all_time"),
            InlineKeyboardButton("🎰 Slots", callback_data="leaderboard_slots_all_time")
        ],
        [
            InlineKeyboardButton("🎳 Bowling", callback_data="leaderboard_bowling_all_time"),
            InlineKeyboardButton("🏀 Basketball", callback_data="leaderboard_basketball_all_time")
        ],
        [
            InlineKeyboardButton("⚽ Football", callback_data="leaderboard_football_all_time"),
            InlineKeyboardButton("🎡 Wheel", callback_data="leaderboard_wheel_all_time")
        ],
        [
            InlineKeyboardButton("🪙 Coinflip", callback_data="leaderboard_coinflip_all_time"),
            InlineKeyboardButton("📊 Your Stats", callback_data="leaderboard_mystats")
        ],
        [
            InlineKeyboardButton("🔙 Back", callback_data="menu_games")
        ]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    if update.message:
        await update.message.reply_text(message, reply_markup=reply_markup, parse_mode='Markdown')
    else:
        await update.callback_query.edit_message_text(message, reply_markup=reply_markup, parse_mode='Markdown')

async def leaderboard_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle leaderboard menu callbacks"""
    query = update.callback_query
    await query.answer()
    
    data = query.data.split('_')
    
    if len(data) < 2:
        return
    
    action = data[1]
    
    if action == "overall" and len(data) >= 3:
        period = data[2]
        await show_overall_leaderboard(update, context, period)
    elif action in ["dice", "darts", "slots", "bowling", "basketball", "football", "wheel", "coinflip"] and len(data) >= 3:
        game_type = action
        period = data[2]
        await show_game_leaderboard(update, context, game_type, period)
    elif action == "mystats":
        await show_user_stats(update, context)
    elif action == "period":
        game_type = data[2]
        await show_period_selection(update, context, game_type)

async def show_overall_leaderboard(update: Update, context: ContextTypes.DEFAULT_TYPE, period: str = "all_time"):
    """Show overall leaderboard"""
    query = update.callback_query
    
    # Get leaderboard data
    leaderboard = await get_overall_leaderboard(limit=10, period=period)
    
    # Format period for display
    period_display = {
        "all_time": "All Time",
        "daily": "Today",
        "weekly": "This Week",
        "monthly": "This Month"
    }.get(period, "All Time")
    
    # Create message
    message = f"🏆 **OVERALL LEADERBOARD - {period_display}** 🏆\n\n"
    
    if not leaderboard:
        message += "No data available for this period."
    else:
        for i, entry in enumerate(leaderboard):
            medal = "🥇" if i == 0 else "🥈" if i == 1 else "🥉" if i == 2 else f"{i+1}."
            message += (
                f"{medal} **{entry['display_name']}**\n"
                f"   💰 Profit: {format_money(entry['profit'])}\n"
                f"   🎮 Games: {entry['total_bets']} | ✅ Win Rate: {entry['win_rate']}%\n\n"
            )
    
    # Create keyboard for period selection
    keyboard = [
        [
            InlineKeyboardButton("📅 All Time", callback_data="leaderboard_overall_all_time"),
            InlineKeyboardButton("📆 Today", callback_data="leaderboard_overall_daily")
        ],
        [
            InlineKeyboardButton("📆 This Week", callback_data="leaderboard_overall_weekly"),
            InlineKeyboardButton("📆 This Month", callback_data="leaderboard_overall_monthly")
        ],
        [
            InlineKeyboardButton("🔙 Back", callback_data="menu_leaderboard")
        ]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(message, reply_markup=reply_markup, parse_mode='Markdown')

async def show_game_leaderboard(update: Update, context: ContextTypes.DEFAULT_TYPE, game_type: str, period: str = "all_time"):
    """Show leaderboard for a specific game"""
    query = update.callback_query
    
    # Get leaderboard data
    leaderboard = await get_game_leaderboard(game_type, limit=10, period=period)
    
    # Format period for display
    period_display = {
        "all_time": "All Time",
        "daily": "Today",
        "weekly": "This Week",
        "monthly": "This Month"
    }.get(period, "All Time")
    
    # Format game type for display
    game_display = {
        "dice": "🎲 DICE",
        "darts": "🎯 DARTS",
        "slots": "🎰 SLOTS",
        "bowling": "🎳 BOWLING",
        "basketball": "🏀 BASKETBALL",
        "football": "⚽ FOOTBALL",
        "wheel": "🎡 WHEEL",
        "coinflip": "🪙 COINFLIP"
    }.get(game_type, game_type.upper())
    
    # Create message
    message = f"🏆 **{game_display} LEADERBOARD - {period_display}** 🏆\n\n"
    
    if not leaderboard:
        message += "No data available for this period."
    else:
        for i, entry in enumerate(leaderboard):
            medal = "🥇" if i == 0 else "🥈" if i == 1 else "🥉" if i == 2 else f"{i+1}."
            message += (
                f"{medal} **{entry['display_name']}**\n"
                f"   💰 Profit: {format_money(entry['profit'])}\n"
                f"   🎮 Games: {entry['total_bets']} | ✅ Win Rate: {entry['win_rate']}%\n\n"
            )
    
    # Create keyboard for period selection
    keyboard = [
        [
            InlineKeyboardButton("📅 All Time", callback_data=f"leaderboard_{game_type}_all_time"),
            InlineKeyboardButton("📆 Today", callback_data=f"leaderboard_{game_type}_daily")
        ],
        [
            InlineKeyboardButton("📆 This Week", callback_data=f"leaderboard_{game_type}_weekly"),
            InlineKeyboardButton("📆 This Month", callback_data=f"leaderboard_{game_type}_monthly")
        ],
        [
            InlineKeyboardButton("🔙 Back", callback_data="menu_leaderboard")
        ]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(message, reply_markup=reply_markup, parse_mode='Markdown')

async def show_user_stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show user's personal stats and rankings"""
    query = update.callback_query
    user_id = query.from_user.id
    
    # Get user's overall ranking
    overall_ranking = await get_user_ranking(user_id)
    
    # Get user's game-specific rankings
    game_types = ["dice", "darts", "slots", "bowling", "basketball", "football", "wheel", "coinflip"]
    game_rankings = {}
    
    for game_type in game_types:
        game_rankings[game_type] = await get_user_ranking(user_id, game_type)
    
    # Create message
    message = (
        f"📊 **YOUR STATS & RANKINGS** 📊\n\n"
        f"👤 **{overall_ranking['display_name']}**\n\n"
        f"🌟 **Overall Ranking:** {overall_ranking['rank'] or 'N/A'}\n"
        f"💰 Total Profit: {format_money(overall_ranking['profit'])}\n"
        f"🎮 Games Played: {overall_ranking['total_bets']}\n"
        f"✅ Win Rate: {overall_ranking['win_rate']}%\n\n"
        f"**Game Rankings:**\n"
    )
    
    for game_type, ranking in game_rankings.items():
        if ranking['total_bets'] > 0:
            game_emoji = {
                "dice": "🎲",
                "darts": "🎯",
                "slots": "🎰",
                "bowling": "🎳",
                "basketball": "🏀",
                "football": "⚽",
                "wheel": "🎡",
                "coinflip": "🪙"
            }.get(game_type, "🎮")
            
            message += (
                f"{game_emoji} **{game_type.capitalize()}:** Rank #{ranking['rank'] or 'N/A'}\n"
                f"   Games: {ranking['total_bets']} | Profit: {format_money(ranking['profit'])}\n"
            )
    
    keyboard = [
        [
            InlineKeyboardButton("🔙 Back", callback_data="menu_leaderboard")
        ]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(message, reply_markup=reply_markup, parse_mode='Markdown')

async def show_period_selection(update: Update, context: ContextTypes.DEFAULT_TYPE, game_type: str):
    """Show period selection for leaderboards"""
    query = update.callback_query
    
    message = (
        f"📅 **SELECT TIME PERIOD** 📅\n\n"
        f"Choose a time period for the leaderboard:"
    )
    
    keyboard = [
        [
            InlineKeyboardButton("📅 All Time", callback_data=f"leaderboard_{game_type}_all_time"),
            InlineKeyboardButton("📆 Today", callback_data=f"leaderboard_{game_type}_daily")
        ],
        [
            InlineKeyboardButton("📆 This Week", callback_data=f"leaderboard_{game_type}_weekly"),
            InlineKeyboardButton("📆 This Month", callback_data=f"leaderboard_{game_type}_monthly")
        ],
        [
            InlineKeyboardButton("🔙 Back", callback_data="menu_leaderboard")
        ]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(message, reply_markup=reply_markup, parse_mode='Markdown')