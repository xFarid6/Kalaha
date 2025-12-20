"""
Pong - Game Entities
Contains Paddle, Ball, and Vector2 classes
"""

import pygame
import random
from dataclasses import dataclass
from collections import deque
from constants import *


@dataclass
class Vector2:
    """2D Vector for position and velocity"""
    x: float
    y: float
    
    def __add__(self, other):
        return Vector2(self.x + other.x, self.y + other.y)
    
    def __mul__(self, scalar):
        return Vector2(self.x * scalar, self.y * scalar)


class Paddle:
    """Paddle entity with optional AI"""
    
    def __init__(self, x: float, y: float, is_ai: bool = False):
        self.pos = Vector2(x, y)
        self.width = PADDLE_WIDTH
        self.height = PADDLE_HEIGHT
        self.speed = PADDLE_SPEED
        self.is_ai = is_ai
        self.score = 0
        
    def move_up(self):
        """Move paddle up within screen bounds"""
        self.pos.y = max(0, self.pos.y - self.speed)
        
    def move_down(self):
        """Move paddle down within screen bounds"""
        self.pos.y = min(SCREEN_HEIGHT - self.height, self.pos.y + self.speed)
        
    def ai_update(self, ball_y: float):
        """Simple AI that follows the ball"""
        paddle_center = self.pos.y + self.height / 2
        
        if ball_y < paddle_center - 20:
            self.move_up()
        elif ball_y > paddle_center + 20:
            self.move_down()
    
    def get_rect(self) -> pygame.Rect:
        """Get pygame Rect for collision detection"""
        return pygame.Rect(self.pos.x, self.pos.y, self.width, self.height)
    
    def draw(self, screen: pygame.Surface):
        """Draw paddle with glow effect"""
        rect = self.get_rect()
        
        # Draw paddle body
        pygame.draw.rect(screen, PURPLE_LIGHT, rect)
        pygame.draw.rect(screen, PURPLE, rect, 2)  # Border
        
        # Glow effect
        glow_surf = pygame.Surface((self.width + 10, self.height + 10), pygame.SRCALPHA)
        pygame.draw.rect(glow_surf, (*PURPLE, 50), glow_surf.get_rect(), border_radius=5)
        screen.blit(glow_surf, (self.pos.x - 5, self.pos.y - 5))


class Ball:
    """Ball entity with trail effect"""
    
    def __init__(self, x: float, y: float):
        self.pos = Vector2(x, y)
        self.vel = Vector2(BALL_SPEED_X, BALL_SPEED_Y)
        self.size = BALL_SIZE
        self.trail: deque = deque(maxlen=TRAIL_LENGTH)
        self.speed_multiplier = 1.0
        
    def update(self):
        """Update ball position and handle wall bounces"""
        self.pos = self.pos + self.vel
        self.trail.append((self.pos.x, self.pos.y))
        
        # Bounce off top and bottom walls
        if self.pos.y <= 0 or self.pos.y >= SCREEN_HEIGHT - self.size:
            self.vel.y *= -1
            
    def check_paddle_collision(self, paddle: Paddle) -> bool:
        """Check and handle paddle collision"""
        ball_rect = pygame.Rect(self.pos.x, self.pos.y, self.size, self.size)
        paddle_rect = paddle.get_rect()
        
        if ball_rect.colliderect(paddle_rect):
            # Reverse X direction
            self.vel.x *= -1
            
            # Add variation based on where ball hits paddle
            paddle_center = paddle.pos.y + paddle.height / 2
            ball_center = self.pos.y + self.size / 2
            hit_pos = (ball_center - paddle_center) / (paddle.height / 2)  # -1 to 1
            
            self.vel.y = hit_pos * 8  # Max deflection
            
            # Increase speed slightly
            self.speed_multiplier = min(1.5, self.speed_multiplier + 0.05)
            self.vel.x = self.vel.x * 1.05
            
            return True
        return False
        
    def reset(self, direction: int = 1):
        """Reset ball to center"""
        self.pos = Vector2(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2)
        self.vel = Vector2(BALL_SPEED_X * direction, random.uniform(-3, 3))
        self.trail.clear()
        self.speed_multiplier = 1.0
        
    def is_out_left(self) -> bool:
        """Check if ball went off left side"""
        return self.pos.x < 0
        
    def is_out_right(self) -> bool:
        """Check if ball went off right side"""
        return self.pos.x > SCREEN_WIDTH
        
    def draw(self, screen: pygame.Surface):
        """Draw ball with trail and glow effects"""
        # Draw trail
        for i, (tx, ty) in enumerate(self.trail):
            alpha = int(255 * (i / TRAIL_LENGTH))
            size = int(self.size * (i / TRAIL_LENGTH))
            trail_surf = pygame.Surface((size * 2, size * 2), pygame.SRCALPHA)
            pygame.draw.circle(trail_surf, (*GOLD, alpha), (size, size), size)
            screen.blit(trail_surf, (tx - size, ty - size))
        
        # Draw ball
        pygame.draw.circle(screen, GOLD_LIGHT, (int(self.pos.x), int(self.pos.y)), self.size)
        
        # Glow effect
        glow_surf = pygame.Surface((self.size * 4, self.size * 4), pygame.SRCALPHA)
        pygame.draw.circle(glow_surf, (*GOLD, 80), (self.size * 2, self.size * 2), self.size * 2)
        screen.blit(glow_surf, (self.pos.x - self.size * 2, self.pos.y - self.size * 2))
