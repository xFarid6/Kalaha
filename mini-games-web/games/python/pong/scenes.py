"""
Pong - Game Scenes
Contains Scene base class, TitleScene, and GameScene
"""

import pygame
from constants import *
from entities import Paddle, Ball


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
            if self.paddle2.score >= WIN_SCORE:
                self.winner = 2
                
        elif self.ball.is_out_right():
            self.paddle1.score += 1
            self.ball.reset(direction=-1)
            if self.paddle1.score >= WIN_SCORE:
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
