import random
from collections import OrderedDict
from typing import List, Tuple, Optional, Any, Dict

# Imports with fallback
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
TT: Dict[int, Tuple[float, int, str]] = {}

# Global counter for nodes visited
NODES_VISITED = 0

def evaluate_heuristic(board: List[int], player: int, strategy: str = 'balanced') -> float:
    """
    Advanced heuristic evaluation with multiple strategies.
    Positive value favors Player 0 (P1/Max).
    Strategies: 'balanced', 'aggressive', 'defensive', 'basic'
    """
    store_diff = board[P1_STORE] - board[P2_STORE]
    
    if strategy == 'basic':
        return float(store_diff)
        
    p1_side_seeds = sum(board[i] for i in P1_PITS)
    p2_side_seeds = sum(board[i] for i in P2_PITS)
    side_diff = p1_side_seeds - p2_side_seeds
    
    score = float(store_diff)
    
    if strategy == 'balanced':
        score += 0.5 * side_diff
    elif strategy == 'defensive':
        score += 0.8 * side_diff
        empty_p1 = sum(1 for i in P1_PITS if board[i] == 0)
        score -= 2.0 * empty_p1
    elif strategy == 'aggressive':
        score += 0.3 * side_diff
        
    return score

def order_moves(board: List[int], moves: List[int], player: int) -> List[int]:
    """
    Orders moves to improve Alpha-Beta pruning.
    """
    ordered = []
    
    for move in moves:
        sim_board, extra_turn = apply_move(board, move, player)
        
        score_diff = (sim_board[P1_STORE] - sim_board[P2_STORE]) if player == 0 else (sim_board[P2_STORE] - sim_board[P1_STORE])
        prev_diff = (board[P1_STORE] - board[P2_STORE]) if player == 0 else (board[P2_STORE] - board[P1_STORE])
        
        captured = (score_diff - prev_diff) > 1
        
        priority = 0.0
        if extra_turn:
            priority += 1000.0
        if captured:
            priority += 500.0
        
        priority += random.random()
        
        ordered.append((priority, move))
        
    ordered.sort(key=lambda x: x[0], reverse=True)
    return [m for p, m in ordered]

def alphabeta_tt_db(board: List[int], depth: int, alpha: float, beta: float, maximizing_player: bool, strategy: str = 'balanced') -> float:
    """
    Minimax with Alpha-Beta pruning, Transposition Table, and Endgame DB.
    """
    global NODES_VISITED
    NODES_VISITED += 1
    
    current_player = 0 if maximizing_player else 1
    
    # 1. Endgame DB Lookup (if seeds low enough)
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
            val = float(final_board[P1_STORE] - final_board[P2_STORE])
            
            # Save solved terminal state to DB + TT
            endgame_db.add(board, current_player, int(val))
            TT[board_hash] = (val, 100, 'EXACT') 
            return val
        
        val = evaluate_heuristic(board, 0, strategy)
        TT[board_hash] = (val, depth, 'EXACT')
        return val
    
    possible_moves = legal_moves(board, current_player)
    ordered_moves = order_moves(board, possible_moves, current_player)
    
    value: float
    tt_flag: str = 'EXACT'

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
    
    return value

def get_best_move(board: List[int], player: int, depth: int = MAX_DEPTH, strategy: str = 'balanced') -> Tuple[Optional[int], int]:
    """
    Determine the best move for the AI.
    Returns: (best_move, nodes_analyzed)
    """
    global NODES_VISITED
    NODES_VISITED = 0
    
    possible_moves = legal_moves(board, player)
    ordered_moves = order_moves(board, possible_moves, player)
    
    if not ordered_moves:
        return None, 0
        
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
            
    return best_move, NODES_VISITED
