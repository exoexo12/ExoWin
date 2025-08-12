import os
import logging
from dotenv import load_dotenv
from telegram import Update, BotCommand
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    PreCheckoutQueryHandler,
    ContextTypes,
    filters
)

# Import utilities
from src.utils.logger import bot_logger
from src.utils.config_validator import config_validator
from src.utils.error_handler import handle_errors, handle_callback_errors
from src.utils.rate_limiter import rate_limiter
from src.utils.validators import validator

# Import modules
from src.games.coinflip_animated import coinflip_callback

# Telegram Animated Games (use native Telegram animations)
from src.games.dice_animated import dice_callback
from src.games.slots_animated import slots_callback
from src.games.darts_animated import darts_callback
from src.games.basketball_animated import basketball_callback
from src.games.football_animated import football_callback
from src.games.bowling_animated import bowling_callback

# Import message handlers for regular games
# from src.games.darts import darts_message_handler
# from src.games.bowling import bowling_message_handler

# Web App Games (complex interactive games) - no Telegram callbacks needed
from src.games.wheel_animated import wheel_callback
from src.wallet import (
    wallet_command,
    wallet_callback,
    wallet_message_handler,
    process_pre_checkout,
    process_successful_payment,
    crypto_deposit_command,
    crypto_withdraw_command,
    crypto_callback,
    crypto_message_handler
)
from src.admin import admin_command, admin_callback, admin_message_handler, broadcast_command
from src.menus import (
    main_menu_command, main_menu_callback,
    games_menu_command, games_menu_callback,
    deposit_menu_command, deposit_menu_callback,
    profile_menu_command, profile_menu_callback,
    settings_menu_command, settings_menu_callback,
    bonuses_menu_command, bonuses_menu_callback,
    leaderboard_menu_command, leaderboard_menu_callback
)

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Get bot token from environment variable
BOT_TOKEN = os.getenv("BOT_TOKEN")

@handle_errors
async def start(update: Update, context):
    """Send a welcome message when the command /start is issued."""
    user_id = update.effective_user.id
    
    # Rate limiting
    if not rate_limiter.check_action_limit(user_id, max_actions=5, window=60):
        remaining = rate_limiter.get_remaining_time(user_id, "action")
        await update.message.reply_text(
            f"⏰ Please wait {remaining} seconds before using commands again.",
            parse_mode='Markdown'
        )
        return
    
    from src.database import get_user
    
    user_first_name = update.effective_user.first_name
    bot_logger.info(f"User {user_id} ({user_first_name}) started the bot")
    
    # Prepare user data for database
    user_data = {
        "username": update.effective_user.username,
        "first_name": update.effective_user.first_name,
        "last_name": update.effective_user.last_name
    }
    
    # Initialize user in database
    user = await get_user(user_id, user_data)
    
    welcome_message = (
        f"🎰 **Welcome to ExoWin 👑, {user_first_name}!** 🎰\n\n"
        f"💰 You start with **$1.00** in your wallet!\n"
        f"🎮 Play games to win more money\n"
        f"💸 Withdraw when you reach **$50**\n\n"
        f"🚀 **Features:**\n"
        f"• 🎮 Interactive mini-games\n"
        f"• 💰 Cryptocurrency deposits\n"
        f"• 🔒 No KYC required\n"
        f"• 🎁 Daily bonuses\n"
        f"• 👥 Referral rewards\n\n"
        f"Use the menu below to get started! 🎯"
    )
    
    # Show main menu
    await update.message.reply_text(welcome_message, parse_mode='Markdown')
    await main_menu_command(update, context)

