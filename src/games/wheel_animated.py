import random
import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from src.database import get_user, update_user_balance, record_transaction, record_game
from src.utils.formatting import format_money

# Active wheel games for multiplayer
active_wheel_games = {}

# Wheel segments with different multipliers
WHEEL_SEGMENTS = {
    1: {"color": "🔴", "multiplier": 2, "probability": 0.4},
    2: {"color": "🟡", "multiplier": 3, "probability": 0.25},
    3: {"color": "🟢", "multiplier": 5, "probability": 0.15},
    4: {"color": "🔵", "multiplier": 10, "probability": 0.1},
    5: {"color": "🟣", "multiplier": 20, "probability": 0.07},
    6: {"color": "⚫", "multiplier": 50, "probability": 0.03}
}

async def wheel_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle the /wheel command"""
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
            InlineKeyboardButton("🎡 Solo Wheel", callback_data="wheel_solo"),
            InlineKeyboardButton("👥 Multiplayer", callback_data="wheel_multiplayer")
        ],
        [
            InlineKeyboardButton("📊 Wheel Info", callback_data="wheel_info")
        ],
        [
            InlineKeyboardButton("🏆 Leaderboard", callback_data="leaderboard_wheel_all_time")
        ],
        [
            InlineKeyboardButton("🔙 Back to Games", callback_data="menu_games")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    message_text = (
        "🎡 **WHEEL OF FORTUNE** 🎡\n\n"
        f"💰 Balance: {format_money(user['balance'])}\n\n"
        "Spin the wheel and win big!\n\n"
        "**Segments:**\n"
        "🔴 Red: 2x (40% chance)\n"
        "🟡 Yellow: 3x (25% chance)\n"
        "🟢 Green: 5x (15% chance)\n"
        "🔵 Blue: 10x (10% chance)\n"
        "🟣 Purple: 20x (7% chance)\n"
        "⚫ Black: 50x (3% chance)"
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

async def wheel_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle wheel game callbacks"""
    query = update.callback_query
    await query.answer()
    
    data = query.data.split('_')
    action = data[1]
    
    if action == "solo":
        # Show color selection for solo game
        keyboard = []
        for segment_id, segment in WHEEL_SEGMENTS.items():
            keyboard.append([
                InlineKeyboardButton(
                    f"{segment['color']} {segment['multiplier']}x", 
                    callback_data=f"wheel_pick_{segment_id}"
                )
            ])
        
        keyboard.append([InlineKeyboardButton("🔙 Back", callback_data="wheel_back")])
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            "🎡 **SOLO WHEEL GAME**\n\n"
            "Pick your color to bet on:\n"
            "Higher multipliers = lower chance!",
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
    
    elif action == "multiplayer":
        # Show bet amount selection for multiplayer
        keyboard = [
            [
                InlineKeyboardButton("💰 $5", callback_data="wheel_mp_bet_5"),
                InlineKeyboardButton("💰 $10", callback_data="wheel_mp_bet_10"),
                InlineKeyboardButton("💰 $25", callback_data="wheel_mp_bet_25")
            ],
            [
                InlineKeyboardButton("💰 $50", callback_data="wheel_mp_bet_50"),
                InlineKeyboardButton("💰 $100", callback_data="wheel_mp_bet_100"),
                InlineKeyboardButton("💰 $250", callback_data="wheel_mp_bet_250")
            ],
            [
                InlineKeyboardButton("🔙 Back", callback_data="wheel_back")
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            "🎡 **MULTIPLAYER WHEEL**\n\n"
            "Choose bet amount for the game:\n"
            "Winner takes the entire pot!",
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
    
    elif action == "pick":
        # Handle color selection for solo game
        segment_id = int(data[2])
        segment = WHEEL_SEGMENTS[segment_id]
        
        keyboard = [
            [
                InlineKeyboardButton("💰 $1", callback_data=f"wheel_solo_bet_{segment_id}_1"),
                InlineKeyboardButton("💰 $5", callback_data=f"wheel_solo_bet_{segment_id}_5"),
                InlineKeyboardButton("💰 $10", callback_data=f"wheel_solo_bet_{segment_id}_10")
            ],
            [
                InlineKeyboardButton("💰 $25", callback_data=f"wheel_solo_bet_{segment_id}_25"),
                InlineKeyboardButton("💰 $50", callback_data=f"wheel_solo_bet_{segment_id}_50"),
                InlineKeyboardButton("💰 $100", callback_data=f"wheel_solo_bet_{segment_id}_100")
            ],
            [
                InlineKeyboardButton("🔙 Back", callback_data="wheel_solo")
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            f"🎡 **WHEEL GAME**\n\n"
            f"🎯 Your color: {segment['color']} **{segment['multiplier']}x**\n"
            f"🎲 Win chance: **{segment['probability']*100:.1f}%**\n\n"
            f"Choose your bet amount:",
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
    
    elif action == "solo" and len(data) >= 5:
        # Handle solo game execution
        segment_id = int(data[3])
        bet_amount = float(data[4])
        await execute_solo_wheel_game(query, segment_id, bet_amount)
    
    elif action == "mp" and data[2] == "bet":
        # Handle multiplayer bet amount selection
        bet_amount = float(data[3])
        await start_multiplayer_wheel(query, context, bet_amount)
    
    elif action == "join":
        # Handle joining multiplayer game
        game_id = data[2]
        await join_wheel_game(query, game_id)
    
    elif action == "start":
        # Handle starting multiplayer game
        game_id = data[2]
        await start_wheel_game(query, game_id)

async def execute_solo_wheel_game(query, segment_id: int, bet_amount: float):
    """Execute a solo wheel game with animation"""
    user = await get_user(query.from_user.id)
    segment = WHEEL_SEGMENTS[segment_id]
    
    if user["balance"] < bet_amount:
        await query.edit_message_text(
            f"❌ Insufficient funds!\n"
            f"Balance: {format_money(user['balance'])}\n"
            f"Required: {format_money(bet_amount)}"
        )
        return
    
    # Deduct bet amount
    await update_user_balance(user["user_id"], -bet_amount)
    await record_transaction(user["user_id"], -bet_amount, "wheel bet", "Solo wheel game")
    
    # Show spinning animation
    await query.edit_message_text(
        f"🎡 **SPINNING WHEEL...**\n\n"
        f"🎯 Your bet: {segment['color']} **{segment['multiplier']}x**\n"
        f"💰 Amount: {format_money(bet_amount)}\n\n"
        f"🎡 Spinning... 🎡",
        parse_mode='Markdown'
    )
    
    # Create spinning animation
    spin_frames = ["🎡", "🔄", "⭕", "🎯", "🎡", "🔄", "⭕", "🎯"]
    
    for i in range(8):
        await asyncio.sleep(0.5)
        await query.edit_message_text(
            f"🎡 **SPINNING WHEEL...**\n\n"
            f"🎯 Your bet: {segment['color']} **{segment['multiplier']}x**\n"
            f"💰 Amount: {format_money(bet_amount)}\n\n"
            f"{spin_frames[i]} Spinning... {spin_frames[i]}",
            parse_mode='Markdown'
        )
    
    # Determine result based on probability
    rand = random.random()
    cumulative_prob = 0
    result_segment_id = 1
    
    for seg_id, seg_data in WHEEL_SEGMENTS.items():
        cumulative_prob += seg_data['probability']
        if rand <= cumulative_prob:
            result_segment_id = seg_id
            break
    
    result_segment = WHEEL_SEGMENTS[result_segment_id]
    won = segment_id == result_segment_id
    winnings = bet_amount * segment['multiplier'] if won else 0
    
    # Record game
    game_id = await record_game(user["user_id"], "wheel", bet_amount, "win" if won else "loss", winnings)
    
    if won:
        await update_user_balance(user["user_id"], winnings)
        await record_transaction(user["user_id"], winnings, "wheel win", f"Game ID: {game_id}")
    
    # Get updated balance
    user = await get_user(user["user_id"])
    
    # Show result with animation
    if won:
        result_text = (
            f"🎉 **JACKPOT!** 🎉\n\n"
            f"🎡 **RESULT:** {result_segment['color']} **{result_segment['multiplier']}x**\n"
            f"🎯 Your bet: {segment['color']} **{segment['multiplier']}x** ✅\n\n"
            f"💰 Bet: {format_money(bet_amount)}\n"
            f"🏆 Won: **{format_money(winnings)}** ({segment['multiplier']}x)\n"
            f"💳 Balance: {format_money(user['balance'])}"
        )
    else:
        result_text = (
            f"😢 **WHEEL STOPPED!**\n\n"
            f"🎡 **RESULT:** {result_segment['color']} **{result_segment['multiplier']}x**\n"
            f"🎯 Your bet: {segment['color']} **{segment['multiplier']}x** ❌\n\n"
            f"💸 Lost: {format_money(bet_amount)}\n"
            f"💳 Balance: {format_money(user['balance'])}"
        )
    
    keyboard = [
        [
            InlineKeyboardButton("🎡 Spin Again", callback_data=f"wheel_solo_bet_{segment_id}_{bet_amount}"),
            InlineKeyboardButton("💰 Double Bet", callback_data=f"wheel_solo_bet_{segment_id}_{bet_amount*2}")
        ],
        [
            InlineKeyboardButton("🎨 New Color", callback_data="wheel_solo"),
            InlineKeyboardButton("👥 Multiplayer", callback_data="wheel_multiplayer")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.message.reply_text(result_text, reply_markup=reply_markup, parse_mode='Markdown')

async def start_multiplayer_wheel(query, context: ContextTypes.DEFAULT_TYPE, bet_amount: float):
    """Start a multiplayer wheel game"""
    user = await get_user(query.from_user.id)
    
    if user["balance"] < bet_amount:
        await query.edit_message_text(
            f"❌ Insufficient funds!\n"
            f"Balance: {format_money(user['balance'])}\n"
            f"Required: {format_money(bet_amount)}"
        )
        return
    
    game_id = f"wheel_{query.message.chat.id}_{random.randint(1000, 9999)}"
    
    # Create new multiplayer game
    active_wheel_games[game_id] = {
        'creator': query.from_user.id,
        'creator_name': query.from_user.first_name,
        'bet_amount': bet_amount,
        'players': {},
        'status': 'waiting',
        'chat_id': query.message.chat.id
    }
    
    keyboard = [
        [
            InlineKeyboardButton("🎯 Join Game", callback_data=f"wheel_join_{game_id}"),
            InlineKeyboardButton("🎡 Start Spin", callback_data=f"wheel_start_{game_id}")
        ],
        [
            InlineKeyboardButton("❌ Cancel", callback_data=f"wheel_cancel_{game_id}")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        f"🎡 **MULTIPLAYER WHEEL GAME**\n\n"
        f"🎯 Host: {query.from_user.first_name}\n"
        f"💰 Entry Fee: {format_money(bet_amount)}\n"
        f"👥 Players: 1/10\n\n"
        f"**How to play:**\n"
        f"• Everyone pays entry fee\n"
        f"• Wheel spins once for all players\n"
        f"• Everyone wins based on result!\n"
        f"• Higher multipliers = bigger wins\n\n"
        f"⏰ Waiting for players to join...",
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

async def join_wheel_game(query, game_id: str):
    """Join a multiplayer wheel game"""
    if game_id not in active_wheel_games:
        await query.edit_message_text("❌ Game not found or already finished!")
        return
    
    game = active_wheel_games[game_id]
    user_id = query.from_user.id
    
    if user_id == game['creator']:
        await query.answer("You're already the host of this game!")
        return
    
    if user_id in game['players']:
        await query.answer("You're already in this game!")
        return
    
    if len(game['players']) >= 9:  # Max 10 players (9 + creator)
        await query.answer("Game is full!")
        return
    
    user = await get_user(user_id)
    if user["balance"] < game['bet_amount']:
        await query.answer(f"Insufficient funds! Need {format_money(game['bet_amount'])}")
        return
    
    # Add player to game
    game['players'][user_id] = {
        'name': query.from_user.first_name,
        'paid': False
    }
    
    # Update game message
    player_count = len(game['players']) + 1  # +1 for creator
    keyboard = [
        [
            InlineKeyboardButton("🎯 Join Game", callback_data=f"wheel_join_{game_id}"),
            InlineKeyboardButton("🎡 Start Spin", callback_data=f"wheel_start_{game_id}")
        ],
        [
            InlineKeyboardButton("❌ Cancel", callback_data=f"wheel_cancel_{game_id}")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        f"🎡 **MULTIPLAYER WHEEL GAME**\n\n"
        f"🎯 Host: {game['creator_name']}\n"
        f"💰 Entry Fee: {format_money(game['bet_amount'])}\n"
        f"👥 Players: {player_count}/10\n\n"
        f"**Players joined:**\n"
        f"• {game['creator_name']} (Host)\n" +
        "\n".join([f"• {p['name']}" for p in game['players'].values()]) +
        f"\n\n⏰ Waiting for more players...",
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

async def start_wheel_game(query, game_id: str):
    """Start the multiplayer wheel game"""
    if game_id not in active_wheel_games:
        await query.edit_message_text("❌ Game not found!")
        return
    
    game = active_wheel_games[game_id]
    
    if query.from_user.id != game['creator']:
        await query.answer("Only the host can start the game!")
        return
    
    if len(game['players']) == 0:
        await query.answer("Need at least 1 other player to start!")
        return
    
    # Collect entry fees from all players
    all_players = [game['creator']] + list(game['players'].keys())
    total_pot = 0
    
    for player_id in all_players:
        user = await get_user(player_id)
        if user["balance"] < game['bet_amount']:
            await query.edit_message_text(
                f"❌ Game cancelled!\n"
                f"Player {user['username'] or 'Unknown'} has insufficient funds."
            )
            del active_wheel_games[game_id]
            return
        
        await update_user_balance(player_id, -game['bet_amount'])
        await record_transaction(player_id, -game['bet_amount'], "wheel entry", f"Multiplayer game {game_id}")
        total_pot += game['bet_amount']
    
    # Start the game
    await query.edit_message_text(
        f"🎡 **WHEEL SPINNING!**\n\n"
        f"💰 Total Pot: {format_money(total_pot)}\n"
        f"👥 Players: {len(all_players)}\n\n"
        f"🎡 The wheel is spinning... 🎡",
        parse_mode='Markdown'
    )
    
    # Create spinning animation
    spin_frames = ["🎡", "🔄", "⭕", "🎯", "🌟", "✨", "💫", "🎊"]
    
    for i in range(16):  # Longer animation for suspense
        await asyncio.sleep(0.3)
        frame = spin_frames[i % len(spin_frames)]
        await query.edit_message_text(
            f"🎡 **WHEEL SPINNING!**\n\n"
            f"💰 Total Pot: {format_money(total_pot)}\n"
            f"👥 Players: {len(all_players)}\n\n"
            f"{frame} Spinning... {frame}",
            parse_mode='Markdown'
        )
    
    # Determine result
    rand = random.random()
    cumulative_prob = 0
    result_segment_id = 1
    
    for seg_id, seg_data in WHEEL_SEGMENTS.items():
        cumulative_prob += seg_data['probability']
        if rand <= cumulative_prob:
            result_segment_id = seg_id
            break
    
    result_segment = WHEEL_SEGMENTS[result_segment_id]
    
    # Calculate winnings for each player
    individual_winnings = game['bet_amount'] * result_segment['multiplier']
    
    # Award winnings to all players
    for player_id in all_players:
        await update_user_balance(player_id, individual_winnings)
        await record_transaction(player_id, individual_winnings, "wheel win", f"Multiplayer game {game_id}")
        await record_game(player_id, "wheel", game['bet_amount'], "win", individual_winnings)
    
    # Create result message
    result_text = (
        f"🎉 **WHEEL STOPPED!** 🎉\n\n"
        f"🎡 **RESULT:** {result_segment['color']} **{result_segment['multiplier']}x**\n\n"
        f"💰 Entry Fee: {format_money(game['bet_amount'])}\n"
        f"🏆 Each Player Won: **{format_money(individual_winnings)}**\n"
        f"📈 Profit per Player: **{format_money(individual_winnings - game['bet_amount'])}**\n\n"
        f"**All Players Won:**\n"
    )
    
    for player_id in all_players:
        user = await get_user(player_id)
        result_text += f"• {user['username'] or 'Unknown'}: +{format_money(individual_winnings - game['bet_amount'])}\n"
    
    keyboard = [
        [
            InlineKeyboardButton("🎡 New Game", callback_data="wheel_multiplayer"),
            InlineKeyboardButton("🏠 Main Menu", callback_data="main_menu")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.message.reply_text(result_text, reply_markup=reply_markup, parse_mode='Markdown')
    
    # Clean up game
    del active_wheel_games[game_id]

# Export the callback handler
wheel_callback_handler = wheel_callback