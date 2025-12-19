import os
import json
from typing import Dict, List, Any
from datetime import datetime
from collections import defaultdict

RESULTS_FILE = os.path.join(os.path.dirname(__file__), "test_results.json")

def load_results() -> List[Dict[str, Any]]:
    """Load all test results from JSON file"""
    if not os.path.exists(RESULTS_FILE):
        print(f"No results file found at {RESULTS_FILE}")
        return []
    
    with open(RESULTS_FILE, 'r') as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            print("Error reading results file")
            return []

def analyze_by_depth(results: List[Dict[str, Any]]) -> None:
    """Analyze performance by bot depth"""
    depth_stats = defaultdict(lambda: {"wins": 0, "total": 0, "moves": []})
    
    for result in results:
        depth = result.get("bot_depth", 0)
        depth_stats[depth]["total"] += 1
        depth_stats[depth]["moves"].append(result.get("move_count", 0))
        
        if result.get("agent_won", False):
            depth_stats[depth]["wins"] += 1
    
    print("\n" + "="*60)
    print("PERFORMANCE BY MINIMAX DEPTH")
    print("="*60)
    print(f"{'Depth':<10} {'Games':<10} {'Win Rate':<12} {'Avg Moves':<12}")
    print("-" * 60)
    
    for depth in sorted(depth_stats.keys()):
        stats = depth_stats[depth]
        win_rate = (stats["wins"] / stats["total"]) * 100 if stats["total"] > 0 else 0
        avg_moves = sum(stats["moves"]) / len(stats["moves"]) if stats["moves"] else 0
        print(f"{depth:<10} {stats['total']:<10} {win_rate:>6.1f}%      {avg_moves:>6.1f}")
    
    print("="*60)

def analyze_by_strategy(results: List[Dict[str, Any]]) -> None:
    """Analyze performance by bot strategy"""
    strat_stats = defaultdict(lambda: {"wins": 0, "total": 0})
    
    for result in results:
        strategy = result.get("bot_strategy", "unknown")
        strat_stats[strategy]["total"] += 1
        
        if result.get("agent_won", False):
            strat_stats[strategy]["wins"] += 1
    
    print("\n" + "="*60)
    print("PERFORMANCE BY STRATEGY")
    print("="*60)
    print(f"{'Strategy':<15} {'Games':<10} {'Win Rate':<12}")
    print("-" * 60)
    
    for strategy in sorted(strat_stats.keys()):
        stats = strat_stats[strategy]
        win_rate = (stats["wins"] / stats["total"]) * 100 if stats["total"] > 0 else 0
        print(f"{strategy:<15} {stats['total']:<10} {win_rate:>6.1f}%")
    
    print("="*60)

def display_recent_games(results: List[Dict[str, Any]], n: int = 10) -> None:
    """Display recent N games"""
    print(f"\n" + "="*60)
    print(f"LAST {min(n, len(results))} GAMES")
    print("="*60)
    
    for i, result in enumerate(results[-n:], 1):
        agent_p = result.get("agent_player", 0)
        depth = result.get("bot_depth", 0)
        strategy = result.get("bot_strategy", "unknown")
        winner = result.get("winner", -1)
        move_count = result.get("move_count", 0)
        
        agent_won = "✓ WIN" if result.get("agent_won", False) else "✗ LOSS"
        if winner == 2:
            agent_won = "~ DRAW"
        
        print(f"{i:2}. Agent(P{agent_p+1}) vs Bot(depth={depth}, {strategy}): "
              f"{agent_won} | Moves: {move_count}")
    
    print("="*60)

def calculate_overall_stats(results: List[Dict[str, Any]]) -> None:
    """Calculate and display overall statistics"""
    if not results:
        print("\nNo results to analyze!")
        return
    
    total_games = len(results)
    total_wins = sum(1 for r in results if r.get("agent_won", False))
    total_draws = sum(1 for r in results if r.get("winner", -1) == 2)
    total_losses = total_games - total_wins - total_draws
    
    win_rate = (total_wins / total_games) * 100
    
    all_moves = [r.get("move_count", 0) for r in results if "move_count" in r]
    avg_moves = sum(all_moves) / len(all_moves) if all_moves else 0
    
    print("\n" + "="*60)
    print("OVERALL STATISTICS")
    print("="*60)
    print(f"Total Games:    {total_games}")
    print(f"Wins:           {total_wins} ({win_rate:.1f}%)")
    print(f"Losses:         {total_losses}")
    print(f"Draws:          {total_draws}")
    print(f"Avg Game Length: {avg_moves:.1f} moves")
    print("="*60)

def main():
    print("\n" + "🎯 " * 20)
    print(" " * 20 + "KALAHA MODEL EVALUATION RESULTS")
    print("🎯 " * 20)
    
    results = load_results()
    
    if not results:
        print("\n❌ No test results found. Run benchmark_bot.py or evaluate_all.py first!")
        return
    
    calculate_overall_stats(results)
    analyze_by_depth(results)
    analyze_by_strategy(results)
    display_recent_games(results, n=15)
    
    print("\n✅ Analysis complete!\n")

if __name__ == "__main__":
    main()
