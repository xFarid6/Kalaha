from enum import Enum, auto

# Colors (Brown/Gold Aesthetic)
BG_COLOR = (40, 26, 13)         # Deep Coffee
TEXT_COLOR = (245, 245, 220)    # Cream
ACCENT_COLOR = (218, 165, 32)   # Gold
BUTTON_COLOR = (101, 67, 33)    # Dark Wood
BUTTON_HOVER = (139, 69, 19)    # Saddle Brown
BOX_BORDER = (100, 100, 100)    # Gray for hitbox outlines

# Constants - Responsive Design
# Base Logic Resolution: 1024x768
WIDTH, HEIGHT = 1024, 768

class GameState(Enum):
    TITLE = auto()
    HOME = auto()
    GAME = auto()
