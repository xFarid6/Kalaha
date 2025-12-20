# Rust-Python Bridge Setup

This folder contains a native Rust extension for Python.

## Prerequisites
1.  **Rust**: [Install Rust](https://rustup.rs/)
2.  **Maturin**: Install via pip:
    ```bash
    pip install maturin
    ```

## How to Build and Run
1.  **Navigate** to this directory:
    ```bash
    cd rust-python-integration
    ```
2.  **Build and Install** the extension locally:
    ```bash
    maturin develop
    ```
3.  **Run** the test script:
    ```bash
    python python/test_bridge.py
    ```

## Project Structure
- `Cargo.toml`: Rust dependencies and build configuration.
- `pyproject.toml`: Integration with Python build system.
- `src/lib.rs`: Rust source code with PyO3 bindings.
- `python/test_bridge.py`: Python code to verify the integration.
