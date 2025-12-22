import numpy as np
import math

# Physics Config
GRAVITY = 9.8
LENGTH = 100 # Length of pole (pixels effectively, need scaling)
MASS_CART = 1.0
MASS_POLE = 0.5
TOTAL_MASS = MASS_CART + MASS_POLE
POLEMASS_LENGTH = MASS_POLE * (LENGTH / 2) # Half length center of mass
FORCE_MAG = 20.0
DT_PHYSICS = 0.02 # 50Hz physics

# Sim Config
MAX_X = 300 # Rail limit (+- 300)
HEIGHT_THRESHOLD = LENGTH - 10 # Tip needs to be this high relative to pivot

class Agent:
    def __init__(self, network):
        self.network = network
        self.reset()
        
    def reset(self):
        # State
        self.x = 0.0
        self.x_dot = 0.0
        self.theta = math.pi / 2 # Upright (90 deg) ? 
        # Actually standard: 0 = Vertical Up? Or 0 = Right?
        # Let's say -PI/2 = Up.
        # Let's align with user image: 
        # let's say theta = 0 is straight UP.
        # Random perturbation start
        self.theta = 0.0 + np.random.uniform(-0.05, 0.05)
        
        self.theta_dot = 0.0
        
        self.fitness = 0.0
        self.alive = True
        self.time_alive = 0.0
        
        # For rendering
        self.cart_y = 0 # Relative to rail center
        
    def update(self, dt_acc):
        """
        dt_acc: accumulated delta time.
        We run physics in fixed steps.
        returns: (x, y_tip) for viz
        """
        if not self.alive:
            return
            
        # Neural Control
        # Inputs: Pos (norm), DirX, DirY, AngVel
        norm_x = self.x / MAX_X
        dir_x = math.sin(self.theta)
        dir_y = math.cos(self.theta) # 1 if Up
        ang_vel = self.theta_dot
        
        inputs = np.array([norm_x, dir_x, dir_y, ang_vel])
        output = self.network.forward(inputs)
        force = output[0] * FORCE_MAG
        
        # Physics Step (Euler)
        # Simplified equations for Cart-Pole
        
        costheta = math.cos(self.theta)
        sintheta = math.sin(self.theta)
        
        # Temp vars
        temp = (force + POLEMASS_LENGTH * self.theta_dot**2 * sintheta) / TOTAL_MASS
        
        # Angular Accel
        theta_acc = (GRAVITY * sintheta - costheta * temp) / (LENGTH * (4.0/3.0 - MASS_POLE * costheta**2 / TOTAL_MASS))
        
        # Linear Accel
        x_acc = temp - POLEMASS_LENGTH * theta_acc * costheta / TOTAL_MASS
        
        # Integrate
        self.x += self.x_dot * DT_PHYSICS
        self.x_dot += x_acc * DT_PHYSICS
        
        self.theta += self.theta_dot * DT_PHYSICS
        self.theta_dot += theta_acc * DT_PHYSICS
        
        self.time_alive += DT_PHYSICS
        
        # Check Fail Condition
        # If cart hits limits
        if abs(self.x) > MAX_X:
            self.alive = False
            
        # If pole falls too far (e.g. > 45 degrees from vertical)
        # Vertical is 0.
        if abs(self.theta) > 1.0: # ~60 degrees
            self.alive = False
            
        # Calculate Fitness
        # Reward per step alive
        reward = 1.0 * DT_PHYSICS 
        
        # Penalties
        # Penalty for ang vel (shake)
        penalty_drift = abs(self.theta_dot) * 0.01 * DT_PHYSICS
        # Penalty for distance from center
        penalty_dist = (abs(self.x) / MAX_X) * 0.1 * DT_PHYSICS
        
        self.fitness += reward - penalty_drift - penalty_dist

    def get_tip_pos(self):
        # 0 is UP.
        tip_x = self.x + math.sin(self.theta) * LENGTH
        tip_y = -math.cos(self.theta) * LENGTH # Y Up is negative in Pygame usually, assuming center 0,0
        return self.x, tip_x, tip_y
