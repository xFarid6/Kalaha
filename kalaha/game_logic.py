import copy

# Constants
P1_PITS = list(range(0, 6))
P1_STORE = 6
P2_PITS = list(range(7, 13))
P2_STORE = 13
TOTAL_PITS = 14
SEEDS_PER_PIT = 6

def initial_state():
    """
    Returns the initial board state as a list of 14 integers.
    Indices 0-5: Player 1 pits (6 seeds each)
    Index 6: Player 1 store (0 seeds)
    Indices 7-12: Player 2 pits (6 seeds each)
    Index 13: Player 2 store (0 seeds)
    """
    board = [0] * TOTAL_PITS
    for i in P1_PITS + P2_PITS:
        board[i] = SEEDS_PER_PIT
    return board

def legal_moves(board, player):
    """
    Returns a list of valid pit indices for the given player.
    Player 0 = Player 1
    Player 1 = Player 2
    """
    if player == 0:
        return [i for i in P1_PITS if board[i] > 0]
    else:
        return [i for i in P2_PITS if board[i] > 0]

def is_terminal(board):
    """
    Checks if the game is over (one side has no seeds).
    Returns True if terminal, False otherwise.
    """
    p1_empty = all(board[i] == 0 for i in P1_PITS)
    p2_empty = all(board[i] == 0 for i in P2_PITS)
    return p1_empty or p2_empty

def evaluate(board):
    """
    Simple evaluation function: P1 Score - P2 Score.
    """
    return board[P1_STORE] - board[P2_STORE]

def cleanup_board(board):
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

def apply_move(board, move, player):
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
    # If the last seed lands in the player's own store
    if player == 0 and current_idx == P1_STORE:
        return new_board, True
    if player == 1 and current_idx == P2_STORE:
        return new_board, True
        
    # Check for Capture
    # If last seed lands in an empty pit owned by the player, 
    # and the opposite pit has seeds.
    was_empty = (new_board[current_idx] == 1) # It was 0 before we added 1
    
    # Check ownership and capture eligibility
    if was_empty:
        if player == 0 and current_idx in P1_PITS:
            opposite_idx = 12 - current_idx
            if new_board[opposite_idx] > 0:
                # Capture!
                captured_seeds = new_board[opposite_idx] + 1 # +1 is the seed we just placed
                new_board[P1_STORE] += captured_seeds
                new_board[current_idx] = 0
                new_board[opposite_idx] = 0
                
        elif player == 1 and current_idx in P2_PITS:
            opposite_idx = 12 - current_idx
            if new_board[opposite_idx] > 0:
                 # Capture!
                captured_seeds = new_board[opposite_idx] + 1
                new_board[P2_STORE] += captured_seeds
                new_board[current_idx] = 0
                new_board[opposite_idx] = 0
                
    return new_board, False
