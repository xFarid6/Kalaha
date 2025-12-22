import numpy as np
import math

CELL_SIZE = 32
GRID_W = 512 // CELL_SIZE
GRID_H = 512 // CELL_SIZE
MAX_AGENTS_PER_CELL = 64 # Soft limit buffer

class UniformGrid:
    def __init__(self):
        # 3D Array: [X, Y, Slot] -> AgentID
        self.cells = np.zeros((GRID_W, GRID_H, MAX_AGENTS_PER_CELL), dtype=np.int32)
        self.counts = np.zeros((GRID_W, GRID_H), dtype=np.int32)
        
    def clear(self):
        self.counts.fill(0)
        
    def update(self, store, active_indices):
        self.clear()
        
        # Vectorized or Loop? 
        # Python loop over indices is safer for specific active list.
        # But allow bulk update if needed.
        
        for idx in active_indices:
            x = store.pos[idx, 0]
            y = store.pos[idx, 1]
            
            cx = int(x / CELL_SIZE)
            cy = int(y / CELL_SIZE)
            
            # Clamp
            cx = max(0, min(GRID_W - 1, cx))
            cy = max(0, min(GRID_H - 1, cy))
            
            cnt = self.counts[cx, cy]
            if cnt < MAX_AGENTS_PER_CELL:
                self.cells[cx, cy, cnt] = idx
                self.counts[cx, cy] += 1
                
    def query(self, x, y, radius):
        # Return list of indices
        found = []
        
        cx = int(x / CELL_SIZE)
        cy = int(y / CELL_SIZE)
        rad_cells = int(math.ceil(radius / CELL_SIZE))
        
        min_x = max(0, cx - rad_cells)
        max_x = min(GRID_W - 1, cx + rad_cells)
        min_y = max(0, cy - rad_cells)
        max_y = min(GRID_H - 1, cy + rad_cells)
        
        for ix in range(min_x, max_x + 1):
            for iy in range(min_y, max_y + 1):
                count = self.counts[ix, iy]
                if count > 0:
                    # Append valid slice
                    # found.extend(self.cells[ix, iy, :count])
                    # Optimized: yield or iterate
                    # Just returning indices
                    # Converting to python list is slow 
                    # but necessary for consuming in python loops.
                    for k in range(count):
                        found.append(self.cells[ix, iy, k])
                        
        return found
