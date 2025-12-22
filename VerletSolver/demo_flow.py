import pygame
import sys
import random
import math
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from solver import Solver, Particle

SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 800
BG_COLOR = (0, 0, 0)

def create_chain(solver, x, y, segments, segment_length, is_static_ends=True):
    particles = []
    
    for i in range(segments):
        # Arc or line? Let's make a U shape or just a simple droop
        # Let's make a cup shape:  \_/
        pass

def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Verlet Solver - Flow & Chains")
    clock = pygame.time.Clock()
    
    solver = Solver(SCREEN_WIDTH, SCREEN_HEIGHT)
    solver.gravity_y = 1000.0
    solver.container_radius = 2000 # Effectively disable circular constraint for this demo or make it huge
    
    # Create a Chain "Cup"
    # We want a semi-circle or basket of linked particles
    center_x = SCREEN_WIDTH // 2
    center_y = SCREEN_HEIGHT // 2 + 100
    radius = 200
    count = 40
    
    chain_particles = []
    for i in range(count + 1):
        angle = math.pi + (i / count) * math.pi # Semi-circle from PI to 2PI (bottom half)
        # Actually standard coord system: 0 is right, PI/2 down.
        # We want a cup: angle from 0 to PI (if we offset gravity?)
        # Let's do from 0.1PI to 0.9PI
        start_angle = 0.2 * math.pi
        end_angle = 0.8 * math.pi
        
        theta = start_angle + (i / count) * (end_angle - start_angle)
        
        px = center_x + radius * math.cos(theta)
        py = center_y + radius * math.sin(theta)
        
        pinned = (i == 0 or i == count) # Pin ends
        
        p = Particle(px, py, 5, (255, 255, 255), is_pinned=pinned)
        solver.add_particle(p)
        chain_particles.append(p)
        
    # Link them
    for i in range(len(chain_particles) - 1):
        p1 = chain_particles[i]
        p2 = chain_particles[i+1]
        solver.add_link(p1, p2) # Automatic distance
        
    # Flow Emitter
    flow_rate = 2 # Particles per frame
    stream_x = center_x - 50
    stream_y = 50
    
    running = True
    frame = 0
    total_spawned = 0
    
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        
        # Spawn Flow
        if frame % 1 == 0 and total_spawned < 1500:
            for _ in range(flow_rate):
                px = stream_x + random.uniform(-10, 10)
                py = stream_y + random.uniform(-10, 10)
                radius = random.uniform(3, 6)
                color = (
                    random.randint(50, 255),
                    random.randint(50, 255),
                    255
                )
                p = Particle(px, py, radius, color)
                # Give initial velocity?
                # Verlet velocity is implict (old_x).
                # To add velocity (vx, vy):
                # old_x = x - vx * dt
                # Let's shoot them right slightly
                vx = 200 # pixels/sec
                dt = 1.0/60.0 # Standard
                p.old_x = px - vx * dt
                
                solver.add_particle(p)
                total_spawned += 1
        
        # Physics
        solver.update(1.0 / 60.0)
        
        # Render
        screen.fill(BG_COLOR)
        
        # Draw Links
        for link in solver.links:
            p1 = link.p1
            p2 = link.p2
            pygame.draw.line(screen, (200, 200, 200), (int(p1.x), int(p1.y)), (int(p2.x), int(p2.y)), 2)
            
        # Draw Particles
        for p in solver.particles:
            ix, iy = int(p.x), int(p.y)
            pygame.draw.circle(screen, p.color, (ix, iy), int(p.radius))
            
        pygame.display.flip()
        clock.tick(60)
        frame += 1

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
