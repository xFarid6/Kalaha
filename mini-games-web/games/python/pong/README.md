# Pong - Python Version

A classic Pong game implemented in Python using Pygame with modern effects and AI opponent.

## Features

- **OOP Architecture**: Clean object-oriented design with scene stack navigation
- **Scene System**: Title screen and gameplay scenes
- **AI Opponent**: Play against computer or another human
- **Modern Effects**:
  - Ball trail effect
  - Glow effects on paddles and ball
  - Purple and gold color scheme
  - Smooth animations

## Controls

### Menu
- `↑/↓` - Navigate menu
- `Enter` - Select option

### Gameplay
- **Player 1**: `W/S` - Move paddle up/down
- **Player 2** (if human): `↑/↓` - Move paddle up/down
- `Space` - Pause game  
- `ESC` - Return to menu

## Requirements

```bash
pip install pygame
```

## Run

```bash
python pong.py
```

## Game Rules

- First player to score 5 points wins
- Ball speeds up slightly with each paddle hit
- Ball deflection angle depends on where it hits the paddle

## Code Structure

- `Vector2` - 2D vector class for positions and velocities
- `Paddle` - Paddle entity with AI capable movement
- `Ball` - Ball entity with trail effect and physics
- `Scene` - Base scene class
- `TitleScene` - Menu/title screen
- `GameScene` - Main gameplay
- `Game` - Main game class with scene stack management
