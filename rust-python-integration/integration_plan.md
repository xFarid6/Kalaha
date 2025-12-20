# Rust-Python Integration Strategy

This document outlines the plan for calling Rust code from Python within the Mini Games Gallery project. This integration is primarily aimed at performance-critical components such as AI engines (Minimax, MCTS) or complex physics simulations.

## 1. Objectives
- **Performance**: Move CPU-bound logic (e.g., game tree search) to Rust.
- **Safety**: Leverage Rust's memory safety for stable game engines.
- **Portability**: Create easy-to-distribute Python packages using Rust binaries.

## 2. Tools and Libraries
To bridge the two languages, we will use the following industry-standard tools:

- **PyO3**: A library that provides Rust bindings for the Python interpreter. It allows writing native Python modules in Rust.
- **Maturin**: A build system and publishing tool for binary Python packages. It simplifies the process of compiling Rust and making it available as a Python import.
- **Pygame (Python side)**: Will remain the primary framework for UI and event handling, while the "brain" of the game resides in Rust.

## 3. Recommended Folder Structure
The integration will be contained in a dedicated folder outside the main website to keep the web and native components separate.

```
rust-python-integration/
├── Cargo.toml              # Rust package configuration
├── pyproject.toml          # Python build system configuration (for maturin)
├── src/
│   └── lib.rs              # Rust source code and PyO3 bindings
├── python/
│   └── test_bridge.py      # Python script to test the integration
└── README.md               # Setup and build instructions
```

## 4. Implementation Logic

### Step 1: Define the Rust Interface
We will define a Rust crate of type `cdylib`. Inside `lib.rs`, we use the `#[pyfunction]` and `#[pymodule]` macros from PyO3 to expose Rust functions to Python.

### Step 2: Build with Maturin
Using `maturin develop` during development, the Rust code is compiled and automatically installed into the current virtual environment, allowing for immediate import in Python.

### Step 3: Python Integration
In Python, we simply `import` the module as if it were a regular `.py` file. Python handles the calls, and the heavy lifting is done by the compiled Rust binary.

## 5. Planned Example: Minimax Move Calculator
As a first test case, we will implement a simple Minimax move calculator for a game like Tic-Tac-Toe in Rust and call it from a Python GUI.

## 6. Performance Considerations
- **Data Transfer**: Minimize the cost of crossing the bridge by passing primitive types or avoiding large data copies between Python and Rust.
- **Release Builds**: Always use `maturin develop --release` for performance benchmarking, as debug builds in Rust are significantly slower.

---

*This plan serves as the technical foundation for upcoming native performance enhancements.*
