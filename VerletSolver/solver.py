import math
import random

class Particle:
    __slots__ = ('x', 'y', 'old_x', 'old_y', 'ax', 'ay', 'radius', 'color', 'mass', 'is_pinned')
    
    def __init__(self, x, y, radius, color=(255, 255, 255), is_pinned=False):
        self.x = x
        self.y = y
        self.old_x = x
        self.old_y = y
        self.ax = 0.0
        self.ay = 0.0
        self.radius = radius
        self.color = color
        self.mass = 1.0 # could be radius * radius
        self.is_pinned = is_pinned

class Link:
    __slots__ = ('p1', 'p2', 'target_dist')
    
    def __init__(self, p1, p2, target_dist):
        self.p1 = p1
        self.p2 = p2
        self.target_dist = target_dist

class Solver:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.gravity_x = 0.0
        self.gravity_y = 1000.0
        self.friction = 0.99
        self.ground_friction = 0.7
        
        self.particles = []
        self.links = []
        
        # Sub-steps
        self.sub_steps = 8
        
        # Container
        self.container_center_x = width // 2
        self.container_center_y = height // 2
        self.container_radius = 350
        
        # Grid for Spatial Partitioning
        self.grid_size = 20 # slightly larger than max particle radius
        self.grid = {}
        
    def add_particle(self, p):
        self.particles.append(p)
        return p

    def add_link(self, p1, p2, dist=None):
        if dist is None:
            dx = p1.x - p2.x
            dy = p1.y - p2.y
            dist = math.sqrt(dx*dx + dy*dy)
        
        link = Link(p1, p2, dist)
        self.links.append(link)
        return link

    def update(self, dt):
        sub_dt = dt / self.sub_steps
        
        for _ in range(self.sub_steps):
            self.apply_gravity()
            self.apply_constraint()
            self.solve_links()
            self.solve_collisions()
            self.update_positions(sub_dt)

    def update_positions(self, dt):
        for p in self.particles:
            if p.is_pinned: continue
            
            # Verlet Integration
            # x = x + (x - old_x) + a * dt * dt
            vx = (p.x - p.old_x) * self.friction
            vy = (p.y - p.old_y) * self.friction
            
            p.old_x = p.x
            p.old_y = p.y
            
            p.x = p.x + vx + p.ax * dt * dt
            p.y = p.y + vy + p.ay * dt * dt
            
            # Reset accel
            p.ax = 0
            p.ay = 0

    def apply_gravity(self):
        gx = self.gravity_x
        gy = self.gravity_y
        for p in self.particles:
            p.ax += gx
            p.ay += gy

    def apply_constraint(self):
        # Circular Container
        cx = self.container_center_x
        cy = self.container_center_y
        cr = self.container_radius
        
        for p in self.particles:
            dx = p.x - cx
            dy = p.y - cy
            dist2 = dx*dx + dy*dy
            
            # Use squared distance check first
            limit = cr - p.radius
            if dist2 > limit * limit:
                dist = math.sqrt(dist2)
                if dist > 0.0001:
                    # Normalized vector n
                    nx = dx / dist
                    ny = dy / dist
                    
                    # Project back
                    p.x = cx + nx * limit
                    p.y = cy + ny * limit

    def solve_links(self):
        for link in self.links:
            p1 = link.p1
            p2 = link.p2
            
            dx = p1.x - p2.x
            dy = p1.y - p2.y
            dist = math.sqrt(dx*dx + dy*dy)
            
            if dist == 0: continue
            
            diff = (link.target_dist - dist) / dist
            
            # Move scalar
            mx = dx * diff * 0.5
            my = dy * diff * 0.5
            
            if not p1.is_pinned:
                p1.x += mx
                p1.y += my
            if not p2.is_pinned:
                p2.x -= mx
                p2.y -= my

    def solve_collisions(self):
        # Simple Spatial Hashing
        # 1. Clear Grid
        self.grid.clear()
        
        # 2. Populate Grid
        # Optimization: Local vars
        grid = self.grid
        gs = self.grid_size
        
        for p in self.particles:
            # Map to grid cell
            cell_x = int(p.x / gs)
            cell_y = int(p.y / gs)
            
            key = (cell_x, cell_y)
            if key not in grid:
                grid[key] = []
            grid[key].append(p)
            
        # 3. Check Collisions
        # We check current cell and neighbors relative to direction to avoid dupe checks.
        # Generally: check 8 neighbors + self? Or simpler: just check all neighbors for every particle, 
        # but avoid double booking by p1 < p2 or similar.
        # Ideally, iterate cells.
        
        for (cx, cy), cell_particles in grid.items():
            # Check internal collisions in cell
            self.solve_cell_collisions(cell_particles)
            
            # Check Neighbor cells (only need to check half to avoid duplicate pairs if we did all, 
            # but simplest is just checking neighbors)
            # Neighbors: (x+1, y), (x-1, y+1), (x, y+1), (x+1, y+1) -> Half-neighborhood seems mostly sufficient if orderly?
            # No, let's just check standard neighbors.
            
            neighbors = [
                (cx+1, cy), (cx, cy+1), (cx+1, cy+1), (cx-1, cy+1)
            ]
            
            for nx, ny in neighbors:
                if (nx, ny) in grid:
                    self.solve_cell_vs_cell(cell_particles, grid[(nx, ny)])

    def solve_cell_collisions(self, particles):
        # O(N^2) within the cell
        n = len(particles)
        for i in range(n):
            p1 = particles[i]
            for j in range(i + 1, n):
                p2 = particles[j]
                
                dx = p1.x - p2.x
                dy = p1.y - p2.y
                dist2 = dx*dx + dy*dy
                
                rad_sum = p1.radius + p2.radius
                if dist2 < rad_sum * rad_sum:
                    dist = math.sqrt(dist2)
                    if dist > 0:
                        delta = rad_sum - dist
                        nx = dx / dist
                        ny = dy / dist
                        
                        # Separate
                        rx = nx * delta * 0.5
                        ry = ny * delta * 0.5
                        
                        if not p1.is_pinned:
                            p1.x += rx
                            p1.y += ry
                        if not p2.is_pinned:
                            p2.x -= rx
                            p2.y -= ry

    def solve_cell_vs_cell(self, list1, list2):
        for p1 in list1:
            for p2 in list2:
                dx = p1.x - p2.x
                dy = p1.y - p2.y
                dist2 = dx*dx + dy*dy
                
                rad_sum = p1.radius + p2.radius
                if dist2 < rad_sum * rad_sum:
                    dist = math.sqrt(dist2)
                    if dist > 0:
                        delta = rad_sum - dist
                        nx = dx / dist
                        ny = dy / dist
                        
                        # Separate
                        rx = nx * delta * 0.5
                        ry = ny * delta * 0.5
                        
                        if not p1.is_pinned:
                            p1.x += rx
                            p1.y += ry
                        if not p2.is_pinned:
                            p2.x -= rx
                            p2.y -= ry
