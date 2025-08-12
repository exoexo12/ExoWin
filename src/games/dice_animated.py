import random
import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from src.database import get_user, update_user_balance, record_transaction, record_game
from src.utils.formatting import format_money

# Active dice games for multiplayer
active_dice_games = {}

async def dice_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle the /dice command - Telegram animated dice game"""
    user_id = update.effective_user.id if update.effective_user else update.callback_query.from_user.id
    user = await get_user(user_id)
    
    keyboard = [
        [
            InlineKeyboardButton("🎲 Solo Dice", callback_data="dice_solo"),
            InlineKeyboardButton("👥 Multiplayer", callback_data="dice_multiplayer")
        ],
        [
            InlineKeyboardButton("⚔️ Dice Duel", callback_data="dice_duel"),
            InlineKeyboardButton("📊 How to Play", callback_data="dice_help")
        ],
        [
            InlineKeyboardButton("🏆 Leaderboard", callback_data="leaderboard_dice_all_time")
        ],
        [
            InlineKeyboardButton("🔙 Back to Games", callback_data="menu_games")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    message_text = (
        "🎲 **DICE GAME** 🎲\n\n"
        f"💰 Balance: {format_money(user['balance'])}\n\n"
        "Real Telegram dice animation!\n\n"
        "**Game Modes:**\n"
        "🎲 **Solo**: Guess the number (1-6)\n"
        "👥 **Multiplayer**: Everyone bets, winner takes pot\n"
        "⚔️ **Duel**: Challenge another player\n\n"
        "🏆 **Win 5x your bet** for correct guess!"
    )
    
    # Handle both direct commands and callback queries
    if update.message:
        await update.message.reply_text(
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

async def dice_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle dice game callbacks"""
    query = update.callback_query
    await query.answer()

    data = query.data.split('_')

    # Handle new betting format: dice_number_amount
    if len(data) == 3 and data[0] == "dice" and data[1].isdigit():
        number = int(data[1])
        bet_amount = float(data[2])
        await handle_dice_bet(query, number, bet_amount)
        return

    action = data[1]

    if action == "solo":
        # Show number selection for solo game
        keyboard = []
        for i in range(1, 7):
            keyboard.append([InlineKeyboardButton(f"🎯 Pick {i}", callback_data=f"dice_pick_{i}")])

        keyboard.append([InlineKeyboardButton("🔙 Back", callback_data="dice_back")])
        reply_markup = InlineKeyboardMarkup(keyboard)

        await query.edit_message_text(
            "🎲 **SOLO DICE GAME**\n\n"
            "Pick your lucky number (1-6):\n"
            "Win 5x your bet for correct guess!",
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )

    elif action == "pick":
        # Handle number selection for solo game
        number = int(data[2])

        keyboard = [
            [
                InlineKeyboardButton("💰 $1", callback_data=f"dice_solo_bet_{number}_1"),
                InlineKeyboardButton("💰 $5", callback_data=f"dice_solo_bet_{number}_5"),
                InlineKeyboardButton("💰 $10", callback_data=f"dice_solo_bet_{number}_10")
            ],
            [
                InlineKeyboardButton("💰 $25", callback_data=f"dice_solo_bet_{number}_25"),
                InlineKeyboardButton("💰 $50", callback_data=f"dice_solo_bet_{number}_50"),
                InlineKeyboardButton("💰 $100", callback_data=f"dice_solo_bet_{number}_100")
            ],
            [
                InlineKeyboardButton("🔙 Back", callback_data="dice_solo")
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await query.edit_message_text(
            f"🎲 **DICE GAME**\n\n"
            f"🎯 Your number: **{number}**\n"
            f"Choose your bet amount:",
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )

    elif action == "solo" and len(data) >= 5:
        # Handle solo game execution
        number = int(data[3])
        bet_amount = float(data[4])
        await execute_solo_dice_game(query, number, bet_amount)

    elif action == "multiplayer":
        # Show multiplayer options
        keyboard = [
            [
                InlineKeyboardButton("🎲 Create Game ($5)", callback_data="dice_mp_create_5"),
                InlineKeyboardButton("🎲 Create Game ($10)", callback_data="dice_mp_create_10")
            ],
            [
                InlineKeyboardButton("🎲 Create Game ($25)", callback_data="dice_mp_create_25"),
                InlineKeyboardButton("🎲 Create Game ($50)", callback_data="dice_mp_create_50")
            ],
            [
                InlineKeyboardButton("🔙 Back", callback_data="dice_back")
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await query.edit_message_text(
            "👥 **MULTIPLAYER DICE**\n\n"
            "Create a game for other players to join!\n"
            "Winner takes the entire pot.",
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )

    elif action == "duel":
        # Show duel options
        keyboard = [
            [
                InlineKeyboardButton("⚔️ Create Duel ($10)", callback_data="dice_duel_create_10"),
                InlineKeyboardButton("⚔️ Create Duel ($25)", callback_data="dice_duel_create_25")
            ],
            [
                InlineKeyboardButton("⚔️ Create Duel ($50)", callback_data="dice_duel_create_50"),
                InlineKeyboardButton("⚔️ Create Duel ($100)", callback_data="dice_duel_create_100")
            ],
            [
                InlineKeyboardButton("🔙 Back", callback_data="dice_back")
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await query.edit_message_text(
            "⚔️ **DICE DUEL**\n\n"
            "Challenge another player to a dice duel!\n"
            "Both roll dice, highest number wins!",
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
    
    elif action == "back":
        # Go back to main dice menu
        await dice_command(update, context)
    
    elif action == "help":
        # Show help text
        keyboard = [[InlineKeyboardButton("🔙 Back", callback_data="dice_back")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            "📊 **DICE GAME RULES**\n\n"
            "🎲 **Solo Mode:**\n"
            "• Pick a number (1-6)\n"
            "• Place your bet\n"
            "• If dice shows your number, win 5x your bet!\n\n"
            "👥 **Multiplayer Mode:**\n"
            "• Create a game with your bet\n"
            "• Other players join with same bet\n"
            "• Everyone rolls, highest number wins the pot!\n\n"
            "⚔️ **Duel Mode:**\n"
            "• Challenge another player\n"
            "• Both roll dice\n"
            "• Highest number wins both bets!",
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )

async def execute_solo_dice_game(query, choice: int, bet_amount: float):
    """Execute a solo dice game with Telegram animation"""
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
    await record_transaction(user["user_id"], -bet_amount, "dice bet", "Solo dice game")

    # Show rolling animation
    await query.edit_message_text(
        f"🎲 **ROLLING DICE...**\n\n"
        f"🎯 Your guess: **{choice}**\n"
        f"💰 Bet: {format_money(bet_amount)}\n\n"
        f"🎲 Rolling... 🎲",
        parse_mode='Markdown'
    )

    # Send animated dice using Telegram's built-in dice animation
    dice_message = await query.message.reply_dice(emoji="🎲")

    # Wait for animation to complete
    await asyncio.sleep(4)

    # Get the dice result from Telegram's animation
    result = dice_message.dice.value
    won = choice == result

    # Calculate winnings (5x for correct guess)
    winnings = bet_amount * 5 if won else 0

    # Record game result
    game_id = await record_game(
        user["user_id"],
        "dice",
        bet_amount,
        "win" if won else "loss",
        winnings
    )

    # Update user balance if won
    if won:
        await update_user_balance(user["user_id"], winnings)
        await record_transaction(user["user_id"], winnings, "dice win", f"Game ID: {game_id}")

    # Get updated user data
    user = await get_user(user["user_id"])

    # Create animated result message
    dice_emojis = ["", "⚀", "⚁", "⚂", "⚃", "⚄", "⚅"]

    if won:
        result_text = (
            f"🎉 **JACKPOT!** 🎉\n\n"
            f"{dice_emojis[result]} **RESULT: {result}**\n"
            f"🎯 Your guess: **{choice}** ✅\n\n"
            f"💰 Bet: {format_money(bet_amount)}\n"
            f"🏆 Won: **{format_money(winnings)}** (5x)\n"
            f"📈 Profit: **{format_money(winnings - bet_amount)}**\n"
            f"💳 Balance: {format_money(user['balance'])}"
        )
    else:
        result_text = (
            f"😢 **SO CLOSE!**\n\n"
            f"{dice_emojis[result]} **RESULT: {result}**\n"
            f"🎯 Your guess: **{choice}** ❌\n\n"
            f"💸 Lost: {format_money(bet_amount)}\n"
            f"💳 Balance: {format_money(user['balance'])}\n\n"
            f"🎲 Try again for the win!"
        )

    keyboard = [
        [
            InlineKeyboardButton("🎲 Roll Again", callback_data=f"dice_solo_bet_{choice}_{bet_amount}"),
            InlineKeyboardButton("💰 Double Bet", callback_data=f"dice_solo_bet_{choice}_{bet_amount*2}")
        ],
        [
            InlineKeyboardButton("🔢 New Number", callback_data="dice_solo"),
            InlineKeyboardButton("👥 Multiplayer", callback_data="dice_multiplayer")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.message.reply_text(result_text, reply_markup=reply_markup, parse_mode='Markdown')

async def handle_dice_bet(query, number: int, bet_amount: float):
    """Handle dice betting from the games menu"""
    user_id = query.from_user.id
    user = await get_user(user_id)

    if user["balance"] < bet_amount:
        await query.edit_message_text(
            f"❌ Insufficient funds!\n\n"
            f"💰 Your balance: {format_money(user['balance'])}\n"
            f"💸 Required: {format_money(bet_amount)}\n\n"
            f"🔙 Go back to deposit more funds.",
            parse_mode='Markdown'
        )
        return

    # Deduct bet amount
    await update_user_balance(user_id, -bet_amount)
    await record_transaction(user_id, -bet_amount, "bet")

    # Send dice animation
    dice_message = await query.message.reply_dice(emoji="🎲")

    # Wait for animation to complete
    await asyncio.sleep(4)

    # Get dice result
    dice_result = dice_message.dice.value
    won = dice_result == number

    # Calculate winnings
    winnings = bet_amount * 6 if won else 0

    if won:
        await update_user_balance(user_id, winnings)
        await record_transaction(user_id, winnings, "win")

    # Record game
    await record_game(
        user_id=user_id,
        game_type="dice",
        bet_amount=bet_amount,
        result="win" if won else "loss",
        winnings=winnings,
        game_data={"guess": number, "result": dice_result}
    )

    # Update user balance
    updated_user = await get_user(user_id)

    # Create result message
    if won:
        result_text = (
            f"🎉 **WINNER!** 🎉\n\n"
            f"🎲 Dice rolled: **{dice_result}**\n"
            f"🎯 Your guess: **{number}**\n\n"
            f"💰 Bet: {format_money(bet_amount)}\n"
            f"🏆 Won: {format_money(winnings)}\n"
            f"💳 Balance: {format_money(updated_user['balance'])}"
        )
    else:
        result_text = (
            f"😢 **Better luck next time!**\n\n"
            f"🎲 Dice rolled: **{dice_result}**\n"
            f"🎯 Your guess: **{number}**\n\n"
            f"💸 Lost: {format_money(bet_amount)}\n"
            f"💳 Balance: {format_money(updated_user['balance'])}"
        )

    # Create play again keyboard
    keyboard = [
        [
            InlineKeyboardButton("🎲 Same Bet", callback_data=f"dice_{number}_{bet_amount}"),
            InlineKeyboardButton("💰 Double Bet", callback_data=f"dice_{number}_{bet_amount*2}")
        ],
        [
            InlineKeyboardButton("🎮 New Game", callback_data="menu_games"),
            InlineKeyboardButton("🏠 Main Menu", callback_data="menu_main")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.message.reply_text(result_text, reply_markup=reply_markup, parse_mode='Markdown')

# Export the callback handler
dice_callback_handler = dice_callback
