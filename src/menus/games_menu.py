import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo
from telegram.ext import ContextTypes
from src.database import get_user
from src.utils.formatting import format_money
from dotenv import load_dotenv

load_dotenv()
WEBAPP_URL = os.getenv("WEBAPP_URL", "https://work-1-yvxwuoonnfvrxtzn.prod-runtime.all-hands.dev")

async def games_menu_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Display the games menu"""
    await show_games_menu(update, context)

async def show_games_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show the unified games selection menu"""
    user_id = update.effective_user.id if update.effective_user else update.callback_query.from_user.id
    user = await get_user(user_id)
    
    message = (
        f"🎮 **GAMES** 🎮\n\n"
        f"💰 Balance: {format_money(user['balance'])}\n\n"
        f"Choose your game:"
    )
    
    # Unified games menu with all games in one place
    keyboard = [
        [
            InlineKeyboardButton("🎲 Dice", callback_data="game_dice"),
            InlineKeyboardButton("🎯 Darts", callback_data="game_darts")
        ],
        [
            InlineKeyboardButton("🎰 Slots", callback_data="game_slots"),
            InlineKeyboardButton("🎳 Bowling", callback_data="game_bowling")
        ],
        [
            InlineKeyboardButton("🏀 Basketball", callback_data="game_basketball"),
            InlineKeyboardButton("⚽ Football", callback_data="game_football")
        ],
        [
            InlineKeyboardButton("♠️ Blackjack", callback_data="game_blackjack"),
            InlineKeyboardButton("🎰 Roulette", callback_data="game_roulette")
        ],
        [
            InlineKeyboardButton("💣 Mines", callback_data="game_mines"),
            InlineKeyboardButton("🏗️ Tower", callback_data="game_tower")
        ],
        [
            InlineKeyboardButton("🎡 Wheel", callback_data="game_wheel"),
            InlineKeyboardButton("🚀 Crash", callback_data="game_crash")
        ],
        [
            InlineKeyboardButton("🟡 Plinko", callback_data="game_plinko"),
            InlineKeyboardButton("🪙 Coinflip", callback_data="game_coinflip")
        ],
        [
            InlineKeyboardButton("🎰 Lottery", callback_data="game_lottery"),
            InlineKeyboardButton("🃏 Poker", callback_data="game_poker")
        ],
        [
            InlineKeyboardButton("🔙 Back", callback_data="menu_main")
        ]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    if update.message:
        await update.message.reply_text(message, reply_markup=reply_markup, parse_mode='Markdown')
    else:
        await update.callback_query.edit_message_text(message, reply_markup=reply_markup, parse_mode='Markdown')

async def show_animated_games_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show Telegram animated games menu"""
    user_id = update.callback_query.from_user.id
    user = await get_user(user_id)
    
    message = (
        f"🎲 **ANIMATED GAMES** 🎲\n\n"
        f"💰 Balance: {format_money(user['balance'])}\n\n"
        f"Games with Telegram animations:\n"
        f"• Play in chat with real animations\n"
        f"• Multiplayer betting available\n"
        f"• Instant results based on animation"
    )
    
    keyboard = [
        [
            InlineKeyboardButton("🎲 Dice", callback_data="animated_dice"),
            InlineKeyboardButton("🎯 Darts", callback_data="animated_darts")
        ],
        [
            InlineKeyboardButton("🎰 Slots", callback_data="animated_slots"),
            InlineKeyboardButton("🎳 Bowling", callback_data="animated_bowling")
        ],
        [
            InlineKeyboardButton("🏀 Basketball", callback_data="animated_basketball"),
            InlineKeyboardButton("⚽ Football", callback_data="animated_football")
        ],
        [
            InlineKeyboardButton("🔙 Back to Games", callback_data="menu_games")
        ]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.callback_query.edit_message_text(message, reply_markup=reply_markup, parse_mode='Markdown')

async def show_webapp_games_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show web app games menu"""
    user_id = update.callback_query.from_user.id
    user = await get_user(user_id)
    
    message = (
        f"🎮 **WEB APP GAMES** 🎮\n\n"
        f"💰 Balance: {format_money(user['balance'])}\n\n"
        f"Interactive games with full UI:\n"
        f"• Advanced gameplay mechanics\n"
        f"• Visual interfaces\n"
        f"• Strategy-based games"
    )
    
    keyboard = [
        [
            InlineKeyboardButton("♠️ Blackjack", callback_data="webapp_blackjack"),
            InlineKeyboardButton("🎰 Roulette", callback_data="webapp_roulette")
        ],
        [
            InlineKeyboardButton("💣 Mines", callback_data="webapp_mines"),
            InlineKeyboardButton("🏗️ Tower", callback_data="webapp_tower")
        ],
        [
            InlineKeyboardButton("🚀 Crash", callback_data="webapp_crash"),
            InlineKeyboardButton("🟡 Plinko", callback_data="webapp_plinko")
        ],
        [
            InlineKeyboardButton("🃏 Poker", callback_data="webapp_poker"),
            InlineKeyboardButton("🎰 Lottery", callback_data="webapp_lottery")
        ],
        [
            InlineKeyboardButton("🔙 Back to Games", callback_data="menu_games")
        ]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.callback_query.edit_message_text(message, reply_markup=reply_markup, parse_mode='Markdown')

async def games_menu_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle games menu callback queries"""
    query = update.callback_query
    await query.answer()
    
    data = query.data.split("_")
    
    if len(data) < 2:
        return
    
    category = data[0]
    game_type = data[1]
    
    # Route to specific games
    if category == "game":
        if game_type == "dice":
            # Create a message object from the callback query for animated games
            update.message = update.callback_query.message

            from src.games.dice_animated import dice_command
            await dice_command(update, context)
        elif game_type == "darts":
            update.message = update.callback_query.message
            from src.games.darts_animated import darts_command
            await darts_command(update, context)
        elif game_type == "slots":
            update.message = update.callback_query.message
            from src.games.slots_animated import slots_command
            await slots_command(update, context)
        elif game_type == "bowling":
            update.message = update.callback_query.message
            from src.games.bowling_animated import bowling_command
            await bowling_command(update, context)
        elif game_type == "basketball":
            update.message = update.callback_query.message
            from src.games.basketball_animated import basketball_command
            await basketball_command(update, context)
        elif game_type == "football":
            update.message = update.callback_query.message
            from src.games.football_animated import football_command
            await football_command(update, context)
        elif game_type == "blackjack":
            await show_blackjack_webapp(update, context)
        elif game_type == "roulette":
            await show_roulette_webapp(update, context)
        elif game_type == "mines":
            await show_mines_webapp(update, context)
        elif game_type == "tower":
            await show_tower_webapp(update, context)
        elif game_type == "wheel":
            update.message = update.callback_query.message
            from src.games.wheel_animated import wheel_command
            await wheel_command(update, context)
        elif game_type == "crash":
            await show_crash_webapp(update, context)
        elif game_type == "plinko":
            await show_plinko_webapp(update, context)
        elif game_type == "coinflip":
            update.message = update.callback_query.message
            from src.games.coinflip_animated import coinflip_command
            await coinflip_command(update, context)
        elif game_type == "lottery":
            await show_lottery_webapp(update, context)
        elif game_type == "poker":
            await show_poker_webapp(update, context)
    
    # Legacy support for old callback patterns
    elif category == "games":
        if game_type == "animated":
            await show_animated_games_menu(update, context)
        elif game_type == "webapp":
            await show_webapp_games_menu(update, context)
        elif game_type == "tournaments":
            await show_tournaments_menu(update, context)
        elif game_type == "challenges":
            await show_challenges_menu(update, context)
    
    # Route to animated games (legacy support)
    elif category == "animated":
        if game_type == "dice":
            # Create a message object from the callback query for animated games
            update.message = update.callback_query.message

            update.message = update.callback_query.message
            from src.games.dice_animated import dice_command
            await dice_command(update, context)
        elif game_type == "darts":
            update.message = update.callback_query.message
            update.message = update.callback_query.message
            from src.games.darts_animated import darts_command
            await darts_command(update, context)
        elif game_type == "slots":
            update.message = update.callback_query.message
            update.message = update.callback_query.message
            from src.games.slots_animated import slots_command
            await slots_command(update, context)
        elif game_type == "bowling":
            update.message = update.callback_query.message
            update.message = update.callback_query.message
            from src.games.bowling_animated import bowling_command
            await bowling_command(update, context)
        elif game_type == "basketball":
            update.message = update.callback_query.message
            update.message = update.callback_query.message
            from src.games.basketball_animated import basketball_command
            await basketball_command(update, context)
        elif game_type == "football":
            update.message = update.callback_query.message
            update.message = update.callback_query.message
            from src.games.football_animated import football_command
            await football_command(update, context)
    
    # Route to web app games (legacy support)
    elif category == "webapp":
        if game_type == "blackjack":
            await show_blackjack_webapp(update, context)
        elif game_type == "roulette":
            await show_roulette_webapp(update, context)
        elif game_type == "mines":
            await show_mines_webapp(update, context)
        elif game_type == "tower":
            await show_tower_webapp(update, context)
        elif game_type == "wheel":
            update.message = update.callback_query.message
            from src.games.wheel_animated import wheel_command
            await wheel_command(update, context)
        elif game_type == "crash":
            await show_crash_webapp(update, context)
        elif game_type == "plinko":
            await show_plinko_webapp(update, context)
        elif game_type == "coinflip":
            update.message = update.callback_query.message
            from src.games.coinflip_animated import coinflip_command
            await coinflip_command(update, context)

async def show_tournaments_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show tournaments menu"""
    message = (
        f"🏆 **TOURNAMENTS** 🏆\n\n"
        f"Compete with other players!\n\n"
        f"🎰 Slots Tournament\n"
        f"🎯 Darts Competition\n"
        f"🎲 Dice Championship\n\n"
        f"Coming soon..."
    )
    
    keyboard = [[InlineKeyboardButton("🔙 Back to Games", callback_data="menu_games")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.callback_query.edit_message_text(message, reply_markup=reply_markup, parse_mode='Markdown')

async def show_challenges_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show challenges menu"""
    message = (
        f"⚔️ **CHALLENGES** ⚔️\n\n"
        f"Challenge other players to duels!\n\n"
        f"🎯 Darts Duel\n"
        f"🎲 Dice Battle\n"
        f"🏀 Basketball Shootout\n\n"
        f"Winner takes all!"
    )
    
    keyboard = [[InlineKeyboardButton("🔙 Back to Games", callback_data="menu_games")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.callback_query.edit_message_text(message, reply_markup=reply_markup, parse_mode='Markdown')

# Web App Game Functions
async def show_blackjack_webapp(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show Blackjack web app"""
    user_id = update.callback_query.from_user.id
    user = await get_user(user_id)
    
    message = (
        f"♠️ **BLACKJACK** ♠️\n\n"
        f"💰 Balance: {format_money(user['balance'])}\n\n"
        f"Get as close to 21 as possible!\n"
        f"Beat the dealer to win.\n\n"
        f"🎮 **Interactive Web App**\n"
        f"• Visual card dealing\n"
        f"• Real-time gameplay\n"
        f"• Strategy hints available"
    )
    
    web_app_url = f"{WEBAPP_URL}/games/blackjack?user_id={user_id}"
    
    keyboard = [
        [
            InlineKeyboardButton("🎮 Play Blackjack", web_app=WebAppInfo(url=web_app_url))
        ],
        [
            InlineKeyboardButton("🔙 Back", callback_data="games_webapp")
        ]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.callback_query.edit_message_text(message, reply_markup=reply_markup, parse_mode='Markdown')

async def show_roulette_webapp(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show Roulette web app"""
    user_id = update.callback_query.from_user.id
    user = await get_user(user_id)
    
    message = (
        f"🎰 **ROULETTE** 🎰\n\n"
        f"💰 Balance: {format_money(user['balance'])}\n\n"
        f"Place your bets on the roulette table!\n"
        f"Red/Black, Odd/Even, or specific numbers.\n\n"
        f"🎮 **Interactive Web App**\n"
        f"• Visual roulette wheel\n"
        f"• Multiple betting options\n"
        f"• Real-time spinning animation"
    )
    
    web_app_url = f"{WEBAPP_URL}/games/roulette?user_id={user_id}"
    
    keyboard = [
        [
            InlineKeyboardButton("🎮 Play Roulette", web_app=WebAppInfo(url=web_app_url))
        ],
        [
            InlineKeyboardButton("🔙 Back", callback_data="games_webapp")
        ]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.callback_query.edit_message_text(message, reply_markup=reply_markup, parse_mode='Markdown')

async def show_mines_webapp(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show Mines web app"""
    user_id = update.callback_query.from_user.id
    user = await get_user(user_id)
    
    message = (
        f"💣 **MINES** 💣\n\n"
        f"💰 Balance: {format_money(user['balance'])}\n\n"
        f"Find the gems while avoiding mines!\n"
        f"Cash out anytime to secure your winnings.\n\n"
        f"🎮 **Interactive Web App**\n"
        f"• Visual minefield grid\n"
        f"• Real-time multiplier updates\n"
        f"• Risk vs reward strategy"
    )
    
    web_app_url = f"{WEBAPP_URL}/games/mines?user_id={user_id}"
    
    keyboard = [
        [
            InlineKeyboardButton("🎮 Play Mines", web_app=WebAppInfo(url=web_app_url))
        ],
        [
            InlineKeyboardButton("🔙 Back", callback_data="games_webapp")
        ]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.callback_query.edit_message_text(message, reply_markup=reply_markup, parse_mode='Markdown')

async def show_tower_webapp(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show Tower web app"""
    user_id = update.callback_query.from_user.id
    user = await get_user(user_id)
    
    message = (
        f"🏗️ **TOWER** 🏗️\n\n"
        f"💰 Balance: {format_money(user['balance'])}\n\n"
        f"Climb the tower by choosing the right tiles!\n"
        f"Each level multiplies your winnings.\n\n"
        f"🎮 **Interactive Web App**\n"
        f"• Visual tower climbing\n"
        f"• Progressive multipliers\n"
        f"• Cash out anytime"
    )
    
    web_app_url = f"{WEBAPP_URL}/games/tower?user_id={user_id}"
    
    keyboard = [
        [
            InlineKeyboardButton("🎮 Play Tower", web_app=WebAppInfo(url=web_app_url))
        ],
        [
            InlineKeyboardButton("🔙 Back", callback_data="games_webapp")
        ]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.callback_query.edit_message_text(message, reply_markup=reply_markup, parse_mode='Markdown')



async def show_crash_webapp(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show Crash web app"""
    user_id = update.callback_query.from_user.id
    user = await get_user(user_id)
    
    message = (
        f"🚀 **CRASH** 🚀\n\n"
        f"💰 Balance: {format_money(user['balance'])}\n\n"
        f"Watch the multiplier rise and cash out!\n"
        f"Don't wait too long or it will crash!\n\n"
        f"🎮 **Interactive Web App**\n"
        f"• Real-time multiplier graph\n"
        f"• Auto cash-out options\n"
        f"• Live betting interface"
    )
    
    web_app_url = f"{WEBAPP_URL}/games/crash?user_id={user_id}"
    
    keyboard = [
        [
            InlineKeyboardButton("🎮 Play Crash", web_app=WebAppInfo(url=web_app_url))
        ],
        [
            InlineKeyboardButton("🔙 Back", callback_data="games_webapp")
        ]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.callback_query.edit_message_text(message, reply_markup=reply_markup, parse_mode='Markdown')

async def show_plinko_webapp(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show Plinko web app"""
    user_id = update.callback_query.from_user.id
    user = await get_user(user_id)
    
    message = (
        f"🟡 **PLINKO** 🟡\n\n"
        f"💰 Balance: {format_money(user['balance'])}\n\n"
        f"Drop the ball and watch it bounce!\n"
        f"Choose your risk level for different payouts.\n\n"
        f"🎮 **Interactive Web App**\n"
        f"• Visual ball physics\n"
        f"• Multiple risk levels\n"
        f"• Real-time bouncing animation"
    )
    
    web_app_url = f"{WEBAPP_URL}/games/plinko?user_id={user_id}"
    
    keyboard = [
        [
            InlineKeyboardButton("🎮 Play Plinko", web_app=WebAppInfo(url=web_app_url))
        ],
        [
            InlineKeyboardButton("🔙 Back", callback_data="games_webapp")
        ]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.callback_query.edit_message_text(message, reply_markup=reply_markup, parse_mode='Markdown')


async def show_lottery_webapp(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show Lottery web app"""
    user_id = update.callback_query.from_user.id
    user = await get_user(user_id)
    
    message = (
        f"🎰 **LOTTERY** 🎰\n\n"
        f"💰 Balance: {format_money(user['balance'])}\n\n"
        f"Buy lottery tickets and win big!\n"
        f"Multiple draws throughout the day.\n\n"
        f"🎮 **Interactive Web App**\n"
        f"• Visual ticket selection\n"
        f"• Live draw animations\n"
        f"• Jackpot tracking"
    )
    
    web_app_url = f"{WEBAPP_URL}/games/lottery?user_id={user_id}"
    
    keyboard = [
        [
            InlineKeyboardButton("🎮 Play Lottery", web_app=WebAppInfo(url=web_app_url))
        ],
        [
            InlineKeyboardButton("🔙 Back", callback_data="menu_games")
        ]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.callback_query.edit_message_text(message, reply_markup=reply_markup, parse_mode='Markdown')

async def show_poker_webapp(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show Poker web app"""
    user_id = update.callback_query.from_user.id
    user = await get_user(user_id)
    
    message = (
        f"🃏 **POKER** 🃏\n\n"
        f"💰 Balance: {format_money(user['balance'])}\n\n"
        f"Five Card Draw Poker!\n"
        f"Get the best hand to beat the house.\n\n"
        f"🎮 **Interactive Web App**\n"
        f"• Visual card dealing\n"
        f"• Interactive card selection\n"
        f"• Hand ranking display"
    )
    
    web_app_url = f"{WEBAPP_URL}/games/poker?user_id={user_id}"
    
    keyboard = [
        [
            InlineKeyboardButton("🎮 Play Poker", web_app=WebAppInfo(url=web_app_url))
        ],
        [
            InlineKeyboardButton("🔙 Back", callback_data="menu_games")
        ]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.callback_query.edit_message_text(message, reply_markup=reply_markup, parse_mode='Markdown')

async def show_coinflip_betting_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show coinflip betting interface"""
    user_id = update.callback_query.from_user.id
    user = await get_user(user_id)
    
    message = (
        f"🪙 **COINFLIP** 🪙\n\n"
        f"💰 Balance: {format_money(user['balance'])}\n\n"
        f"Choose your side and bet amount:\n"
        f"• 50/50 chance to win\n"
        f"• Win 2x your bet amount\n"
        f"• Simple and fast!"
    )
    
    # Betting amount buttons
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
    await update.callback_query.edit_message_text(message, reply_markup=reply_markup, parse_mode='Markdown')

async def show_dice_betting_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show dice betting interface"""
    user_id = update.callback_query.from_user.id
    user = await get_user(user_id)
    
    message = (
        f"🎲 **DICE GAME** 🎲\n\n"
        f"💰 Balance: {format_money(user['balance'])}\n\n"
        f"Guess the dice number (1-6):\n"
        f"• Correct guess: Win 6x your bet\n"
        f"• Real Telegram dice animation\n"
        f"• Instant results!"
    )
    
    # Betting amount buttons for each number
    keyboard = [
        [
            InlineKeyboardButton("🎲 1 - $1", callback_data="dice_1_1.0"),
            InlineKeyboardButton("🎲 2 - $1", callback_data="dice_2_1.0"),
            InlineKeyboardButton("🎲 3 - $1", callback_data="dice_3_1.0")
        ],
        [
            InlineKeyboardButton("🎲 4 - $1", callback_data="dice_4_1.0"),
            InlineKeyboardButton("🎲 5 - $1", callback_data="dice_5_1.0"),
            InlineKeyboardButton("🎲 6 - $1", callback_data="dice_6_1.0")
        ],
        [
            InlineKeyboardButton("🎲 1 - $5", callback_data="dice_1_5.0"),
            InlineKeyboardButton("🎲 2 - $5", callback_data="dice_2_5.0"),
            InlineKeyboardButton("🎲 3 - $5", callback_data="dice_3_5.0")
        ],
        [
            InlineKeyboardButton("🎲 4 - $5", callback_data="dice_4_5.0"),
            InlineKeyboardButton("🎲 5 - $5", callback_data="dice_5_5.0"),
            InlineKeyboardButton("🎲 6 - $5", callback_data="dice_6_5.0")
        ],
        [
            InlineKeyboardButton("🔙 Back to Games", callback_data="menu_games")
        ]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.callback_query.edit_message_text(message, reply_markup=reply_markup, parse_mode='Markdown')

# End of games_menu.py
async def show_lottery_betting_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show lottery betting menu"""
    user_id = update.callback_query.from_user.id
    user = await get_user(user_id)

    message = (
        f"🎰 **LOTTERY** 🎰\n\n"
        f"💰 Balance: {format_money(user['balance'])}\n\n"
        f"🎫 Ticket Price: $5.00\n"
        f"🏆 Current Pot: $500.00\n"
        f"⏰ Draw in: 2 hours\n\n"
        f"Buy tickets and win the jackpot!\n"
        f"More tickets = better chances!"
    )

    keyboard = [
        [
            InlineKeyboardButton("🎫 1 Ticket ($5)", callback_data="lottery_1_5.0"),
            InlineKeyboardButton("🎫 5 Tickets ($25)", callback_data="lottery_5_25.0")
        ],
        [
            InlineKeyboardButton("🎫 10 Tickets ($50)", callback_data="lottery_10_50.0"),
            InlineKeyboardButton("🎫 20 Tickets ($100)", callback_data="lottery_20_100.0")
        ],
        [
            InlineKeyboardButton("📊 Lottery Status", callback_data="lottery_status"),
            InlineKeyboardButton("🔙 Back", callback_data="menu_games")
        ]
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.callback_query.edit_message_text(message, reply_markup=reply_markup, parse_mode='Markdown')

async def show_poker_betting_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show poker betting menu"""
    user_id = update.callback_query.from_user.id
    user = await get_user(user_id)

    message = (
        f"🃏 **POKER** 🃏\n\n"
        f"💰 Balance: {format_money(user['balance'])}\n\n"
        f"🎯 Five Card Draw Poker\n"
        f"Get the best hand to win!\n\n"
        f"💡 **How to Play:**\n"
        f"• Get 5 cards\n"
        f"• Choose cards to keep\n"
        f"• Draw new cards\n"
        f"• Beat the house!"
    )

    keyboard = [
        [
            InlineKeyboardButton("💰 $5 Game", callback_data="poker_5.0"),
            InlineKeyboardButton("💰 $10 Game", callback_data="poker_10.0")
        ],
        [
            InlineKeyboardButton("💰 $25 Game", callback_data="poker_25.0"),
            InlineKeyboardButton("💰 $50 Game", callback_data="poker_50.0")
        ],
        [
            InlineKeyboardButton("📋 Rules", callback_data="poker_rules"),
            InlineKeyboardButton("🔙 Back", callback_data="menu_games")
        ]
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.callback_query.edit_message_text(message, reply_markup=reply_markup, parse_mode='Markdown')
