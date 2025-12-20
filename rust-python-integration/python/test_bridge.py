import rust_bridge

def test_rust_functions():
    print("Testing Rust Bridge Integration...")
    
    # Test addition
    a, b = 10, 20
    result = rust_bridge.add(a, b)
    print(f"Rust 'add' function: {a} + {b} = {result}")
    
    # Test string formatting
    str_result = rust_bridge.sum_as_string(100, 200)
    print(f"Rust 'sum_as_string' function: 100 + 200 = {str_result}")

if __name__ == "__main__":
    try:
        test_rust_functions()
    except ImportError:
        print("Error: 'rust_bridge' module not found. Did you run 'maturin develop'?")
    except AttributeError as e:
        print(f"Error: {e}")
