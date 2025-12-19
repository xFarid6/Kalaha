import random

# Constants for Zobrist
NUM_PITS = 14
# Max seeds per pit estimation. 
# Total seeds = 48 (in standard 4 seed game) or 72 (in 6 seed game).
# Theoretically all seeds could end up in one pit (Store).
MAX_SEEDS = 100 

class ZobristHasher:
    def __init__(self):
        self.table = [[0] * MAX_SEEDS for _ in range(NUM_PITS)]
        self.turn_hash = random.getrandbits(64)
        self._init_table()
        
    def _init_table(self):
        for i in range(NUM_PITS):
            for j in range(MAX_SEEDS):
                self.table[i][j] = random.getrandbits(64)
                
    def compute_hash(self, board, current_player):
        """
        Computes the Zobrist hash for a given board and player.
        """
        h = 0
        if current_player == 1: # If Player 2's turn
            h ^= self.turn_hash
            
        for idx, seeds in enumerate(board):
            # Cap seeds index to avoid IndexError if meaningful game state 
            # exceeds expected Max (unlikely but safe)
            s = min(seeds, MAX_SEEDS - 1)
            h ^= self.table[idx][s]
            
        return h

# Global instance
zobrist = ZobristHasher()
