from enum import Enum, auto

# Colors (Brown/Gold Aesthetic)
BG_COLOR = (40, 26, 13)         # Deep Coffee
TEXT_COLOR = (245, 245, 220)    # Cream
ACCENT_COLOR = (218, 165, 32)   # Gold
BUTTON_COLOR = (101, 67, 33)    # Dark Wood
BUTTON_HOVER = (139, 69, 19)    # Saddle Brown
BOX_BORDER = (100, 100, 100)    # Gray for hitbox outlines

# New Borders
BORDER_BOARD = (80, 50, 20)     # Lighter brown for board area
BORDER_STORE = (90, 60, 30)     # Distinct color for stores

# Constants - Responsive Design
# Base Logic Resolution: 1024x768 (Initial, but resizable)
# We will use relative calculations mostly.
WIDTH, HEIGHT = 1024, 768

class GameState(Enum):
    TITLE = auto()
    HOME = auto()
    GAME = auto()
