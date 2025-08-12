"""
Leaderboard functionality for ExoWin games
"""
import asyncio
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from src.database.db import db, games_collection, users_collection
from src.utils.logger import db_logger

async def get_game_leaderboard(game_type: str, limit: int = 10, period: str = "all_time") -> List[Dict[str, Any]]:
    """
    Get leaderboard for a specific game type
    
    Args:
        game_type: Type of game (dice, darts, slots, etc.)
        limit: Number of top players to return
        period: Time period for leaderboard ("daily", "weekly", "monthly", "all_time")
    
    Returns:
        List of top players with their stats
    """
    try:
        # Set time filter based on period
        time_filter = {}
        if period == "daily":
            time_filter = {"timestamp": {"$gte": datetime.now() - timedelta(days=1)}}
        elif period == "weekly":
            time_filter = {"timestamp": {"$gte": datetime.now() - timedelta(weeks=1)}}
        elif period == "monthly":
            time_filter = {"timestamp": {"$gte": datetime.now() - timedelta(days=30)}}
        
        # Build the aggregation pipeline
        pipeline = [
            {"$match": {"game_type": game_type, **time_filter}},
            {"$group": {
                "_id": "$user_id",
                "total_bets": {"$sum": 1},
                "total_bet_amount": {"$sum": "$bet_amount"},
                "total_winnings": {"$sum": "$winnings"},
                "profit": {"$sum": {"$subtract": ["$winnings", "$bet_amount"]}},
                "wins": {"$sum": {"$cond": [{"$eq": ["$result", "win"]}, 1, 0]}},
                "losses": {"$sum": {"$cond": [{"$eq": ["$result", "loss"]}, 1, 0]}}
            }},
            {"$sort": {"profit": -1}},
            {"$limit": limit},
            {"$lookup": {
                "from": "users",
                "localField": "_id",
                "foreignField": "user_id",
                "as": "user_info"
            }},
            {"$unwind": "$user_info"},
            {"$project": {
                "user_id": "$_id",
                "username": {"$ifNull": ["$user_info.username", "Anonymous"]},
                "first_name": {"$ifNull": ["$user_info.first_name", ""]},
                "last_name": {"$ifNull": ["$user_info.last_name", ""]},
                "total_bets": 1,
                "total_bet_amount": 1,
                "total_winnings": 1,
                "profit": 1,
                "wins": 1,
                "losses": 1,
                "win_rate": {
                    "$cond": [
                        {"$eq": [{"$add": ["$wins", "$losses"]}, 0]},
                        0,
                        {"$multiply": [
                            {"$divide": ["$wins", {"$add": ["$wins", "$losses"]}]},
                            100
                        ]}
                    ]
                }
            }}
        ]
        
        # Execute the aggregation
        leaderboard = await games_collection.aggregate(pipeline).to_list(length=limit)
        
        # Format the results
        for entry in leaderboard:
            entry["display_name"] = entry.get("username") or f"{entry.get('first_name', '')} {entry.get('last_name', '')}".strip() or f"User {entry['user_id']}"
            
            # Round numeric values
            entry["win_rate"] = round(entry["win_rate"], 1)
            entry["profit"] = round(entry["profit"], 2)
            entry["total_winnings"] = round(entry["total_winnings"], 2)
            entry["total_bet_amount"] = round(entry["total_bet_amount"], 2)
        
        return leaderboard
    
    except Exception as e:
        db_logger.error(f"Error getting leaderboard for {game_type}: {e}")
        return []

async def get_overall_leaderboard(limit: int = 10, period: str = "all_time") -> List[Dict[str, Any]]:
    """
    Get overall leaderboard across all games
    
    Args:
        limit: Number of top players to return
        period: Time period for leaderboard ("daily", "weekly", "monthly", "all_time")
    
    Returns:
        List of top players with their stats
    """
    try:
        # Set time filter based on period
        time_filter = {}
        if period == "daily":
            time_filter = {"timestamp": {"$gte": datetime.now() - timedelta(days=1)}}
        elif period == "weekly":
            time_filter = {"timestamp": {"$gte": datetime.now() - timedelta(weeks=1)}}
        elif period == "monthly":
            time_filter = {"timestamp": {"$gte": datetime.now() - timedelta(days=30)}}
        
        # Build the aggregation pipeline
        pipeline = [
            {"$match": time_filter},
            {"$group": {
                "_id": "$user_id",
                "total_bets": {"$sum": 1},
                "total_bet_amount": {"$sum": "$bet_amount"},
                "total_winnings": {"$sum": "$winnings"},
                "profit": {"$sum": {"$subtract": ["$winnings", "$bet_amount"]}},
                "wins": {"$sum": {"$cond": [{"$eq": ["$result", "win"]}, 1, 0]}},
                "losses": {"$sum": {"$cond": [{"$eq": ["$result", "loss"]}, 1, 0]}}
            }},
            {"$sort": {"profit": -1}},
            {"$limit": limit},
            {"$lookup": {
                "from": "users",
                "localField": "_id",
                "foreignField": "user_id",
                "as": "user_info"
            }},
            {"$unwind": "$user_info"},
            {"$project": {
                "user_id": "$_id",
                "username": {"$ifNull": ["$user_info.username", "Anonymous"]},
                "first_name": {"$ifNull": ["$user_info.first_name", ""]},
                "last_name": {"$ifNull": ["$user_info.last_name", ""]},
                "total_bets": 1,
                "total_bet_amount": 1,
                "total_winnings": 1,
                "profit": 1,
                "wins": 1,
                "losses": 1,
                "win_rate": {
                    "$cond": [
                        {"$eq": [{"$add": ["$wins", "$losses"]}, 0]},
                        0,
                        {"$multiply": [
                            {"$divide": ["$wins", {"$add": ["$wins", "$losses"]}]},
                            100
                        ]}
                    ]
                }
            }}
        ]
        
        # Execute the aggregation
        leaderboard = await games_collection.aggregate(pipeline).to_list(length=limit)
        
        # Format the results
        for entry in leaderboard:
            entry["display_name"] = entry.get("username") or f"{entry.get('first_name', '')} {entry.get('last_name', '')}".strip() or f"User {entry['user_id']}"
            
            # Round numeric values
            entry["win_rate"] = round(entry["win_rate"], 1)
            entry["profit"] = round(entry["profit"], 2)
            entry["total_winnings"] = round(entry["total_winnings"], 2)
            entry["total_bet_amount"] = round(entry["total_bet_amount"], 2)
        
        return leaderboard
    
    except Exception as e:
        db_logger.error(f"Error getting overall leaderboard: {e}")
        return []

