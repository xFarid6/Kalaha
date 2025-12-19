import gymnasium as gym
from gymnasium import spaces
import numpy as np
import sys
import os

# Adjust path to import game_logic from parent directory
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from kalaha.game_logic import (
    initial_state, legal_moves, apply_move, is_terminal, 
    evaluate, cleanup_board, P1_PITS, P2_PITS, P1_STORE, P2_STORE
)

class KalahaEnv(gym.Env):
    """
    Kalaha Environment for Reinforcement Learning.
    Follows Gymnasium API.
    
    Observation Space: Box(15)
        - 0-5: My Pits
        - 6: My Store
        - 7-12: Opponent Pits
        - 13: Opponent Store
        - 14: Current Player (0 or 1) - actually helpful context? 
              Canonical view implies we always see board as "Me vs Opponent".
              So 14 could be just a placeholder or extra info like "Move Number".
              Let's keep it simple: Just board relative to current player.
    
    Action Space: Discrete(6)
        - 0-5 representing the 6 pits to sow from.
    """
    metadata = {'render.modes': ['human']}

    def __init__(self):
        super(KalahaEnv, self).__init__()
        
        # 14 pits + 1 extra info (optional, e.g., turn number or just flat 14)
        # User feedback suggested Box(15) with Player info, but Canonical View 
        # usually hides actual player ID and just presents "My state vs Opp state".
        # We will separate "Me" and "Opponent" strictly.
        
        self.observation_space = spaces.Box(
            low=0, high=72, shape=(15,), dtype=np.int32
        )
        
        self.action_space = spaces.Discrete(6)
        
        self.board = None
        self.current_player = 0
        self.max_moves = 200 # Prevent infinite games during training
        self.move_count = 0

    def reset(self, seed=None, options=None):
        super().reset(seed=seed)
        self.board = initial_state()
        self.current_player = 0
        self.move_count = 0
        return self._get_obs(), {}

    def step(self, action):
        """
        Action is an integer 0-5 (relative to current player's pits).
        """
        # 1. Validate Action
        # Map 0-5 to actual board indices
        if self.current_player == 0:
            actual_move = action # 0-5
        else:
            actual_move = action + 7 # 7-12
            
        valid_moves = legal_moves(self.board, self.current_player)
        
        # Illegal Move Handling
        # In MaskablePPO this shouldn't happen, but if it does (e.g. standard PPO),
        # we must punish heavily or ignore.
        if actual_move not in valid_moves:
            # Huge Penalty and Terminate? Or just ignore?
            # Standard RL practice: Masking is better. 
            # If forced: return penalties.
            return self._get_obs(), -10, True, False, {"error": "illegal_move"}
        
        # 2. Apply Move
        self.board, extra_turn = apply_move(self.board, actual_move, self.current_player)
        self.move_count += 1
        
        reward = 0
        terminated = False
        truncated = False
        
        # 3. Check for Game Over
        if is_terminal(self.board):
            terminated = True
            self.board = cleanup_board(self.board)
            p1_score = self.board[P1_STORE]
            p2_score = self.board[P2_STORE]
            
            # Reward logic: relative to who just moved? 
            # OR relative to self.current_player (the agent)?
            # Usually step returns reward for the action taken.
            # So if P1 moved and won, reward +1.
            
            if self.current_player == 0:
                reward = 1 if p1_score > p2_score else (-1 if p2_score > p1_score else 0)
            else:
                reward = 1 if p2_score > p1_score else (-1 if p1_score > p2_score else 0)
                
        elif self.move_count >= self.max_moves:
            truncated = True
        
        # 4. Switch Turns (if no extra turn)
        if not extra_turn:
            self.current_player = 1 - self.current_player
            
        # NOTE: self-play means we might just be handling the environment logic,
        # but masking who the "agent" is.
        # If we use a single agent training loop, 'step' usually implies 'environment reacts'.
        # In turn-based games, 'step' might need to include the OPPONENT'S move too
        # if we are training 1 agent vs fixed opponent.
        # IF Self-Play: The env usually returns the state for the NEXT player.
        # The training loop handles switching agents.
        # Here we return the observation for WHICHEVER player is active now (self.current_player).
        
        return self._get_obs(), reward, terminated, truncated, {}

    def _get_obs(self):
        """
        Returns Canonical View:
        Indices 0-6 represent 'Current Player', 7-13 'Opponent'.
        """
        obs = np.zeros(15, dtype=np.int32)
        
        if self.current_player == 0:
            # Me: 0-6 (P1), Opp: 7-13 (P2)
            obs[0:6] = self.board[0:6]        # My Pits
            obs[6] = self.board[P1_STORE]     # My Store
            obs[7:13] = self.board[7:13]      # Opp Pits
            obs[13] = self.board[P2_STORE]    # Opp Store
            obs[14] = 0 # ID 0
        else:
            # Me: 7-13 (P2), Opp: 0-6 (P1)
            obs[0:6] = self.board[7:13]       # My Pits
            obs[6] = self.board[P2_STORE]     # My Store
            obs[7:13] = self.board[0:6]       # Opp Pits
            obs[13] = self.board[P1_STORE]    # Opp Store
            obs[14] = 1 # ID 1
            
        return obs

    def action_masks(self):
        """
        Returns boolean mask of valid actions for the current player.
        Used by sb3-contrib MaskablePPO.
        """
        # Action space is 0-5.
        mask = [False] * 6
        
        if self.current_player == 0:
            pits = list(range(0, 6))
        else:
            pits = list(range(7, 13))
            
        for i, pit_idx in enumerate(pits):
            if self.board[pit_idx] > 0:
                mask[i] = True
                
        return mask

    def render(self, mode='human'):
        # Reuse existing print logic or simple print
        print(f"Player {self.current_player+1} Turn. Board: {self.board}")
