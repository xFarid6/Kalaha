import copy
from typing import List, Tuple

# Constants
P1_PITS = list(range(0, 6))
P1_STORE = 6
P2_PITS = list(range(7, 13))
P2_STORE = 13
TOTAL_PITS = 14
SEEDS_PER_PIT = 6

def initial_state() -> List[int]:
    """
    Returns the initial board state as a list of 14 integers.
    """
    board = [0] * TOTAL_PITS
    for i in P1_PITS + P2_PITS:
        board[i] = SEEDS_PER_PIT
    return board

def legal_moves(board: List[int], player: int) -> List[int]:
    """
    Returns a list of valid pit indices for the given player.
    """
    if player == 0:
        return [i for i in P1_PITS if board[i] > 0]
    else:
        return [i for i in P2_PITS if board[i] > 0]

def is_terminal(board: List[int]) -> bool:
    """
    Checks if the game is over (one side has no seeds).
    """
    p1_empty = all(board[i] == 0 for i in P1_PITS)
    p2_empty = all(board[i] == 0 for i in P2_PITS)
    return p1_empty or p2_empty

def evaluate(board: List[int]) -> int:
    """
    Simple evaluation function: P1 Score - P2 Score.
    """
    return board[P1_STORE] - board[P2_STORE]

def cleanup_board(board: List[int]) -> List[int]:
    """
    Moves remaining seeds to respective stores when game ends.
    Returns the cleaned board.
    """
    new_board = list(board) # Copy
    for i in P1_PITS:
        new_board[P1_STORE] += new_board[i]
        new_board[i] = 0
    for i in P2_PITS:
        new_board[P2_STORE] += new_board[i]
        new_board[i] = 0
    return new_board

def apply_move(board: List[int], move: int, player: int) -> Tuple[List[int], bool]:
    """
    Applies a move to the board.
    Returns: (new_board, extra_turn_boolean)
    """
    new_board = list(board)
    seeds = new_board[move]
    new_board[move] = 0
    
    current_idx = move
    
    while seeds > 0:
        current_idx = (current_idx + 1) % TOTAL_PITS
        
        # Skip opponent's store
        if player == 0 and current_idx == P2_STORE:
            continue
        if player == 1 and current_idx == P1_STORE:
            continue
            
        new_board[current_idx] += 1
        seeds -= 1
        
    # Check for Extra Turn
    if player == 0 and current_idx == P1_STORE:
        return new_board, True
    if player == 1 and current_idx == P2_STORE:
        return new_board, True
        
    # Check for Capture
    was_empty = (new_board[current_idx] == 1) 
    
    if was_empty:
        if player == 0 and current_idx in P1_PITS:
            opposite_idx = 12 - current_idx
            if new_board[opposite_idx] > 0:
                captured_seeds = new_board[opposite_idx] + 1
                new_board[P1_STORE] += captured_seeds
                new_board[current_idx] = 0
                new_board[opposite_idx] = 0
                
        elif player == 1 and current_idx in P2_PITS:
            opposite_idx = 12 - current_idx
            if new_board[opposite_idx] > 0:
                captured_seeds = new_board[opposite_idx] + 1
                new_board[P2_STORE] += captured_seeds
                new_board[current_idx] = 0
                new_board[opposite_idx] = 0
                
    return new_board, False

def get_sowing_path(board: List[int], move: int, player: int) -> List[int]:
    """
    Calculates the sequence of pits that receive a seed during this move.
    Returns a list of pit indices.
    """
    path = []
    seeds = board[move]
    current_idx = move
    
    temp_seeds = seeds
    
    while temp_seeds > 0:
        current_idx = (current_idx + 1) % TOTAL_PITS
        
        # Skip opponent's store
        if player == 0 and current_idx == P2_STORE:
            continue
        if player == 1 and current_idx == P1_STORE:
            continue
            
        path.append(current_idx)
        temp_seeds -= 1
        
    return path
