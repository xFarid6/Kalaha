import random
from typing import List

# Constants for Zobrist
NUM_PITS = 14
MAX_SEEDS = 100 

class ZobristHasher:
    def __init__(self) -> None:
        self.table: List[List[int]] = [[0] * MAX_SEEDS for _ in range(NUM_PITS)]
        self.turn_hash: int = random.getrandbits(64)
        self._init_table()
        
    def _init_table(self) -> None:
        for i in range(NUM_PITS):
            for j in range(MAX_SEEDS):
                self.table[i][j] = random.getrandbits(64)
                
    def compute_hash(self, board: List[int], current_player: int) -> int:
        """
        Computes the Zobrist hash for a given board and player.
        """
        h = 0
        if current_player == 1: # If Player 2's turn
            h ^= self.turn_hash
            
        for idx, seeds in enumerate(board):
            s = min(seeds, MAX_SEEDS - 1)
            h ^= self.table[idx][s]
            
        return h

# Global instance
zobrist = ZobristHasher()
