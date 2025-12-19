# Future Projects: Games for AI Training

This document lists 30 games with simple logic but interesting AI training potential (RL, MCTS, self-play). Ordered roughly from simplest to most complex, while remaining easy to implement.

---

## Deterministic Turn-Based Games
*Perfect for MCTS / Minimax*

1. **Tris (Tic-Tac-Toe)**
   - Classic 3×3 grid
   - Solved game, perfect for learning MCTS basics
   
2. **Connect-4**
   - 6×7 grid
   - More complex than Tris, still tractable
   
3. **Gomoku (5 in a row)**
   - 15×15 board
   - Larger state space, good for neural networks
   
4. **Nim**
   - Remove objects from piles
   - Mathematical game theory classic
   
5. **Wythoff Nim**
   - Two-pile variant of Nim
   - Interesting optimal strategy
   
6. **Misère Nim**
   - Reverse objective (lose to win)
   - Tests AI's strategic flexibility
   
7. **Take-the-Last (1–3 objects)**
   - Simple subtraction game
   - Fast training, perfect for RL intro
   
8. **Kayles (simplified)**
   - Combinatorial game
   - Clear winning/losing positions
   
9. **Othello / Reversi**
   - 8×8 board with piece flipping
   - Classic AI benchmark
   
10. **Mancala / Kalaha** ✅ **(Current Project)**
    - Seed-sowing game
    - Complex endgames, perfect for DB + RL

---

## Perfect Information + Deep Strategy

11. **Hex** (small board)
    - Connection game
    - Proven to be PSPACE-complete
    
12. **Isolation**
    - Move blocking game
    - Good for minimax with evaluation functions
    
13. **Breakthrough**
    - Simplified chess-like game
    - Fast games, deep tactics
    
14. **Amazons** (reduced version)
    - Queen movement + blocking
    - Rich strategic depth
    
15. **Mini-Checkers**
    - 8×8 or smaller board
    - Forced captures add complexity
    
16. **Mini-Chess** (5×5 or 6×6)
    - Reduced chess variant
    - Faster games, full chess tactics

---

## Stochastic / Random Elements
*Interesting for RL*

17. **Pig** (dice game)
    - Risk-reward decision
    - Probability-based strategy
    
18. **Blackjack** (single-deck)
    - Card counting + basic strategy
    - Classic RL benchmark
    
19. **Kuhn Poker**
    - Minimal poker variant (3 cards)
    - Game theory equilibrium
    
20. **Liar's Dice** (simplified)
    - Bluffing + probability
    - Imperfect information
    
21. **Yahtzee** (reduced version)
    - Dice combinations
    - Planning + randomness

---

## Single-Player / Planning
*Optimal for pure RL*

22. **2048**
    - Tile merging puzzle
    - Clear reward signal
    
23. **Snake**
    - Grid navigation
    - Survival + growth objective
    
24. **Gridworld with obstacles**
    - Path planning
    - Customizable difficulty
    
25. **Sokoban** (small levels)
    - Box pushing puzzle
    - Backtracking required
    
26. **Frozen Lake** (custom)
    - Stochastic movement
    - Classic OpenAI Gym env
    
27. **Taxi** (classic Gym)
    - Pickup + dropoff task
    - Multi-objective planning

---

## Hybrid / Meta-Strategic

28. **Rock-Paper-Scissors**
    - Meta-game strategy
    - Mixed Nash equilibrium
    
29. **Prisoner's Dilemma** (iterated)
    - Cooperation vs defection
    - Evolutionary strategies
    
30. **Battleship** (reduced version)
    - Search + probability
    - Opponent modeling

---

## Selection Criteria

A game is **perfect for AI training** if it is:

✅ **Fast to simulate** (< 1ms per game)  
✅ **Easy to implement** (< 500 lines of code)  
✅ **Repeatable** (millions of episodes)  
✅ **Clear objective** (win/lose/score)

👉 Even "trivial" games (for humans) can be **excellent AI testbeds** due to:
- Controlled complexity
- Fast iteration
- Easy debugging
- Reproducible results

---

## Implementation Priority for This Project

After Kalaha, consider:

### Short-term (1-2 weeks each)
1. **Connect-4** → Practice larger state space
2. **2048** → Pure RL without opponent
3. **Hex (7×7)** → MCTS + NN combination

### Medium-term (1 month each)
4. **Mini-Chess** → Complex tactics
5. **Blackjack** → Stochastic environment
6. **Gomoku** → Larger board, opening book

### Long-term (2+ months)
7. **AlphaZero framework** → Generalized for multiple games
8. **Multi-game agent** → Transfer learning across games

---

## Resources

- **OpenAI Gym**: Pre-built environments
- **PettingZoo**: Multi-agent environments
- **MuZero Paper**: General game-playing without rules
- **AlphaZero Paper**: MCTS + deep RL

---

## Why These Games Matter

Training AI on simple games teaches:
- **MCTS implementation** (tree search)
- **Self-play dynamics** (opponent modeling)
- **Neural network architecture** (policy/value heads)
- **Hyperparameter tuning** (learning rate, exploration)
- **Evaluation metrics** (Elo rating, win rate)

→ Skills transfer to **real-world RL problems** (robotics, optimization, control).
