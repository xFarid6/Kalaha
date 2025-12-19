import pygame
import sys
import time

# Colors (Brown/Gold Aesthetic)
BG_COLOR = (40, 26, 13)         # Deep Coffee
TEXT_COLOR = (245, 245, 220)    # Cream
ACCENT_COLOR = (218, 165, 32)   # Gold
BUTTON_COLOR = (101, 67, 33)    # Dark Wood
BUTTON_HOVER = (139, 69, 19)    # Saddle Brown

# Constants
WIDTH, HEIGHT = 800, 600

class GameGUI:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Kalaha (Mancala)")
        self.clock = pygame.time.Clock()
        self.font_big = pygame.font.SysFont("Arial", 64, bold=True)
        self.font_med = pygame.font.SysFont("Arial", 32)
        self.font_small = pygame.font.SysFont("Arial", 24)
        
        # State
        self.state = "TITLE" # TITLE, HOME, GAME
        self.start_time = time.time()
        
        # Config Defaults
        self.config = {
            "strategy": "balanced",
            "depth": 6,
            "difficulty": "Medium",
            "ball_color": "Gold"
        }
        
        # Presets
        self.strategies = ["basic", "balanced", "aggressive", "defensive", "PPO-Agent"]
        self.difficulties = ["Beginner", "Easy", "Medium", "Hard", "Hell"]
        self.colors = ["Gold", "Red", "Blue", "Green", "White"]
        
        # Slider Interaction
        self.slider_rect = pygame.Rect(0, 0, 0, 0)
        self.slider_bar_rect = pygame.Rect(0, 0, 0, 0) # Initialize this too
        self.dragging_slider = False
        
        # UI Elements (Rects)
        self.buttons = {}

    def draw_text(self, text, font, color, center=None, top_left=None):
        surf = font.render(text, True, color)
        if center:
            rect = surf.get_rect(center=center)
        elif top_left:
            rect = surf.get_rect(topleft=top_left)
        else:
            rect = surf.get_rect() # default 0,0
            
        self.screen.blit(surf, rect)
        return rect
        
    def draw_button(self, text, rect, active=False):
        color = BUTTON_HOVER if active else BUTTON_COLOR
        pygame.draw.rect(self.screen, color, rect, border_radius=10)
        pygame.draw.rect(self.screen, ACCENT_COLOR, rect, 2, border_radius=10)
        self.draw_text(text, self.font_small, TEXT_COLOR, center=rect.center)

    def handle_title(self):
        # Auto transition after 2 seconds
        if time.time() - self.start_time > 2.0:
            self.state = "HOME"
            return

        self.screen.fill(BG_COLOR)
        self.draw_text("Kalaha", self.font_big, ACCENT_COLOR, center=(WIDTH//2, HEIGHT//2 - 40))
        self.draw_text("(Mancala)", self.font_med, TEXT_COLOR, center=(WIDTH//2, HEIGHT//2 + 20))

    def handle_home(self):
        self.screen.fill(BG_COLOR)
        
        # Header
        self.draw_text("Setup Game", self.font_big, ACCENT_COLOR, center=(WIDTH//2, 80))
        
        # Config Rows
        y = 180
        x_label = 250
        x_val = 550
        
        # Strategy
        self.draw_text("Strategy:", self.font_med, TEXT_COLOR, center=(x_label, y))
        self.draw_text(f"< {self.config['strategy']} >", self.font_med, ACCENT_COLOR, center=(x_val, y))
        self.buttons["strategy_prev"] = pygame.Rect(x_val - 140, y - 15, 30, 30)
        self.buttons["strategy_next"] = pygame.Rect(x_val + 110, y - 15, 30, 30)
        
        y += 70
        # Difficulty
        self.draw_text("Difficulty:", self.font_med, TEXT_COLOR, center=(x_label, y))
        self.draw_text(f"< {self.config['difficulty']} >", self.font_med, ACCENT_COLOR, center=(x_val, y))
        self.buttons["diff_prev"] = pygame.Rect(x_val - 140, y - 15, 30, 30)
        self.buttons["diff_next"] = pygame.Rect(x_val + 110, y - 15, 30, 30)
        
        y += 70
        # Depth Slider
        self.draw_text(f"Depth ({self.config['depth']}):", self.font_med, TEXT_COLOR, center=(x_label, y))
        
        # Slider Bar
        bar_rect = pygame.Rect(x_val - 100, y-5, 200, 10)
        pygame.draw.rect(self.screen, BUTTON_COLOR, bar_rect, border_radius=5)
        
        # Slider Handle
        # Map depth 1-20 to x pos
        ratio = (self.config['depth'] - 1) / 19
        handle_x = bar_rect.x + (ratio * bar_rect.width)
        handle_rect = pygame.Rect(handle_x - 10, y - 15, 20, 30)
        
        pygame.draw.rect(self.screen, ACCENT_COLOR, handle_rect, border_radius=5)
        self.slider_rect = handle_rect
        self.slider_bar_rect = bar_rect # For clicking on bar

        y += 70
        # Ball Color
        self.draw_text("Ball Color:", self.font_med, TEXT_COLOR, center=(x_label, y))
        self.draw_text(f"< {self.config['ball_color']} >", self.font_med, ACCENT_COLOR, center=(x_val, y))
        self.buttons["color_prev"] = pygame.Rect(x_val - 140, y - 15, 30, 30)
        self.buttons["color_next"] = pygame.Rect(x_val + 110, y - 15, 30, 30)

        # PLAY Button
        play_rect = pygame.Rect(WIDTH//2 - 100, HEIGHT - 100, 200, 60)
        self.draw_button("PLAY", play_rect, active=play_rect.collidepoint(pygame.mouse.get_pos()))
        self.buttons["play"] = play_rect
        
        # Instructions
        instr_text = "Instructions:\n- Click < > to change settings\n- Drag slider for Depth\n- 'Custom' difficulty sets manual depth"
        lines = instr_text.split('\n')
        iy = HEIGHT - 80
        for line in lines:
            self.draw_text(line, self.font_small, (150, 150, 150), top_left=(20, iy))
            iy += 25

    def cycle_option(self, key, options, direction):
        idx = options.index(self.config[key])
        new_idx = (idx + direction) % len(options)
        self.config[key] = options[new_idx]
        
    def update_difficulty_preset(self):
        mapping = {
            "Beginner": 2,
            "Easy": 4,
            "Medium": 6,
            "Hard": 10,
            "Hell": 14 
        }
        if self.config['difficulty'] in mapping:
            self.config['depth'] = mapping[self.config['difficulty']]

    def handle_slider_drag(self, pos):
        # Calculate new depth based on x position relative to bar
        bar = self.slider_bar_rect
        rel_x = pos[0] - bar.x
        ratio = max(0, min(1, rel_x / bar.width))
        new_depth = int(1 + ratio * 19) # 1 to 20
        
        if new_depth != self.config['depth']:
            self.config['depth'] = new_depth
            # If sliding, switch to Custom difficulty unless it matches a preset exactly?
            # Simpler to just switch to Custom to indicate manual override
            self.config['difficulty'] = "Custom"

    def run(self):
        running = True
        while running:
            # Events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                
                if self.state == "HOME":
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        pos = event.pos
                        
                        # Strategy
                        if self.buttons.get("strategy_prev", pygame.Rect(0,0,0,0)).collidepoint(pos):
                            self.cycle_option("strategy", self.strategies, -1)
                        if self.buttons.get("strategy_next", pygame.Rect(0,0,0,0)).collidepoint(pos):
                            self.cycle_option("strategy", self.strategies, 1)

                        # Difficulty
                        if self.buttons.get("diff_prev", pygame.Rect(0,0,0,0)).collidepoint(pos):
                            self.cycle_option("difficulty", self.difficulties, -1)
                            self.update_difficulty_preset()
                        if self.buttons.get("diff_next", pygame.Rect(0,0,0,0)).collidepoint(pos):
                            self.cycle_option("difficulty", self.difficulties, 1)
                            self.update_difficulty_preset()
                            
                        # Color
                        if self.buttons.get("color_prev", pygame.Rect(0,0,0,0)).collidepoint(pos):
                            self.cycle_option("ball_color", self.colors, -1)
                        if self.buttons.get("color_next", pygame.Rect(0,0,0,0)).collidepoint(pos):
                            self.cycle_option("ball_color", self.colors, 1)
                            
                        # Play
                        if self.buttons.get("play", pygame.Rect(0,0,0,0)).collidepoint(pos):
                            print(f"Starting Game with {self.config}")
                            # Transition to GAME state
                        
                        # Slider Click
                        if self.slider_rect.collidepoint(pos) or self.slider_bar_rect.collidepoint(pos):
                            self.dragging_slider = True
                            self.handle_slider_drag(pos)
                            
                    elif event.type == pygame.MOUSEBUTTONUP:
                        self.dragging_slider = False
                        
                    elif event.type == pygame.MOUSEMOTION:
                        if self.dragging_slider:
                            self.handle_slider_drag(event.pos)

            # Drawing
            if self.state == "TITLE":
                self.handle_title()
            elif self.state == "HOME":
                self.handle_home()
            
            pygame.display.flip()
            self.clock.tick(60)

        pygame.quit()
        sys.exit()

def run_gui():
    app = GameGUI()
    app.run()

if __name__ == "__main__":
    run_gui()
