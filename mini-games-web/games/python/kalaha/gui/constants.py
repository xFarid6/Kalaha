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
WIDTH, HEIGHT = 1024, 768

# Application States
class AppState(Enum):
    """Top-level application states"""
    TITLE = auto()
    HOME = auto()
    GAME = auto()

# Game Screen States
class ScreenState(Enum):
    """Game screen internal states"""
    IDLE = auto()
    THINKING = auto()
    ANIMATING = auto()
    UNDO_ANIMATING = auto()

# Backwards compatibility
GameState = AppState
