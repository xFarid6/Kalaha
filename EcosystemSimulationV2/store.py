import numpy as np

MAX_AGENTS = 2000 # Buffer for 1600 + reproduction
# NN Buffer sizes
MAX_NODES = MAX_AGENTS * 20 # Approx 20 nodes per agent
MAX_EDGES = MAX_AGENTS * 50 # Approx 50 edges per agent

class DataStore:
    def __init__(self):
        # --- Component Arrays (SoA) ---
        self.count = 0
        self.active_indices = [] # List of active IDs
        
        # Physics
        self.pos = np.zeros((MAX_AGENTS, 2), dtype=np.float32)
        self.vel = np.zeros((MAX_AGENTS, 2), dtype=np.float32)
        self.angle = np.zeros(MAX_AGENTS, dtype=np.float32)
        self.radius = np.zeros(MAX_AGENTS, dtype=np.float32)
        
        # Logic
        self.energy = np.zeros(MAX_AGENTS, dtype=np.float32)
        self.type = np.zeros(MAX_AGENTS, dtype=np.int8) # 0=Prey, 1=Predator
        self.color = np.zeros((MAX_AGENTS, 3), dtype=np.uint8)
        self.age = np.zeros(MAX_AGENTS, dtype=np.float32)
        self.alive = np.zeros(MAX_AGENTS, dtype=np.bool_)
        
        # NN Mapping
        self.genome_node_start = np.zeros(MAX_AGENTS, dtype=np.int32)
        self.genome_node_count = np.zeros(MAX_AGENTS, dtype=np.int32)
        self.genome_edge_start = np.zeros(MAX_AGENTS, dtype=np.int32)
        self.genome_edge_count = np.zeros(MAX_AGENTS, dtype=np.int32)
        
        # --- Flattened NN Graph ---
        self.node_val = np.zeros(MAX_NODES, dtype=np.float32)
        self.node_bias = np.zeros(MAX_NODES, dtype=np.float32)
        self.node_type = np.zeros(MAX_NODES, dtype=np.int8) # 0=In, 1=Hid, 2=Out
        
        self.edge_source = np.zeros(MAX_EDGES, dtype=np.int32)
        self.edge_target = np.zeros(MAX_EDGES, dtype=np.int32)
        self.edge_weight = np.zeros(MAX_EDGES, dtype=np.float32)
        
        # Allocators
        self.next_node_idx = 0
        self.next_edge_idx = 0

    def allocate_agent(self):
        # Find first dead slot or append if we tracked count strictly
        # Simple stack-based free list or just linear scan for this demo
        # For simplicity: just use 'count' as next ID if we don't handle fragmentation yet.
        # But we need to handle death. 
        # Let's verify 'alive'
        
        idx = -1
        # Try finding a dead spot
        # Optimization: Maintain a list of free indices.
        # Check if we have capacity
        if self.count < MAX_AGENTS:
            # We assume slots [0..count-1] are used? No, fragmentation happens.
            # Let's linear search for !alive. Slow for spawning but fine for prototype.
            # Faster: use mask
            dead_slots = np.where(self.alive == False)[0]
            if len(dead_slots) > 0:
                idx = dead_slots[0]
            else:
                return -1 # Full
        else:
            return -1
            
        # Reset data for this slot
        self.pos[idx] = 0
        self.vel[idx] = 0
        self.energy[idx] = 0
        self.alive[idx] = True
        self.count += 1
        return idx

    def free_agent(self, idx):
        self.alive[idx] = False
        self.count -= 1
        # We don't necessarily defrag nodes/edges here, simple leak for prototype or reset pointers.
        # In a real engine, we'd have a free list for node/edge blocks too.

    def allocate_nn_block(self, agent_idx, num_nodes, num_edges):
        # Simply append to the end of node/edge arrays
        # (Fragmentation in NN arrays is an issue for long running sims, but we ignore for this demo scope)
        
        n_start = self.next_node_idx
        e_start = self.next_edge_idx
        
        if n_start + num_nodes >= MAX_NODES or e_start + num_edges >= MAX_EDGES:
            print("NN Buffer Overflow!")
            return False
            
        self.genome_node_start[agent_idx] = n_start
        self.genome_node_count[agent_idx] = num_nodes
        self.genome_edge_start[agent_idx] = e_start
        self.genome_edge_count[agent_idx] = num_edges
        
        self.next_node_idx += num_nodes
        self.next_edge_idx += num_edges
        return True
