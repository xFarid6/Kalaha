import pygame
import sys
import random
import math
import os

# Ensure import
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from solver import Solver, Particle

# Config
SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 800
BG_COLOR = (30, 30, 30)

def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Verlet Solver - 2400 Objects")
    clock = pygame.time.Clock()
    
    solver = Solver(SCREEN_WIDTH, SCREEN_HEIGHT)
    
    # Spawn 2400 particles
    # To fit them, we spawn them in a grid pattern initially to avoid massive overlap explosion
    count = 0
    cols = 50
    start_x = 200
    start_y = 100
    spacing = 10
    
    # Palette
    colors = [
        (255, 100, 100), (100, 255, 100), (100, 100, 255), 
        (255, 255, 100), (255, 100, 255), (100, 255, 255)
    ]
    
    print("Spawning particles...")
    
    for i in range(2400):
        # Varying radius
        radius = random.choice([3, 4, 5, 8, 12]) if random.random() > 0.05 else 15
        
        # Grid spawn
        row = i // cols
        col = i % cols
        x = start_x + col * spacing
        y = start_y + row * spacing
        
        # Jitter
        x += random.uniform(-1, 1)
        
        color = random.choice(colors)
        
        p = Particle(x, y, radius, color)
        solver.add_particle(p)
        count += 1
        
    print(f"Spawned {count} particles.")

    running = True
    while running:
        # Input
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        
        # Physics Update
        # Fixed dt for stability
        solver.update(1.0 / 60.0)
        
        # Render
        screen.fill(BG_COLOR)
        
        # Draw Container
        pygame.draw.circle(screen, (50, 50, 50), (solver.container_center_x, solver.container_center_y), solver.container_radius)
        
        # Draw Particles
        # Batch drawing? Pygame doesn't straightforwardly support batch geometry besides blits.
        # Minimal state change approach: Group by color maybe?
        # For now, just draw.
        for p in solver.particles:
            # Cast to int
            ix, iy = int(p.x), int(p.y)
            pygame.draw.circle(screen, p.color, (ix, iy), p.radius)
            
        # Draw Info
        fps = clock.get_fps()
        pygame.display.set_caption(f"Verlet Solver - {count} Objects - FPS: {fps:.2f}")

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
