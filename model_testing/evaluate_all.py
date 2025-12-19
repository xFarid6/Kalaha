import os
import sys
from typing import List, Dict, Any
from benchmark_bot import benchmark_single

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Test configurations
DIFFICULTY_CONFIGS = [
    {"name": "Random Baseline", "depth": 1, "strategy": "basic"},
    {"name": "Beginner", "depth": 2, "strategy": "basic"},
    {"name": "Easy", "depth": 4, "strategy": "balanced"},
    {"name": "Medium", "depth": 6, "strategy": "balanced"},
    # {"name": "Hard", "depth": 10, "strategy": "balanced"},
    # {"name": "Hell", "depth": 14, "strategy": "aggressive"},
    # {"name": "Endgame Master", "depth": 8, "strategy": "defensive"},
]

def evaluate_all_difficulties(num_games: int = 50, agent_as_p1: bool = True) -> List[Dict[str, Any]]:
    """
    Evaluate RL agent against all difficulty levels
    
    Args:
        num_games: Number of games per difficulty
        agent_as_p1: If True, agent plays as Player 1
    
    Returns:
        List of benchmark results
    """
    results = []
    agent_player = 0 if agent_as_p1 else 1
    
    print("\n" + "="*70)
    print(f"FULL EVALUATION: RL Agent as Player {agent_player + 1}")
    print(f"Testing against {len(DIFFICULTY_CONFIGS)} difficulty levels")
    print(f"{num_games} games per difficulty")
    print("="*70)
    
    for i, config in enumerate(DIFFICULTY_CONFIGS, 1):
        print(f"\n[{i}/{len(DIFFICULTY_CONFIGS)}] Testing: {config['name']}")
        print("-" * 70)
        
        result = benchmark_single(
            agent_player=agent_player,
            bot_depth=config['depth'],
            bot_strategy=config['strategy'],
            num_games=num_games
        )
        
        if result:
            result['difficulty_name'] = config['name']
            results.append(result)
    
    # Print summary
    print("\n" + "="*70)
    print("EVALUATION SUMMARY")
    print("="*70)
    print(f"{'Difficulty':<20} {'Depth':<8} {'Strategy':<12} {'Win Rate':<10} {'Avg Moves':<10}")
    print("-" * 70)
    
    for res in results:
        conf = res['configuration']
        stats = res['results']
        print(f"{res['difficulty_name']:<20} {conf['bot_depth']:<8} "
              f"{conf['bot_strategy']:<12} {stats['win_rate']:>6.1f}%    "
              f"{stats['avg_moves']:>6.1f}")
    
    print("="*70)
    
    # Calculate overall performance
    if results:
        avg_win_rate = sum(r['results']['win_rate'] for r in results) / len(results)
        print(f"\nOverall Average Win Rate: {avg_win_rate:.1f}%")
        
        # Performance classification
        if avg_win_rate >= 80:
            rating = "🏆 EXCELLENT - Superhuman performance!"
        elif avg_win_rate >= 70:
            rating = "⭐ VERY GOOD - Strong competitive play"
        elif avg_win_rate >= 60:
            rating = "✓ GOOD - Competent player"
        elif avg_win_rate >= 50:
            rating = "~ AVERAGE - Needs improvement"
        else:
            rating = "✗ POOR - Requires more training"
        
        print(f"Performance Rating: {rating}\n")
    
    return results

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Evaluate RL agent against all difficulties")
    parser.add_argument("--games", type=int, default=50,
                       help="Number of games per difficulty (default: 50)")
    parser.add_argument("--agent-p2", action="store_true",
                       help="Agent plays as Player 2 (default: Player 1)")
    
    args = parser.parse_args()
    
    evaluate_all_difficulties(
        num_games=args.games,
        agent_as_p1=not args.agent_p2
    )
