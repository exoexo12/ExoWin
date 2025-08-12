from flask import Flask, render_template, request, jsonify, send_from_directory, session
from flask_cors import CORS
import os
import sys
import json
import asyncio
import random
import secrets
from datetime import timedelta
from dotenv import load_dotenv

# Add parent directory to path to import from src
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Load environment variables
load_dotenv()

from webapp.sync_db import get_user, update_user_balance, record_transaction, record_game, get_leaderboard
from src.utils.logger import webapp_logger
from src.utils.validators import validator
from src.utils.error_handler import GameError, InsufficientFundsError, InvalidBetError
from src.games.blackjack import create_blackjack_game, hit_blackjack, stand_blackjack, get_game, set_game, clear_game
from src.games.roulette import create_roulette_game, get_roulette_game, place_roulette_bet, spin_roulette, clear_roulette_game
from src.games.crash import create_crash_game, get_crash_game, update_crash_game, cash_out_crash, clear_crash_game
from src.games.mines import create_mines_game, get_mines_game, reveal_mines_tile, cash_out_mines, clear_mines_game
from src.games.tower import create_tower_game, get_tower_game, choose_tower_tile, cash_out_tower, clear_tower_game
from src.games.plinko import create_plinko_game, get_plinko_game, drop_plinko_ball, clear_plinko_game
from src.games.poker import create_poker_game, get_poker_game, finish_poker_game, clear_poker_game
from src.games.lottery import create_lottery_game, get_lottery_game, select_lottery_numbers, draw_lottery_numbers, clear_lottery_game

app = Flask(__name__)
CORS(app, origins="*", allow_headers="*", methods="*")

# Configure Flask for Telegram Web Apps
app.config['SECRET_KEY'] = os.getenv('FLASK_SECRET_KEY', secrets.token_hex(32))
app.permanent_session_lifetime = timedelta(hours=24)

# Security headers
@app.after_request
def add_security_headers(response):
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'SAMEORIGIN'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    return response

@app.route('/')
def index():
    """Health check endpoint"""
    return jsonify({'status': 'ok', 'message': 'Gamble Bot Web App Server Running'})

@app.route('/games/<game_name>')
def game_page(game_name):
    """Serve game pages"""
    user_id = request.args.get('user_id')
    if not user_id:
        return "User ID required", 400
    
    # Get user data
    try:
        user = get_user(int(user_id))
    except Exception as e:
        return f"Error loading user data: {str(e)}", 500
    
    return render_template(f'games/{game_name}.html', user=user, user_id=user_id)

@app.route('/leaderboard')
def leaderboard_page():
    """Serve leaderboard page"""
    user_id = request.args.get('user_id')
    game_type = request.args.get('game_type', 'all')
    period = request.args.get('period', 'all_time')
    
    if not user_id:
        return "User ID required", 400
    
    # Get user data and leaderboard
    try:
        user = get_user(int(user_id))
        leaderboard_data = get_leaderboard(game_type, period)
    except Exception as e:
        return f"Error loading data: {str(e)}", 500
    
    return render_template('leaderboard.html', 
                          user=user, 
                          user_id=user_id, 
                          leaderboard=leaderboard_data,
                          game_type=game_type,
                          period=period)

