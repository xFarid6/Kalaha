# Ecosystem V2 Architecture (DOD & Multithreaded)

This document outlines the Data-Oriented Design (DOD) architecture for the simulation. The primary goal is to structure data for cache efficiency and easy parallelization, serving as a prototype for a high-performance C++/Rust implementation.

## 1. Data Store (SoA)
Instead of an `Agent` class holding attributes, we use a `DataStore` class holding large arrays for each attribute. An "Agent" is simply an Integer ID (index) into these arrays.

### Component Arrays (Numpy)
All arrays are of size `MAX_AGENTS`.
- **Position**: `pos[N, 2]` (float32) - x, y
- **Velocity**: `vel[N, 2]` (float32) - vx, vy
- **Angle**: `angle[N]` (float32) - Current facing angle
- **Energy**: `energy[N]` (float32) - Current energy
- **Type**: `type[N]` (uint8) - 0=Prey, 1=Predator
- **Color**: `color[N, 3]` (uint8) - RGB
- **Radius**: `radius[N]` (float32) - Size

### Neural Network Data (Graph)
We flatten the neural networks into global arrays to avoid pointer chasing.
- **Node Data**:
    - `node_val[M]`: Current activation value.
    - `node_bias[M]`: Bias.
    - `node_type[M]`: Input, Hidden, or Output.
- **Edge Data**:
    - `edge_source[K]`: Index of source node.
    - `edge_target[K]`: Index of target node.
    - `edge_weight[K]`: Connection weight.
- **Agent -> NN Mapping**:
    - `agent_node_start[N]`: Index in `node_*` arrays where this agent's nodes begin.
    - `agent_node_count[N]`: Number of nodes for this agent.
    - `agent_edge_start[N]`: Index in `edge_*` arrays.
    - `agent_edge_count[N]`: Number of edges.

## 2. Systems
Systems are stateless functions that operate on ranges of data.
Signature: `system_function(store, start_index, end_index, *args)`

### Movement System
- **Input**: `pos`, `vel`, `angle`.
- **Logic**:
    - `pos += vel * dt`
    - **Warp Space**: If `pos.x < 0` -> `pos.x = WIDTH`.
    
### Vision System
- **Input**: `pos`, `angle`, SpatialGrid.
- **Logic**:
    - Iterate `start_index` to `end_index`.
    - Raycast using `SpatialGrid` to find neighbors.
    - Write inputs to `node_val` (the Input nodes).

### Brain System (Solver)
- **Logic**:
    - Iterate agents.
    - **Step 1**: Reset non-input nodes.
    - **Step 2**: Iterate Edges (for that agent). `node_val[target] += node_val[source] * weight`.
    - **Step 3**: Apply Activation (Tanh/Sigmoid) to Hidden/Output nodes.
    - **Step 4**: Read Output nodes -> Update `vel`/`angle`.

## 3. Multithreading (Task Scheduler)
- **Worker Pool**: $T$ threads (e.g., 4 or 8).
- **Job**: A tuple `(SystemFunc, StartIdx, EndIdx, StorePtr)`.
- **Sync Points**:
    1. **Pre-Update**: Build Spatial Hash (Single Threaded, or Parallel Sort).
    2. **Phase 1 (Parallel)**: Vision (Read Pos/Grid, Write NN Inputs).
    3. **Phase 2 (Parallel)**: Brain (Read NN Inputs, Write Vel/Angle).
    4. **Phase 3 (Parallel)**: Movement (Read Vel, Write Pos).
    5. **Post-Update**: Logic (Spawning/Death) (Single Threaded mainly).

## 4. Space Partitioning
- **Uniform Grid**: Map divided into cells (e.g., size 32x32).
- **Storage**:
    - `cell_counts[GRID_W, GRID_H]`: Number of agents in cell.
    - `cell_agents[GRID_W, GRID_H, MAX_PER_CELL]`: Indices of agents.
- **Usage**: Vision system only checks cells within raycasting range.
