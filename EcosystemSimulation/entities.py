import pygame
import math
import random
from nn import Genome

# Config
WIDTH = 1200
HEIGHT = 900

# Constants
RAY_COUNT = 7
RAY_SPREAD = math.radians(120) # Total spread
RAY_RANGE_PREY = 150
RAY_RANGE_PREDATOR = 400

MAX_ENERGY_PREY = 100
MAX_ENERGY_PREDATOR = 150

DECAY_PREY = 5
DECAY_PREDATOR = 8
MOVE_COST = 5

SPLIT_COST_PREY = 60
SPLIT_THRESHOLD_PREY = 90
SPLIT_TIMER_PREY = 5.0 # Seconds

EAT_GAIN = 40
DIGEST_TIME = 1.0

class Entity:
    def __init__(self, x, y, radius, color, genome=None):
        self.x = x
        self.y = y
        self.angle = random.uniform(0, math.pi*2)
        self.radius = radius
        self.color = color
        
        # Physics
        self.speed = 0
        self.max_speed = 100
        self.ang_vel = 0
        
        # Energy
        self.energy = 50
        self.alive = True
        self.age = 0
        
        # Brain
        self.genome = genome if genome else Genome(RAY_COUNT*2 + 2, 2) # Inputs: Rays*2 + Bias + Energy
        
        # Ray inputs
        self.ray_results = [] # Stores (dist_normalized, type)
        
    def update(self, dt, grid):
        if not self.alive: return
        self.age += dt
        
        # 1. Sense
        self.sense(grid)
        
        # 2. Think
        inputs = [1.0] # Bias
        inputs.append(self.energy / 100.0) # Normalized Energy
        
        # Rays
        for scan in self.ray_results:
            inputs.append(scan[0]) # Dist (1.0 = close, 0.0 = far/nothing)
            inputs.append(scan[1]) # Type (1=Prey, -1=Predator, 0=Nothing)
            
        outputs = self.genome.feed_forward(inputs)
        
        # 3. Act
        # Output 0: Speed (Sigmoid 0-1) -> Scale to max_speed
        # Output 1: Turn (Tanh -1 to 1) -> Scale to max_turn
        
        target_speed = outputs[0] * self.max_speed
        turn = outputs[1] * 5.0 # Max turn rate
        
        # Energy Constraint for Prey (stopping to charge)
        # Note: Logic in subclass might override
        
        self.move(target_speed, turn, dt)
        
        # Energy Decay
        self.energy -= self.get_decay_rate() * dt
        # Move cost
        self.energy -= (abs(self.speed) / self.max_speed) * MOVE_COST * dt
        
        if self.energy <= 0:
            self.on_no_energy()

        # Bounds
        if self.x < 0: self.x = 0; self.angle += math.pi
        if self.x > WIDTH: self.x = WIDTH; self.angle += math.pi
        if self.y < 0: self.y = 0; self.angle += math.pi
        if self.y > HEIGHT: self.y = HEIGHT; self.angle += math.pi

    def get_decay_rate(self):
        return 1.0

    def on_no_energy(self):
        self.energy = 0
        self.speed = 0

    def move(self, speed, turn, dt):
        self.angle += turn * dt
        self.speed = speed
        
        vx = math.cos(self.angle) * self.speed
        vy = math.sin(self.angle) * self.speed
        
        self.x += vx * dt
        self.y += vy * dt

    def sense(self, grid):
        # Raycast
        # We need nearby entities.
        # Grid passed implies spatial hash wrapper.
        
        self.ray_results = []
        near = grid.get_nearby(self.x, self.y, self.get_view_range())
        
        start_angle = self.angle - RAY_SPREAD/2
        step = RAY_SPREAD / (RAY_COUNT - 1)
        
        for i in range(RAY_COUNT):
            ray_angle = start_angle + i * step
            
            # Cast ray
            # Simplify: Ray is a line segment. Check intersection with circles.
            # Find closest intersection.
            
            closest_dist = self.get_view_range()
            hit_type = 0 # 0=Nothing, 1=Prey, -1=Predator
            
            # Vector
            rx = math.cos(ray_angle)
            ry = math.sin(ray_angle)
            
            for other in near:
                if other is self: continue
                
                # Circle intersection math
                # Project Circle Center to Ray
                # V = Other - Self
                vx = other.x - self.x
                vy = other.y - self.y
                
                # Dot product (Self to Other . Ray Dir)
                t = vx * rx + vy * ry
                
                if t > 0: # In front
                    # Closest point on ray to circle center
                    px = self.x + rx * t
                    py = self.y + ry * t
                    
                    # Distance from closest point to circle center
                    dx = px - other.x
                    dy = py - other.y
                    dist_sq = dx*dx + dy*dy
                    
                    if dist_sq < other.radius * other.radius:
                        # Intersection!
                        # Exact distance is t - sqrt(r^2 - dist_sq)
                        dt = math.sqrt(other.radius*other.radius - dist_sq)
                        hit_dist = t - dt
                        
                        if hit_dist < closest_dist and hit_dist > 0:
                            closest_dist = hit_dist
                            # Identify type
                            if isinstance(other, Prey): hit_type = 1.0
                            elif isinstance(other, Predator): hit_type = -1.0
            
            # Normalize dist (1 = Close, 0 = Far)
            norm_dist = 1.0 - (closest_dist / self.get_view_range())
            self.ray_results.append((norm_dist, hit_type))

    def get_view_range(self):
        return 100

