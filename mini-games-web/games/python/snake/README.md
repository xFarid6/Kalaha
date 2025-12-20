# Snake - Python Version

A classic Snake game implemented in Python using Pygame with modern effects and clean OOP architecture.

## Features

- **Modular OOP Design**: Separate files for constants, entities, scenes, game logic, and main
- **Scene System**: Title screen, gameplay, and game over scenes with scene stack navigation
- **Modern Visuals**:
  - Gradient snake body (head is brightest)
  - Glowing food effect
  - Purple and gold UI theme
  - Grid overlay
- **Smooth Controls**: Arrow keys or WASD
- **Score Tracking**: Points awarded for each food eaten

## Controls

### Menu
- `↑/↓` or `W/S` - Navigate menu
- `Enter` - Select option

### Gameplay
- `↑/↓/←/→` or `W/A/S/D` - Control snake direction
- `Space` - Pause game
- `ESC` - Return to menu

## Requirements

```bash
pip install pygame
```

## Run

```bash
python main.py
```

## Game Rules

- Eat the red food to grow and score points
- Don't hit the walls or yourself
- Each food gives you 10 points
- The game speeds up as you get longer (FPS = 10)

## Code Structure

- **`constants.py`** - Game configuration, colors, grid settings
- **`entities.py`** - Snake and Food classes with collision detection
- **`scenes.py`** - TitleScene, GameScene, GameOverScene
- **`game.py`** - Main game class with scene stack
- **`main.py`** - Entry point

## Architecture

This game uses the same modular architecture as Pong:
- Scene stack for navigation between screens
- Entity-based design for game objects
- Centralized constants for easy configuration
- Clean separation of concerns
