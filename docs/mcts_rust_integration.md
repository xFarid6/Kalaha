# MCTS in Rust + Python Integration Architecture

## Overview
This document outlines the architecture for implementing **Monte Carlo Tree Search (MCTS)** in Rust while keeping the neural network training in Python, targeting an **AlphaZero-style** agent for Kalaha.

---

## Conceptual Division of Responsibilities

### 🦀 Rust Components (High-Performance Core)

**What Rust Handles**:
1. **Kalaha Game State Representation**
   - Board state (14 integers)
   - Legal move generation
   - Move application (fast simulation)
   
2. **MCTS Algorithm**
   - **Selection**: UCB tree traversal
   - **Expansion**: Add new nodes
   - **Rollout/Simulation**: Fast random/heuristic playouts
   - **Backpropagation**: Update visit counts and values
   
3. **Policy/Value Output**
   - Visit-count distribution (policy)
   - Best move recommendation
   - Value estimate (win probability)

**Key Point**: Rust is **completely unaware** of neural networks.

---

### 🐍 Python Components (ML Training)

**What Python Handles**:
1. **Neural Network** (PyTorch)
   - Policy head: P(move | state)
   - Value head: V(state) ∈ [-1, 1]
   
2. **Training Loop**
   - Self-play game generation
   - Experience replay buffer
   - SGD optimization
   - Checkpointing
   
3. **Experiment Orchestration**
   - Hyperparameter tuning
   - TensorBoard logging
   - Model evaluation

**Key Point**: Python is **completely unaware** of MCTS internal tree structure.

---

## Communication Protocol: Rust ↔ Python

### Interface Design

The Rust MCTS acts as a **black-box policy improvement operator**:

```
Python                    Rust MCTS
  │                          │
  ├──────── state ──────────→│
  │                          │ (run 800 simulations)
  │                          │ (build search tree)
  │                          │
  │←─── (policy, value) ─────┤
  │                          │
```

**API Contract**:
```python
# Python calls Rust
mcts_result = rust_mcts.search(
    board_state=[6,6,6,6,6,6,0,6,6,6,6,6,6,0],
    current_player=0,
    num_simulations=800,
    eval_fn=neural_network_eval  # Python callback
)

# Rust returns
{
    'policy': [0.05, 0.10, 0.30, 0.40, 0.10, 0.05],  # Visit distribution
    'value': 0.67,                                    # Estimated win prob
    'best_move': 3                                    # Most visited move
}
```

---

## PyO3 + Maturin: The Bridge

### Why PyO3?
- **Zero-copy**: Minimal overhead for data transfer
- **Native Module**: Rust compiles to Python extension (`.pyd`/`.so`)
- **Bidirectional**: Python can call Rust, Rust can call Python callbacks

### Architecture

```
┌─────────────────────────────────────────┐
│          Python Training Script        │
│  ┌───────────────────────────────────┐ │
│  │  Neural Network (PyTorch)         │ │
│  │  - policy_net(state) → policy     │ │
│  │  - value_net(state) → value       │ │
│  └───────────────────────────────────┘ │
│              ▲          │               │
│              │ callback │ result        │
│              │          ▼               │
│  ┌───────────────────────────────────┐ │
│  │  kalaha_mcts (Rust Module)        │ │ ← PyO3
│  │  - search(state, num_sims, eval)  │ │
│  └───────────────────────────────────┘ │
└─────────────────────────────────────────┘
             Compiled with Maturin
```

---

## Rust MCTS Implementation Plan

### Step 1: Define Core Structs

```rust
// src/game.rs
#[derive(Clone)]
pub struct KalahaState {
    board: [i8; 14],
    current_player: u8,
}

impl KalahaState {
    pub fn legal_moves(&self) -> Vec<usize> { /* ... */ }
    pub fn apply_move(&mut self, mv: usize) -> bool { /* extra turn? */ }
    pub fn is_terminal(&self) -> bool { /* ... */ }
    pub fn get_winner(&self) -> Option<i8> { /* -1, 0, 1 */ }
}
```

```rust
// src/mcts.rs
pub struct MCTSNode {
    state: KalahaState,
    parent: Option<*mut MCTSNode>,
    children: Vec<*mut MCTSNode>,
    
    visit_count: u32,
    total_value: f32,
    prior_prob: f32,  // From neural network
    
    move_from_parent: Option<usize>,
}
```

### Step 2: MCTS Core Algorithm

