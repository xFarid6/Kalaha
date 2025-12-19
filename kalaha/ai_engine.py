import random
from collections import OrderedDict
try:
    from game_logic import (
        legal_moves, apply_move, is_terminal, evaluate,
        P1_PITS, P2_PITS, P1_STORE, P2_STORE, cleanup_board
    )
    from zobrist_hashing import zobrist
except ImportError:
    from kalaha.game_logic import (
        legal_moves, apply_move, is_terminal, evaluate,
        P1_PITS, P2_PITS, P1_STORE, P2_STORE, cleanup_board
    )
    from kalaha.zobrist_hashing import zobrist

# Constants
MAX_DEPTH = 6
INF = float('inf')

try:
    from game_logic import (
        legal_moves, apply_move, is_terminal, evaluate,
        P1_PITS, P2_PITS, P1_STORE, P2_STORE, cleanup_board
    )
    from zobrist_hashing import zobrist
    from endgame_db import endgame_db
except ImportError:
    from kalaha.game_logic import (
        legal_moves, apply_move, is_terminal, evaluate,
        P1_PITS, P2_PITS, P1_STORE, P2_STORE, cleanup_board
    )
    from kalaha.zobrist_hashing import zobrist
    from kalaha.endgame_db import endgame_db

# Constants
MAX_DEPTH = 6
INF = float('inf')

# Transposition Table
TT = {}

def evaluate_heuristic(board, player, strategy='balanced'):
    """
    Advanced heuristic evaluation with multiple strategies.
    Positive value favors Player 0 (P1/Max).
    Strategies: 'balanced', 'aggressive', 'defensive', 'basic'
    """
    store_diff = board[P1_STORE] - board[P2_STORE]
    
    if strategy == 'basic':
        return store_diff
        
    p1_side_seeds = sum(board[i] for i in P1_PITS)
    p2_side_seeds = sum(board[i] for i in P2_PITS)
    side_diff = p1_side_seeds - p2_side_seeds
    
    score = store_diff
    
    if strategy == 'balanced':
        score += 0.5 * side_diff
    elif strategy == 'defensive':
        # Prioritize keeping seeds on own side to prevent opponent capturing/running out
        score += 0.8 * side_diff
        # Penalize empty pits on own side?
        empty_p1 = sum(1 for i in P1_PITS if board[i] == 0)
        score -= 2.0 * empty_p1
    elif strategy == 'aggressive':
        # Prioritize side control less, focus on mobility/captures (handled in move ordering?)
        # Maybe value opponent having few seeds (vulnrability)
        score += 0.3 * side_diff
        
    return score

def order_moves(board, moves, player):
    """
    Orders moves to improve Alpha-Beta pruning.
    Priorities:
    1. Extra Turn moves
    2. Capture moves (heuristic check)
    3. Others
    """
    ordered = []
    
    for move in moves:
        # Simulate to check for properties
        # This is slightly expensive, but usually worth it for pruning.
        # To avoid full copy inside sorting, we do a lightweight check or just simulate.
        # Given small Board size, simulation is OK.
        
        sim_board, extra_turn = apply_move(board, move, player)
        
        score_diff = (sim_board[P1_STORE] - sim_board[P2_STORE]) if player == 0 else (sim_board[P2_STORE] - sim_board[P1_STORE])
        prev_diff = (board[P1_STORE] - board[P2_STORE]) if player == 0 else (board[P2_STORE] - board[P1_STORE])
        
        captured = (score_diff - prev_diff) > 1 # If store increased by more than 1 (the seed dropped), a capture occurred.
        
        priority = 0
        if extra_turn:
            priority += 1000
        if captured:
            priority += 500
        
        # Add random noise to break ties or use heuristic
        priority += random.random()
        
        ordered.append((priority, move))
        
    ordered.sort(key=lambda x: x[0], reverse=True)
    return [m for p, m in ordered]

