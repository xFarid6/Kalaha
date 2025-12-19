import os
import sys
import gymnasium as gym
import numpy as np
from typing import Optional, Callable
from sb3_contrib import MaskablePPO # type: ignore
from sb3_contrib.common.wrappers import ActionMasker # type: ignore
from sb3_contrib.common.maskable.policies import MaskableActorCriticPolicy # type: ignore
from stable_baselines3.common.callbacks import CheckpointCallback # type: ignore
from stable_baselines3.common.monitor import Monitor # type: ignore

# Ensure we can import the env
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

try:
    from kalaha.training.kalaha_env import KalahaEnv
except ImportError:
    # Use generic import if local resolution fails, assuming package structure
    pass

# Parameters - V1 (High Performance)
# Increased total training time for better convergence
TIMESTEPS_PER_ITERATION: int = 50_000
TOTAL_ITERATIONS: int = 40  # 2,000,000 steps
MODEL_DIR: str = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'models'))
LOG_DIR: str = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'logs'))

def make_env() -> gym.Env:
    # Local import to avoid top-level failures if package not perfectly set
    from kalaha.training.kalaha_env import KalahaEnv
    env = KalahaEnv()
    env = ActionMasker(env, lambda e: e.action_masks())
    env = Monitor(env, LOG_DIR)
    return env

def train() -> None:
    os.makedirs(MODEL_DIR, exist_ok=True)
    os.makedirs(LOG_DIR, exist_ok=True)
    
    print("Initializing Kalaha Training V1 (High Accuracy)...")
    
    env: gym.Env = make_env()
    
    # Initialize Agent
    model_name: str = "kalaha_v1_best"
    model_path: str = os.path.join(MODEL_DIR, f"{model_name}.zip")
    
    # Configuration for "Maximum Results"
    policy_kwargs: dict = dict(
        net_arch=[256, 256, 256]
    )
    
    model: MaskablePPO
    
    if os.path.exists(model_path):
        print(f"Loading existing V1 model from {model_path} to continue training...")
        model = MaskablePPO.load(model_path, env=env)
    else:
        print("Creating new PPO V1 model (Deep Network, Optimized Hyperparams)")
        model = MaskablePPO(
            MaskableActorCriticPolicy,
            env,
            verbose=1,
            learning_rate=1e-4,          # Slower, more precise
            n_steps=4096,                # Collect more experience before update
            batch_size=256,              # Larger batch for stable gradients
            n_epochs=10,                 # Train more on each batch
            gamma=0.995,                 # Focus on long-term victory
            gae_lambda=0.98,
            ent_coef=0.01,               # Encourage exploration
            policy_kwargs=policy_kwargs,
            tensorboard_log=LOG_DIR
        )
        
    # Callbacks
    checkpoint_callback = CheckpointCallback(
        save_freq=50_000,
        save_path=MODEL_DIR,
        name_prefix="kalaha_v1"
    )
    
    print(f"Starting V1 Training for {TOTAL_ITERATIONS} iterations...")
    
    for i in range(TOTAL_ITERATIONS):
        print(f"--- Iteration {i+1}/{TOTAL_ITERATIONS} ---")
        model.learn(
            total_timesteps=TIMESTEPS_PER_ITERATION, 
            callback=checkpoint_callback,
            reset_num_timesteps=False # CRITICAL for incremental training
        )
        
        # Save "latest" and "best" (conceptually)
        model.save(os.path.join(MODEL_DIR, "kalaha_v1_latest"))
        
        # Overwrite the unified 'kalaha_latest' for the GUI
        model.save(os.path.join(MODEL_DIR, "kalaha_latest")) 
        
        # Also save the specific v1 checkpoint
        model.save(os.path.join(MODEL_DIR, model_name))

        print(f"Iteration {i+1} complete. Model saved.")
        
    print("Training V1 Complete!")

if __name__ == "__main__":
    try:
        train()
    except Exception as e:
        print(f"Training Failed: {e}")
        import traceback
        traceback.print_exc()
