# Model Testing Suite

This folder contains scripts for evaluating the trained RL agent's performance.

## Files

- **`training_directives.md`**: Guidelines on when to stop training and how to monitor performance
- **`benchmark_bot.py`**: Test agent against a specific bot configuration
- **`evaluate_all.py`**: Comprehensive evaluation against all difficulty levels
- **`view_results.py`**: Analyze and display test results
- **`test_results.json`**: Unified results database (auto-generated)

## Quick Start

### 1. Single Benchmark
Test against a specific difficulty:

```bash
# Default: Agent as P1 vs Minimax(6, balanced), 100 games
python model_testing/benchmark_bot.py

# Custom configuration
python model_testing/benchmark_bot.py --depth 10 --strategy aggressive --games 200

# Agent as Player 2
python model_testing/benchmark_bot.py --agent-player 1 --depth 8
```

### 2. Full Evaluation
Test against all difficulty levels:

```bash
# 50 games per difficulty (recommended)
python model_testing/evaluate_all.py

# Quick test (10 games per difficulty)
python model_testing/evaluate_all.py --games 10

# Agent plays as Player 2
python model_testing/evaluate_all.py --agent-p2
```

### 3. View Results
Analyze all test results:

```bash
python model_testing/view_results.py
```

## Results File Format

Each game result in `test_results.json` contains:

```json
{
  "agent_player": 0,
  "bot_depth": 6,
  "bot_strategy": "balanced",
  "winner": 0,
  "agent_won": true,
  "p1_score": 28,
  "p2_score": 20,
  "move_count": 42,
  "timestamp": "2025-12-19T20:15:30.123456"
}
```

## Performance Benchmarks

| Difficulty | Depth | Strategy | Target Win Rate |
|------------|-------|----------|----------------|
| Random | 1 | basic | 95%+ |
| Beginner | 2 | basic | 90%+ |
| Easy | 4 | balanced | 80%+ |
| Medium | 6 | balanced | 70%+ |
| Hard | 10 | balanced | 55%+ |
| Hell | 14 | aggressive | 45%+ |

## Workflow

1. **Train model**: `python kalaha/ai_training/train_v2.py`
2. **Quick test**: `python model_testing/benchmark_bot.py --depth 6 --games 50`
3. **Full evaluation**: `python model_testing/evaluate_all.py`
4. **Review**: `python model_testing/view_results.py`
5. **Decide**: Continue training or stop based on performance

## Tips

- Run `evaluate_all.py` every 500k training steps
- Save best checkpoint when win rate peaks
- Compare results over time using `view_results.py`
- Track performance in TensorBoard alongside these tests
