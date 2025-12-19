import pygame
import sys
import time
import os
from enum import Enum, auto

# Colors (Brown/Gold Aesthetic)
BG_COLOR = (40, 26, 13)         # Deep Coffee
TEXT_COLOR = (245, 245, 220)    # Cream
ACCENT_COLOR = (218, 165, 32)   # Gold
BUTTON_COLOR = (101, 67, 33)    # Dark Wood
BUTTON_HOVER = (139, 69, 19)    # Saddle Brown
BOX_BORDER = (100, 100, 100)    # Gray for hitbox outlines

# Constants - Responsive Design
# Base Logic Resolution: 1024x768
WIDTH, HEIGHT = 1024, 768

class GameState(Enum):
    TITLE = auto()
    HOME = auto()
    GAME = auto()

class GameScreen:
    def __init__(self, screen, font_med, font_small, config, on_exit):
        self.screen = screen
        self.font_med = font_med
        self.font_small = font_small
        self.config = config
        self.on_exit = on_exit # Callback to go back up
        
        # Imports
        try:
            from game_logic import initial_state, legal_moves, apply_move, is_terminal, cleanup_board
            from ai_engine import get_best_move
            from endgame_db import endgame_db
            self.game_logic = {
                'initial_state': initial_state, 
                'legal': legal_moves, 
                'apply': apply_move, 
                'terminal': is_terminal, 
                'cleanup': cleanup_board,
                'ai': get_best_move,
                'db': endgame_db
            }
        except ImportError:
            sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
            from kalaha.game_logic import initial_state, legal_moves, apply_move, is_terminal, cleanup_board
            from kalaha.ai_engine import get_best_move
            from kalaha.endgame_db import endgame_db
            self.game_logic = {
                'initial_state': initial_state, 
                'legal': legal_moves, 
                'apply': apply_move, 
                'terminal': is_terminal, 
                'cleanup': cleanup_board,
                'ai': get_best_move,
                'db': endgame_db
            }

        self.rl_model = None
        self.reset_game()

    def reset_game(self):
        self.board = self.game_logic['initial_state']()
        self.current_player = 0
        self.game_over = False
        self.winner = -1
        self.is_bot = True # Default P2=Bot
        self.pit_rects = []
        self.buttons = {}
        
    def load_rl_model(self):
        if self.rl_model: return self.rl_model
        try:
            from sb3_contrib import MaskablePPO
            model_path = os.path.join("models", "kalaha_latest.zip")
            if not os.path.exists(model_path):
                 model_path = os.path.join("..", "models", "kalaha_latest.zip")
                 
            if os.path.exists(model_path):
                self.rl_model = MaskablePPO.load(model_path)
                print("RL Model loaded.")
                return self.rl_model
        except: pass
        return None

    def get_rl_move(self, board, player):
        model = self.load_rl_model()
        if not model: return None
        import numpy as np
        obs = np.zeros(15, dtype=np.int32)
        # Canonical logic
        if player == 0:
            obs[0:6] = board[0:6]; obs[6] = board[6]; obs[7:13] = board[7:13]; obs[13] = board[13]; obs[14] = 0
        else:
            obs[0:6] = board[7:13]; obs[6] = board[13]; obs[7:13] = board[0:6]; obs[13] = board[6]; obs[14] = 1
        
        mask = [False]*6
        pits = list(range(0,6)) if player == 0 else list(range(7,13))
        for i, p in enumerate(pits):
            if board[p] > 0: mask[i] = True
            
        action, _ = model.predict(obs, action_masks=mask, deterministic=True)
        return int(action) if player == 0 else int(action + 7)

    def update(self, events):
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN:
                pos = event.pos
                if self.game_over:
                    if self.buttons.get("reset", pygame.Rect(0,0,0,0)).collidepoint(pos):
                        self.on_exit() # Calls goto_home
                else:
                    if self.current_player == 0 or not self.is_bot:
                        for rect, idx in self.pit_rects:
                            if rect.collidepoint(pos):
                                moves = self.game_logic['legal'](self.board, self.current_player)
                                if idx in moves:
                                    self._apply_move_logic(idx)

    def bot_step(self):
        # Called from main loop to handle blocking bot logic
        if not self.game_over and self.is_bot and self.current_player == 1:
             move = None
             if self.config['strategy'] == 'PPO-Agent':
                 move = self.get_rl_move(self.board, self.current_player)
             else:
                 move = self.game_logic['ai'](self.board, self.current_player, depth=self.config['depth'], strategy=self.config['strategy'])
             
             if move is not None:
                 self._apply_move_logic(move)


    def _apply_move_logic(self, idx):
        self.board, extra = self.game_logic['apply'](self.board, idx, self.current_player)
        if not extra:
            self.current_player = 1 - self.current_player
        
        if self.game_logic['terminal'](self.board):
            self.board = self.game_logic['cleanup'](self.board)
            self.game_over = True
            p1 = self.board[6]; p2 = self.board[13]
            self.winner = 0 if p1 > p2 else 1 if p2 > p1 else 2
            self.game_logic['db'].save()

    def draw_text(self, text, font, color, center=None, top_left=None):
        surf = font.render(text, True, color)
        if center: rect = surf.get_rect(center=center)
        elif top_left: rect = surf.get_rect(topleft=top_left)
        else: rect = surf.get_rect()
        self.screen.blit(surf, rect)
        return rect
        
    def draw_button(self, text, rect, active=False):
        color = BUTTON_HOVER if active else BUTTON_COLOR
        pygame.draw.rect(self.screen, color, rect, border_radius=10)
        pygame.draw.rect(self.screen, ACCENT_COLOR, rect, 2, border_radius=10)
        self.draw_text(text, self.font_small, TEXT_COLOR, center=rect.center)

    def draw(self):
        
        # Responsive Coordinates
        W, H = self.screen.get_size() # Should be WIDTH, HEIGHT
        cx, cy = W // 2, H // 2
        
        self.screen.fill(BG_COLOR)
        
        # Turn
        status = f"Player {self.current_player + 1}"
        if self.is_bot and self.current_player == 1: status += " (Bot)"
        self.draw_text(f"Turn: {status}", self.font_med, ACCENT_COLOR, center=(cx, 40))

        # AI Hint
        hint = self.get_rl_move(self.board, self.current_player)
        if hint is not None:
            rel = hint+1 if self.current_player==0 else hint-7+1
            self.draw_text(f"AI Suggests: Pit {rel}", self.font_small, (100, 200, 100), top_left=(W-250, H-40))

        # Info Panel - Relative
        panel_w = 220
        panel_h = 450
        panel_x = 40
        panel_y = 120
        panel = pygame.Rect(panel_x, panel_y, panel_w, panel_h)
        pygame.draw.rect(self.screen, BUTTON_COLOR, panel, border_radius=10)
        
        py = panel_y + 30
        self.draw_text("SCORE", self.font_med, ACCENT_COLOR, center=(panel.centerx, py)); py+=50
        self.draw_text(f"P1: {self.board[6]}", self.font_small, TEXT_COLOR, center=(panel.centerx, py)); py+=40
        self.draw_text(f"P2: {self.board[13]}", self.font_small, TEXT_COLOR, center=(panel.centerx, py)); py+=60
        self.draw_text("CONFIG", self.font_med, ACCENT_COLOR, center=(panel.centerx, py)); py+=40
        self.draw_text(f"{self.config['strategy']}", self.font_small, TEXT_COLOR, center=(panel.centerx, py)); py+=40
        self.draw_text(f"{self.config['difficulty']}", self.font_small, TEXT_COLOR, center=(panel.centerx, py)); py+=40
        self.draw_text(f"Depth: {self.config['depth']}", self.font_small, TEXT_COLOR, center=(panel.centerx, py))

        # Board - Relative
        board_w = 600
        board_h = 350
        board_x = cx - (board_w // 2) + 50 # Shift slightly right due to panel
        board_y = cy - (board_h // 2)
        
        board_area = pygame.Rect(board_x, board_y, board_w, board_h)
        pygame.draw.rect(self.screen, BUTTON_COLOR, board_area, border_radius=20)
        
        # Pits & Stores
        self.pit_rects = []
        
        # Dimensions
        pit_radius = 35
        pit_spacing = 80
        store_w = 60
        store_h = 240
        
        # Store Positions
        p2_store_rect = pygame.Rect(board_x + 20, board_y + (board_h - store_h)//2, store_w, store_h)
        p1_store_rect = pygame.Rect(board_x + board_w - 20 - store_w, board_y + (board_h - store_h)//2, store_w, store_h)

        # Pit Rows
        # P2 Top Row
        t_row_y = board_y + 100
        b_row_y = board_y + board_h - 100
        
        start_pit_x = p2_store_rect.right + 20 + pit_radius
        
        # P2 (Top)
        for i in range(6):
            idx = 12-i
            # 12 is leftmost of P2 (closest to their store)
            # Layout: STORE | 12 11 10 9 8 7 |
            x = start_pit_x + i * pit_spacing
            center = (x, t_row_y)
            
            pygame.draw.circle(self.screen, (60,40,20), center, pit_radius)
            pygame.draw.circle(self.screen, ACCENT_COLOR, center, pit_radius, 2)
            self.draw_text(str(self.board[idx]), self.font_small, TEXT_COLOR, center=center)
            
        # P1 (Bottom)
        for i in range(6):
            idx = i
            # 0 is leftmost (Start from left)
            # Layout: | 0 1 2 3 4 5 | STORE
            x = start_pit_x + i * pit_spacing
            center = (x, b_row_y)
            
            pygame.draw.circle(self.screen, (60,40,20), center, pit_radius)
            hl_color = ACCENT_COLOR if (self.current_player==0 and not self.game_over) else (100,100,100)
            pygame.draw.circle(self.screen, hl_color, center, pit_radius, 2)
            self.draw_text(str(self.board[idx]), self.font_small, TEXT_COLOR, center=center)
            
            r = pygame.Rect(0,0, pit_radius*2, pit_radius*2); r.center = center
            self.pit_rects.append((r, idx))
            
        # Draw Stores
        pygame.draw.rect(self.screen, (60,40,20), p2_store_rect, border_radius=10)
        self.draw_text(str(self.board[13]), self.font_med, TEXT_COLOR, center=p2_store_rect.center)
        
        pygame.draw.rect(self.screen, (60,40,20), p1_store_rect, border_radius=10)
        self.draw_text(str(self.board[6]), self.font_med, TEXT_COLOR, center=p1_store_rect.center)
        
        if self.game_over:
            over = pygame.Surface((W, H), pygame.SRCALPHA)
            over.fill((0,0,0,180))
            self.screen.blit(over, (0,0))
            txt = "Draw!"
            if self.winner==0: txt="Player 1 Wins!"
            elif self.winner==1: txt="Player 2 Wins!"
            self.draw_text(txt, pygame.font.SysFont("Arial", 64, bold=True), ACCENT_COLOR, center=(cx, cy))
            
            rst_w, rst_h = 200, 60
            rst = pygame.Rect(cx - rst_w//2, cy + 80, rst_w, rst_h)
            self.draw_button("Menu", rst, active=rst.collidepoint(pygame.mouse.get_pos()))
            self.buttons["reset"] = rst

class GameGUI:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
        pygame.display.set_caption("Kalaha (Mancala)")
        self.clock = pygame.time.Clock()
        self.font_big = pygame.font.SysFont("Arial", 64, bold=True)
        self.font_med = pygame.font.SysFont("Arial", 32)
        self.font_small = pygame.font.SysFont("Arial", 24)
        
        self.state = GameState.TITLE
        self.start_time = time.time()
        
        self.config = { "strategy": "balanced", "depth": 6, "difficulty": "Medium", "ball_color": "Gold" }
        self.strategies = ["basic", "balanced", "aggressive", "defensive", "PPO-Agent"]
        self.difficulties = ["Beginner", "Easy", "Medium", "Hard", "Hell"]
        self.colors = ["Gold", "Red", "Blue", "Green", "White"]
        
        self.slider_rect = pygame.Rect(0, 0, 0, 0)
        self.slider_bar_rect = pygame.Rect(0, 0, 0, 0)
        self.dragging_slider = False
        self.buttons = {}
        
        self.game_screen = None

    def draw_text(self, text, font, color, center=None, top_left=None):
        surf = font.render(text, True, color)
        rect = surf.get_rect(center=center) if center else surf.get_rect(topleft=top_left) if top_left else surf.get_rect()
        self.screen.blit(surf, rect)
        return rect
        
    def draw_button(self, text, rect, active=False):
        color = BUTTON_HOVER if active else BUTTON_COLOR
        pygame.draw.rect(self.screen, color, rect, border_radius=10)
        pygame.draw.rect(self.screen, ACCENT_COLOR, rect, 2, border_radius=10)
        self.draw_text(text, self.font_small, TEXT_COLOR, center=rect.center)
        
    def draw_nav_button(self, text, rect):
        # Draw hitbox box
        pygame.draw.rect(self.screen, BOX_BORDER, rect, 1) # Thin gray border
        self.draw_text(text, self.font_small, ACCENT_COLOR, center=rect.center)

    def handle_title(self):
        W, H = self.screen.get_size()
        if time.time() - self.start_time > 2.0:
            self.state = GameState.HOME
            return
        self.screen.fill(BG_COLOR)
        self.draw_text("Kalaha", self.font_big, ACCENT_COLOR, center=(W//2, H//2 - 40))
        self.draw_text("(Mancala)", self.font_med, TEXT_COLOR, center=(W//2, H//2 + 20))

    def handle_home(self):
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

    def goto_home(self):
        # We also need to clear game_screen to free resources or just logic
        self.game_screen = None # Setting this to None is handled in run loop check
        self.state = GameState.HOME

    def run(self):
        while True:
            events = pygame.event.get()
            for event in events:
                if event.type == pygame.QUIT:
                    pygame.quit(); sys.exit()
                
                if self.state == GameState.HOME:
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
                            self.game_screen = GameScreen(self.screen, self.font_med, self.font_small, self.config, self.goto_home)
                            self.state = GameState.GAME

                    elif event.type == pygame.MOUSEBUTTONUP:
                        self.dragging_slider = False
                    elif event.type == pygame.MOUSEMOTION and self.dragging_slider:
                        self.handle_slider_drag(event.pos)

            if self.state == GameState.TITLE:
                self.handle_title()
            elif self.state == GameState.HOME:
                self.handle_home()
            elif self.state == GameState.GAME:
                # CRITICAL FIX: Check if game_screen exists.
                # If we transition to HOME inside game_screen.update (via goto_home),
                # self.state might become HOME, but we finish this iteration.
                if self.game_screen and self.state == GameState.GAME:
                    self.game_screen.update(events)
                    
                    # Double check state hasn't changed
                    if self.game_screen and self.state == GameState.GAME:
                        self.game_screen.bot_step()
                        self.game_screen.draw()

            pygame.display.flip()
            self.clock.tick(60)

def run_gui():
    GameGUI().run()

if __name__ == "__main__":
    run_gui()