@handle_errors
async def help_command(update: Update, context):
    """Send a help message when the command /help is issued."""
    user_id = update.effective_user.id
    bot_logger.info(f"User {user_id} requested help")
    
    help_message = (
        "🎮 ExoWin 👑 Help 🎮\n\n"
        "🎲 Game Commands:\n"
        "• /coinflip [heads/tails] [amount] - Flip a coin\n"
        "• /dice [number 1-6] [amount] - Roll a dice\n"
        "• /slots [amount] - Play slot machine\n"
        "• /roulette - Play roulette\n"
        "• /blackjack [amount] - Play blackjack\n"
        "• /crash [amount] - Play crash game\n"
        "• /lottery - Join the lottery\n"
        "• /poker [amount] - Play video poker\n"
        "• /plinko [risk] [amount] - Play plinko\n"
        "• /darts [amount] - Play darts\n"
        "• /bowling [amount] - Play bowling\n\n"
        "💰 Wallet Commands:\n"
        "• /wallet - Manage your wallet\n"
        "• /balance or /bal - Check your balance\n"
        "• /deposit - Deposit cryptocurrency\n"
        "• /withdraw - Withdraw cryptocurrency\n\n"
        "ℹ️ Other Commands:\n"
        "• /start - Start the bot\n"
        "• /help - Show this help message\n"
        "• /stats - View your gambling statistics\n\n"
        "💡 Tips:\n"
        "• You start with $1 in your wallet\n"
        "• You need at least $50 to withdraw\n"
        "• Use the buttons to navigate through games\n"
        "• Deposit cryptocurrency to play with higher stakes\n"
        "• All deposits go to the main wallet after confirmation\n"
        "• Withdrawals are processed from the main wallet\n\n"
        "If you have any questions or issues, please contact support."
    )
    
    await update.message.reply_text(help_message)

@handle_errors
async def balance_command(update: Update, context):
    """Show user balance when the command /balance is issued."""
    from src.database import get_user
    from src.utils.formatting import format_money
    
    user_id = update.effective_user.id
    bot_logger.info(f"User {user_id} checked balance")
    user = await get_user(user_id)
    
    balance_message = (
        "💰 Your Balance 💰\n\n"
        f"Current balance: {format_money(user['balance'])}\n\n"
        "Use /wallet to manage your funds."
    )
    
    await update.message.reply_text(balance_message)

@handle_errors
async def stats_command(update: Update, context):
    """Show user statistics when the command /stats is issued."""
    from src.database import get_user
    from src.utils.formatting import format_money, format_user_stats
    
    user_id = update.effective_user.id
    bot_logger.info(f"User {user_id} requested stats")
    user = await get_user(user_id)
    
    stats_message = (
        "📊 Your Gambling Statistics 📊\n\n"
        f"{format_user_stats(user)}\n\n"
        "Keep playing to improve your stats!"
    )
    
    await update.message.reply_text(stats_message)

async def handle_message(update: Update, context):
    """Handle regular messages."""
    from src.menus.deposit_menu import deposit_message_handler
    from src.wallet.withdrawal_system import withdrawal_system
    
    # Check if this is a response to an admin or wallet action
    if await admin_message_handler(update, context):
        return
    
    if await wallet_message_handler(update, context):
        return
    
    if await crypto_message_handler(update, context):
        return
    
    if await deposit_message_handler(update, context):
        return
    
    # Check withdrawal system messages
    if 'withdrawal_step' in context.user_data:
        if context.user_data['withdrawal_step'] == 'amount':
            if await withdrawal_system.process_withdrawal_amount(update, context):
                return
        elif context.user_data['withdrawal_step'] == 'address':
            if await withdrawal_system.process_withdrawal_address(update, context):
                return
    
    # Webapp games are handled through the web interface, not Telegram messages
    
    # Default response for other messages
    await update.message.reply_text(
        "I don't understand that command. Use /menu to see the main menu or /help for commands."
    )

