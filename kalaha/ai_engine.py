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

# Transposition Table
# Key: Hash (int)
# Value: (score, depth, flag, best_move)
TT = {}

def evaluate_heuristic(board, player):
    """
    Advanced heuristic evaluation.
    Positive value favors Player 0 (P1/Max).
    """
    score = board[P1_STORE] - board[P2_STORE]
    
    # Material on board (0.5 weight)
    # Having seeds on your side is generally good for defense and mobility
    p1_side_seeds = sum(board[i] for i in P1_PITS)
    p2_side_seeds = sum(board[i] for i in P2_PITS)
    
    score += 0.5 * (p1_side_seeds - p2_side_seeds)
    
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

def alphabeta_tt(board, depth, alpha, beta, maximizing_player):
    """
    Minimax with Alpha-Beta pruning and Transposition Table.
    """
    current_player = 0 if maximizing_player else 1
    board_hash = zobrist.compute_hash(board, current_player)
    
    # TT Lookup
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

    if depth == 0 or is_terminal(board):
        if is_terminal(board):
            final_board = cleanup_board(board)
            return final_board[P1_STORE] - final_board[P2_STORE]
        
        val = evaluate_heuristic(board, 0)
        TT[board_hash] = (val, depth, 'EXACT')
        return val
    
    possible_moves = legal_moves(board, current_player)
    ordered_moves = order_moves(board, possible_moves, current_player)
    
    best_value = -INF if maximizing_player else INF
    # default flag
    tt_flag = 'EXACT' 

    if maximizing_player:
        value = -INF
        for move in ordered_moves:
            new_board, extra = apply_move(board, move, 0)
            
            if extra:
                score = alphabeta_tt(new_board, depth, alpha, beta, True)
            else:
                score = alphabeta_tt(new_board, depth - 1, alpha, beta, False)

            if score > value:
                value = score
            
            alpha = max(alpha, value)
            if alpha >= beta:
                tt_flag = 'LOWERBOUND' # Beta cutoff
                break
    else:
        value = INF
        for move in ordered_moves:
            new_board, extra = apply_move(board, move, 1)
            
            if extra:
                score = alphabeta_tt(new_board, depth, alpha, beta, False)
            else:
                score = alphabeta_tt(new_board, depth - 1, alpha, beta, True)
            
            if score < value:
                value = score
                
            beta = min(beta, value)
            if beta <= alpha:
                tt_flag = 'UPPERBOUND' # Alpha cutoff
                break

    # Store in TT
    # If we had a cutoff, the value is a bound.
    # Actually, simple version:
    # If val <= original_alpha -> Upper Bound (Fail Low)
    # If val >= original_beta -> Lower Bound (Fail High)
    # Else Exact
    # Here using simplified flag assignment from loop break
    
    TT[board_hash] = (value, depth, tt_flag)
    return value

def get_best_move(board, player, depth=MAX_DEPTH):
    """
    Determine the best move for the AI.
    player: 0 (Maximizing, P1) or 1 (Minimizing, P2)
    Returns the best move index.
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
            score = alphabeta_tt(new_board, depth, alpha, beta, player == 0)
        else:
            score = alphabeta_tt(new_board, depth - 1, alpha, beta, player != 0)
        
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
