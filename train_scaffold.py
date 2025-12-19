import sys
import os
import gymnasium as gym
from sb3_contrib import MaskablePPO
from sb3_contrib.common.wrappers import ActionMasker
from sb3_contrib.common.maskable.policies import MaskableActorCriticPolicy

# Ensure we can import the env
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

from kalaha.training.kalaha_env import KalahaEnv

def make_env():
    return KalahaEnv()

def mask_fn(env: gym.Env):
    return env.action_masks()

def train():
    print("Initializing Kalaha RL Training...")
    
    # 1. Create Environment wrapped with Action Masker
    # Action Masking is CRITICAL for Kalaha to avoid illegal moves
    env = KalahaEnv()
    env = ActionMasker(env, mask_fn)
    
    # 2. Define Model
    # Using MaskablePPO from sb3-contrib
    model = MaskablePPO(
        MaskableActorCriticPolicy,
        env,
        verbose=1,
        learning_rate=3e-4,
        gamma=0.99,
        n_steps=2048,
        batch_size=64,
        tensorboard_log="./kalaha_tensorboard/"
    )
    
    # 3. Train (for a short demo duration)
    # In real training: total_timesteps=1_000_000+
    print("Starting Learning Loop...")
    model.learn(total_timesteps=10000)
    
    # 4. Save
    model.save("kalaha_ppo_model")
    print("Model saved as kalaha_ppo_model.zip")
    
    # Demonstration of loading and playing would go here

if __name__ == "__main__":
    # Check if libraries are installed
    try:
        import sb3_contrib
        import gymnasium
    except ImportError:
        print("Error: Missing libraries.")
        print("Please run: pip install gymnasium stable-baselines3 sb3-contrib shimmy")
        sys.exit(1)
        
    train()
