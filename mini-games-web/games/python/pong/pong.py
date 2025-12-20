"""
Pong Game - Python Implementation
A classic Pong game with OOP architecture, scene stack navigation, and modern effects.
"""

import pygame
import sys
import random
from dataclasses import dataclass
from typing import List, Tuple, Optional
from collections import deque

# Initialize Pygame
pygame.init()

# Constants
SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 600
FPS = 60

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
PURPLE = (147, 51, 234)
PURPLE_LIGHT = (168, 85, 247)
GOLD = (218, 165, 32)
GOLD_LIGHT = (238, 185, 52)

# Game settings
PADDLE_WIDTH = 15
PADDLE_HEIGHT = 100
PADDLE_SPEED = 7
BALL_SIZE = 15
BALL_SPEED_X = 6
BALL_SPEED_Y = 6
TRAIL_LENGTH = 15


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
    """Paddle entity"""
    
    def __init__(self, x: float, y: float, is_ai: bool = False):
        self.pos = Vector2(x, y)
        self.width = PADDLE_WIDTH
        self.height = PADDLE_HEIGHT
        self.speed = PADDLE_SPEED
        self.is_ai = is_ai
        self.score = 0
        
    def move_up(self):
        self.pos.y = max(0, self.pos.y - self.speed)
        
    def move_down(self):
        self.pos.y = min(SCREEN_HEIGHT - self.height, self.pos.y + self.speed)
        
    def ai_update(self, ball_y: float):
        """Simple AI that follows the ball"""
        paddle_center = self.pos.y + self.height / 2
        
        if ball_y < paddle_center - 20:
            self.move_up()
        elif ball_y > paddle_center + 20:
            self.move_down()
    
    def get_rect(self) -> pygame.Rect:
        return pygame.Rect(self.pos.x, self.pos.y, self.width, self.height)
    
    def draw(self, screen: pygame.Surface):
        rect = self.get_rect()
        
        # Gradient effect (simplified)
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
        self.pos = self.pos + self.vel
        self.trail.append((self.pos.x, self.pos.y))
        
        # Bounce off top and bottom
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
        return self.pos.x < 0
        
    def is_out_right(self) -> bool:
        return self.pos.x > SCREEN_WIDTH
        
    def draw(self, screen: pygame.Surface):
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


# ===== Scene System =====

class Scene:
    """Base scene class"""
    
    def __init__(self, game):
        self.game = game
        
    def handle_event(self, event: pygame.event.Event):
        """Handle pygame events"""
        pass
        
    def update(self, dt: float):
        """Update scene logic"""
        pass
        
    def draw(self, screen: pygame.Surface):
        """Draw scene"""
        pass