```rust
pub struct MCTS {
    root: *mut MCTSNode,
    num_simulations: u32,
}

impl MCTS {
    // 1. Selection: UCB traversal
    fn select(&mut self) -> *mut MCTSNode {
        let mut node = self.root;
        while !node.is_leaf() {
            node = self.best_child(node);  // UCB formula
        }
        node
    }
    
    // 2. Expansion: Add children
    fn expand(&mut self, node: *mut MCTSNode, priors: Vec<f32>) {
        let moves = node.state.legal_moves();
        for (mv, prior) in moves.iter().zip(priors) {
            let child = MCTSNode::new(node.state.clone(), Some(mv), prior);
            node.children.push(child);
        }
    }
    
    // 3. Simulation / Evaluation
    fn evaluate(&self, node: *mut MCTSNode, eval_fn: &dyn Fn(&KalahaState) -> (Vec<f32>, f32)) -> f32 {
        if node.state.is_terminal() {
            return node.state.get_winner().unwrap() as f32;
        }
        
        // Call Python neural network
        let (policy, value) = eval_fn(&node.state);
        value
    }
    
    // 4. Backpropagation
    fn backpropagate(&mut self, node: *mut MCTSNode, value: f32) {
        let mut current = node;
        while let Some(parent) = current.parent {
            current.visit_count += 1;
            current.total_value += value;
            current = parent;
        }
    }
}
```

### Step 3: PyO3 Python Bindings

```rust
// src/lib.rs
use pyo3::prelude::*;

#[pyclass]
pub struct RustMCTS {
    mcts: MCTS,
}

#[pymethods]
impl RustMCTS {
    #[new]
    pub fn new() -> Self {
        RustMCTS { mcts: MCTS::new() }
    }
    
    pub fn search(
        &mut self,
        board: [i8; 14],
        current_player: u8,
        num_simulations: u32,
        eval_fn: PyObject,  // Python callback
    ) -> PyResult<(Vec<f32>, f32, usize)> {
        
        // Wrap Python function
        let evaluator = |state: &KalahaState| {
            Python::with_gil(|py| {
                let result = eval_fn.call1(py, (state.board.to_vec(), state.current_player))?;
                let (policy, value): (Vec<f32>, f32) = result.extract(py)?;
                Ok((policy, value))
            }).unwrap()
        };
        
        // Run MCTS
        self.mcts.reset(KalahaState { board, current_player });
        
        for _ in 0..num_simulations {
            let leaf = self.mcts.select();
            let value = self.mcts.evaluate(leaf, &evaluator);
            self.mcts.backpropagate(leaf, value);
        }
        
        // Extract policy (visit distribution)
        let policy = self.mcts.get_visit_distribution();
        let value = self.mcts.root_value();
        let best_move = self.mcts.best_move();
        
        Ok((policy, value, best_move))
    }
}

#[pymodule]
fn kalaha_mcts(_py: Python, m: &PyModule) -> PyResult<()> {
    m.add_class::<RustMCTS>()?;
    Ok(())
}
```

---

## Building with Maturin

### Setup

```bash
# Create Rust project
maturin new kalaha-mcts
cd kalaha-mcts

# Add dependencies
cargo add pyo3 --features extension-module
```

**`Cargo.toml`**:
```toml
[package]
name = "kalaha-mcts"
version = "0.1.0"
edition = "2021"

[lib]
name = "kalaha_mcts"
crate-type = ["cdylib"]

[dependencies]
pyo3 = { version = "0.20", features = ["extension-module"] }
```

### Build & Install

```bash
# Development mode (editable install)
maturin develop --release

# Production wheel
maturin build --release
pip install target/wheels/kalaha_mcts-*.whl
```

---

## Python Integration: AlphaZero Training Loop

```python
import torch
import torch.nn as nn
from kalaha_mcts import RustMCTS

class KalahaNet(nn.Module):
    def __init__(self):
        super().__init__()
        self.fc = nn.Sequential(
            nn.Linear(15, 128),
            nn.ReLU(),
            nn.Linear(128, 128),
            nn.ReLU(),
        )
        self.policy_head = nn.Linear(128, 6)
        self.value_head = nn.Linear(128, 1)
    
    def forward(self, x):
        features = self.fc(x)
        policy = torch.softmax(self.policy_head(features), dim=-1)
        value = torch.tanh(self.value_head(features))
        return policy, value

def neural_network_eval(board, player):
    """Callback for Rust MCTS"""
    state = torch.tensor(board + [player], dtype=torch.float32)
    with torch.no_grad():
        policy, value = model(state)
    return policy.numpy().tolist(), value.item()

# Training loop
model = KalahaNet()
mcts = RustMCTS()

for episode in range(10000):
    state = initial_state()
    game_history = []
    
    while not is_terminal(state):
        # MCTS search with neural network guidance
        policy, value, move = mcts.search(
            board=state.board,
            current_player=state.player,
            num_simulations=800,
            eval_fn=neural_network_eval
        )
        
        # Store training data
        game_history.append((state, policy, value))
        
        # Apply move
        state = apply_move(state, move)
    
    # Train neural network on game
    for state, target_policy, target_value in game_history:
        # Compute loss and update weights
        policy_loss = cross_entropy(model.policy(state), target_policy)
        value_loss = mse(model.value(state), target_value)
        loss = policy_loss + value_loss
        loss.backward()
        optimizer.step()
```