class Prey(Entity):
    def __init__(self, x, y, genome=None):
        super().__init__(x, y, 6, (100, 255, 100), genome)
        self.max_speed = 120
        self.energy = MAX_ENERGY_PREY
        self.split_timer = 0
        
    def get_view_range(self):
        return RAY_RANGE_PREY
    
    def get_decay_rate(self):
        return DECAY_PREY

    def on_no_energy(self):
        self.speed = 0
        # Recharge
        self.energy += 15 * 0.016 # small recharge per frame? 
        if self.energy > MAX_ENERGY_PREY: self.energy = MAX_ENERGY_PREY

    def update(self, dt, grid):
        if self.energy <= 0:
            # Override update to stay still and recharge
            self.on_no_energy()
            self.age += dt
            return # Skip movement/thinking
            
        super().update(dt, grid)
        
        # Splitting Logic
        self.split_timer += dt
        if self.energy > SPLIT_THRESHOLD_PREY and self.split_timer > SPLIT_TIMER_PREY:
            return self.split()
        return None

    def split(self):
        self.energy -= SPLIT_COST_PREY
        self.split_timer = 0
        
        # Create Child
        child_genome = self.genome.copy()
        child_genome.mutate()
        
        child = Prey(self.x, self.y, child_genome)
        child.energy = 40 # Start energy
        return child

class Predator(Entity):
    def __init__(self, x, y, genome=None):
        super().__init__(x, y, 10, (255, 50, 50), genome)
        self.max_speed = 130
        self.energy = MAX_ENERGY_PREDATOR
        self.digest_timer = 0
        self.eaten_count = 0
        
    def get_view_range(self):
        return RAY_RANGE_PREDATOR

    def get_decay_rate(self):
        return DECAY_PREDATOR

    def on_no_energy(self):
        self.alive = False # Starve

    def update(self, dt, grid):
        super().update(dt, grid)
        if self.digest_timer > 0:
            self.digest_timer -= dt
            
        # Check digestion/eating happens in simulation loop collision check mostly, 
        # or here if checking overlap.
        # But simulation loop handles spatial queries better. 
        # We'll handle 'try_eat' call from main loop.
        
        # Reproduction (eaten enough?)
        # Prompt: "in order to split predators need to eat"
        # Let's say every 3 eats?
        pass

    def try_eat(self, prey):
        if self.digest_timer <= 0:
            dist = math.hypot(self.x - prey.x, self.y - prey.y)
            if dist < self.radius + prey.radius:
                # Eat
                self.energy += EAT_GAIN
                if self.energy > MAX_ENERGY_PREDATOR: self.energy = MAX_ENERGY_PREDATOR
                self.digest_timer = DIGEST_TIME
                self.eaten_count += 1
                return True
        return False
        
    def try_reproduce(self):
        if self.eaten_count >= 2 and self.energy > 80:
            self.eaten_count = 0
            self.energy -= 40
            
            child_genome = self.genome.copy()
            child_genome.mutate()
            child = Predator(self.x, self.y, child_genome)
            return child
        return None
