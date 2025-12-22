import pygame
import sys
import os
import math
import numpy as np

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from trainer import Population, GENERATION_TIME
from cleanup import cleanup_models

# Config
WIDTH = 1200
HEIGHT = 600
BG_COLOR = (40, 40, 45)
RAIL_Y = 400
SCALE = 1.0 

class Visualizer:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Inverted Pendulum AI")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("Consolas", 16)
        self.title_font = pygame.font.SysFont("Consolas", 24, bold=True)
        
        self.trainer = Population()
        
        self.ghost_mode = True
        self.sim_speed = 1.0
        self.time_elapsed = 0.0
        
        self.gen_start_time = pygame.time.get_ticks()

    def run(self):
        running = True
        while running:
            # dt = self.clock.tick(60) / 1000.0
            self.clock.tick(60)
            # Fixed physics step logic handled in trainer?
            # Trainer needs 'dt' for physics.
            # Visualizer runs at 60fps, physics might need smaller steps.
            # Let's do 1 physics update per frame with fixed dt * speed.
            
            raw_dt = 1.0/60.0
            dt = raw_dt * self.sim_speed
            
            # Input
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_g:
                        self.ghost_mode = not self.ghost_mode
                    if event.key == pygame.K_UP:
                        self.sim_speed *= 2.0
                    if event.key == pygame.K_DOWN:
                        self.sim_speed /= 2.0
            
            # Logic
            self.trainer.update(dt)
            self.time_elapsed += dt
            
            # Check Generation End
            if self.trainer.is_generation_done(self.time_elapsed):
                self.trainer.evolve()
                self.time_elapsed = 0.0
                
                # Cleanup every 5 gens
                if self.trainer.generation % 5 == 0:
                     cleanup_models(self.trainer.output_dir)

            # Render
            self.render()
            pygame.display.flip()
            
        self.trainer.shutdown()
        pygame.quit()
        sys.exit()

    def render(self):
        self.screen.fill(BG_COLOR)
        
        # Draw Rail
        pygame.draw.line(self.screen, (200, 200, 200), (WIDTH//2 - 300, RAIL_Y), (WIDTH//2 + 300, RAIL_Y), 4)
        pygame.draw.line(self.screen, (100, 100, 100), (WIDTH//2, RAIL_Y - 10), (WIDTH//2, RAIL_Y + 10), 2) # Center Marker
        
        # Sort agents to draw best last (on top)
        # We don't want to sort the actual list every frame if it messes up index logic in ThreadPool? 
        # ThreadPool works on list objects. Sorting valid.
        # Actually Trainer.update uses chunks, if we sort mid-update it might be bad?
        # Update is sequential to render (single thread coord).
        
        sorted_agents = sorted(self.trainer.agents, key=lambda a: a.fitness, reverse=True)
        best = sorted_agents[0]
        
        # Draw Ghosts
        if self.ghost_mode:
            # Draw top 50% ?
            count = len(sorted_agents) // 2
            for i in range(1, count):
                self.draw_agent(sorted_agents[i], alpha=30)
                
        # Draw Best
        self.draw_agent(best, alpha=255, is_best=True)
        
        # Draw NN
        self.draw_network(best.network)
        
        # Draw HUD
        self.draw_hud(best)

    def draw_agent(self, agent, alpha=255, is_best=False):
        if not agent.alive: return
        
        cx = WIDTH // 2 + agent.x
        cy = RAIL_Y
        
        _, tx, ty = agent.get_tip_pos()
        # tx is relative to cart
        tip_x = WIDTH // 2 + tx
        tip_y = RAIL_Y + ty # ty is negative (up)
        
        # Surface for alpha
        surf = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        
        color = (200, 200, 200)
        if is_best: color = (255, 100, 100)
        
        # Cart
        pygame.draw.rect(surf, (*color, alpha), (cx - 20, cy - 10, 40, 20))
        
        # Pole
        pygame.draw.line(surf, (*color, alpha), (cx, cy), (tip_x, tip_y), 6)
        
        # Joints
        pygame.draw.circle(surf, (50, 50, 50, alpha), (int(cx), int(cy)), 5)
        pygame.draw.circle(surf, (200, 50, 50, alpha), (int(tip_x), int(tip_y)), 8)
        
        self.screen.blit(surf, (0,0))

    def draw_network(self, nn):
        # Draw in bottom left
        start_x = 50
        start_y = HEIGHT - 150
        
        layer_dist = 60
        node_dist = 20
        
        # Inputs (4)
        input_pos = []
        for i in range(4):
            x = start_x
            y = start_y + i * node_dist
            input_pos.append((x, y))
            pygame.draw.circle(self.screen, (255, 255, 255), (x, y), 5)
            
        # Hidden (8)
        hidden_pos = []
        for i in range(8):
            x = start_x + layer_dist
            y = start_y + (i * node_dist) - (2 * node_dist) # Center slightly
            hidden_pos.append((x, y))
            pygame.draw.circle(self.screen, (255, 255, 255), (x, y), 5)
            
        # Output (1)
        out_x = start_x + layer_dist * 2
        out_y = start_y + 1.5 * node_dist
        pygame.draw.circle(self.screen, (255, 255, 255), (out_x, out_y), 5)
        
        # Connections
        # Input -> Hidden
        for i in range(4):
            for j in range(8):
                w = nn.w1[i, j]
                self.draw_weight(input_pos[i], hidden_pos[j], w)
                
        # Hidden -> Output
        for i in range(8):
                w = nn.w2[i, 0]
                self.draw_weight(hidden_pos[i], (out_x, out_y), w)

    def draw_weight(self, start, end, weight):
        thickness = max(1, min(5, int(abs(weight) * 2)))
        color = (100, 255, 100) if weight > 0 else (255, 100, 100)
        # Alpha based on strength?
        pygame.draw.line(self.screen, color, start, end, thickness)

    def draw_hud(self, best_agent):
        panel_w = 250
        panel_h = 100
        pygame.draw.rect(self.screen, (30, 30, 35), (10, 10, panel_w, panel_h), border_radius=10)
        pygame.draw.rect(self.screen, (200, 200, 200), (10, 10, panel_w, panel_h), 2, border_radius=10)
        
        gen_txt = self.title_font.render(f"Generation {self.trainer.generation:03d}", True, (255, 255, 255))
        time_txt = self.font.render(f"Time: {self.time_elapsed:.2f}s", True, (200, 200, 200))
        fit_txt = self.font.render(f"Best Fit: {best_agent.fitness:.2f}", True, (100, 255, 100))
        speed_txt = self.font.render(f"Speed: {self.sim_speed}x", True, (200, 200, 200))
        
        self.screen.blit(gen_txt, (25, 20))
        self.screen.blit(time_txt, (25, 50))
        self.screen.blit(fit_txt, (25, 70))
        self.screen.blit(speed_txt, (140, 50))
        
        # Controls Help
        help_txt = "[G] Ghost Mode | [UP/DOWN] Speed"
        self.screen.blit(self.font.render(help_txt, True, (150, 150, 150)), (10, HEIGHT - 20))

if __name__ == "__main__":
    Visualizer().run()