@app.route('/api/user/<int:user_id>')
def get_user_data(user_id):
    """Get user data API endpoint"""
    try:
        user = get_user(user_id)
        
        return jsonify({
            'success': True,
            'user': {
                'user_id': user['user_id'],
                'balance': user['balance'],
                'total_bets': user.get('total_bets', 0),
                'total_wins': user.get('total_wins', 0),
                'total_losses': user.get('total_losses', 0)
            }
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/leaderboard')
def get_leaderboard_data():
    """Get leaderboard data API endpoint"""
    try:
        game_type = request.args.get('game_type', 'all')
        period = request.args.get('period', 'all_time')
        limit = int(request.args.get('limit', 10))
        
        leaderboard_data = get_leaderboard(game_type, period, limit)
        
        return jsonify({
            'success': True,
            'leaderboard': leaderboard_data,
            'game_type': game_type,
            'period': period
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/game/bet', methods=['POST'])
def place_bet():
    """Place a bet API endpoint"""
    try:
        data = request.get_json()
        user_id = data.get('user_id')
        game_type = data.get('game_type')
        bet_amount = float(data.get('bet_amount'))
        game_data = data.get('game_data', {})
        
        if not all([user_id, game_type, bet_amount]):
            return jsonify({'success': False, 'error': 'Missing required fields'}), 400
        
        # Get user and check balance
        user = get_user(user_id)
        
        if user['balance'] < bet_amount:
            return jsonify({
                'success': False, 
                'error': 'Insufficient balance',
                'balance': user['balance']
            }), 400
        
        # Deduct bet amount
        update_user_balance(user_id, -bet_amount)
        record_transaction(user_id, -bet_amount, "bet", f"{game_type} bet")
        
        # Process game logic based on game type
        result = process_game_logic(game_type, bet_amount, game_data)
        
        # Record game result
        game_id = record_game(
            user_id, game_type, bet_amount, 
            result['outcome'], result['winnings']
        )
        
        # Update balance if won
        if result['winnings'] > 0:
            update_user_balance(user_id, result['winnings'])
            record_transaction(user_id, result['winnings'], "win", f"{game_type} win")
        
        # Get updated user data
        updated_user = get_user(user_id)
        
        return jsonify({
            'success': True,
            'result': result,
            'new_balance': updated_user['balance'],
            'game_id': game_id
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

def process_game_logic(game_type, bet_amount, game_data):
    """Process game logic and return result"""
    try:
        if game_type == 'coinflip':
            # Coinflip game logic
            user_choice = game_data.get('choice', 'heads')  # heads or tails
            result = random.choice(['heads', 'tails'])
            
            if user_choice == result:
                winnings = bet_amount * 2  # 2x multiplier for correct guess
                return {
                    'outcome': 'win',
                    'winnings': winnings,
                    'result': result,
                    'user_choice': user_choice,
                    'multiplier': 2.0,
                    'message': f'You chose {user_choice} and it landed on {result}! You won!'
                }
            else:
                return {
                    'outcome': 'loss',
                    'winnings': 0,
                    'result': result,
                    'user_choice': user_choice,
                    'message': f'You chose {user_choice} but it landed on {result}. Better luck next time!'
                }
        
        elif game_type == 'crash':
            # Crash game logic
            crash_point = round(random.uniform(1.01, 10.0), 2)
            cash_out_at = game_data.get('cash_out_at', 2.0)
            
            if cash_out_at <= crash_point:
                winnings = bet_amount * cash_out_at
                return {
                    'outcome': 'win',
                    'winnings': winnings,
                    'crash_point': crash_point,
                    'cash_out_at': cash_out_at,
                    'multiplier': cash_out_at,
                    'message': f'Cashed out at {cash_out_at}x! Crash was at {crash_point}x'
                }
            else:
                return {
                    'outcome': 'loss',
                    'winnings': 0,
                    'crash_point': crash_point,
                    'cash_out_at': cash_out_at,
                    'message': f'Crashed at {crash_point}x before your cash out at {cash_out_at}x!'
                }
        
        elif game_type == 'dice':
            # Dice game logic
            target = game_data.get('target', 50)  # Target number (1-100)
            over_under = game_data.get('over_under', 'over')  # 'over' or 'under'
            
            roll = random.randint(1, 100)
            
            won = False
            if over_under == 'over' and roll > target:
                won = True
            elif over_under == 'under' and roll < target:
                won = True
            
            if won:
                # Calculate multiplier based on probability
                if over_under == 'over':
                    probability = (100 - target) / 100
                else:
                    probability = target / 100
                
                multiplier = 0.95 / probability  # 95% RTP
                winnings = bet_amount * multiplier
                
                return {
                    'outcome': 'win',
                    'winnings': winnings,
                    'roll': roll,
                    'target': target,
                    'over_under': over_under,
                    'multiplier': multiplier,
                    'message': f'Rolled {roll}! You won with {over_under} {target}!'
                }
            else:
                return {
                    'outcome': 'loss',
                    'winnings': 0,
                    'roll': roll,
                    'target': target,
                    'over_under': over_under,
                    'message': f'Rolled {roll}. You needed {over_under} {target}.'
                }
        
        elif game_type == 'plinko':
            # Plinko game logic
            risk_level = game_data.get('risk', 'medium')  # low, medium, high
            
            # Define multipliers for different risk levels
            multipliers = {
                'low': [0.5, 0.7, 1.0, 1.2, 1.5, 1.2, 1.0, 0.7, 0.5],
                'medium': [0.2, 0.5, 1.0, 2.0, 5.0, 2.0, 1.0, 0.5, 0.2],
                'high': [0.1, 0.3, 0.5, 2.0, 10.0, 2.0, 0.5, 0.3, 0.1]
            }
            
            # Simulate ball drop (weighted towards center)
            weights = [1, 2, 4, 6, 8, 6, 4, 2, 1]
            bucket = random.choices(range(9), weights=weights)[0]
            multiplier = multipliers[risk_level][bucket]
            
            winnings = bet_amount * multiplier
            
            return {
                'outcome': 'win' if multiplier > 1.0 else 'loss',
                'winnings': winnings,
                'bucket': bucket,
                'multiplier': multiplier,
                'risk_level': risk_level,
                'message': f'Ball landed in bucket {bucket + 1} with {multiplier}x multiplier!'
            }
        
        elif game_type == 'mines':
            # Mines game logic
            mines_count = game_data.get('mines', 3)
            revealed_positions = game_data.get('revealed', [])
            action = game_data.get('action', 'reveal')  # 'reveal' or 'cashout'
            
            # Generate consistent mine positions for this game session
            seed = game_data.get('seed', random.randint(1, 1000000))
            random.seed(seed)
            mine_positions = random.sample(range(25), mines_count)
            random.seed()  # Reset seed
            
            if action == 'reveal':
                position = game_data.get('position')
                if position in mine_positions:
                    return {
                        'outcome': 'loss',
                        'winnings': 0,
                        'mine_positions': mine_positions,
                        'hit_mine': True,
                        'position': position,
                        'message': 'Hit a mine! Game over.'
                    }
                else:
                    # Calculate current multiplier
                    gems_found = len(revealed_positions) + 1
                    safe_tiles = 25 - mines_count
                    multiplier = 1.0
                    for i in range(gems_found):
                        multiplier *= (safe_tiles - i) / (25 - mines_count - i)
                    
                    return {
                        'outcome': 'continue',
                        'winnings': 0,
                        'position': position,
                        'gems_found': gems_found,
                        'multiplier': multiplier,
                        'hit_mine': False,
                        'seed': seed,
                        'message': f'Found a gem! Current multiplier: {multiplier:.2f}x'
                    }
            
            elif action == 'cashout':
                gems_found = len(revealed_positions)
                if gems_found == 0:
                    multiplier = 1.0
                else:
                    safe_tiles = 25 - mines_count
                    multiplier = 1.0
                    for i in range(gems_found):
                        multiplier *= (safe_tiles - i) / (25 - mines_count - i)
                
                winnings = bet_amount * multiplier
                
                return {
                    'outcome': 'win',
                    'winnings': winnings,
                    'gems_found': gems_found,
                    'multiplier': multiplier,
                    'message': f'Cashed out with {gems_found} gems! Multiplier: {multiplier:.2f}x'
                }
        
        elif game_type == 'roulette':
            # Roulette game logic
            bet_type = game_data.get('bet_type', 'number')  # number, color, odd_even
            bet_value = game_data.get('bet_value')
            
            # Generate winning number (0-36)
            winning_number = random.randint(0, 36)
            
            # Determine color
            if winning_number == 0:
                winning_color = 'green'
            elif winning_number in [1,3,5,7,9,12,14,16,18,19,21,23,25,27,30,32,34,36]:
                winning_color = 'red'
            else:
                winning_color = 'black'
            
            won = False
            multiplier = 0
            
            if bet_type == 'number' and bet_value == winning_number:
                won = True
                multiplier = 36  # 36:1 payout for single number
            elif bet_type == 'color' and bet_value == winning_color:
                won = True
                multiplier = 2  # 2:1 payout for color
            elif bet_type == 'odd_even':
                if bet_value == 'odd' and winning_number % 2 == 1 and winning_number != 0:
                    won = True
                    multiplier = 2
                elif bet_value == 'even' and winning_number % 2 == 0 and winning_number != 0:
                    won = True
                    multiplier = 2
            
            winnings = bet_amount * multiplier if won else 0
            
            return {
                'outcome': 'win' if won else 'loss',
                'winnings': winnings,
                'winning_number': winning_number,
                'winning_color': winning_color,
                'bet_type': bet_type,
                'bet_value': bet_value,
                'multiplier': multiplier,
                'message': f'Ball landed on {winning_number} ({winning_color})!'
            }
        
        elif game_type == 'slots':
            # Slots game logic
            symbols = ['🍒', '🍋', '🍊', '🍇', '🔔', '💎', '7️⃣']
            weights = [30, 25, 20, 15, 7, 2, 1]  # Weighted probabilities
            
            # Spin reels
            reel1 = random.choices(symbols, weights=weights)[0]
            reel2 = random.choices(symbols, weights=weights)[0]
            reel3 = random.choices(symbols, weights=weights)[0]
            
            # Check for wins
            multiplier = 0
            if reel1 == reel2 == reel3:
                # Three of a kind
                symbol_multipliers = {
                    '🍒': 5, '🍋': 10, '🍊': 15, '🍇': 20,
                    '🔔': 50, '💎': 100, '7️⃣': 500
                }
                multiplier = symbol_multipliers.get(reel1, 5)
            elif reel1 == reel2 or reel2 == reel3 or reel1 == reel3:
                # Two of a kind
                multiplier = 2
            
            winnings = bet_amount * multiplier
            
            return {
                'outcome': 'win' if multiplier > 0 else 'loss',
                'winnings': winnings,
                'reels': [reel1, reel2, reel3],
                'multiplier': multiplier,
                'message': f'Reels: {reel1} {reel2} {reel3}' + (f' - {multiplier}x win!' if multiplier > 0 else ' - No match')
            }
        
        elif game_type == 'blackjack':
            # Simplified blackjack logic
            action = game_data.get('action', 'deal')
            
            if action == 'deal':
                # Deal initial cards
                player_cards = [random.randint(1, 11), random.randint(1, 11)]
                dealer_cards = [random.randint(1, 11)]
                
                player_total = sum(player_cards)
                
                # Handle aces
                if player_total > 21 and 11 in player_cards:
                    player_cards[player_cards.index(11)] = 1
                    player_total = sum(player_cards)
                
                if player_total == 21:
                    # Blackjack!
                    winnings = bet_amount * 2.5
                    return {
                        'outcome': 'win',
                        'winnings': winnings,
                        'player_cards': player_cards,
                        'dealer_cards': dealer_cards,
                        'player_total': player_total,
                        'multiplier': 2.5,
                        'message': 'Blackjack! You won!'
                    }
                elif player_total > 21:
                    # Bust
                    return {
                        'outcome': 'loss',
                        'winnings': 0,
                        'player_cards': player_cards,
                        'dealer_cards': dealer_cards,
                        'player_total': player_total,
                        'message': 'Bust! You went over 21.'
                    }
                else:
                    # Continue game
                    return {
                        'outcome': 'continue',
                        'winnings': 0,
                        'player_cards': player_cards,
                        'dealer_cards': dealer_cards,
                        'player_total': player_total,
                        'message': f'Your total: {player_total}. Hit or Stand?'
                    }
        
        elif game_type == 'tower':
            # Tower game logic
            action = game_data.get('action', 'start')
            
            if action == 'select_tile':
                level = game_data.get('level', 0)
                tile = game_data.get('tile', 0)
                current_level = game_data.get('current_level', 0)
                
                # Each level has 2 safe tiles and 1 dangerous tile
                safe_tiles = random.sample(range(3), 2)
                
                if tile in safe_tiles:
                    # Safe tile - advance level
                    new_level = current_level + 1
                    multipliers = [1.0, 1.5, 2.25, 3.38, 5.06, 7.59, 11.39, 17.09]
                    
                    if new_level >= 8:
                        # Reached the top!
                        winnings = bet_amount * multipliers[7]
                        return {
                            'outcome': 'win',
                            'winnings': winnings,
                            'level': new_level,
                            'multiplier': multipliers[7],
                            'message': 'You reached the top of the tower!'
                        }
                    else:
                        return {
                            'outcome': 'continue',
                            'winnings': 0,
                            'level': new_level,
                            'multiplier': multipliers[new_level],
                            'message': f'Safe! Advanced to level {new_level + 1}'
                        }
                else:
                    # Dangerous tile - game over
                    return {
                        'outcome': 'loss',
                        'winnings': 0,
                        'level': current_level,
                        'message': 'Hit a dangerous tile! Game over.'
                    }
        
        elif game_type == 'wheel':
            # Wheel of Fortune game logic
            selected_segment = game_data.get('selected_segment', 1)
            
            # Define wheel segments with their multipliers
            segments = {
                1: 2, 2: 3, 3: 5, 4: 2,
                5: 10, 6: 3, 7: 5, 8: 20
            }
            
            # Spin the wheel (weighted towards lower multipliers)
            weights = [25, 20, 15, 25, 8, 20, 15, 2]  # Lower chance for higher multipliers
            winning_segment = random.choices(list(segments.keys()), weights=weights)[0]
            
            if winning_segment == selected_segment:
                multiplier = segments[winning_segment]
                winnings = bet_amount * multiplier
                return {
                    'outcome': 'win',
                    'winnings': winnings,
                    'winning_segment': winning_segment,
                    'selected_segment': selected_segment,
                    'multiplier': multiplier,
                    'message': f'Perfect prediction! {multiplier}x multiplier!'
                }
            else:
                return {
                    'outcome': 'loss',
                    'winnings': 0,
                    'winning_segment': winning_segment,
                    'selected_segment': selected_segment,
                    'message': f'Wheel landed on segment {winning_segment}'
                }
        
        elif game_type == 'roll':
            # Simple dice roll game (alias for dice)
            return process_game_logic('dice', bet_amount, game_data)
        
        # Default case for unimplemented games
        return {
            'outcome': 'loss',
            'winnings': 0,
            'message': f'Game {game_type} not implemented yet'
        }
        
    except Exception as e:
        return {
            'outcome': 'error',
            'winnings': 0,
            'message': f'Game error: {str(e)}'
        }

# Blackjack specific endpoints
@app.route('/api/blackjack/deal', methods=['POST'])
def blackjack_deal():
    """Deal new blackjack hand"""
    try:
        data = request.get_json()
        user_id = data.get('user_id')
        bet_amount = float(data.get('bet_amount'))
        
        if not all([user_id, bet_amount]):
            return jsonify({'success': False, 'error': 'Missing required fields'}), 400
        
        # Get user and check balance
        user = get_user(user_id)
        
        if user['balance'] < bet_amount:
            return jsonify({
                'success': False, 
                'error': 'Insufficient balance',
                'balance': user['balance']
            }), 400
        
        # Deduct bet amount
        update_user_balance(user_id, -bet_amount)
        record_transaction(user_id, -bet_amount, "bet", "blackjack bet")
        
        # Create new game
        game = create_blackjack_game(user_id, bet_amount)
        set_game(user_id, game)
        
        # Get updated user data
        updated_user = get_user(user_id)
        
        return jsonify({
            'success': True,
            'game': game.to_dict(),
            'new_balance': updated_user['balance']
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/blackjack/hit', methods=['POST'])
def blackjack_hit():
    """Hit in blackjack game"""
    try:
        data = request.get_json()
        user_id = data.get('user_id')
        
        if not user_id:
            return jsonify({'success': False, 'error': 'Missing user_id'}), 400
        
        # Get active game
        game = get_game(user_id)
        if not game:
            return jsonify({'success': False, 'error': 'No active game'}), 400
        
        # Hit
        result = hit_blackjack(game)
        
        # If game is over, handle winnings
        if game.game_over:
            winnings = game.get_winnings()
            
            # Record game result
            game_id = record_game(
                user_id, "blackjack", game.bet_amount,
                "win" if winnings > game.bet_amount else "loss" if winnings == 0 else "push",
                winnings
            )
            
            # Update balance with winnings
            if winnings > 0:
                update_user_balance(user_id, winnings)
                record_transaction(user_id, winnings, "win", "blackjack win")
            
            # Clear game
            clear_game(user_id)
            
            # Get updated user data
            updated_user = get_user(user_id)
            result['new_balance'] = updated_user['balance']
        
        return jsonify({
            'success': True,
            'game': result
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/blackjack/stand', methods=['POST'])
def blackjack_stand():
    """Stand in blackjack game"""
    try:
        data = request.get_json()
        user_id = data.get('user_id')
        
        if not user_id:
            return jsonify({'success': False, 'error': 'Missing user_id'}), 400
        
        # Get active game
        game = get_game(user_id)
        if not game:
            return jsonify({'success': False, 'error': 'No active game'}), 400
        
        # Stand
        result = stand_blackjack(game)
        
        # Handle winnings
        winnings = game.get_winnings()
        
        # Record game result
        game_id = record_game(
            user_id, "blackjack", game.bet_amount,
            "win" if winnings > game.bet_amount else "loss" if winnings == 0 else "push",
            winnings,
            {
                "player_hand": [str(card) for card in game.player_hand],
                "dealer_hand": [str(card) for card in game.dealer_hand],
                "player_score": game.get_player_score(),
                "dealer_score": game.get_dealer_score()
            }
        )
        
        # Update balance with winnings
        if winnings > 0:
            update_user_balance(user_id, winnings)
            record_transaction(user_id, winnings, "win", "blackjack win")
        
        # Clear game
        clear_game(user_id)
        
        # Get updated user data
        updated_user = get_user(user_id)
        result['new_balance'] = updated_user['balance']
        
        return jsonify({
            'success': True,
            'game': result
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# ==================== ROULETTE API ENDPOINTS ====================
@app.route('/api/roulette/start', methods=['POST'])
def roulette_start():
    """Start a new roulette game"""
    try:
        data = request.get_json()
        user_id = data.get('user_id')
        
        if not user_id:
            return jsonify({'success': False, 'error': 'Missing user_id'}), 400
        
        # Create new game
        game = create_roulette_game(user_id)
        
        return jsonify({
            'success': True,
            'game': game.get_game_state() if hasattr(game, 'get_game_state') else {
                'bets': game.bets,
                'total_bet': game.total_bet,
                'game_over': game.game_over
            }
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/roulette/bet', methods=['POST'])
def roulette_bet():
    """Place a bet in roulette"""
    try:
        data = request.get_json()
        user_id = data.get('user_id')
        bet_type = data.get('bet_type')
        bet_amount = float(data.get('bet_amount'))
        
        if not all([user_id, bet_type, bet_amount]):
            return jsonify({'success': False, 'error': 'Missing required fields'}), 400
        
        # Get user and check balance
        user = get_user(user_id)
        if user['balance'] < bet_amount:
            return jsonify({
                'success': False,
                'error': 'Insufficient balance',
                'balance': user['balance']
            }), 400
        
        # Place bet
        success = place_roulette_bet(user_id, bet_type, bet_amount)
        if not success:
            return jsonify({'success': False, 'error': 'Failed to place bet'}), 400
        
        # Deduct bet from balance
        new_balance = update_user_balance(user_id, -bet_amount)
        record_transaction(user_id, -bet_amount, 'roulette_bet', f'Roulette bet: {bet_type}')
        
        game = get_roulette_game(user_id)
        
        return jsonify({
            'success': True,
            'game': {
                'bets': game.bets,
                'total_bet': game.total_bet,
                'game_over': game.game_over
            },
            'new_balance': new_balance
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/roulette/spin', methods=['POST'])
def roulette_spin():
    """Spin the roulette wheel"""
    try:
        data = request.get_json()
        user_id = data.get('user_id')
        
        if not user_id:
            return jsonify({'success': False, 'error': 'Missing user_id'}), 400
        
        # Spin wheel
        winning_number = spin_roulette(user_id)
        if winning_number is None:
            return jsonify({'success': False, 'error': 'No active game'}), 400
        
        game = get_roulette_game(user_id)
        
        # Handle winnings
        if game.winnings > 0:
            new_balance = update_user_balance(user_id, game.winnings)
            record_transaction(user_id, game.winnings, 'roulette_win', f'Roulette win: {game.winning_number}')
            record_game(user_id, 'roulette', game.total_bet, game.winnings, 'win')
        else:
            user = get_user(user_id)
            new_balance = user['balance']
            record_game(user_id, 'roulette', game.total_bet, 0, 'lose')
        
        result = {
            'success': True,
            'game': {
                'winning_number': game.winning_number,
                'winning_color': game.winning_color,
                'bets': game.bets,
                'total_bet': game.total_bet,
                'winnings': game.winnings,
                'payout_details': game.payout_details,
                'game_over': game.game_over,
                'result': game.result
            },
            'new_balance': new_balance
        }
        
        # Clear game
        clear_roulette_game(user_id)
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# ==================== CRASH API ENDPOINTS ====================
@app.route('/api/crash/start', methods=['POST'])
def crash_start():
    """Start a new crash game"""
    try:
        data = request.get_json()
        user_id = data.get('user_id')
        bet_amount = float(data.get('bet_amount'))
        
        if not all([user_id, bet_amount]):
            return jsonify({'success': False, 'error': 'Missing required fields'}), 400
        
        # Get user and check balance
        user = get_user(user_id)
        if user['balance'] < bet_amount:
            return jsonify({
                'success': False,
                'error': 'Insufficient balance',
                'balance': user['balance']
            }), 400
        
        # Deduct bet from balance
        new_balance = update_user_balance(user_id, -bet_amount)
        record_transaction(user_id, -bet_amount, 'crash_bet', 'Crash game bet')
        
        # Create game
        game = create_crash_game(user_id, bet_amount)
        
        return jsonify({
            'success': True,
            'game': {
                'current_multiplier': game.current_multiplier,
                'is_running': game.is_running,
                'game_over': game.game_over,
                'bet_amount': game.bet_amount
            },
            'new_balance': new_balance
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/crash/update', methods=['POST'])
def crash_update():
    """Update crash game state"""
    try:
        data = request.get_json()
        user_id = data.get('user_id')
        
        if not user_id:
            return jsonify({'success': False, 'error': 'Missing user_id'}), 400
        
        game = update_crash_game(user_id)
        if not game:
            return jsonify({'success': False, 'error': 'No active game'}), 400
        
        return jsonify({
            'success': True,
            'game': {
                'current_multiplier': game.current_multiplier,
                'is_running': game.is_running,
                'game_over': game.game_over,
                'result': game.result,
                'winnings': game.winnings,
                'cashed_out': game.cashed_out
            }
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/crash/cashout', methods=['POST'])
def crash_cashout():
    """Cash out from crash game"""
    try:
        data = request.get_json()
        user_id = data.get('user_id')
        
        if not user_id:
            return jsonify({'success': False, 'error': 'Missing user_id'}), 400
        
        success = cash_out_crash(user_id)
        if not success:
            return jsonify({'success': False, 'error': 'Cannot cash out'}), 400
        
        game = get_crash_game(user_id)
        
        # Handle winnings
        if game.winnings > 0:
            new_balance = update_user_balance(user_id, game.winnings)
            record_transaction(user_id, game.winnings, 'crash_win', f'Crash win at {game.cash_out_multiplier:.2f}x')
            record_game(user_id, 'crash', game.bet_amount, game.winnings, 'win')
        else:
            user = get_user(user_id)
            new_balance = user['balance']
            record_game(user_id, 'crash', game.bet_amount, 0, 'lose')
        
        result = {
            'success': True,
            'game': {
                'current_multiplier': game.current_multiplier,
                'cash_out_multiplier': game.cash_out_multiplier,
                'winnings': game.winnings,
                'game_over': game.game_over,
                'result': game.result,
                'cashed_out': game.cashed_out
            },
            'new_balance': new_balance
        }
        
        # Clear game
        clear_crash_game(user_id)
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# ==================== MINES API ENDPOINTS ====================
@app.route('/api/mines/start', methods=['POST'])
def mines_start():
    """Start a new mines game"""
    try:
        data = request.get_json()
        user_id = data.get('user_id')
        bet_amount = float(data.get('bet_amount'))
        mines_count = int(data.get('mines_count', 5))
        
        if not all([user_id, bet_amount]):
            return jsonify({'success': False, 'error': 'Missing required fields'}), 400
        
        # Get user and check balance
        user = get_user(user_id)
        if user['balance'] < bet_amount:
            return jsonify({
                'success': False,
                'error': 'Insufficient balance',
                'balance': user['balance']
            }), 400
        
        # Deduct bet from balance
        new_balance = update_user_balance(user_id, -bet_amount)
        record_transaction(user_id, -bet_amount, 'mines_bet', 'Mines game bet')
        
        # Create game
        game = create_mines_game(user_id, bet_amount, mines_count)
        
        return jsonify({
            'success': True,
            'game': game.get_game_state(),
            'new_balance': new_balance
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/mines/reveal', methods=['POST'])
def mines_reveal():
    """Reveal a tile in mines game"""
    try:
        data = request.get_json()
        user_id = data.get('user_id')
        position = int(data.get('position'))
        
        if not all([user_id is not None, position is not None]):
            return jsonify({'success': False, 'error': 'Missing required fields'}), 400
        
        result = reveal_mines_tile(user_id, position)
        if result is None:
            return jsonify({'success': False, 'error': 'No active game'}), 400
        
        game = get_mines_game(user_id)
        
        # If hit mine, record loss
        if result.get('hit_mine'):
            record_game(user_id, 'mines', game.bet_amount, 'lose', 0, {
                'mines_count': game.mines_count,
                'revealed_tiles': game.revealed_tiles,
                'mines_positions': game.mines_positions,
                'hit_position': position
            })
            clear_mines_game(user_id)
        
        return jsonify({
            'success': True,
            'result': result,
            'game': game.get_game_state()
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/mines/cashout', methods=['POST'])
def mines_cashout():
    """Cash out from mines game"""
    try:
        data = request.get_json()
        user_id = data.get('user_id')
        
        if not user_id:
            return jsonify({'success': False, 'error': 'Missing user_id'}), 400
        
        success = cash_out_mines(user_id)
        if not success:
            return jsonify({'success': False, 'error': 'Cannot cash out'}), 400
        
        game = get_mines_game(user_id)
        
        # Handle winnings
        new_balance = update_user_balance(user_id, game.winnings)
        record_transaction(user_id, game.winnings, 'mines_win', f'Mines cashout at {game.current_multiplier:.2f}x')
        record_game(user_id, 'mines', game.bet_amount, 'win', game.winnings, {
            'mines_count': game.mines_count,
            'revealed_tiles': game.revealed_tiles,
            'mines_positions': game.mines_positions,
            'multiplier': game.current_multiplier
        })
        
        result = {
            'success': True,
            'game': game.get_game_state(),
            'new_balance': new_balance
        }
        
        # Clear game
        clear_mines_game(user_id)
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# ==================== TOWER API ENDPOINTS ====================
@app.route('/api/tower/start', methods=['POST'])
def tower_start():
    """Start a new tower game"""
    try:
        data = request.get_json()
        user_id = data.get('user_id')
        bet_amount = float(data.get('bet_amount'))
        
        if not all([user_id, bet_amount]):
            return jsonify({'success': False, 'error': 'Missing required fields'}), 400
        
        # Get user and check balance
        user = get_user(user_id)
        if user['balance'] < bet_amount:
            return jsonify({
                'success': False,
                'error': 'Insufficient balance',
                'balance': user['balance']
            }), 400
        
        # Deduct bet from balance
        new_balance = update_user_balance(user_id, -bet_amount)
        record_transaction(user_id, -bet_amount, 'tower_bet', 'Tower game bet')
        
        # Create game
        game = create_tower_game(user_id, bet_amount)
        
        return jsonify({
            'success': True,
            'game': game.get_game_state(),
            'new_balance': new_balance
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/tower/choose', methods=['POST'])
def tower_choose():
    """Choose a tile in tower game"""
    try:
        data = request.get_json()
        user_id = data.get('user_id')
        tile_index = int(data.get('tile_index'))
        
        if not all([user_id is not None, tile_index is not None]):
            return jsonify({'success': False, 'error': 'Missing required fields'}), 400
        
        result = choose_tower_tile(user_id, tile_index)
        if result is None:
            return jsonify({'success': False, 'error': 'No active game'}), 400
        
        game = get_tower_game(user_id)
        
        # If hit trap or completed tower, handle winnings
        if game.game_over:
            if game.result == 'trap':
                record_game(user_id, 'tower', game.bet_amount, 0, 'lose')
            elif game.result == 'completed':
                new_balance = update_user_balance(user_id, game.winnings)
                record_transaction(user_id, game.winnings, 'tower_win', f'Tower completed at level {game.current_level}')
                record_game(user_id, 'tower', game.bet_amount, game.winnings, 'win')
                result['new_balance'] = new_balance
            
            clear_tower_game(user_id)
        
        return jsonify({
            'success': True,
            'result': result,
            'game': game.get_game_state()
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/tower/cashout', methods=['POST'])
def tower_cashout():
    """Cash out from tower game"""
    try:
        data = request.get_json()
        user_id = data.get('user_id')
        
        if not user_id:
            return jsonify({'success': False, 'error': 'Missing user_id'}), 400
        
        success = cash_out_tower(user_id)
        if not success:
            return jsonify({'success': False, 'error': 'Cannot cash out'}), 400
        
        game = get_tower_game(user_id)
        
        # Handle winnings
        new_balance = update_user_balance(user_id, game.winnings)
        record_transaction(user_id, game.winnings, 'tower_win', f'Tower cashout at level {game.current_level}')
        record_game(user_id, 'tower', game.bet_amount, game.winnings, 'win')
        
        result = {
            'success': True,
            'game': game.get_game_state(),
            'new_balance': new_balance
        }
        
        # Clear game
        clear_tower_game(user_id)
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# ==================== PLINKO API ENDPOINTS ====================
@app.route('/api/plinko/drop', methods=['POST'])
def plinko_drop():
    """Drop a ball in plinko game"""
    try:
        data = request.get_json()
        user_id = data.get('user_id')
        bet_amount = float(data.get('bet_amount'))
        risk_level = data.get('risk_level', 'medium')
        
        if not all([user_id, bet_amount]):
            return jsonify({'success': False, 'error': 'Missing required fields'}), 400
        
        # Get user and check balance
        user = get_user(user_id)
        if user['balance'] < bet_amount:
            return jsonify({
                'success': False,
                'error': 'Insufficient balance',
                'balance': user['balance']
            }), 400
        
        # Deduct bet from balance
        new_balance = update_user_balance(user_id, -bet_amount)
        record_transaction(user_id, -bet_amount, 'plinko_bet', 'Plinko game bet')
        
        # Create game and drop ball
        game = create_plinko_game(user_id, bet_amount, risk_level)
        result = drop_plinko_ball(user_id)
        
        # Handle winnings
        if game.winnings > 0:
            new_balance = update_user_balance(user_id, game.winnings)
            record_transaction(user_id, game.winnings, 'plinko_win', f'Plinko win: {result["multiplier"]}x')
            record_game(user_id, 'plinko', game.bet_amount, game.winnings, 'win')
        else:
            record_game(user_id, 'plinko', game.bet_amount, 0, 'lose')
        
        response = {
            'success': True,
            'result': result,
            'game': game.get_game_state(),
            'new_balance': new_balance
        }
        
        # Clear game
        clear_plinko_game(user_id)
        
        return jsonify(response)
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# ==================== POKER API ENDPOINTS ====================
@app.route('/api/poker/start', methods=['POST'])
def poker_start():
    """Start a new poker game"""
    try:
        data = request.get_json()
        user_id = data.get('user_id')
        bet_amount = float(data.get('bet_amount'))
        
        if not all([user_id, bet_amount]):
            return jsonify({'success': False, 'error': 'Missing required fields'}), 400
        
        # Get user and check balance
        user = get_user(user_id)
        if user['balance'] < bet_amount:
            return jsonify({
                'success': False,
                'error': 'Insufficient balance',
                'balance': user['balance']
            }), 400
        
        # Deduct bet from balance
        new_balance = update_user_balance(user_id, -bet_amount)
        record_transaction(user_id, -bet_amount, 'poker_bet', 'Poker game bet')
        
        # Create game
        game = create_poker_game(user_id, bet_amount)
        
        return jsonify({
            'success': True,
            'game': game.get_game_state(),
            'new_balance': new_balance
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/poker/finish', methods=['POST'])
def poker_finish():
    """Finish poker game and determine winner"""
    try:
        data = request.get_json()
        user_id = data.get('user_id')
        
        if not user_id:
            return jsonify({'success': False, 'error': 'Missing user_id'}), 400
        
        success = finish_poker_game(user_id)
        if not success:
            return jsonify({'success': False, 'error': 'No active game'}), 400
        
        game = get_poker_game(user_id)
        
        # Handle winnings
        if game.winnings > 0:
            new_balance = update_user_balance(user_id, game.winnings)
            record_transaction(user_id, game.winnings, 'poker_win', f'Poker win: {game.player_hand_rank[1]}')
            record_game(user_id, 'poker', game.bet_amount, game.winnings, game.result)
        else:
            user = get_user(user_id)
            new_balance = user['balance']
            record_game(user_id, 'poker', game.bet_amount, 0, game.result)
        
        result = {
            'success': True,
            'game': game.get_game_state(),
            'new_balance': new_balance
        }
        
        # Clear game
        clear_poker_game(user_id)
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# ==================== LOTTERY API ENDPOINTS ====================
@app.route('/api/lottery/start', methods=['POST'])
def lottery_start():
    """Start a new lottery game"""
    try:
        data = request.get_json()
        user_id = data.get('user_id')
        bet_amount = float(data.get('bet_amount'))
        
        if not all([user_id, bet_amount]):
            return jsonify({'success': False, 'error': 'Missing required fields'}), 400
        
        # Get user and check balance
        user = get_user(user_id)
        if user['balance'] < bet_amount:
            return jsonify({
                'success': False,
                'error': 'Insufficient balance',
                'balance': user['balance']
            }), 400
        
        # Deduct bet from balance
        new_balance = update_user_balance(user_id, -bet_amount)
        record_transaction(user_id, -bet_amount, 'lottery_bet', 'Lottery ticket purchase')
        
        # Create game
        game = create_lottery_game(user_id, bet_amount)
        
        return jsonify({
            'success': True,
            'game': game.get_game_state(),
            'new_balance': new_balance
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/lottery/select', methods=['POST'])
def lottery_select():
    """Select lottery numbers"""
    try:
        data = request.get_json()
        user_id = data.get('user_id')
        numbers = data.get('numbers')
        
        if not all([user_id, numbers]):
            return jsonify({'success': False, 'error': 'Missing required fields'}), 400
        
        success = select_lottery_numbers(user_id, numbers)
        if not success:
            return jsonify({'success': False, 'error': 'Invalid number selection'}), 400
        
        game = get_lottery_game(user_id)
        
        return jsonify({
            'success': True,
            'game': game.get_game_state()
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/lottery/draw', methods=['POST'])
def lottery_draw():
    """Draw winning lottery numbers"""
    try:
        data = request.get_json()
        user_id = data.get('user_id')
        
        if not user_id:
            return jsonify({'success': False, 'error': 'Missing user_id'}), 400
        
        success = draw_lottery_numbers(user_id)
        if not success:
            return jsonify({'success': False, 'error': 'No active game or numbers not selected'}), 400
        
        game = get_lottery_game(user_id)
        
        # Handle winnings
        if game.winnings > 0:
            new_balance = update_user_balance(user_id, game.winnings)
            record_transaction(user_id, game.winnings, 'lottery_win', f'Lottery win: {game.matches} matches')
            record_game(user_id, 'lottery', game.bet_amount, game.winnings, 'win')
        else:
            user = get_user(user_id)
            new_balance = user['balance']
            record_game(user_id, 'lottery', game.bet_amount, 0, 'lose')
        
        result = {
            'success': True,
            'game': game.get_game_state(),
            'new_balance': new_balance
        }
        
        # Clear game
        clear_lottery_game(user_id)
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/static/<path:filename>')
def static_files(filename):
    """Serve static files"""
    return send_from_directory('static', filename)

if __name__ == '__main__':
    port = int(os.getenv('FLASK_PORT', 12000))
    debug = os.getenv('DEBUG', 'False').lower() == 'true'
    
    # Check for SSL certificates
    ssl_context = None
    cert_path = os.getenv('SSL_CERT_PATH')
    key_path = os.getenv('SSL_KEY_PATH')
    
    if cert_path and key_path and os.path.exists(cert_path) and os.path.exists(key_path):
        ssl_context = (cert_path, key_path)
        print(f"Running with SSL using {cert_path} and {key_path}")
    else:
        print("SSL certificates not found, running without SSL")
    
    app.run(host='0.0.0.0', port=port, debug=debug, ssl_context=ssl_context)