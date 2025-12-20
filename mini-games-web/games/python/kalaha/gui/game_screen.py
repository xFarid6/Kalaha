import pygame
import sys
import os
import time
import numpy as np
from typing import List, Tuple, Dict, Any, Optional
from sb3_contrib import MaskablePPO # type: ignore

from kalaha.gui.constants import (
    BG_COLOR, TEXT_COLOR, ACCENT_COLOR, BUTTON_COLOR, BUTTON_HOVER,
    BORDER_BOARD, BORDER_STORE, ScreenState
)

# Imports with fallback or absolute paths
try:
    from kalaha.game_logic import (
        initial_state, legal_moves, apply_move, is_terminal, cleanup_board, 
        get_sowing_path
    )
    from kalaha.ai_engine import get_best_move
    from kalaha.endgame_db import endgame_db
except ImportError:
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
    from kalaha.game_logic import (
        initial_state, legal_moves, apply_move, is_terminal, cleanup_board, 
        get_sowing_path
    )
    from kalaha.ai_engine import get_best_move
    from kalaha.endgame_db import endgame_db

class GameScreen:
    def __init__(self, screen: pygame.Surface, font_med: pygame.font.Font, font_small: pygame.font.Font, config: Dict[str, Any], on_exit: Any) -> None:
        self.screen = screen
        self.font_med = font_med
        self.font_small = font_small
        self.config = config
        self.on_exit = on_exit # Callback to go back up
        
        self.game_logic = {
            'initial_state': initial_state, 
            'legal': legal_moves, 
            'apply': apply_move, 
            'terminal': is_terminal, 
            'cleanup': cleanup_board,
            'ai': get_best_move,
            'db': endgame_db,
            'get_path': get_sowing_path
        }

        self.rl_model: Optional[MaskablePPO] = None
        
        # State
        self.state: ScreenState = ScreenState.IDLE # IDLE, THINKING, ANIMATING, UNDO_ANIMATING
        self.anim_queue: List[int] = [] # List of pit indices to highlight
        self.anim_timer: float = 0
        self.anim_current_idx: Optional[int] = None
        self.anim_move_idx: int = -1
        
        self.last_move_nodes: int = 0
        self.total_nodes_analyzed: int = 0
        self.bot_choices: List[int] = [] # Track all bot choices
        
        # Game history for UNDO feature (hash-based to save memory)
        self.game_history: List[Dict[str, Any]] = []
        
        # UNDO feature: store hashes + minimal data
        self.undo_history: List[Dict[str, Any]] = []
        self.MAX_UNDOS: int = 20
        
        self.bot_thinking_start: float = 0
        self.board: List[int] = []
        self.current_player: int = 0
        self.game_over: bool = False
        self.winner: int = -1
        self.is_bot: bool = True
        self.pit_rects: List[Tuple[pygame.Rect, int]] = []
        self.buttons: Dict[str, pygame.Rect] = {}
        
        self.reset_game()

    def reset_game(self) -> None:
        self.board = self.game_logic['initial_state']()
        self.current_player = 0
        self.game_over = False
        self.winner = -1
        self.is_bot = True # Default P2=Bot
        self.pit_rects = []
        self.buttons = {}
        self.state = ScreenState.IDLE
        self.anim_queue = []
        self.last_move_nodes = 0
        self.total_nodes_analyzed = 0
        self.bot_choices = []
        
        # Initialize game history with starting state
        self.game_history = [{
            'board': self.board.copy(),
            'current_player': self.current_player,
            'move_that_led_here': None,
            'timestamp': time.time()
        }]
        
        # Initialize undo history with starting state (hash-based)
        self.undo_history = [{
            'board_hash': hash(tuple(self.board)),
            'board': self.board.copy(),  # Keep for reconstruction
            'current_player': self.current_player,
            'move_that_led_here': None
        }]
        
    def undo_move(self) -> bool:
        """Undo the last move. Returns True if successful."""
        if len(self.undo_history) <= 1:  # Only initial state
            return False
            
        if self.state != ScreenState.IDLE:  # Safety check
            return False
            
        # Reverse animation
        if len(self.undo_history) >= 2:
            prev_state = self.undo_history[-2]
            current_state = self.undo_history[-1]
            move = current_state['move_that_led_here']
            
            if move is not None:
                # Calculate reverse path
                path = self.game_logic['get_path'](prev_state['board'], move, prev_state['current_player'])
                self.anim_queue = list(reversed(path))
                self.state = ScreenState.UNDO_ANIMATING
                self.anim_timer = time.time()
        
        # Pop current state
        self.undo_history.pop()
        
        # Restore previous
        prev_state = self.undo_history[-1]
        self.board = prev_state['board'].copy()
        self.current_player = prev_state['current_player']
        
        # Also update game_history for consistency
        if len(self.game_history) > 1:
            self.game_history.pop()
        
        return True
        
    def load_rl_model(self) -> Optional[MaskablePPO]:
        if self.rl_model: return self.rl_model
        try:
            model_path = os.path.join("models", "kalaha_latest.zip")
            if not os.path.exists(model_path):
                 model_path = os.path.join("..", "models", "kalaha_latest.zip")
                 
            if os.path.exists(model_path):
                self.rl_model = MaskablePPO.load(model_path)
                return self.rl_model
        except Exception as e:
            print(f"Failed to load RL model: {e}")
            pass
        return None

    def get_rl_move(self, board: List[int], player: int) -> Optional[int]:
        model = self.load_rl_model()
        if not model: return None
        
        obs = np.zeros(15, dtype=np.int32)
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

    def trigger_move(self, idx: int) -> None:
        # Calculate animation path
        path = self.game_logic['get_path'](self.board, idx, self.current_player)
        self.anim_queue = path
        self.state = ScreenState.ANIMATING
        self.anim_timer = time.time()
        self.anim_move_idx = idx

    def update(self, events: List[pygame.event.Event]) -> None:
        current_time = time.time()
        
        # Handle Animation (normal forward)
        if self.state == ScreenState.ANIMATING:
            if not self.anim_queue:
                # Animation Done, Apply Logic
                self._apply_move_logic(self.anim_move_idx)
                self.state = ScreenState.IDLE
                self.anim_current_idx = None
            else:
                sow_delay = self.config.get('anim_speed', 0.5)
                # If time passed, pop next
                if current_time - self.anim_timer > sow_delay:
                    self.anim_current_idx = self.anim_queue.pop(0)
                    self.anim_timer = current_time
            return # Block interaction during animation
        
        # Handle UNDO Animation (backwards)
        if self.state == ScreenState.UNDO_ANIMATING:
            if not self.anim_queue:
                # UNDO animation complete
                self.state = ScreenState.IDLE
                self.anim_current_idx = None
            else:
                sow_delay = self.config.get('anim_speed', 0.5) * 0.7  # Slightly faster for undo
                if current_time - self.anim_timer > sow_delay:
                    self.anim_current_idx = self.anim_queue.pop(0)
                    self.anim_timer = current_time
            return

        # Handle Bot Thinking Delay
        if self.state == ScreenState.THINKING:
            # Add artificial delay 0.5s + computation
            if current_time - self.bot_thinking_start > 0.5:
                self.execute_bot_move()
            return

        # Handle Input
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN:
                pos = event.pos
                if self.game_over:
                    if self.buttons.get("reset", pygame.Rect(0,0,0,0)).collidepoint(pos):
                        self.on_exit()
                else:
                    # Check UNDO button
                    if self.buttons.get("undo", pygame.Rect(0,0,0,0)).collidepoint(pos):
                        if self.undo_move():
                            print("Move undone!")
                    
                    if self.current_player == 0 or not self.is_bot:
                        # Only allow legal moves
                        moves = self.game_logic['legal'](self.board, self.current_player)
                        for rect, idx in self.pit_rects:
                            if rect.collidepoint(pos):
                                if idx in moves:
                                    self.trigger_move(idx)
                                    
    def bot_step(self) -> None:
        # Check if we should start bot thinking
        if self.state == ScreenState.IDLE and not self.game_over and self.is_bot and self.current_player == 1:
            self.state = ScreenState.THINKING
            self.bot_thinking_start = time.time()

    def execute_bot_move(self) -> None:
        move = None
        nodes = 0
        if self.config['strategy'] == 'PPO-Agent':
             move = self.get_rl_move(self.board, self.current_player)
             nodes = 1 # RL is instant
        else:
             move, nodes = self.game_logic['ai'](self.board, self.current_player, depth=self.config['depth'], strategy=self.config['strategy'])
        
        self.last_move_nodes = nodes
        self.total_nodes_analyzed += nodes
        
        if move is not None:
            self.bot_choices.append(move)
            self.trigger_move(move)
        else:
            self.state = ScreenState.IDLE # Should not happen if game not over

    def _apply_move_logic(self, idx: int) -> None:
        self.board, extra = self.game_logic['apply'](self.board, idx, self.current_player)
        if not extra:
            self.current_player = 1 - self.current_player
        
        # Record state in history
        self.game_history.append({
            'board': self.board.copy(),
            'current_player': self.current_player,
            'move_that_led_here': idx,
            'timestamp': time.time()
        })
        
        # Record state in undo history (hash-based)
        self.undo_history.append({
            'board_hash': hash(tuple(self.board)),
            'board': self.board.copy(),
            'current_player': self.current_player,
            'move_that_led_here': idx
        })
        
        # Limit undo history to MAX_UNDOS
        if len(self.undo_history) > self.MAX_UNDOS + 1:  # +1 for initial state
            self.undo_history.pop(0)
        
        if self.game_logic['terminal'](self.board):
            self.board = self.game_logic['cleanup'](self.board)
            self.game_over = True
            p1 = self.board[6]; p2 = self.board[13]
            self.winner = 0 if p1 > p2 else 1 if p2 > p1 else 2
            self.game_logic['db'].save()

    def draw_text(self, text: str, font: pygame.font.Font, color: Tuple[int,int,int], center: Optional[Tuple[int,int]] = None, top_left: Optional[Tuple[int,int]] = None, right: Optional[Tuple[int,int]] = None) -> pygame.Rect:
        surf = font.render(text, True, color)
        if center: rect = surf.get_rect(center=center)
        elif top_left: rect = surf.get_rect(topleft=top_left)
        elif right: rect = surf.get_rect(topright=right)
        else: rect = surf.get_rect()
        self.screen.blit(surf, rect)
        return rect
        
    def draw_button(self, text: str, rect: pygame.Rect, active: bool = False) -> None:
        color = BUTTON_HOVER if active else BUTTON_COLOR
        pygame.draw.rect(self.screen, color, rect, border_radius=10)
        pygame.draw.rect(self.screen, ACCENT_COLOR, rect, 2, border_radius=10)
        self.draw_text(text, self.font_small, TEXT_COLOR, center=rect.center)

    def draw(self) -> None:
        # Responsive 5-Zone Layout
        W, H = self.screen.get_size()
        
        # Dimensions for zones
        top_bar_h = 80
        bottom_bar_h = 100
        left_sidebar_w = 250
        right_sidebar_w = 200 # For hints/extra
        
        # Main Board Area Calculation
        board_area_rect = pygame.Rect(
            left_sidebar_w, 
            top_bar_h, 
            W - left_sidebar_w - right_sidebar_w, 
            H - top_bar_h - bottom_bar_h
        )
        
        self.screen.fill(BG_COLOR)
        
        # === TOP BAR (Status) ===
        status = f"Player {self.current_player + 1}"
        if self.is_bot and self.current_player == 1: status += " (Bot)"
        self.draw_text(f"Turn: {status}", self.font_med, ACCENT_COLOR, center=(W//2, top_bar_h//2))
        
        if self.state == ScreenState.ANIMATING:
            status_txt = "Distributing..."
        elif self.state == ScreenState.THINKING:
            status_txt = "Thinking..."
        else:
            status_txt = "Waiting..."
        self.draw_text(status_txt, self.font_small, (150,150,150), center=(W//2, top_bar_h//2 + 30))

        # === LEFT SIDEBAR (Stats & Config) ===
        # Background for sidebar (optional, just use BG_COLOR)
        panel_x = 20
        panel_y = top_bar_h + 20
        
        self.draw_text("SCORE", self.font_med, ACCENT_COLOR, top_left=(panel_x, panel_y)); panel_y+=40
        self.draw_text(f"P1: {self.board[6]}", self.font_small, TEXT_COLOR, top_left=(panel_x, panel_y)); panel_y+=30
        self.draw_text(f"P2: {self.board[13]}", self.font_small, TEXT_COLOR, top_left=(panel_x, panel_y)); panel_y+=50
        
        self.draw_text("CONFIG", self.font_med, ACCENT_COLOR, top_left=(panel_x, panel_y)); panel_y+=40
        self.draw_text(f"{self.config['strategy']}", self.font_small, TEXT_COLOR, top_left=(panel_x, panel_y)); panel_y+=30
        self.draw_text(f"{self.config['difficulty']}", self.font_small, TEXT_COLOR, top_left=(panel_x, panel_y)); panel_y+=30
        self.draw_text(f"Depth: {self.config['depth']}", self.font_small, TEXT_COLOR, top_left=(panel_x, panel_y)); panel_y+=50
        
        self.draw_text("STATS", self.font_med, ACCENT_COLOR, top_left=(panel_x, panel_y)); panel_y+=40
        self.draw_text(f"Last move nodes: {self.last_move_nodes}", self.font_small, TEXT_COLOR, top_left=(panel_x, panel_y)); panel_y+=30
        self.draw_text(f"Total nodes analyzed: {self.total_nodes_analyzed}", self.font_small, TEXT_COLOR, top_left=(panel_x, panel_y)); panel_y+=30

        # === RIGHT SIDEBAR (Hints) ===
        # AI Hint
        hint = self.get_rl_move(self.board, self.current_player)
        hint_x = W - right_sidebar_w + 20
        hint_y = top_bar_h + 20
        if hint is not None:
            rel = hint+1 if self.current_player==0 else hint-7+1
            self.draw_text(f"AI Hint: Pit {rel}", self.font_small, (100, 200, 100), top_left=(hint_x, hint_y))

        # === BOARD AREA ===
        # Padding within the board area
        padding = 20
        draw_rect = board_area_rect.inflate(-padding*2, -padding*2)
        
        # Max out the board size while maintaining aspect ratio or just filling
        # Logic: We want to fill this specific draw_rect
        # Draw Border
        pygame.draw.rect(self.screen, BORDER_BOARD, draw_rect, border_radius=20)
        # Add a thicker outline
        pygame.draw.rect(self.screen, ACCENT_COLOR, draw_rect, 2, border_radius=20)
        
        # Calculate proportional coordinates
        cx = draw_rect.centerx
        cy = draw_rect.centery
        bw = draw_rect.width
        bh = draw_rect.height
        
        # Stores
        store_w = bw * 0.12 # 12% width
        store_h = bh * 0.7  # 70% height
        
        # P2 Store (Left)
        p2_store_rect = pygame.Rect(draw_rect.x + 20, cy - store_h/2, store_w, store_h)
        # P1 Store (Right) - Ensure correct spacing
        p1_store_rect = pygame.Rect(draw_rect.right - 20 - store_w, cy - store_h/2, store_w, store_h)
        
        # Pits Area
        # Space between stores
        pits_area_w = (p1_store_rect.x - 20) - (p2_store_rect.right + 20)
        pit_spacing = pits_area_w / 6
        pit_radius = min(pit_spacing / 2.5, bh * 0.15) # Scale radius
        
        start_pit_x = p2_store_rect.right + 20 + (pit_spacing/2)
        
        t_row_y = cy - (bh * 0.15)
        b_row_y = cy + (bh * 0.15)
        
        self.pit_rects = []
        
        # Draw Pits
        for i in range(6):
            # P2 (Top)
            idx = 12-i
            x = start_pit_x + i * pit_spacing
            center = (x, t_row_y)
            self.draw_pit(idx, center, int(pit_radius))

            # P1 (Bottom)
            idx_p1 = i
            x = start_pit_x + i * pit_spacing
            center = (x, b_row_y)
            self.draw_pit(idx_p1, center, int(pit_radius))
            
            # Clickable handling for P1
            # Hitbox can be slightly larger
            r = pygame.Rect(0,0, pit_radius*2.2, pit_radius*2.2); r.center = center
            self.pit_rects.append((r, idx_p1))

        # Draw Stores with distinct border
        pygame.draw.rect(self.screen, (60,40,20), p2_store_rect, border_radius=10)
        pygame.draw.rect(self.screen, BORDER_STORE, p2_store_rect, 4, border_radius=10) # Thicker distinct border
        self.draw_text(str(self.board[13]), self.font_med, TEXT_COLOR, center=p2_store_rect.center)
        
        pygame.draw.rect(self.screen, (60,40,20), p1_store_rect, border_radius=10)
        pygame.draw.rect(self.screen, BORDER_STORE, p1_store_rect, 4, border_radius=10) # Thicker distinct border
        self.draw_text(str(self.board[6]), self.font_med, TEXT_COLOR, center=p1_store_rect.center)
        
        # === BOTTOM BAR (Controls) ===
        # UNDO Button
        if not self.game_over and len(self.undo_history) > 1:
            undo_w, undo_h = 180, 50
            undo_x = 30
            undo_y = H - bottom_bar_h + 25
            undo_rect = pygame.Rect(undo_x, undo_y, undo_w, undo_h)
            
            is_active = undo_rect.collidepoint(pygame.mouse.get_pos()) and self.state == ScreenState.IDLE
            self.draw_button(f"← UNDO ({len(self.undo_history)-1})", undo_rect, active=is_active)
            self.buttons["undo"] = undo_rect
            
            # Show undo count
            undos_available = min(len(self.undo_history) - 1, self.MAX_UNDOS)
            self.draw_text(f"{undos_available}/{self.MAX_UNDOS} undos", self.font_small, (150,150,150), 
                          top_left=(undo_x, undo_y + undo_h + 5))
        
        # === OVERLAYS ===
        if self.game_over:
            over = pygame.Surface((W, H), pygame.SRCALPHA)
            over.fill((0,0,0,180))
            self.screen.blit(over, (0,0))
            txt = "Draw!"
            if self.winner==0: txt="Player 1 Wins!"
            elif self.winner==1: txt="Player 2 Wins!"
            self.draw_text(txt, pygame.font.SysFont("Arial", 64, bold=True), ACCENT_COLOR, center=(W//2, H//2))
            
            rst_w, rst_h = 200, 60
            rst = pygame.Rect(W//2 - rst_w//2, H//2 + 80, rst_w, rst_h)
            self.draw_button("Menu", rst, active=rst.collidepoint(pygame.mouse.get_pos()))
            self.buttons["reset"] = rst

    def draw_pit(self, idx: int, center: Tuple[float, float], radius: int) -> None:
        # Color Logic
        fill = (60,40,20)
        
        # Highlight Logic
        if self.state == ScreenState.ANIMATING and self.anim_current_idx == idx:
            fill = (150, 100, 50) # Highlight Color
            
        pygame.draw.circle(self.screen, fill, center, radius)
        
        # Ouline - distinct for player side logic
        outline = ACCENT_COLOR
        if self.current_player == 0 and idx < 7 and not self.game_over:
             outline = ACCENT_COLOR
        else:
             outline = (80,60,40)
             
        pygame.draw.circle(self.screen, outline, center, radius, 2)
        self.draw_text(str(self.board[idx]), self.font_small, TEXT_COLOR, center=center)
