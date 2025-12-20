"""
Snake - Game Scenes  
Contains Scene base class, TitleScene, GameScene, and GameOverScene
"""

import pygame
from constants import *
from entities import Snake, Food


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
        self.menu_items = ["Play", "Quit"]
        
    def handle_event(self, event: pygame.event.Event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                self.selected = (self.selected - 1) % len(self.menu_items)
            elif event.key == pygame.K_DOWN:
                self.selected = (self.selected + 1) % len(self.menu_items)
            elif event.key == pygame.K_RETURN:
                if self.selected == 0:  # Play
                    self.game.push_scene(GameScene(self.game))
                elif self.selected == 1:  # Quit
                    self.game.running = False
                    
    def draw(self, screen: pygame.Surface):
        screen.fill(BLACK)
        
        # Title
        title_surf = self.title_font.render("SNAKE", True, GREEN_LIGHT)
        title_rect = title_surf.get_rect(center=(SCREEN_WIDTH / 2, 150))
        screen.blit(title_surf, title_rect)
        
        # Subtitle
        subtitle_surf = self.small_font.render("Classic Arcade • Modern Style", True, PURPLE_LIGHT)
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
    
    def __init__(self, game):
        super().__init__(game)
        self.snake = Snake()
        self.food = Food(self.snake)
        self.score = 0
        self.paused = False
        
        # Fonts
        self.score_font = pygame.font.Font(None, 48)
        self.ui_font = pygame.font.Font(None, 36)
        
    def handle_event(self, event: pygame.event.Event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.game.pop_scene()
            elif event.key == pygame.K_SPACE:
                self.paused = not self.paused
            elif event.key in (pygame.K_UP, pygame.K_w):
                self.snake.set_direction(UP)
            elif event.key in (pygame.K_DOWN, pygame.K_s):
                self.snake.set_direction(DOWN)
            elif event.key in (pygame.K_LEFT, pygame.K_a):
                self.snake.set_direction(LEFT)
            elif event.key in (pygame.K_RIGHT, pygame.K_d):
                self.snake.set_direction(RIGHT)
                
    def update(self, dt: float):
        if self.paused:
            return
            
        # Move snake
        self.snake.update()
        
        # Check if snake ate food
        if self.snake.get_head() == self.food.pos:
            self.snake.grow()
            self.food.respawn(self.snake)
            self.score += 10
            
        # Check collisions (game over)
        if self.snake.check_self_collision() or self.snake.check_wall_collision():
            self.game.push_scene(GameOverScene(self.game, self.score))
                
    def draw(self, screen: pygame.Surface):
        screen.fill(BLACK)
        
        # Draw grid (subtle)
        for x in range(0, SCREEN_WIDTH, GRID_SIZE):
            pygame.draw.line(screen, (30, 30, 30), (x, 0), (x, SCREEN_HEIGHT))
        for y in range(0, SCREEN_HEIGHT, GRID_SIZE):
            pygame.draw.line(screen, (30, 30, 30), (0, y), (SCREEN_WIDTH, y))
        
        # Draw entities
        self.food.draw(screen)
        self.snake.draw(screen)
        
        # Draw score
        score_surf = self.score_font.render(f"Score: {self.score}", True, GOLD)
        screen.blit(score_surf, (20, 20))
        
        # Draw paused message
        if self.paused:
            pause_surf = self.ui_font.render("PAUSED", True, PURPLE_LIGHT)
            pause_rect = pause_surf.get_rect(center=(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2))
            
            # Background for text
            bg_rect = pause_rect.inflate(40, 20)
            pygame.draw.rect(screen, BLACK, bg_rect)
            pygame.draw.rect(screen, PURPLE, bg_rect, 3, border_radius=8)
            
            screen.blit(pause_surf, pause_rect)


class GameOverScene(Scene):
    """Game over scene"""
    
    def __init__(self, game, final_score: int):
        super().__init__(game)
        self.final_score = final_score
        self.title_font = pygame.font.Font(None, 80)
        self.score_font = pygame.font.Font(None, 60)
        self.menu_font = pygame.font.Font(None, 40)
        self.selected = 0
        self.menu_items = ["Play Again", "Main Menu"]
        
    def handle_event(self, event: pygame.event.Event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                self.selected = (self.selected - 1) % len(self.menu_items)
            elif event.key == pygame.K_DOWN:
                self.selected = (self.selected + 1) % len(self.menu_items)
            elif event.key == pygame.K_RETURN:
                if self.selected == 0:  # Play Again
                    self.game.pop_scene()  # Remove game over
                    self.game.pop_scene()  # Remove old game
                    self.game.push_scene(GameScene(self.game))  # New game
                elif self.selected == 1:  # Main Menu
                    self.game.pop_scene()  # Remove game over
                    self.game.pop_scene()  # Remove old game
                    
    def draw(self, screen: pygame.Surface):
        screen.fill(BLACK)
        
        # Game Over title
        title_surf = self.title_font.render("GAME OVER", True, RED)
        title_rect = title_surf.get_rect(center=(SCREEN_WIDTH / 2, 150))
        screen.blit(title_surf, title_rect)
        
        # Final score
        score_surf = self.score_font.render(f"Score: {self.final_score}", True, GOLD_LIGHT)
        score_rect = score_surf.get_rect(center=(SCREEN_WIDTH / 2, 250))
        screen.blit(score_surf, score_rect)
        
        # Menu items
        for i, item in enumerate(self.menu_items):
            color = GREEN_LIGHT if i == self.selected else WHITE
            item_surf = self.menu_font.render(item, True, color)
            item_rect = item_surf.get_rect(center=(SCREEN_WIDTH / 2, 380 + i * 60))
            screen.blit(item_surf, item_rect)
            
            # Selection indicator
            if i == self.selected:
                pygame.draw.rect(screen, PURPLE, item_rect.inflate(20, 20), 3, border_radius=10)
