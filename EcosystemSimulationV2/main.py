import pygame
import sys
import random
import os
import time
import math

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from store import DataStore, MAX_AGENTS
from scheduler import TaskScheduler
from grid import UniformGrid
from nn_graph import generate_nn_structure, mutate_agent_nn
from systems import sys_movement, sys_vision, sys_brain, sys_energy, RAY_COUNT

# Config
WIDTH = 512
HEIGHT = 512
BG_COLOR = (20, 20, 25)
FPS = 60

class SimulationV2:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Ecosystem V2 (DOD + Multithreaded)")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("Consolas", 14)
        
        self.store = DataStore()
        self.scheduler = TaskScheduler(num_threads=4) 
        self.grid = UniformGrid()
        
        self.paused = False
        
        # Spawn Initial
        self.spawn_agents(1500, type_id=0) # Prey
        self.spawn_agents(100, type_id=1)  # Predator

    def spawn_agents(self, count, type_id):
        input_count = 2 + RAY_COUNT * 2 # Bias, Energy, (Dist, Type) * Rays
        output_count = 2 # Speed, Turn
        
        for _ in range(count):
            idx = self.store.allocate_agent()
            if idx == -1: break
            
            self.store.pos[idx, 0] = random.uniform(0, WIDTH)
            self.store.pos[idx, 1] = random.uniform(0, HEIGHT)
            self.store.angle[idx] = random.uniform(0, 6.28)
            self.store.type[idx] = type_id
            
            if type_id == 0: # Prey
                self.store.color[idx] = (100, 255, 100)
                self.store.energy[idx] = 100
                self.store.radius[idx] = 4
            else: # Predator
                self.store.color[idx] = (255, 50, 50)
                self.store.energy[idx] = 150
                self.store.radius[idx] = 6
                
            generate_nn_structure(self.store, idx, input_count, output_count)

    def run(self):
        running = True
        
        while running:
            # dt = self.clock.tick(FPS) / 1000.0
            self.clock.tick(FPS)
            dt = 1.0/60.0 # Fixed step for logic stability
            
            # Events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        self.paused = not self.paused

            if not self.paused:
                self.update_logic(dt)
            
            self.render()
            
            # HUD
            fps = self.clock.get_fps()
            alive_count = self.store.count # Approximation
            # Real alive could be checked
            # txt = f"FPS: {fps:.1f} | Agents: {alive_count}"
            # self.screen.blit(self.font.render(txt, True, (200, 200, 200)), (10, 10))
            
            pygame.display.flip()
            
        self.scheduler.shutdown()
        pygame.quit()
        sys.exit()

    def update_logic(self, dt):
        # 1. Identify active agents
        # We need a list of indices for the scheduler
        # Optimization: Store maintain this list or we filter 'alive' mask
        # Filtering inside python loop is slow.
        # Numpy where is fast.
        
        # indices = np.where(self.store.alive)[0] # Returns tuple
        # But we want list for scheduler chunks? Scheduler accepts numpy array slice? 
        # Scheduler chunks list. Numpy indexing works.
        
        active_indices = list(self.store.active_indices) # If we maintain it
        # Wait, I didn't verify `active_indices` maintenance in store.py.
        # store.py implementation was: `self.active_indices = []` at init, 
        # but `allocate_agent` didn't append to it.
        # Let's fix that assumption or just scan. 
        # For 1600 agents, scanning 2000 boolean flags is negligible.
        
        import numpy as np
        active_indices = np.where(self.store.alive)[0]
        
        if len(active_indices) == 0: return

        # 2. Update Grid (Single Threaded)
        self.grid.update(self.store, active_indices)
        
        # 3. Vision (Multithreaded)
        # Needs Store + Grid
        self.scheduler.run_system(sys_vision, self.store, active_indices, self.grid)
        
        # 4. Brain (Multithreaded)
        self.scheduler.run_system(sys_brain, self.store, active_indices, dt)
        
        # 5. Movement (Multithreaded)
        self.scheduler.run_system(sys_movement, self.store, active_indices, dt, WIDTH, HEIGHT)
        
        # 6. Energy/Logic (Multithreaded)
        self.scheduler.run_system(sys_energy, self.store, active_indices, dt)

    def render(self):
        self.screen.fill(BG_COLOR)
        
        active_indices = list(self.store.active_indices) # Wrong assumption?
        # Let's use the same numpy scan.
        # Inside render loop, python is slow.
        # Ideally we batch render points?
        # Pygame doesn't do batch points easily with variable radius.
        
        # Iterate numpy array directly
        # Faster to iterate native list of indices
        import numpy as np
        indices = np.where(self.store.alive)[0]
        
        # Lock not needed for read if logic is paused or sequential
        
        # Bulk read arrays for perf?
        # pos = self.store.pos[indices]
        # color = self.store.color[indices]
        # rad = self.store.radius[indices]
        # angle = self.store.angle[indices]
        
        # Python loop is the bottleneck here.
        # For 1600 agents, it's roughly 1600 draw calls. Pygame can handle 1600 circles at 60fps usually.
        
        for idx in indices:
            x = int(self.store.pos[idx, 0])
            y = int(self.store.pos[idx, 1])
            r = int(self.store.radius[idx])
            col = self.store.color[idx]
            
            # Body
            pygame.draw.circle(self.screen, col, (x, y), r)
            
            # Eyes/Direction
            ang = self.store.angle[idx]
            ex = x + math.cos(ang) * (r * 0.8)
            ey = y + math.sin(ang) * (r * 0.8)
            
            pygame.draw.circle(self.screen, (255, 255, 255), (int(ex), int(ey)), 2)

if __name__ == "__main__":
    SimulationV2().run()
