import math
import numpy as np
from nn_graph import solve_agent_nn

# Vision Config
RAY_COUNT = 5
RAY_SPREAD = math.radians(90)
RAY_RANGE = 200

def sys_movement(store, indices, dt, width, height):
    for idx in indices:
        if not store.alive[idx]: continue
        
        # Update Pos
        store.pos[idx] += store.vel[idx] * dt
        
        # Warp
        x, y = store.pos[idx]
        if x < 0: store.pos[idx, 0] += width
        elif x > width: store.pos[idx, 0] -= width
        
        if y < 0: store.pos[idx, 1] += height
        elif y > height: store.pos[idx, 1] -= height

def sys_energy(store, indices, dt):
    # Vectorized?
    # store.energy[indices] -= decay * dt
    # Complex logic per type:
    
    for idx in indices:
        if not store.alive[idx]: continue
        
        loss = 5.0 * dt
        # Movement cost
        speed = math.hypot(store.vel[idx, 0], store.vel[idx, 1])
        loss += speed * 0.05 * dt
        
        store.energy[idx] -= loss
        if store.energy[idx] <= 0:
            if store.type[idx] == 1: # Predator dies
                 store.alive[idx] = False
            else: # Prey stops
                store.energy[idx] = 0
                store.vel[idx] = 0

def sys_brain(store, indices, dt):
    for idx in indices:
        if not store.alive[idx]: continue
        
        solve_agent_nn(store, idx)
        
        # Read Outputs
        # Assuming last 2 nodes are outputs
        n_start = store.genome_node_start[idx]
        n_count = store.genome_node_count[idx]
        
        # Output 0: Speed, Output 1: Turn
        out1 = store.node_val[n_start + n_count - 2]
        out2 = store.node_val[n_start + n_count - 1]
        
        # Apply Logic
        # Out1 (Tanh -1 to 1) -> Speed (0 to Max)
        # Let's map -1..1 to 0..Max
        speed = (out1 + 1.0) * 50.0 # Max 100
        turn = out2 * 5.0
        
        store.angle[idx] += turn * dt
        
        vx = math.cos(store.angle[idx]) * speed
        vy = math.sin(store.angle[idx]) * speed
        
        store.vel[idx, 0] = vx
        store.vel[idx, 1] = vy

def sys_vision(store, indices, grid):
    """
    Raycasting.
    Write to Input Nodes.
    Input Nodes Layout:
    0: Bias (Always 1)
    1: Pred/Prey Self Type (Optional?)
    2..2+Rays: Dist
    2+Rays..2+2*Rays: Type
    """
    for idx in indices:
        if not store.alive[idx]: continue
        
        # Get Nearby
        nearby_indices = grid.query(store.pos[idx, 0], store.pos[idx, 1], RAY_RANGE)
        
        start_angle = store.angle[idx] - RAY_SPREAD/2
        step = RAY_SPREAD / (RAY_COUNT - 1)
        
        n_start = store.genome_node_start[idx]
        
        # Set Bias
        store.node_val[n_start] = 1.0
        # Set Energy/Type info?
        store.node_val[n_start + 1] = store.energy[idx] / 100.0
        
        for r in range(RAY_COUNT):
            angle = start_angle + r * step
            rx = math.cos(angle)
            ry = math.sin(angle)
            
            closest_dist = RAY_RANGE
            type_val = 0.0
            
            # Check Intersections
            for other_idx in nearby_indices:
                if other_idx == idx: continue
                if not store.alive[other_idx]: continue
                
                # Math
                ox = store.pos[other_idx, 0]
                oy = store.pos[other_idx, 1]
                orad = store.radius[other_idx]
                
                vx = ox - store.pos[idx, 0]
                vy = oy - store.pos[idx, 1]
                
                t = vx * rx + vy * ry
                if t > 0:
                    px = store.pos[idx, 0] + rx * t
                    py = store.pos[idx, 1] + ry * t
                    
                    dist_sq = (px - ox)**2 + (py - oy)**2
                    if dist_sq < orad*orad:
                        hit_dist = t - math.sqrt(orad*orad - dist_sq)
                        if hit_dist < closest_dist and hit_dist > 0:
                            closest_dist = hit_dist
                            # Type: 1 if Prey, -1 if Predator
                            if store.type[other_idx] == 0: type_val = 1.0
                            else: type_val = -1.0
            
            # Write Inputs
            # Input index base: 2
            norm_dist = 1.0 - (closest_dist / RAY_RANGE)
            store.node_val[n_start + 2 + r*2] = norm_dist
            store.node_val[n_start + 2 + r*2 + 1] = type_val
