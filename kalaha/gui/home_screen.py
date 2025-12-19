import pygame
from typing import List, Dict, Any, Tuple, Optional, Callable
from kalaha.gui.constants import (
    BG_COLOR, TEXT_COLOR, ACCENT_COLOR, BUTTON_COLOR, BUTTON_HOVER, BOX_BORDER
)

class HomeScreen:
    def __init__(self, screen: pygame.Surface, font_big: pygame.font.Font, font_med: pygame.font.Font, font_small: pygame.font.Font, config: Dict[str, Any], on_play: Callable[[], None]) -> None:
        self.screen = screen
        self.font_big = font_big
        self.font_med = font_med
        self.font_small = font_small
        self.config = config
        self.on_play = on_play # Callback to switch to GAME state
        
        # Initialize default animation speed if not present
        if 'anim_speed' not in self.config:
            self.config['anim_speed'] = 0.5 # Default 0.5s
        
        self.strategies: List[str] = ["basic", "balanced", "aggressive", "defensive", "PPO-Agent"]
        self.difficulties: List[str] = ["Beginner", "Easy", "Medium", "Hard", "Hell"]
        self.colors: List[str] = ["Gold", "Red", "Blue", "Green", "White"]
        
        self.buttons: Dict[str, pygame.Rect] = {}
        
        # Sliders
        self.depth_slider: Dict[str, Any] = {'rect': pygame.Rect(0,0,0,0), 'bar': pygame.Rect(0,0,0,0), 'dragging': False}
        self.anim_slider: Dict[str, Any] = {'rect': pygame.Rect(0,0,0,0), 'bar': pygame.Rect(0,0,0,0), 'dragging': False}

    def draw_text(self, text: str, font: pygame.font.Font, color: Tuple[int,int,int], center: Optional[Tuple[int,int]] = None, top_left: Optional[Tuple[int,int]] = None) -> pygame.Rect:
        surf = font.render(text, True, color)
        rect = surf.get_rect(center=center) if center else surf.get_rect(topleft=top_left) if top_left else surf.get_rect()
        self.screen.blit(surf, rect)
        return rect
        
    def draw_nav_button(self, text: str, rect: pygame.Rect) -> None:
        # Draw hitbox box
        pygame.draw.rect(self.screen, BOX_BORDER, rect, 1) # Thin gray border
        self.draw_text(text, self.font_small, ACCENT_COLOR, center=rect.center)
        
    def draw_button(self, text: str, rect: pygame.Rect, active: bool = False) -> None:
        color = BUTTON_HOVER if active else BUTTON_COLOR
        pygame.draw.rect(self.screen, color, rect, border_radius=10)
        pygame.draw.rect(self.screen, ACCENT_COLOR, rect, 2, border_radius=10)
        self.draw_text(text, self.font_small, TEXT_COLOR, center=rect.center)
        
    def draw(self) -> None:
        W, H = self.screen.get_size()
        cx, cy = W // 2, H // 2
        
        self.screen.fill(BG_COLOR)
        self.draw_text("Setup Game", self.font_big, ACCENT_COLOR, center=(cx, 60))
        
        # Responsive Layout
        col_lbl_x = cx - 150
        col_val_x = cx + 150
        start_y = 160
        step_y = 70
        
        y = start_y
        
        # Strategy
        self.draw_text("Strategy:", self.font_med, TEXT_COLOR, center=(col_lbl_x, y))
        self.draw_text(f"{self.config['strategy']}", self.font_med, ACCENT_COLOR, center=(col_val_x, y))
        b_prev = pygame.Rect(col_val_x - 160, y - 15, 30, 30)
        b_next = pygame.Rect(col_val_x + 130, y - 15, 30, 30)
        self.draw_nav_button("<", b_prev)
        self.draw_nav_button(">", b_next)
        self.buttons["strategy_prev"] = b_prev
        self.buttons["strategy_next"] = b_next
        
        y += step_y
        # Difficulty
        self.draw_text("Difficulty:", self.font_med, TEXT_COLOR, center=(col_lbl_x, y))
        self.draw_text(f"{self.config['difficulty']}", self.font_med, ACCENT_COLOR, center=(col_val_x, y))
        b_prev = pygame.Rect(col_val_x - 160, y - 15, 30, 30)
        b_next = pygame.Rect(col_val_x + 130, y - 15, 30, 30)
        self.draw_nav_button("<", b_prev)
        self.draw_nav_button(">", b_next)
        self.buttons["diff_prev"] = b_prev
        self.buttons["diff_next"] = b_next
        
        y += step_y
        # Depth Slider - manually drawn
        self.draw_text(f"Depth ({self.config['depth']}):", self.font_med, TEXT_COLOR, center=(col_lbl_x, y))
        bar_rect = pygame.Rect(col_val_x - 100, y-5, 200, 10)
        pygame.draw.rect(self.screen, BUTTON_COLOR, bar_rect, border_radius=5)
        ratio = (self.config['depth'] - 1) / 19
        handle_x = bar_rect.x + (ratio * bar_rect.width)
        handle_rect = pygame.Rect(handle_x - 10, y - 15, 20, 30)
        pygame.draw.rect(self.screen, ACCENT_COLOR, handle_rect, border_radius=5)
        self.depth_slider['rect'] = handle_rect
        self.depth_slider['bar'] = bar_rect
        
        y += step_y
        # Color
        self.draw_text("Ball Color:", self.font_med, TEXT_COLOR, center=(col_lbl_x, y))
        self.draw_text(f"{self.config['ball_color']}", self.font_med, ACCENT_COLOR, center=(col_val_x, y))
        b_prev = pygame.Rect(col_val_x - 160, y - 15, 30, 30)
        b_next = pygame.Rect(col_val_x + 130, y - 15, 30, 30)
        self.draw_nav_button("<", b_prev)
        self.draw_nav_button(">", b_next)
        self.buttons["color_prev"] = b_prev
        self.buttons["color_next"] = b_next
        
        y += step_y
        # Animation Speed Slider
        self.draw_text(f"Speed ({self.config['anim_speed']:.1f}s):", self.font_med, TEXT_COLOR, center=(col_lbl_x, y))
        bar_rect = pygame.Rect(col_val_x - 100, y-5, 200, 10)
        pygame.draw.rect(self.screen, BUTTON_COLOR, bar_rect, border_radius=5)
        # Range 0.1 to 2.0
        min_s, max_s = 0.1, 2.0
        ratio = (self.config['anim_speed'] - min_s) / (max_s - min_s)
        handle_x = bar_rect.x + (ratio * bar_rect.width)
        handle_rect = pygame.Rect(handle_x - 10, y - 15, 20, 30)
        pygame.draw.rect(self.screen, ACCENT_COLOR, handle_rect, border_radius=5)
        self.anim_slider['rect'] = handle_rect
        self.anim_slider['bar'] = bar_rect
        
        # Play
        play_w, play_h = 240, 70
        play_rect = pygame.Rect(cx - play_w//2, H - 100, play_w, play_h) # Moved down
        self.draw_button("PLAY", play_rect, active=play_rect.collidepoint(pygame.mouse.get_pos()))
        self.buttons["play"] = play_rect
        
        # Instructions
        self.draw_text("Click box borders < > to change settings", self.font_small, (150,150,150), top_left=(20, H-40))

    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type == pygame.MOUSEBUTTONDOWN:
            pos = event.pos
            if self.buttons.get("strategy_prev", pygame.Rect(0,0,0,0)).collidepoint(pos): self.cycle_option("strategy", self.strategies, -1)
            if self.buttons.get("strategy_next", pygame.Rect(0,0,0,0)).collidepoint(pos): self.cycle_option("strategy", self.strategies, 1)
            if self.buttons.get("diff_prev", pygame.Rect(0,0,0,0)).collidepoint(pos): 
                self.cycle_option("difficulty", self.difficulties, -1); self.update_difficulty_preset()
            if self.buttons.get("diff_next", pygame.Rect(0,0,0,0)).collidepoint(pos): 
                self.cycle_option("difficulty", self.difficulties, 1); self.update_difficulty_preset()
            if self.buttons.get("color_prev", pygame.Rect(0,0,0,0)).collidepoint(pos): self.cycle_option("ball_color", self.colors, -1)
            if self.buttons.get("color_next", pygame.Rect(0,0,0,0)).collidepoint(pos): self.cycle_option("ball_color", self.colors, 1)
            
            # Sliders
            if self.check_slider_click(self.depth_slider, pos): 
                self.depth_slider['dragging'] = True
                self.handle_depth_drag(pos)
                
            if self.check_slider_click(self.anim_slider, pos): 
                self.anim_slider['dragging'] = True
                self.handle_anim_drag(pos)
                
            if self.buttons.get("play", pygame.Rect(0,0,0,0)).collidepoint(pos):
                self.on_play()

        elif event.type == pygame.MOUSEBUTTONUP:
            self.depth_slider['dragging'] = False
            self.anim_slider['dragging'] = False
            
        elif event.type == pygame.MOUSEMOTION:
            if self.depth_slider['dragging']: self.handle_depth_drag(event.pos)
            if self.anim_slider['dragging']: self.handle_anim_drag(event.pos)

    def check_slider_click(self, slider_obj: Dict[str, Any], pos: Tuple[int, int]) -> bool:
        return slider_obj['rect'].collidepoint(pos) or slider_obj['bar'].collidepoint(pos)

    def cycle_option(self, key: str, options: List[str], direction: int) -> None:
        idx = options.index(self.config[key])
        self.config[key] = options[(idx + direction) % len(options)]
        
    def update_difficulty_preset(self) -> None:
        mapping = { "Beginner": 2, "Easy": 4, "Medium": 6, "Hard": 10, "Hell": 14 }
        if self.config['difficulty'] in mapping:
            self.config['depth'] = mapping[self.config['difficulty']]

    def handle_depth_drag(self, pos: Tuple[int, int]) -> None:
        bar = self.depth_slider['bar']
        rel_x = pos[0] - bar.x
        ratio = max(0, min(1, rel_x / bar.width))
        self.config['depth'] = int(1 + ratio * 19)
        self.config['difficulty'] = "Custom"

    def handle_anim_drag(self, pos: Tuple[int, int]) -> None:
        bar = self.anim_slider['bar']
        rel_x = pos[0] - bar.x
        ratio = max(0, min(1, rel_x / bar.width))
        # Range 0.1 to 2.0
        val = 0.1 + (ratio * 1.9)
        self.config['anim_speed'] = round(val, 1)
