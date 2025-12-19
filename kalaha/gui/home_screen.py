import pygame
from kalaha.gui.constants import (
    BG_COLOR, TEXT_COLOR, ACCENT_COLOR, BUTTON_COLOR, BUTTON_HOVER, BOX_BORDER
)

class HomeScreen:
    def __init__(self, screen, font_big, font_med, font_small, config, on_play):
        self.screen = screen
        self.font_big = font_big
        self.font_med = font_med
        self.font_small = font_small
        self.config = config
        self.on_play = on_play # Callback to switch to GAME state
        
        self.strategies = ["basic", "balanced", "aggressive", "defensive", "PPO-Agent"]
        self.difficulties = ["Beginner", "Easy", "Medium", "Hard", "Hell"]
        self.colors = ["Gold", "Red", "Blue", "Green", "White"]
        
        self.buttons = {}
        self.slider_rect = pygame.Rect(0, 0, 0, 0)
        self.slider_bar_rect = pygame.Rect(0, 0, 0, 0)
        self.dragging_slider = False

    def draw_text(self, text, font, color, center=None, top_left=None):
        surf = font.render(text, True, color)
        rect = surf.get_rect(center=center) if center else surf.get_rect(topleft=top_left) if top_left else surf.get_rect()
        self.screen.blit(surf, rect)
        return rect
        
    def draw_nav_button(self, text, rect):
        # Draw hitbox box
        pygame.draw.rect(self.screen, BOX_BORDER, rect, 1) # Thin gray border
        self.draw_text(text, self.font_small, ACCENT_COLOR, center=rect.center)
        
    def draw_button(self, text, rect, active=False):
        color = BUTTON_HOVER if active else BUTTON_COLOR
        pygame.draw.rect(self.screen, color, rect, border_radius=10)
        pygame.draw.rect(self.screen, ACCENT_COLOR, rect, 2, border_radius=10)
        self.draw_text(text, self.font_small, TEXT_COLOR, center=rect.center)

    def draw(self):
        W, H = self.screen.get_size()
        cx, cy = W // 2, H // 2
        
        self.screen.fill(BG_COLOR)
        self.draw_text("Setup Game", self.font_big, ACCENT_COLOR, center=(cx, 80))
        
        # Responsive Layout
        col_lbl_x = cx - 150
        col_val_x = cx + 150
        start_y = 200
        step_y = 80
        
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
        # Depth
        self.draw_text(f"Depth ({self.config['depth']}):", self.font_med, TEXT_COLOR, center=(col_lbl_x, y))
        bar_rect = pygame.Rect(col_val_x - 100, y-5, 200, 10)
        pygame.draw.rect(self.screen, BUTTON_COLOR, bar_rect, border_radius=5)
        ratio = (self.config['depth'] - 1) / 19
        handle_x = bar_rect.x + (ratio * bar_rect.width)
        handle_rect = pygame.Rect(handle_x - 10, y - 15, 20, 30)
        pygame.draw.rect(self.screen, ACCENT_COLOR, handle_rect, border_radius=5)
        self.slider_rect = handle_rect
        self.slider_bar_rect = bar_rect
        
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
        
        # Play
        play_w, play_h = 240, 70
        play_rect = pygame.Rect(cx - play_w//2, H - 150, play_w, play_h)
        self.draw_button("PLAY", play_rect, active=play_rect.collidepoint(pygame.mouse.get_pos()))
        self.buttons["play"] = play_rect
        
        # Instructions
        self.draw_text("Click box borders < > to change settings", self.font_small, (150,150,150), top_left=(20, H-40))

    def handle_event(self, event):
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
            
            if self.slider_rect.collidepoint(pos) or self.slider_bar_rect.collidepoint(pos):
                self.dragging_slider = True; self.handle_slider_drag(pos)
                
            if self.buttons.get("play", pygame.Rect(0,0,0,0)).collidepoint(pos):
                self.on_play()

        elif event.type == pygame.MOUSEBUTTONUP:
            self.dragging_slider = False
        elif event.type == pygame.MOUSEMOTION and self.dragging_slider:
            self.handle_slider_drag(event.pos)

    def cycle_option(self, key, options, direction):
        idx = options.index(self.config[key])
        self.config[key] = options[(idx + direction) % len(options)]
        
    def update_difficulty_preset(self):
        mapping = { "Beginner": 2, "Easy": 4, "Medium": 6, "Hard": 10, "Hell": 14 }
        if self.config['difficulty'] in mapping:
            self.config['depth'] = mapping[self.config['difficulty']]

    def handle_slider_drag(self, pos):
        bar = self.slider_bar_rect
        rel_x = pos[0] - bar.x
        ratio = max(0, min(1, rel_x / bar.width))
        self.config['depth'] = int(1 + ratio * 19)
        self.config['difficulty'] = "Custom"
