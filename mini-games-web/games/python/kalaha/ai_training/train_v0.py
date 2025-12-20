import os
import sys
import gymnasium as gym
from typing import Optional
from sb3_contrib import MaskablePPO # type: ignore
from sb3_contrib.common.wrappers import ActionMasker # type: ignore
from sb3_contrib.common.maskable.policies import MaskableActorCriticPolicy # type: ignore
from stable_baselines3.common.callbacks import CheckpointCallback # type: ignore
from stable_baselines3.common.monitor import Monitor # type: ignore

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

# Parameters
TIMESTEPS_PER_ITERATION: int = 50_000
TOTAL_ITERATIONS: int = 10 
MODEL_DIR: str = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'models'))
LOG_DIR: str = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'logs'))

def make_env() -> gym.Env:
    from kalaha.training.kalaha_env import KalahaEnv
    env = KalahaEnv()
    env = ActionMasker(env, lambda e: e.action_masks())
    env = Monitor(env, LOG_DIR)
    return env

def train() -> None:
    os.makedirs(MODEL_DIR, exist_ok=True)
    os.makedirs(LOG_DIR, exist_ok=True)
    
    print("Initializing Full Kalaha Training (v0)...")
    
    env: gym.Env = make_env()
    
    # Initialize Agent
    model_path: str = os.path.join(MODEL_DIR, "kalaha_latest.zip")
    
    model: MaskablePPO
    
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
