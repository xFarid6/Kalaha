"""
Pong - Constants and Configuration
All game constants, colors, and settings
"""

import pygame

# Initialize Pygame
pygame.init()

# Screen dimensions
SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 600
FPS = 60

# Colors - Purple/Gold theme
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
PURPLE = (147, 51, 234)
PURPLE_LIGHT = (168, 85, 247)
GOLD = (218, 165, 32)
GOLD_LIGHT = (238, 185, 52)

# Paddle settings
PADDLE_WIDTH = 15
PADDLE_HEIGHT = 100
PADDLE_SPEED = 7

# Ball settings
BALL_SIZE = 15
BALL_SPEED_X = 6
BALL_SPEED_Y = 6
TRAIL_LENGTH = 15

# Game settings
WIN_SCORE = 5
