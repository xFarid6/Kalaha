import os
import sys
import gymnasium as gym
from sb3_contrib import MaskablePPO
from sb3_contrib.common.wrappers import ActionMasker
from sb3_contrib.common.maskable.policies import MaskableActorCriticPolicy
from stable_baselines3.common.callbacks import CheckpointCallback
from stable_baselines3.common.monitor import Monitor

# Ensure we can import the env
# We are in kalaha/ai_training, so root is ../..
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

try:
    from kalaha.training.kalaha_env import KalahaEnv
except ImportError:
    # Fallback if run from root
    from kalaha.training.kalaha_env import KalahaEnv

# Parameters
TIMESTEPS_PER_ITERATION = 50_000
TOTAL_ITERATIONS = 10  # Total 500k steps
MODEL_DIR = os.path.join("..", "models") # Relative to this script? No, let's make it absolute or relative to root
# Best to use absolute from root
MODEL_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'models'))
LOG_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'logs'))

def make_env():
    env = KalahaEnv()
    env = ActionMasker(env, lambda e: e.action_masks())
    env = Monitor(env, LOG_DIR)
    return env

def train():
    os.makedirs(MODEL_DIR, exist_ok=True)
    os.makedirs(LOG_DIR, exist_ok=True)
    
    print("Initializing Full Kalaha Training (v0)...")
    
    env = make_env()
    
    # Initialize Agent
    model_path = os.path.join(MODEL_DIR, "kalaha_latest.zip")
    
    if os.path.exists(model_path):
        print(f"Loading existing model from {model_path}")
        model = MaskablePPO.load(model_path, env=env)
    else:
        print("Creating new PPO model")
        model = MaskablePPO(
            MaskableActorCriticPolicy,
            env,
            verbose=1,
            learning_rate=3e-4,
            n_steps=2048,
            batch_size=64,
            tensorboard_log=LOG_DIR
        )
        
    # Callbacks
    checkpoint_callback = CheckpointCallback(
        save_freq=10000,
        save_path=MODEL_DIR,
        name_prefix="kalaha_ppo_v0"
    )
    
    print(f"Starting Training for {TOTAL_ITERATIONS} iterations of {TIMESTEPS_PER_ITERATION} steps...")
    
    for i in range(TOTAL_ITERATIONS):
        print(f"--- Iteration {i+1}/{TOTAL_ITERATIONS} ---")
        model.learn(
            total_timesteps=TIMESTEPS_PER_ITERATION, 
            callback=checkpoint_callback,
            reset_num_timesteps=False
        )
        
        # Save "latest"
        model.save(os.path.join(MODEL_DIR, "kalaha_latest"))
        model.save(os.path.join(MODEL_DIR, f"kalaha_iter_{i+1}"))
        print(f"Iteration {i+1} complete. Model saved.")
        
    print("Training Complete!")

if __name__ == "__main__":
    try:
        train()
    except Exception as e:
        print(f"Training Failed: {e}")
        import traceback
        traceback.print_exc()
