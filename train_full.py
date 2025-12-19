import os
import glob
import sys
import gymnasium as gym
from sb3_contrib import MaskablePPO
from sb3_contrib.common.wrappers import ActionMasker
from sb3_contrib.common.maskable.policies import MaskableActorCriticPolicy
from stable_baselines3.common.callbacks import CheckpointCallback, EvalCallback
from stable_baselines3.common.monitor import Monitor

# Ensure we can import the env
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

from kalaha.training.kalaha_env import KalahaEnv

# Parameters
TIMESTEPS_PER_ITERATION = 50_000
TOTAL_ITERATIONS = 10  # Total 500k steps for intro
MODEL_DIR = "models"
LOG_DIR = "logs"

def make_env():
    env = KalahaEnv()
    env = ActionMasker(env, lambda e: e.action_masks())
    env = Monitor(env, LOG_DIR)
    return env

def train():
    os.makedirs(MODEL_DIR, exist_ok=True)
    os.makedirs(LOG_DIR, exist_ok=True)
    
    print("Initializing Full Kalaha Training...")
    
    env = make_env()
    
    # Initialize Agent
    # If a model exists, load it? For now start fresh or load 'latest'
    model_path = f"{MODEL_DIR}/kalaha_latest.zip"
    
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
        name_prefix="kalaha_ppo"
    )
    
    # Self-Play Loop
    # In a rigorous self-play, we would update the opponent environment. 
    # Current KalahaEnv defines opponent as 'Environment Logic' (Standard Rules) or Random?
    # Our env implements rules. To do self-play, the 'step' function needs to call the opponent model.
    # Currently KalahaEnv.step() just applies a move. It assumes the caller handles the other player?
    # NO: KalahaEnv.step applies ONE move and swaps turn.
    # PPO learns to play BOTH sides if we just flip observation.
    # But when playing, it plays against...?
    # If we train simply with PPO, the "opponent" moves are also chosen by PPO? 
    # No, PPO calls step(), gets new state.
    # If new state is P2 turn, and PPO predicts move for P2.
    # So PPO is playing against ITSELF naturally in a single environment instance 
    # if the env just asks "What move for Player X?".
    # Yes! Because we flip the board in _get_obs, the network ALWAYS sees itself as "Player 0".
    # So it learns: "Given board state X, make move Y".
    # Since it plays both sides in the rollouts, it IS self-play (shared weights).
    # This is "Symmetric Self-Play".
    
    print(f"Starting Training for {TOTAL_ITERATIONS} iterations of {TIMESTEPS_PER_ITERATION} steps...")
    
    for i in range(TOTAL_ITERATIONS):
        print(f"--- Iteration {i+1}/{TOTAL_ITERATIONS} ---")
        model.learn(
            total_timesteps=TIMESTEPS_PER_ITERATION, 
            callback=checkpoint_callback,
            reset_num_timesteps=False
        )
        
        # Save "latest"
        model.save(f"{MODEL_DIR}/kalaha_latest")
        model.save(f"{MODEL_DIR}/kalaha_iter_{i+1}")
        print(f"Iteration {i+1} complete. Model saved.")
        
    print("Training Complete!")

if __name__ == "__main__":
    try:
        train()
    except Exception as e:
        print(f"Training Failed: {e}")
        import traceback
        traceback.print_exc()
