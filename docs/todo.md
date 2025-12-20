# Mini Games Gallery - Project To-Do List

## Project Overview
This project has evolved from a Kalaha-only web game into a comprehensive **Mini Games Gallery** - a collection of classic games reimagined with modern AI and beautiful web interfaces. The project supports both Python implementations (for prototyping and AI development) and JavaScript versions (for web deployment via GitHub Pages).

## Major Goals

### ✅ Phase 1: Project Restructure (COMPLETED)
- [x] Rename `kalaha-web` to `mini-games-web`
- [x] Create organized folder structure (`games/js/`, `games/python/`)
- [x] Move Kalaha files to proper locations
- [x] Create modern homepage with game gallery
- [x] Add purple accents to design theme
- [x] Ensure scalability for future expansion

### 🚧 Phase 2: Pong Development (IN PROGRESS)
- [ ] Implement Python version with pygame
  - [ ] OOP architecture with scene stack navigation
  - [ ] Generate assets (paddles, ball, background)
  - [ ] Add ball trail effect
  - [ ] AI opponent
- [ ] Translate to JavaScript for web
- [ ] Add to game gallery with proper thumbnail

### 📋 Phase 3: Gallery Expansion
- [ ] Add "Coming Soon" cards for all planned games
- [ ] Organize homepage by game categories
- [ ] Generate thumbnails for each game
- [ ] Implement category filtering/navigation

### 🎯 Phase 4: Multi-Game Development
Continue implementing games from the comprehensive list below, prioritizing:
- Deterministic turn-based games (perfect for MCTS/Minimax)
- Games with perfect information and strategic depth
- Simple but engaging single-player games

## Comprehensive Game List

### 🎲 Deterministic Turn-Based Games (Perfect for MCTS/Minimax)
1. **Tris (Tic-Tac-Toe)** - Classic 3x3 grid game
2. **Connect-4** - Drop pieces to connect four in a row
3. **Gomoku** - 5 in a row on larger board
4. **Nim** - Mathematical strategy game
5. **Wythoff Nim** - Variant of Nim with two piles
6. **Misère Nim** - Nim variant where losing is winning
7. **Take-the-Last** - Remove 1-3 objects per turn
8. **Kayles** - Simplified bowling pin game
9. **Othello / Reversi** - Flip opponent's pieces
10. **Mancala / Kalaha** - ✅ COMPLETED (ancient seed-sowing game)

### 🧩 Perfect Information Strategy Games
11. **Hex** - Connect opposite sides on hexagonal board
12. **Isolation** - Block opponent's movement
13. **Breakthrough** - Race pawns to opposite side
14. **Amazons** - Chess-like game with blocking
15. **Mini-Checkers** - Simplified checkers on smaller board
16. **Mini-Chess** - 5x5 or 6x6 chess variant

### 🎰 Stochastic Games (Great for Reinforcement Learning)
17. **Pig** - Dice game with push-your-luck mechanic
18. **Blackjack** - Single-deck card game
19. **Kuhn Poker** - Simplified poker variant
20. **Liar's Dice** - Bluffing dice game (simplified)
21. **Yahtzee** - Dice combination game (reduced version)

### 🎮 Single-Player / Planning Games (Pure RL)
22. **2048** - Sliding number puzzle
23. **Snake** - Classic arcade game
24. **Gridworld** - Navigate grid with obstacles
25. **Sokoban** - Push boxes to targets (small levels)
26. **Frozen Lake** - Custom ice-sliding puzzle
27. **Taxi** - Classic OpenAI Gym environment

### 🔄 Hybrid Strategy Games
28. **Rock-Paper-Scissors** - Meta-strategic patterns
29. **Prisoner's Dilemma** - Iterative cooperation game
30. **Battleship** - Naval combat (reduced board)

### 🕹️ Arcade Classics
31. **Pong** - 🚧 IN PROGRESS (paddle ball game)
32. **Breakout** - Ball and paddle brick breaker
33. **Space Invaders** - Classic shooter (simplified)
34. **Tetris** - Falling block puzzle

## High Priority Tasks

### Kalaha (Original Project)
- [ ] Convert PyTorch model to TensorFlow.js
  - [ ] Install: `pip install tensorflowjs onnx onnx-tf onnxscript`
  - [ ] Convert PyTorch → ONNX → TF.js
  - [ ] Test model loading in browser
  - [ ] Add model switching UI (Minimax vs NN)
- [ ] Deploy to GitHub Pages
  - [ ] Create repository
  - [ ] Configure Pages
  - [ ] Optimize assets
- [ ] Mobile testing (iOS/Android)

### Documentation
- [x] Update todo.md with new multi-game structure
- [ ] Create game development guide
- [ ] Document OOP patterns for Python games
- [ ] Document JS translation workflow
- [ ] Add README to each game folder

## Medium Priority

### Performance & Testing
- [ ] Profile AI engine performance
- [ ] Optimize Canvas rendering (requestAnimationFrame)
- [ ] Add Web Workers for AI computation
- [ ] Unit tests for each game's logic
- [ ] Cross-browser testing
- [ ] Accessibility audit (WCAG)

### UI/UX Improvements
- [ ] Add sound effects library
- [ ] Background music (toggleable)
- [ ] Touch interactions for mobile
- [ ] Dark/light theme toggle
- [ ] Win animations (confetti, etc.)
- [ ] Game statistics dashboard

## Low Priority

### Advanced Features
- [ ] Tournament mode for competitive games
- [ ] AI vs AI spectator mode
- [ ] Game analysis/replay mode
- [ ] Export saved games
- [ ] Leaderboards (privacy-friendly)
- [ ] Multiplayer via WebRTC (future)

### Analytics
- [ ] Privacy-friendly analytics
- [ ] Track popular games
- [ ] AI performance metrics
- [ ] User engagement data

## Completed ✅

### Kalaha Web Implementation
- [x] Port game logic to JavaScript
- [x] Create responsive Canvas UI
- [x] Port Minimax/Alpha-Beta AI
- [x] Add difficulty levels
- [x] Create TensorFlow.js model interface
- [x] Browser testing (human vs human)
- [x] Browser testing (human vs AI)
- [x] Add game state save/load
- [x] Add undo/redo functionality
- [x] Add statistics tracking

### Project Structure
- [x] Rename project to Mini Games Gallery
- [x] Create multi-game folder structure
- [x] Design modern homepage with game grid
- [x] Add purple/gold color scheme
- [x] Create Kalaha game page
- [x] Add responsive design
- [x] Generate game thumbnails

## Development Workflow

### For Each New Game:
1. **Python Implementation**
   - Create in `games/python/[game-name]/`
   - Use OOP with scene stack pattern
   - Develop AI opponent
   - Test and refine

2. **JavaScript Translation**
   - Port to `games/js/[game-name]/`
   - Create Canvas-based UI
   - Optimize for web performance
   - Ensure mobile compatibility

3. **Integration**
   - Generate thumbnail image
   - Add card to homepage gallery
   - Update category organization
   - Write game documentation

4. **Testing & Deployment**
   - Browser testing
   - Mobile testing
   - Performance optimization
   - Deploy updates to GitHub Pages