async def withdrawal_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle withdrawal callback queries"""
    from src.wallet.withdrawal_system import withdrawal_system
    
    query = update.callback_query
    await query.answer()
    
    data = query.data.split("_")
    
    if len(data) < 2:
        return
    
    action = data[1]
    
    if action == "cancel":
        # Clear withdrawal context
        for key in list(context.user_data.keys()):
            if key.startswith('withdrawal_'):
                del context.user_data[key]
        
        await withdrawal_system.show_withdrawal_menu(update, context)
    
    elif action == "history":
        # Show withdrawal history (placeholder)
        message = (
            "📊 **Withdrawal History** 📊\n\n"
            "Your recent withdrawals will appear here.\n"
            "(Feature coming soon)"
        )
        
        keyboard = [
            [InlineKeyboardButton("🔙 Back", callback_data="withdraw_cancel")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(message, reply_markup=reply_markup, parse_mode='Markdown')
    
    elif action == "confirm" and len(data) > 2:
        withdrawal_id = data[2]
        await withdrawal_system.confirm_withdrawal(update, context, withdrawal_id)
    
    elif len(data) > 2:
        # Handle specific crypto selection
        crypto_symbol = data[1].upper()
        await withdrawal_system.handle_crypto_selection(update, context, crypto_symbol)
    
    else:
        # Show withdrawal menu
        await withdrawal_system.show_withdrawal_menu(update, context)

async def post_init(application):
    """Set up bot commands and database after initialization."""
    # Setup database first
    setup_success = await setup_bot()
    if not setup_success:
        logger.error("Failed to setup bot - exiting")
        return
    
    commands = [
        BotCommand("start", "Start the bot"),
        BotCommand("bal", "Check your balance"),
        BotCommand("admin", "Access admin panel (admin only)")
    ]
    
    await application.bot.set_my_commands(commands)
    logger.info("Bot commands have been set up")

async def setup_bot():
    """Setup bot database and configurations"""
    from src.database import setup_database
    
    # Setup database indexes
    bot_logger.info("Setting up database...")
    db_setup_success = await setup_database()
    if not db_setup_success:
        bot_logger.error("Failed to setup database!")
        return False
    
    bot_logger.info("Database setup completed successfully")
    return True

def main():
    """Start the bot."""
    # Validate configuration
    is_valid, issues = config_validator.validate_config()
    if not is_valid:
        bot_logger.error("Configuration validation failed!")
        for issue in issues:
            bot_logger.error(f"- {issue}")
        return
    
    bot_logger.info("🚀 Starting ExoWin 👑...")
    bot_logger.info(config_validator.get_config_status())
    
    # Create the Application
    application = Application.builder().token(BOT_TOKEN).post_init(post_init).build()
    
    # Basic commands
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("balance", balance_command))
    application.add_handler(CommandHandler("bal", balance_command))  # Alias for balance
    
    # Menu commands
    
    # Game commands
    # Telegram Animated Games
    
    # Wallet commands
    application.add_handler(CommandHandler("wallet", wallet_command))
    application.add_handler(CommandHandler("deposit", crypto_deposit_command))
    application.add_handler(CommandHandler("withdraw", crypto_withdraw_command))
    
    # Admin commands
    application.add_handler(CommandHandler("admin", admin_command))
    application.add_handler(CommandHandler("broadcast", broadcast_command))
    
    # Menu callback handlers
    application.add_handler(CallbackQueryHandler(main_menu_callback, pattern="^menu_"))
    application.add_handler(CallbackQueryHandler(games_menu_callback, pattern="^game_"))
    application.add_handler(CallbackQueryHandler(deposit_menu_callback, pattern="^deposit_"))
    application.add_handler(CallbackQueryHandler(deposit_menu_callback, pattern="^crypto_"))
    application.add_handler(CallbackQueryHandler(profile_menu_callback, pattern="^profile_"))
    application.add_handler(CallbackQueryHandler(settings_menu_callback, pattern="^settings_"))
    application.add_handler(CallbackQueryHandler(bonuses_menu_callback, pattern="^bonus_"))
    application.add_handler(CallbackQueryHandler(leaderboard_menu_callback, pattern="^leaderboard_"))
    
    # Game callback query handlers
    # Telegram Animated Games
    application.add_handler(CallbackQueryHandler(dice_callback, pattern="^dice_"))
    application.add_handler(CallbackQueryHandler(slots_callback, pattern="^slots_"))
    application.add_handler(CallbackQueryHandler(darts_callback, pattern="^darts_"))
    application.add_handler(CallbackQueryHandler(basketball_callback, pattern="^basketball_"))
    application.add_handler(CallbackQueryHandler(football_callback, pattern="^football_"))
    application.add_handler(CallbackQueryHandler(bowling_callback, pattern="^bowling_"))
    
    # Animated Games (Telegram native)
    application.add_handler(CallbackQueryHandler(coinflip_callback, pattern="^coinflip_"))
    
    # Web App Games - handled through webapp, no Telegram callbacks needed
    application.add_handler(CallbackQueryHandler(wheel_callback, pattern="^wheel_"))
    application.add_handler(CallbackQueryHandler(wallet_callback, pattern="^wallet_"))
    application.add_handler(CallbackQueryHandler(crypto_callback, pattern="^crypto_"))
    application.add_handler(CallbackQueryHandler(withdrawal_callback, pattern="^withdraw_"))
    application.add_handler(CallbackQueryHandler(admin_callback, pattern="^admin_"))
    
    # Payment handlers
    application.add_handler(PreCheckoutQueryHandler(process_pre_checkout))
    application.add_handler(MessageHandler(filters.SUCCESSFUL_PAYMENT, process_successful_payment))
    
    # Message handler
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    # Start the Bot
    application.run_polling()
    
    logger.info("Bot started")

if __name__ == '__main__':
    main()