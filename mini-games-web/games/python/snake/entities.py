"""
Snake - Game Entities
Contains Snake, Food, and Vector2 classes
"""

import pygame
import random
from dataclasses import dataclass
from typing import List, Tuple
from constants import *


@dataclass
class Vector2:
    """2D Vector for grid positions"""
    x: int
    y: int
    
    def __add__(self, other):
        return Vector2(self.x + other[0], self.y + other[1])
    
    def __eq__(self, other):
        return self.x == other.x and self.y == other.y
    
    def to_tuple(self) -> Tuple[int, int]:
        return (self.x, self.y)


class Snake:
    """Snake entity"""
    
    def __init__(self):
        # Start in the middle of the screen
        start_x = GRID_WIDTH // 2
        start_y = GRID_HEIGHT // 2
        
        # Snake body is list of Vector2 positions (head first)
        self.body: List[Vector2] = [
            Vector2(start_x, start_y),
            Vector2(start_x - 1, start_y),
            Vector2(start_x - 2, start_y)
        ]
        
        self.direction = RIGHT
        self.next_direction = RIGHT
        self.grow_pending = 0
        
    def set_direction(self, new_direction: Tuple[int, int]):
        """Set new direction (but prevent 180-degree turns)"""
        # Can't turn directly backwards
        if (new_direction[0] + self.direction[0] == 0 and 
            new_direction[1] + self.direction[1] == 0):
            return
        self.next_direction = new_direction
        
    def update(self):
        """Move snake forward"""
        self.direction = self.next_direction
        
        # Calculate new head position
        head = self.body[0]
        new_head = head + self.direction
        
        # Add new head
        self.body.insert(0, new_head)
        
        # Remove tail (unless growing)
        if self.grow_pending > 0:
            self.grow_pending -= 1
        else:
            self.body.pop()
            
    def grow(self, amount: int = GROWTH_PER_FOOD):
        """Make snake grow by amount"""
        self.grow_pending += amount
        
    def get_head(self) -> Vector2:
        """Get head position"""
        return self.body[0]
        
    def check_self_collision(self) -> bool:
        """Check if head collided with body"""
        head = self.get_head()
        return head in self.body[1:]
        
    def check_wall_collision(self) -> bool:
        """Check if hit wall"""
        head = self.get_head()
        return (head.x < 0 or head.x >= GRID_WIDTH or 
                head.y < 0 or head.y >= GRID_HEIGHT)
                
    def draw(self, screen: pygame.Surface):
        """Draw snake with gradient effect"""
        for i, segment in enumerate(self.body):
            # Calculate color gradient (head is brightest)
            brightness = 1.0 - (i / len(self.body)) * 0.5
            color = tuple(int(c * brightness) for c in GREEN_LIGHT)
            
            # Draw segment
            rect = pygame.Rect(
                segment.x * GRID_SIZE,
                segment.y * GRID_SIZE,
                GRID_SIZE - 2,  # Leave small gap
                GRID_SIZE - 2
            )
            
            pygame.draw.rect(screen, color, rect, border_radius=4)
            
            # Head gets special highlight
            if i == 0:
                pygame.draw.rect(screen, GOLD, rect, 2, border_radius=4)


class Food:
    """Food entity"""
    
    def __init__(self, snake: Snake):
        self.pos = Vector2(0, 0)
        self.respawn(snake)
        
    def respawn(self, snake: Snake):
        """Place food at random position not on snake"""
        while True:
            self.pos = Vector2(
                random.randint(0, GRID_WIDTH - 1),
                random.randint(0, GRID_HEIGHT - 1)
            )
            
            # Make sure food doesn't spawn on snake
            if self.pos not in snake.body:
                break
                
    def draw(self, screen: pygame.Surface):
        """Draw food with pulsing effect"""
        rect = pygame.Rect(
            self.pos.x * GRID_SIZE,
            self.pos.y * GRID_SIZE,
            GRID_SIZE - 2,
            GRID_SIZE - 2
        )
        
        # Draw food
        pygame.draw.rect(screen, RED, rect, border_radius=6)
        
        # Add glow
        glow_surf = pygame.Surface((GRID_SIZE + 4, GRID_SIZE + 4), pygame.SRCALPHA)
        pygame.draw.rect(glow_surf, (*RED, 100), glow_surf.get_rect(), border_radius=8)
        screen.blit(glow_surf, (self.pos.x * GRID_SIZE - 2, self.pos.y * GRID_SIZE - 2))
