import os
import sys
import json
import numpy as np
from datetime import datetime
from typing import Dict, Any, Optional

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from kalaha.game_logic import initial_state, apply_move, is_terminal, cleanup_board
from kalaha.ai_engine import get_best_move
from sb3_contrib import MaskablePPO # type: ignore

RESULTS_FILE = os.path.join(os.path.dirname(__file__), "test_results.json")

def load_rl_agent(model_path: str = "../models/kalaha_latest.zip") -> Optional[MaskablePPO]:
    """Load the trained RL agent"""
    full_path = os.path.join(os.path.dirname(__file__), model_path)
    if os.path.exists(full_path):
        return MaskablePPO.load(full_path)
    print(f"Model not found at {full_path}")
    return None

def get_rl_move(model: MaskablePPO, board: list, player: int) -> int:
    """Get move from RL agent"""
    obs = np.zeros(15, dtype=np.int32)
    if player == 0:
        obs[0:6] = board[0:6]
        obs[6] = board[6]
        obs[7:13] = board[7:13]
        obs[13] = board[13]
        obs[14] = 0
    else:
        obs[0:6] = board[7:13]
        obs[6] = board[13]
        obs[7:13] = board[0:6]
        obs[13] = board[6]
        obs[14] = 1
    
    mask = [False] * 6
    pits = list(range(0, 6)) if player == 0 else list(range(7, 13))
    for i, p in enumerate(pits):
        if board[p] > 0:
            mask[i] = True
    
    action, _ = model.predict(obs, action_masks=mask, deterministic=True)
    return int(action) if player == 0 else int(action + 7)

def play_game(agent_player: int, bot_depth: int, bot_strategy: str = 'balanced') -> Dict[str, Any]:
    """
    Play a single game: RL Agent vs Minimax Bot
    
    Args:
        agent_player: 0 if agent is P1, 1 if agent is P2
        bot_depth: Minimax search depth
        bot_strategy: Bot strategy (basic, balanced, aggressive, defensive)
    
    Returns:
        Game result dictionary
    """
    model = load_rl_agent()
    if not model:
        return {"error": "Model not found"}
    
    board = initial_state()
    current_player = 0
    move_count = 0
    
    while not is_terminal(board):
        if current_player == agent_player:
            # RL Agent move
            move = get_rl_move(model, board, current_player)
        else:
            # Bot move
            move, _ = get_best_move(board, current_player, depth=bot_depth, strategy=bot_strategy)
            if move is None:
                break
        
        board, extra = apply_move(board, move, current_player)
        move_count += 1
        
        if not extra:
            current_player = 1 - current_player
    
    # Determine winner
    board = cleanup_board(board)
    p1_score = board[6]
    p2_score = board[13]
    
    if p1_score > p2_score:
        winner = 0
    elif p2_score > p1_score:
        winner = 1
    else:
        winner = 2  # Draw
    
    return {
        "agent_player": agent_player,
        "bot_depth": bot_depth,
        "bot_strategy": bot_strategy,
        "winner": winner,
        "agent_won": winner == agent_player,
        "p1_score": p1_score,
        "p2_score": p2_score,
        "move_count": move_count,
        "timestamp": datetime.now().isoformat()
    }

def save_result(result: Dict[str, Any]) -> None:
    """Append result to JSON file"""
    results = []
    if os.path.exists(RESULTS_FILE):
        with open(RESULTS_FILE, 'r') as f:
            try:
                results = json.load(f)
            except json.JSONDecodeError:
                results = []
    
    results.append(result)
    
    with open(RESULTS_FILE, 'w') as f:
        json.dump(results, f, indent=2)

def benchmark_single(agent_player: int = 0, bot_depth: int = 6, bot_strategy: str = 'balanced', num_games: int = 100) -> Dict[str, Any]:
    """
    Benchmark RL agent vs a specific bot configuration
    
    Args:
        agent_player: 0 or 1 (which player is the agent)
        bot_depth: Minimax depth
        bot_strategy: Bot strategy
        num_games: Number of games to play
    
    Returns:
        Summary statistics
    """
    print(f"\n{'='*60}")
    print(f"Benchmarking: Agent (P{agent_player+1}) vs Minimax({bot_depth}, {bot_strategy})")
    print(f"Games: {num_games}")
    print(f"{'='*60}\n")
    
    wins = 0
    losses = 0
    draws = 0
    total_moves = 0
    
    for i in range(num_games):
        result = play_game(agent_player, bot_depth, bot_strategy)
        
        if "error" in result:
            print(f"Error: {result['error']}")
            return {}
        
        save_result(result)
        
        if result["agent_won"]:
            wins += 1
        elif result["winner"] == 2:
            draws += 1
        else:
            losses += 1
        
        total_moves += result["move_count"]
        
        # Progress indicator
        if (i + 1) % 10 == 0:
            current_wr = (wins / (i + 1)) * 100
            print(f"Progress: {i+1}/{num_games} | Win Rate: {current_wr:.1f}%")
    
    win_rate = (wins / num_games) * 100
    avg_moves = total_moves / num_games
    
    summary = {
        "configuration": {
            "agent_player": agent_player,
            "bot_depth": bot_depth,
            "bot_strategy": bot_strategy,
            "num_games": num_games
        },
        "results": {
            "wins": wins,
            "losses": losses,
            "draws": draws,
            "win_rate": win_rate,
            "avg_moves": avg_moves
        },
        "timestamp": datetime.now().isoformat()
    }
    
    print(f"\n{'='*60}")
    print(f"Results:")
    print(f"  Wins: {wins} ({win_rate:.1f}%)")
    print(f"  Losses: {losses}")
    print(f"  Draws: {draws}")
    print(f"  Avg Moves: {avg_moves:.1f}")
    print(f"{'='*60}\n")
    
    return summary

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Benchmark RL agent vs Minimax bot")
    parser.add_argument("--agent-player", type=int, default=0, choices=[0, 1],
                       help="Which player is the agent (0 or 1)")
    parser.add_argument("--depth", type=int, default=6,
                       help="Minimax search depth (1-20)")
    parser.add_argument("--strategy", type=str, default="balanced",
                       choices=["basic", "balanced", "aggressive", "defensive"],
                       help="Bot strategy")
    parser.add_argument("--games", type=int, default=100,
                       help="Number of games to play")
    
    args = parser.parse_args()
    
    benchmark_single(
        agent_player=args.agent_player,
        bot_depth=args.depth,
        bot_strategy=args.strategy,
        num_games=args.games
    )