async def get_user_ranking(user_id: int, game_type: Optional[str] = None, period: str = "all_time") -> Dict[str, Any]:
    """
    Get a user's ranking in the leaderboard
    
    Args:
        user_id: User ID to get ranking for
        game_type: Type of game (dice, darts, slots, etc.) or None for overall ranking
        period: Time period for leaderboard ("daily", "weekly", "monthly", "all_time")
    
    Returns:
        Dictionary with user's ranking and stats
    """
    try:
        # Set time filter based on period
        time_filter = {}
        if period == "daily":
            time_filter = {"timestamp": {"$gte": datetime.now() - timedelta(days=1)}}
        elif period == "weekly":
            time_filter = {"timestamp": {"$gte": datetime.now() - timedelta(weeks=1)}}
        elif period == "monthly":
            time_filter = {"timestamp": {"$gte": datetime.now() - timedelta(days=30)}}
        
        # Add game type filter if specified
        game_filter = {}
        if game_type:
            game_filter = {"game_type": game_type}
        
        # Get user's stats
        user_stats_pipeline = [
            {"$match": {"user_id": user_id, **game_filter, **time_filter}},
            {"$group": {
                "_id": "$user_id",
                "total_bets": {"$sum": 1},
                "total_bet_amount": {"$sum": "$bet_amount"},
                "total_winnings": {"$sum": "$winnings"},
                "profit": {"$sum": {"$subtract": ["$winnings", "$bet_amount"]}},
                "wins": {"$sum": {"$cond": [{"$eq": ["$result", "win"]}, 1, 0]}},
                "losses": {"$sum": {"$cond": [{"$eq": ["$result", "loss"]}, 1, 0]}}
            }}
        ]
        
        user_stats_result = await games_collection.aggregate(user_stats_pipeline).to_list(length=1)
        
        if not user_stats_result:
            return {
                "user_id": user_id,
                "rank": None,
                "total_bets": 0,
                "total_bet_amount": 0,
                "total_winnings": 0,
                "profit": 0,
                "wins": 0,
                "losses": 0,
                "win_rate": 0
            }
        
        user_stats = user_stats_result[0]
        
        # Calculate user's rank
        rank_pipeline = [
            {"$match": {**game_filter, **time_filter}},
            {"$group": {
                "_id": "$user_id",
                "profit": {"$sum": {"$subtract": ["$winnings", "$bet_amount"]}}
            }},
            {"$sort": {"profit": -1}}
        ]
        
        rank_results = await games_collection.aggregate(rank_pipeline).to_list(length=None)
        
        # Find user's position in the sorted list
        user_rank = None
        for i, entry in enumerate(rank_results):
            if entry["_id"] == user_id:
                user_rank = i + 1
                break
        
        # Get user info
        user_info = await users_collection.find_one({"user_id": user_id})
        
        # Calculate win rate
        total_games = user_stats["wins"] + user_stats["losses"]
        win_rate = (user_stats["wins"] / total_games * 100) if total_games > 0 else 0
        
        return {
            "user_id": user_id,
            "username": user_info.get("username") if user_info else None,
            "first_name": user_info.get("first_name") if user_info else None,
            "last_name": user_info.get("last_name") if user_info else None,
            "display_name": user_info.get("username") or f"{user_info.get('first_name', '')} {user_info.get('last_name', '')}".strip() or f"User {user_id}" if user_info else f"User {user_id}",
            "rank": user_rank,
            "total_bets": user_stats["total_bets"],
            "total_bet_amount": round(user_stats["total_bet_amount"], 2),
            "total_winnings": round(user_stats["total_winnings"], 2),
            "profit": round(user_stats["profit"], 2),
            "wins": user_stats["wins"],
            "losses": user_stats["losses"],
            "win_rate": round(win_rate, 1)
        }
    
    except Exception as e:
        db_logger.error(f"Error getting user ranking for user {user_id}: {e}")
        return {
            "user_id": user_id,
            "rank": None,
            "error": str(e)
        }