class TitleScene(Scene):
    """Title/Menu scene"""
    
    def __init__(self, game):
        super().__init__(game)
        self.title_font = pygame.font.Font(None, 100)
        self.menu_font = pygame.font.Font(None, 50)
        self.small_font = pygame.font.Font(None, 30)
        self.selected = 0
        self.menu_items = ["Play vs AI", "Play vs Human", "Quit"]
        
    def handle_event(self, event: pygame.event.Event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                self.selected = (self.selected - 1) % len(self.menu_items)
            elif event.key == pygame.K_DOWN:
                self.selected = (self.selected + 1) % len(self.menu_items)
            elif event.key == pygame.K_RETURN:
                if self.selected == 0:  # Play vs AI
                    self.game.push_scene(GameScene(self.game, ai_opponent=True))
                elif self.selected == 1:  # Play vs Human
                    self.game.push_scene(GameScene(self.game, ai_opponent=False))
                elif self.selected == 2:  # Quit
                    self.game.running = False
                    
    def draw(self, screen: pygame.Surface):
        screen.fill(BLACK)
        
        # Draw background elements
        for i in range(10):
            alpha = 30
            pygame.draw.circle(screen, (*PURPLE, alpha), 
                             (random.randint(0, SCREEN_WIDTH), random.randint(0, SCREEN_HEIGHT)), 
                             random.randint(20, 100))
        
        # Title
        title_surf = self.title_font.render("PONG", True, GOLD)
        title_rect = title_surf.get_rect(center=(SCREEN_WIDTH / 2, 150))
        screen.blit(title_surf, title_rect)
        
        # Subtitle
        subtitle_surf = self.small_font.render("Classic Arcade • Modern AI", True, PURPLE_LIGHT)
        subtitle_rect = subtitle_surf.get_rect(center=(SCREEN_WIDTH / 2, 220))
        screen.blit(subtitle_surf, subtitle_rect)
        
        # Menu items
        for i, item in enumerate(self.menu_items):
            color = GOLD_LIGHT if i == self.selected else WHITE
            item_surf = self.menu_font.render(item, True, color)
            item_rect = item_surf.get_rect(center=(SCREEN_WIDTH / 2, 350 + i * 70))
            screen.blit(item_surf, item_rect)
            
            # Selection indicator
            if i == self.selected:
                pygame.draw.rect(screen, PURPLE, item_rect.inflate(20, 20), 3, border_radius=10)


class GameScene(Scene):
    """Main gameplay scene"""
    
    def __init__(self, game, ai_opponent: bool = True):
        super().__init__(game)
        self.ai_opponent = ai_opponent
        
        # Create entities
        self.paddle1 = Paddle(50, SCREEN_HEIGHT / 2 - PADDLE_HEIGHT / 2)
        self.paddle2 = Paddle(SCREEN_WIDTH - 50 - PADDLE_WIDTH, 
                             SCREEN_HEIGHT / 2 - PADDLE_HEIGHT / 2, 
                             is_ai=ai_opponent)
        self.ball = Ball(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2)
        
        # Fonts
        self.score_font = pygame.font.Font(None, 74)
        self.ui_font = pygame.font.Font(None, 36)
        
        self.paused = False
        self.winner = None
        self.win_score = 5
        
    def handle_event(self, event: pygame.event.Event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.game.pop_scene()
            elif event.key == pygame.K_SPACE:
                self.paused = not self.paused
                
    def update(self, dt: float):
        if self.paused or self.winner:
            return
            
        # Player 1 controls (W/S)
        keys = pygame.key.get_pressed()
        if keys[pygame.K_w]:
            self.paddle1.move_up()
        if keys[pygame.K_s]:
            self.paddle1.move_down()
            
        # Player 2 controls (Arrow keys) or AI
        if self.ai_opponent:
            self.paddle2.ai_update(self.ball.pos.y)
        else:
            if keys[pygame.K_UP]:
                self.paddle2.move_up()
            if keys[pygame.K_DOWN]:
                self.paddle2.move_down()
        
        # Update ball
        self.ball.update()
        
        # Check paddle collisions
        self.ball.check_paddle_collision(self.paddle1)
        self.ball.check_paddle_collision(self.paddle2)
        
        # Check scoring
        if self.ball.is_out_left():
            self.paddle2.score += 1
            self.ball.reset(direction=1)
            if self.paddle2.score >= self.win_score:
                self.winner = 2
                
        elif self.ball.is_out_right():
            self.paddle1.score += 1
            self.ball.reset(direction=-1)
            if self.paddle1.score >= self.win_score:
                self.winner = 1
                
    def draw(self, screen: pygame.Surface):
        screen.fill(BLACK)
        
        # Draw center line
        for y in range(0, SCREEN_HEIGHT, 30):
            pygame.draw.rect(screen, (50, 50, 50), (SCREEN_WIDTH / 2 - 2, y, 4, 20))
        
        # Draw entities
        self.paddle1.draw(screen)
        self.paddle2.draw(screen)
        self.ball.draw(screen)
        
        # Draw scores
        score1_surf = self.score_font.render(str(self.paddle1.score), True, PURPLE_LIGHT)
        score2_surf = self.score_font.render(str(self.paddle2.score), True, PURPLE_LIGHT)
        screen.blit(score1_surf, (SCREEN_WIDTH / 4, 50))
        screen.blit(score2_surf, (3 * SCREEN_WIDTH / 4 - score2_surf.get_width(), 50))
        
        # Draw UI messages
        if self.paused:
            pause_surf = self.ui_font.render("PAUSED", True, GOLD)
            pause_rect = pause_surf.get_rect(center=(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2))
            screen.blit(pause_surf, pause_rect)
            
        if self.winner:
            winner_text = f"Player {self.winner} Wins!" if not self.ai_opponent or self.winner == 1 else "AI Wins!"
            winner_surf = self.score_font.render(winner_text, True, GOLD_LIGHT)
            winner_rect = winner_surf.get_rect(center=(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2))
            screen.blit(winner_surf, winner_rect)
            
            restart_surf = self.ui_font.render("Press ESC for Menu", True, WHITE)
            restart_rect = restart_surf.get_rect(center=(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 + 80))
            screen.blit(restart_surf, restart_rect)


# ===== Game Class =====

class Game:
    """Main game class with scene stack"""
    
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Pong")
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


# ===== Entry Point =====

if __name__ == "__main__":
    game = Game()
    game.run()