---

## Implementation Roadmap

### Phase 1: Rust Game Engine (Week 1)
- [ ] Define `KalahaState` struct
- [ ] Implement move generation and application
- [ ] Write unit tests for game logic
- [ ] Benchmark: Target 1M simulations/second

### Phase 2: Basic MCTS (Week 2)
- [ ] Implement `MCTSNode` and tree structure
- [ ] Core MCTS loop (select, expand, simulate, backpropagate)
- [ ] Random rollout policy
- [ ] Python bindings (PyO3)

### Phase 3: Neural Network Integration (Week 3)
- [ ] Design callback interface for Python eval
- [ ] Test with dummy neural network
- [ ] Optimize Python ↔ Rust crossing
- [ ] Add prior probabilities to expansion

### Phase 4: AlphaZero Training (Week 4)
- [ ] Implement Python training loop
- [ ] Self-play game generation
- [ ] Experience replay buffer
- [ ] Model checkpointing and evaluation

### Phase 5: Optimization (Week 5+)
- [ ] Virtual loss for parallel MCTS
- [ ] Batch evaluation (send multiple states to NN)
- [ ] Dirichlet noise for exploration
- [ ] Temperature-based move selection

---

## Performance Targets

### Rust MCTS
- **Simulation speed**: 1-10M nodes/second (pure Rust, no NN)
- **Memory**: < 100MB for 800-simulation tree
- **Latency**: < 100ms for 800 simulations + NN evaluation

### Python Training
- **Self-play**: 100 games/hour (with NN eval)
- **Training throughput**: 1000 batches/hour
- **Convergence**: Superhuman play in 100k games

---

## Advantages of This Architecture

1. ✅ **Speed**: Rust MCTS is 100x faster than Python implementation
2. ✅ **Flexibility**: Easy to swap NN architectures (PyTorch → TensorFlow)
3. ✅ **Debugging**: Can test Rust MCTS with dummy eval functions
4. ✅ **Scalability**: Easy to parallelize (multiple Rust threads, single Python NN)
5. ✅ **Modularity**: Rust and Python codebases are independent

---

## Potential Challenges

### 1. Python ↔ Rust Overhead
**Issue**: Calling Python eval from Rust for every simulation is slow.

**Solutions**:
- Batch evaluations: Collect 32 leaf nodes, evaluate together
- Async evaluation: Queue requests, process in parallel
- Leaf node caching: Avoid redundant NN calls

### 2. GIL (Global Interpreter Lock)
**Issue**: Python callback blocks Rust threads.

**Solutions**:
- Release GIL in Rust between calls
- Use `nogil` Python extensions (Cython/Numba)
- Move NN inference to separate process (ZeroMQ)

### 3. Memory Management
**Issue**: MCTS tree grows large, pointer safety is critical.

**Solutions**:
- Use `Box<MCTSNode>` instead of raw pointers
- Implement arena allocator
- Prune tree after each move

---

## Comparison: Pure Python vs Rust MCTS

| Metric                  | Pure Python | Rust + PyO3 | Speedup |
|------------------------|-------------|-------------|---------|
| Simulations/sec        | 10k         | 1M          | 100x    |
| Memory per node        | 200 bytes   | 64 bytes    | 3x      |
| Development time       | 1 week      | 4 weeks     | 0.25x   |
| Debugging difficulty   | Easy        | Hard        | 0.5x    |

**Verdict**: Rust is worth it for **production AlphaZero**, not for prototyping.

---

## Conclusion

This architecture provides:
- **Best of both worlds**: Rust speed + Python ML ecosystem
- **Clean separation**: MCTS and NN are independent modules
- **Scalability**: Can optimize each component separately
- **Research-friendly**: Easy to experiment with different algorithms

**Next Steps**:
1. Prototype Rust game engine
2. Benchmark against pure Python MCTS
3. If 10x+ speedup → continue with PyO3 integration
4. Otherwise → optimize Python first (Numba, vectorization)

The Kalaha state space is small enough that a **well-optimized Python MCTS** might suffice. Consider Rust only if targeting **1M+ simulations per move** or building a **production-grade engine**.
