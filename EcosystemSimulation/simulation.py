import pygame
import sys
import random
import math
import os

# Ensure import
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from entities import Prey, Predator, WIDTH, HEIGHT

# Config
FPS = 60
BG_COLOR = (40, 40, 45)

class SpatialHash:
    def __init__(self, cell_size):
        self.cell_size = cell_size
        self.grid = {}

    def clear(self):
        self.grid = {}

    def insert(self, entity):
        cx = int(entity.x / self.cell_size)
        cy = int(entity.y / self.cell_size)
        key = (cx, cy)
        if key not in self.grid:
            self.grid[key] = []
        self.grid[key].append(entity)
        
    def get_nearby(self, x, y, radius):
        # Result set
        found = []
        
        cx = int(x / self.cell_size)
        cy = int(y / self.cell_size)
        
        range_cells = int(math.ceil(radius / self.cell_size))
        
        for dx in range(-range_cells, range_cells + 1):
            for dy in range(-range_cells, range_cells + 1):
                key = (cx + dx, cy + dy)
                if key in self.grid:
                    found.extend(self.grid[key])
        return found

class Simulation:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Ecosystem Simulation")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("Consolas", 14)
        
        self.spatial = SpatialHash(150)
        self.entities = []
        
        # Initial Population
        for _ in range(40):
            self.entities.append(Prey(random.uniform(0, WIDTH), random.uniform(0, HEIGHT)))
            
        for _ in range(10):
            self.entities.append(Predator(random.uniform(0, WIDTH), random.uniform(0, HEIGHT)))
            
        self.soft_textures = {} # Cache for soft circle surfaces

    def get_soft_texture(self, radius, color):
        key = (int(radius), color)
        if key in self.soft_textures:
            return self.soft_textures[key]
        
        # Create gradient surface
        size = int(radius * 2.5) # Slightly larger for glow
        surf = pygame.Surface((size, size), pygame.SRCALPHA)
        center = (size//2, size//2)
        
        # Layers
        # Outer glow (low alpha)
        pygame.draw.circle(surf, (*color, 50), center, size//2)
        # Inner core (high alpha)
        pygame.draw.circle(surf, (*color, 200), center, int(radius))
        # Solid center
        pygame.draw.circle(surf, (*color, 255), center, int(radius*0.6))
        
        self.soft_textures[key] = surf
        return surf

    def run(self):
        running = True
        while running:
            dt = 1.0 / 60.0 # Fixed for stability or self.clock.tick()/1000
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                if event.type == pygame.MOUSEBUTTONDOWN:
                    # Spawn debug
                    mx, my = pygame.mouse.get_pos()
                    if event.button == 1:
                        self.entities.append(Prey(mx, my))
                    elif event.button == 3:
                        self.entities.append(Predator(mx, my))
            
            # 1. Spatial Hash Update
            self.spatial.clear()
            for e in self.entities:
                if e.alive:
                    self.spatial.insert(e)
            
            # 2. Logic Update
            new_entities = []
            
            for e in self.entities:
                if not e.alive: continue
                
                # Check Death if Prey eaten?
                # Actually Predator logic checks eating.
                
                # Update (Sense -> Think -> Act)
                res = e.update(dt, self.spatial)
                
                # Handle reproduction
                if res and isinstance(res, (Prey, Predator)):
                    new_entities.append(res)
                    
                # Predator specific: Try to eat
                if isinstance(e, Predator):
                    # Find preys nearby?
                    # Optimization: Just check collision with nearby from spatial
                    nearby = self.spatial.get_nearby(e.x, e.y, e.radius + 20)
                    for other in nearby:
                        if isinstance(other, Prey) and other.alive:
                            if e.try_eat(other):
                                other.alive = False # Mark dead
                                break # One eat per frame
                                
                    # Try reproduce
                    child = e.try_reproduce()
                    if child: new_entities.append(child)

            # Add new
            self.entities.extend(new_entities)
            
            # Prune dead
            self.entities = [e for e in self.entities if e.alive]
            
            # 3. Render
            self.screen.fill(BG_COLOR)
            
            for e in self.entities:
                # Body
                texture = self.get_soft_texture(e.radius, e.color)
                rect = texture.get_rect(center=(e.x, e.y))
                self.screen.blit(texture, rect)
                
                # Eyes
                eye_offset = e.radius * 0.6
                eye_spacing = 0.4
                
                # Front vector
                fx = math.cos(e.angle)
                fy = math.sin(e.angle)
                # Right vector
                rx = -fy
                ry = fx
                
                # Two eyes
                for side in [-1, 1]:
                    ex = e.x + fx * eye_offset + rx * (e.radius * eye_spacing * side)
                    ey = e.y + fy * eye_offset + ry * (e.radius * eye_spacing * side)
                    
                    # Pupil Logic
                    # Min ray dist determines size.
                    # Default relaxed
                    min_dist = 1.0 # Normalized (1=Close, 0=Far in ray results? No inverse)
                    # In entity.py: norm_dist = 1.0 - (dist / range). So 1.0 is CLOSE.
                    
                    # We want close -> big pupil.
                    # Let's find max input from rays (which is proximity)
                    proximity = 0.0
                    if e.ray_results:
                        proximity = max([r[0] for r in e.ray_results])
                    
                    # Map proximity (0..1) to pupil size.
                    # Close (1.0) -> Big pupil.
                    # Far (0.0) -> Small pupil.
                    
                    eye_radius = e.radius * 0.35
                    pupil_radius = eye_radius * (0.3 + 0.5 * proximity)
                    
                    # White
                    pygame.draw.circle(self.screen, (255, 255, 255), (int(ex), int(ey)), int(eye_radius))
                    # Pupil
                    pygame.draw.circle(self.screen, (0, 0, 0), (int(ex), int(ey)), int(pupil_radius))
            
            # Stats
            prey_count = sum(1 for e in self.entities if isinstance(e, Prey))
            pred_count = sum(1 for e in self.entities if isinstance(e, Predator))
            
            txt = self.font.render(f"Prey: {prey_count} | Predators: {pred_count} | FPS: {self.clock.get_fps():.1f}", True, (200, 200, 200))
            self.screen.blit(txt, (10, 10))

            pygame.display.flip()
            self.clock.tick(FPS)

        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    Simulation().run()