def alphabeta_tt_db(board, depth, alpha, beta, maximizing_player, strategy='balanced'):
    """
    Minimax with Alpha-Beta pruning, Transposition Table, and Endgame DB.
    """
    current_player = 0 if maximizing_player else 1
    
    # 1. Endgame DB Lookup (if seeds low enough)
    # Check if total seeds is within DB range (e.g. <= max_seeds in DB + X to grow it?)
    # For now, trust the user logic "read from when seeds <= 10" (or loaded max)
    total_seeds = sum(board)
    if total_seeds <= max(10, endgame_db.max_seeds):
        exact_val = endgame_db.lookup(board, current_player)
        if exact_val is not None:
            return exact_val

    board_hash = zobrist.compute_hash(board, current_player)
    
    # 2. TT Lookup
    if board_hash in TT:
        tt_val, tt_depth, tt_flag = TT[board_hash]
        if tt_depth >= depth:
            if tt_flag == 'EXACT':
                return tt_val
            elif tt_flag == 'LOWERBOUND':
                alpha = max(alpha, tt_val)
            elif tt_flag == 'UPPERBOUND':
                beta = min(beta, tt_val)
            
            if alpha >= beta:
                return tt_val

    # 3. Terminal Node or Depth Limit
    if depth == 0 or is_terminal(board):
        if is_terminal(board):
            final_board = cleanup_board(board)
            val = final_board[P1_STORE] - final_board[P2_STORE]
            
            # Save solved terminal state to DB + TT
            endgame_db.add(board, current_player, val)
            TT[board_hash] = (val, 100, 'EXACT') # Depth 100 for terminal
            return val
        
        val = evaluate_heuristic(board, 0, strategy)
        TT[board_hash] = (val, depth, 'EXACT')
        return val
    
    possible_moves = legal_moves(board, current_player)
    ordered_moves = order_moves(board, possible_moves, current_player)
    
    best_value = -INF if maximizing_player else INF
    tt_flag = 'EXACT' 

    if maximizing_player:
        value = -INF
        for move in ordered_moves:
            new_board, extra = apply_move(board, move, 0)
            
            if extra:
                score = alphabeta_tt_db(new_board, depth, alpha, beta, True, strategy)
            else:
                score = alphabeta_tt_db(new_board, depth - 1, alpha, beta, False, strategy)

            if score > value:
                value = score
            
            alpha = max(alpha, value)
            if alpha >= beta:
                tt_flag = 'LOWERBOUND'
                break
    else:
        value = INF
        for move in ordered_moves:
            new_board, extra = apply_move(board, move, 1)
            
            if extra:
                score = alphabeta_tt_db(new_board, depth, alpha, beta, False, strategy)
            else:
                score = alphabeta_tt_db(new_board, depth - 1, alpha, beta, True, strategy)
            
            if score < value:
                value = score
                
            beta = min(beta, value)
            if beta <= alpha:
                tt_flag = 'UPPERBOUND' 
                break

    TT[board_hash] = (value, depth, tt_flag)
    
    # If this was a deep search result (e.g. fully solved or very deep), we could add to DB too?
    # For now, only terminal states are added to DB safely inside the recursion.
    
    return value

def get_best_move(board, player, depth=MAX_DEPTH, strategy='balanced'):
    """
    Determine the best move for the AI.
    """
    possible_moves = legal_moves(board, player)
    ordered_moves = order_moves(board, possible_moves, player)
    
    if not ordered_moves:
        return None
        
    best_move = -1
    best_value = -INF if player == 0 else INF
        
    alpha = -INF
    beta = INF
    
    for move in ordered_moves:
        new_board, extra_turn = apply_move(board, move, player)
        
        if extra_turn:
            score = alphabeta_tt_db(new_board, depth, alpha, beta, player == 0, strategy)
        else:
            score = alphabeta_tt_db(new_board, depth - 1, alpha, beta, player != 0, strategy)
        
        if player == 0:
            if score > best_value:
                best_value = score
                best_move = move
            alpha = max(alpha, best_value)
        else:
            if score < best_value:
                best_value = score
                best_move = move
            beta = min(beta, best_value)
            
    return best_move
