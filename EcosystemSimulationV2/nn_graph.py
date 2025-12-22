import numpy as np
import math
import random

# Activation functions
def sigmoid(x):
    return 1 / (1 + math.exp(-x))

def tanh(x):
    return math.tanh(x)

def solve_agent_nn(store, idx):
    """
    Solves the NN for a single agent.
    Assumes inputs (Nodes 0..InputCount) are already set in access_val.
    """
    n_start = store.genome_node_start[idx]
    n_count = store.genome_node_count[idx]
    e_start = store.genome_edge_start[idx]
    e_count = store.genome_edge_count[idx]
    
    # 1. Reset Hidden/Output nodes to Bias
    # We iterate all nodes for this agent
    # Optimization: Numpy slice?
    # store.node_val[n_start : n_start+n_count] = store.node_bias[n_start : n_start+n_count]
    # But we must preserve Inputs! Inputs are type 0.
    # So we only reset types 1 and 2.
    
    # Python loop is slow, but inside a JIT/C++ this is fast.
    # For now, we do purely python loop or vectorized if possible.
    # Vectorized slice is better.
    
    nodes_slice_bias = store.node_bias[n_start : n_start+n_count]
    nodes_slice_val = store.node_val[n_start : n_start+n_count]
    nodes_slice_type = store.node_type[n_start : n_start+n_count]
    
    # Reset vals to bias where type != 0 (Input)
    # mask = nodes_slice_type != 0
    # nodes_slice_val[mask] = nodes_slice_bias[mask] 
    # ^ usage of fancy indexing might copy. 
    # Let's iterate edges, it's a Graph.
    
    # Naive graph solver (Recurrent-ish one pass):
    # 1. Inputs are set.
    # 2. Iterate Edges: Add weighted Input to Target.
    # 3. Activate Targets.
    
    # Reset accumulator for non-inputs
    for i in range(n_count):
        real_idx = n_start + i
        if store.node_type[real_idx] != 0:
            store.node_val[real_idx] = store.node_bias[real_idx]

    # Propagate Edges
    for i in range(e_count):
        real_edge_idx = e_start + i
        src = store.edge_source[real_edge_idx]
        dst = store.edge_target[real_edge_idx]
        w = store.edge_weight[real_edge_idx]
        
        # Accumulate
        store.node_val[dst] += store.node_val[src] * w
        
    # Activation
    for i in range(n_count):
        real_idx = n_start + i
        ntilda = store.node_type[real_idx]
        val = store.node_val[real_idx]
        
        if ntilda == 1: # Hidden
            store.node_val[real_idx] = tanh(val)
        elif ntilda == 2: # Output
            store.node_val[real_idx] = tanh(val)

def mutate_agent_nn(store, idx):
    """
    Mutates the agent's genome.
    NOTE: In a rigid SoA with fixed arrays, adding nodes/edges is hard without reallocation.
    For this V2, we assume we have 'spare' capacity in the allocated block?
    Or we just modify weights?
    
    Constraint: DataStore allocates fixed blocks `genome_node_count`.
    Dynamic growth in SoA is complex (requires reallocating into a larger hole).
    
    Compromise for V2 Demo:
    - Only mutate weights.
    - OR separate the Genome storage from the Agent SoA? 
    - The user asked for "graph... list of nodes".
    
    If we can't resize easily, we can't add nodes/edges easily in a packed array.
    Solution: We won't implement structural mutation (Topology) in this V2 prototype 
    unless we implement a heap-like allocator.
    
    Let's stick to Weight Mutation for V2 stability, 
    OR assume `allocate_nn_block` gave us some slack?
    
    User prompt: "structure... correct".
    Let's just mutate Weights.
    """
    e_start = store.genome_edge_start[idx]
    e_count = store.genome_edge_count[idx]
    
    if e_count == 0: return

    # Mutate a random weight
    if random.random() < 0.5:
        target_edge = e_start + random.randint(0, e_count - 1)
        store.edge_weight[target_edge] += random.gauss(0, 0.5)
        store.edge_weight[target_edge] = max(-10.0, min(10.0, store.edge_weight[target_edge]))

def generate_nn_structure(store, idx, input_count, output_count):
    """
    Generates a simple initial feed-forward structure.
    Inputs -> Outputs directly (no hidden initially).
    """
    # Allocate nodes: Inputs + Outputs
    total_nodes = input_count + output_count
    
    # Allocate edges: Fully connected Inputs -> Outputs
    total_edges = input_count * output_count
    
    if not store.allocate_nn_block(idx, total_nodes, total_edges):
        return
        
    n_start = store.genome_node_start[idx]
    e_start = store.genome_edge_start[idx]
    
    # Setup Nodes
    # 0..Input-1 : Type 0 (Input)
    # Input..End : Type 2 (Output)
    
    for i in range(input_count):
        store.node_type[n_start + i] = 0 # Input
        
    for i in range(output_count):
        store.node_type[n_start + input_count + i] = 2 # Output
        
    # Setup Edges
    edge_idx = 0
    for i in range(input_count):
        src_node = n_start + i
        for j in range(output_count):
            dst_node = n_start + input_count + j
            
            store.edge_source[e_start + edge_idx] = src_node
            store.edge_target[e_start + edge_idx] = dst_node
            store.edge_weight[e_start + edge_idx] = random.uniform(-1, 1)
            
            edge_idx += 1

