"""
Snake - Constants and Configuration
All game constants, colors, and settings
"""

import pygame

# Initialize Pygame
pygame.init()

# Screen dimensions
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 10  # Snake speed

# Grid settings
GRID_SIZE = 20
GRID_WIDTH = SCREEN_WIDTH // GRID_SIZE
GRID_HEIGHT = SCREEN_HEIGHT // GRID_SIZE

# Colors - Purple/Gold theme with Green accents
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
PURPLE = (147, 51, 234)
PURPLE_LIGHT = (168, 85, 247)
GOLD = (218, 165, 32)
GOLD_LIGHT = (238, 185, 52)
GREEN = (5, 150, 105)  # For snake
GREEN_LIGHT = (16, 185, 129)
RED = (220, 38, 38)  # For food

# Directions
UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)

# Game settings
INITIAL_SNAKE_LENGTH = 3
GROWTH_PER_FOOD = 1
