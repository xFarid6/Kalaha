"""
Convert PyTorch model to TensorFlow.js format
Pipeline: PyTorch → ONNX → TensorFlow → TensorFlow.js
"""

import os
import sys
import torch
import numpy as np
from sb3_contrib import MaskablePPO

# Step 1: Load trained model
MODEL_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "models", "best_model.zip"))
OUTPUT_DIR = os.path.join("models", "kalaha_tfjs")

print("\n" + "="*60)
print("PyTorch → TensorFlow.js Conversion Pipeline")
print("="*60 + "\n")

print("Step 1: Loading PyTorch model...")
if not os.path.exists(MODEL_PATH):
    print(f"❌ Model not found at {MODEL_PATH}")
    print("Please train a model first using train_v1.py or train_v2.py")
    sys.exit(1)

try:
    model = MaskablePPO.load(MODEL_PATH)
    print(f"✓ Loaded model from {MODEL_PATH}")
except Exception as e:
    print(f"❌ Failed to load model: {e}")
    sys.exit(1)

# Step 2: Export to ONNX
print("\nStep 2: Exporting to ONNX format...")
try:
    import torch.onnx
    
    # Create dummy input
    dummy_input = torch.randn(1, 15, dtype=torch.float32)
    
    # Extract policy network
    policy_net = model.policy
    
    # Export
    onnx_path = "models/kalaha_policy.onnx"
    os.makedirs("models", exist_ok=True)
    
    torch.onnx.export(
        policy_net,
        dummy_input,
        onnx_path,
        export_params=True,
        opset_version=12,
        do_constant_folding=True,
        input_names=['observation'],
        output_names=['action', 'value'],
        dynamic_axes={
            'observation': {0: 'batch_size'},
            'action': {0: 'batch_size'},
            'value': {0: 'batch_size'}
        }
    )
    
    print(f"✓ Exported to ONNX: {onnx_path}")
    
except Exception as e:
    print(f"⚠️  ONNX export failed: {e}")
    print("Alternative: Use direct PyTorch to TensorFlow.js conversion")
    print("\nInstall required packages:")
    print("  pip install tensorflowjs")
    print("  pip install onnx onnx-tf")
    sys.exit(1)

# Step 3: Convert ONNX to TensorFlow
print("\nStep 3: Converting ONNX to TensorFlow...")
try:
    from onnx_tf.backend import prepare
    import onnx
    
    # Load ONNX model
    onnx_model = onnx.load(onnx_path)
    tf_rep = prepare(onnx_model)
    
    # Export to TensorFlow SavedModel format
    tf_model_path = "models/kalaha_tf"
    tf_rep.export_graph(tf_model_path)
    
    print(f"✓ Converted to TensorFlow: {tf_model_path}")
    
except ImportError:
    print("⚠️  onnx-tf not installed")
    print("Install with: pip install onnx-tf")
    sys.exit(1)
except Exception as e:
    print(f"❌ TensorFlow conversion failed: {e}")
    sys.exit(1)

# Step 4: Convert TensorFlow to TensorFlow.js
print("\nStep 4: Converting to TensorFlow.js...")
try:
    import subprocess
    
    result = subprocess.run([
        'tensorflowjs_converter',
        '--input_format=tf_saved_model',
        '--output_format=tfjs_graph_model',
        tf_model_path,
        OUTPUT_DIR
    ], capture_output=True, text=True)
    
    if result.returncode == 0:
        print(f"✓ Converted to TensorFlow.js: {OUTPUT_DIR}")
        print(f"  Model files:")
        for file in os.listdir(OUTPUT_DIR):
            print(f"    - {file}")
    else:
        print(f"❌ Conversion failed: {result.stderr}")
        sys.exit(1)
        
except FileNotFoundError:
    print("⚠️  tensorflowjs_converter not found")
    print("Install with: pip install tensorflowjs")
    sys.exit(1)
except Exception as e:
    print(f"❌ TensorFlow.js conversion failed: {e}")
    sys.exit(1)

# Step 5: Test the model
print("\nStep 5: Testing converted model...")
print("TODO: Implement Node.js test script")
print("Create: js/test_model.js to validate inference")

print("\n" + "="*60)
print("✅ Conversion Complete!")
print("="*60)
print(f"\nModel location: {OUTPUT_DIR}")
print("\nNext steps:")
print("1. Copy model files to kalaha-web/models/")
print("2. Test inference with TensorFlow.js")
print("3. Integrate with game UI\n")
