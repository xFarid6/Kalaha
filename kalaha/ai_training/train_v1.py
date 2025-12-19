import os
import sys
import gymnasium as gym
from sb3_contrib import MaskablePPO
from sb3_contrib.common.wrappers import ActionMasker
from sb3_contrib.common.maskable.policies import MaskableActorCriticPolicy
from stable_baselines3.common.callbacks import CheckpointCallback
from stable_baselines3.common.monitor import Monitor

# Ensure we can import the env
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

try:
    from kalaha.training.kalaha_env import KalahaEnv
except ImportError:
    from kalaha.training.kalaha_env import KalahaEnv

# Parameters - V1 (High Performance)
# Increased total training time for better convergence
TIMESTEPS_PER_ITERATION = 50_000
TOTAL_ITERATIONS = 40  # 2,000,000 steps
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
    
    print("Initializing Kalaha Training V1 (High Accuracy)...")
    
    env = make_env()
    
    # Initialize Agent
    # We DO NOT load the old model by default unless specified, 
    # because the architecture might change (net_arch).
    # If net_arch changes, we must start fresh.
    
    model_name = "kalaha_v1_best"
    model_path = os.path.join(MODEL_DIR, f"{model_name}.zip")
    
    # Configuration for "Maximum Results"
    # 1. Deeper Network: [256, 256, 256] allows capturing complex board patterns.
    # 2. Lower LR: 1e-4 for stable convergence.
    # 3. Validation: High n_steps (4096) for stable updates relative to episode length.
    # 4. Entropy: 0.01 to prevent early convergence to suboptimal strategies.
    
    policy_kwargs = dict(
        net_arch=[256, 256, 256]
    )
    
    if os.path.exists(model_path):
        print(f"Loading existing V1 model from {model_path}")
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
            reset_num_timesteps=False
        )
        
        # Save "latest" and "best" (conceptually)
        model.save(os.path.join(MODEL_DIR, "kalaha_v1_latest"))
        # Also overwrite the unified 'kalaha_latest' if this is indeed better?
        # Maybe keep v1 separate to avoid breaking v0 consumers if architecture differs.
        # But gui_app loads 'kalaha_latest'.
        # We will save as kalaha_latest ONLY if we are confident.
        # For now, let's keep it separate mainly.
        model.save(os.path.join(MODEL_DIR, "kalaha_latest")) # Overwrite for GUI usage
        
        print(f"Iteration {i+1} complete. Model saved.")
        
    print("Training V1 Complete!")

if __name__ == "__main__":
    try:
        train()
    except Exception as e:
        print(f"Training Failed: {e}")
        import traceback
        traceback.print_exc()
