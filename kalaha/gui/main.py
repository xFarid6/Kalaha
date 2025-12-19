import pygame
import sys
import time
from typing import Dict, Any, Optional
from kalaha.gui.constants import WIDTH, HEIGHT, BG_COLOR, TEXT_COLOR, ACCENT_COLOR, GameState
from kalaha.gui.game_screen import GameScreen
from kalaha.gui.home_screen import HomeScreen

class GameGUI:
    def __init__(self) -> None:
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
        pygame.display.set_caption("Kalaha (Mancala)")
        self.clock = pygame.time.Clock()
        self.font_big = pygame.font.SysFont("Arial", 64, bold=True)
        self.font_med = pygame.font.SysFont("Arial", 32)
        self.font_small = pygame.font.SysFont("Arial", 24)
        
        self.state = GameState.TITLE
        self.start_time = time.time()
        
        self.config: Dict[str, Any] = { "strategy": "balanced", "depth": 6, "difficulty": "Medium", "ball_color": "Gold", "anim_speed": 0.5 }
        
        self.game_screen: Optional[GameScreen] = None
        self.home_screen = HomeScreen(self.screen, self.font_big, self.font_med, self.font_small, self.config, self.start_game)

    def start_game(self) -> None:
        self.game_screen = GameScreen(self.screen, self.font_med, self.font_small, self.config, self.goto_home)
        self.state = GameState.GAME

    def goto_home(self) -> None:
        self.game_screen = None 
        self.state = GameState.HOME

    def handle_title(self) -> None:
        W, H = self.screen.get_size()
        if time.time() - self.start_time > 2.0:
            self.state = GameState.HOME
            return
        self.screen.fill(BG_COLOR)
        surf = self.font_big.render("Kalaha", True, ACCENT_COLOR)
        self.screen.blit(surf, surf.get_rect(center=(W//2, H//2 - 40)))
        surf2 = self.font_med.render("(Mancala)", True, TEXT_COLOR)
        self.screen.blit(surf2, surf2.get_rect(center=(W//2, H//2 + 20)))

    def run(self) -> None:
        while True:
            events = pygame.event.get()
            for event in events:
                if event.type == pygame.QUIT:
                    pygame.quit(); sys.exit()
                
                if self.state == GameState.HOME:
                    self.home_screen.handle_event(event)

            if self.state == GameState.TITLE:
                self.handle_title()
            elif self.state == GameState.HOME:
                self.home_screen.draw()
            elif self.state == GameState.GAME:
                if self.game_screen and self.state == GameState.GAME:
                    self.game_screen.update(events)
                    
                    if self.game_screen and self.state == GameState.GAME:
                        self.game_screen.bot_step()
                        self.game_screen.draw()

            pygame.display.flip()
            self.clock.tick(60)

def run_gui() -> None:
    GameGUI().run()

if __name__ == "__main__":
    run_gui()
