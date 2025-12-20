"""Snake - Game Class
Main game class with scene stack management
"""

import pygame
import sys
from typing import List
from constants import *
from scenes import Scene, TitleScene


class Game:
    """Main game class with scene stack"""
    
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Snake")
        self.clock = pygame.time.Clock()
        self.running = True
        self.scene_stack: List[Scene] = []
        
        # Start with title scene
        self.push_scene(TitleScene(self))
        
    def push_scene(self, scene: Scene):
        """Push a new scene onto the stack"""
        self.scene_stack.append(scene)
        
    def pop_scene(self):
        """Pop current scene from stack"""
        if len(self.scene_stack) > 1:
            self.scene_stack.pop()
        else:
            self.running = False
            
    def run(self):
        """Main game loop"""
        while self.running:
            dt = self.clock.tick(FPS) / 1000.0  # Delta time in seconds
            
            # Get current scene
            if not self.scene_stack:
                break
                
            current_scene = self.scene_stack[-1]
            
            # Handle events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                current_scene.handle_event(event)
            
            # Update and draw
            current_scene.update(dt)
            current_scene.draw(self.screen)
            
            # Update display
            pygame.display.flip()
        
        pygame.quit()
        sys.exit()
