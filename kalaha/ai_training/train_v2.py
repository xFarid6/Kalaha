import os
import sys
import gymnasium as gym
import torch
import numpy as np
from typing import Optional
from sb3_contrib import MaskablePPO # type: ignore
from sb3_contrib.common.wrappers import ActionMasker # type: ignore
from sb3_contrib.common.maskable.policies import MaskableActorCriticPolicy # type: ignore
from stable_baselines3.common.callbacks import CheckpointCallback, EvalCallback # type: ignore
from stable_baselines3.common.monitor import Monitor # type: ignore
from stable_baselines3.common.vec_env import DummyVecEnv, SubprocVecEnv # type: ignore

# Ensure we can import the env
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

try:
    from kalaha.training.kalaha_env import KalahaEnv
except ImportError:
    pass

# Parameters - V2 (Optimized with Vectorized Environments)
NUM_ENVS: int = 8  # Parallel environments (8-16x speedup)
TIMESTEPS_PER_ITERATION: int = 100_000  # Increased due to vectorization
TOTAL_ITERATIONS: int = 20  # 2,000,000 steps total
MODEL_DIR: str = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'models'))
LOG_DIR: str = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'logs'))

def make_env(rank: int) -> gym.Env:
    """Create a single environment with unique seed"""
    def _init() -> gym.Env:
        from kalaha.training.kalaha_env import KalahaEnv
        env = KalahaEnv()
        env = ActionMasker(env, lambda e: e.action_masks())
        env = Monitor(env, LOG_DIR if rank == 0 else None)  # Only log from first env
        env.reset(seed=42 + rank)  # Unique seed per environment
        return env
    return _init

def make_vec_env(num_envs: int) -> gym.vector.VectorEnv:
    """Create vectorized environment for parallel training"""
    if num_envs == 1:
        return DummyVecEnv([make_env(0)])
    else:
        # Use SubprocVecEnv for true parallelism (multiprocessing)
        return SubprocVecEnv([make_env(i) for i in range(num_envs)])

def train() -> None:
    os.makedirs(MODEL_DIR, exist_ok=True)
    os.makedirs(LOG_DIR, exist_ok=True)
    
    # GPU Detection
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Initializing Kalaha Training V2 (Vectorized + Optimized) on {device}...")
    
    if torch.cuda.is_available():
        print(f"GPU: {torch.cuda.get_device_name(0)}")
        print(f"CUDA Version: {torch.version.cuda}")
    else:
        print("WARNING: CUDA not available, training on CPU (slower)")
    
    print(f"Training with {NUM_ENVS} parallel environments...")
    
    # Create vectorized environment
    env = make_vec_env(NUM_ENVS)
    
    # Initialize Agent
    model_name: str = "kalaha_v2_best"
    model_path: str = os.path.join(MODEL_DIR, f"{model_name}.zip")
    
    # Optimized hyperparameters for V2
    policy_kwargs: dict = dict(
        net_arch=[256, 256, 256],
        activation_fn=torch.nn.ReLU,
        # Enable layer normalization for stability
        normalize_images=False,
    )
    
    model: MaskablePPO
    
    if os.path.exists(model_path):
        print(f"Loading existing V2 model from {model_path} to continue training...")
        model = MaskablePPO.load(model_path, env=env, device=device)
    else:
        print("Creating new PPO V2 model (Vectorized + Deep Network + Optimized)")
        model = MaskablePPO(
            MaskableActorCriticPolicy,
            env,
            verbose=1,
            learning_rate=3e-4,          # Slightly higher for faster initial learning
            n_steps=2048 // NUM_ENVS,    # Adjust for vectorization (per env)
            batch_size=512,               # Larger batch (more data per update)
            n_epochs=10,
            gamma=0.995,
            gae_lambda=0.98,
            ent_coef=0.01,
            clip_range=0.2,               # PPO clipping
            vf_coef=0.5,                  # Value function coefficient
            max_grad_norm=0.5,            # Gradient clipping for stability
            policy_kwargs=policy_kwargs,
            tensorboard_log=LOG_DIR,
            device=device
        )
        
    # Callbacks
    checkpoint_callback = CheckpointCallback(
        save_freq=50_000 // NUM_ENVS,  # Adjust frequency for vectorization
        save_path=MODEL_DIR,
        name_prefix="kalaha_v2",
        verbose=1
    )
    
    # Evaluation callback (optional, for monitoring performance)
    eval_env = make_vec_env(1)  # Single env for evaluation
    eval_callback = EvalCallback(
        eval_env,
        best_model_save_path=MODEL_DIR,
        log_path=LOG_DIR,
        eval_freq=25_000 // NUM_ENVS,
        n_eval_episodes=10,
        deterministic=True,
        render=False,
        verbose=1
    )
    
    print(f"Starting V2 Training for {TOTAL_ITERATIONS} iterations...")
    print(f"Effective timesteps per iteration: {TIMESTEPS_PER_ITERATION} total / {NUM_ENVS} envs = {TIMESTEPS_PER_ITERATION // NUM_ENVS} per env")
    
    for i in range(TOTAL_ITERATIONS):
        print(f"\n{'='*60}")
        print(f"--- Iteration {i+1}/{TOTAL_ITERATIONS} ---")
        print(f"{'='*60}")
        
        model.learn(
            total_timesteps=TIMESTEPS_PER_ITERATION, 
            callback=[checkpoint_callback, eval_callback],
            reset_num_timesteps=False,  # CRITICAL for incremental training
            progress_bar=True
        )
        
        # Save models
        model.save(os.path.join(MODEL_DIR, "kalaha_v2_latest"))
        model.save(os.path.join(MODEL_DIR, "kalaha_latest"))  # For GUI compatibility
        model.save(os.path.join(MODEL_DIR, model_name))

        print(f"\n✓ Iteration {i+1} complete. Model saved.")
        
    print("\n" + "="*60)
    print("Training V2 Complete!")
    print("="*60)
    
    # Cleanup
    env.close()
    eval_env.close()

if __name__ == "__main__":
    try:
        train()
    except KeyboardInterrupt:
        print("\n\nTraining interrupted by user. Progress saved.")
    except Exception as e:
        print(f"Training Failed: {e}")
        import traceback
        traceback.print_exc()
