import random
from game_logic import (
    legal_moves, apply_move, is_terminal, evaluate,
    P1_PITS, P2_PITS, P1_STORE, P2_STORE, cleanup_board
)

# Constants
MAX_DEPTH = 6
INF = float('inf')

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

def alphabeta(board, depth, alpha, beta, maximizing_player):
    """
    Minimax with Alpha-Beta pruning.
    Returns best score.
    """
    if depth == 0 or is_terminal(board):
        if is_terminal(board):
            final_board = cleanup_board(board)
            return final_board[P1_STORE] - final_board[P2_STORE]
        return evaluate_heuristic(board, 0)
    
    # Helper to get current player index
    current_player = 0 if maximizing_player else 1
    possible_moves = legal_moves(board, current_player)
    
    # Move ordering: prioritize captures or moves closest to store?
    # Simple optimization: check moves that land in store first?
    # For now, standard order.
    
    if maximizing_player:
        value = -INF
        for move in possible_moves:
            new_board, extra_turn = apply_move(board, move, 0)
            
            # If extra turn, continue with same depth and same player
            if extra_turn:
                score = alphabeta(new_board, depth, alpha, beta, True)
            else:
                score = alphabeta(new_board, depth - 1, alpha, beta, False)
                
            value = max(value, score)
            alpha = max(alpha, value)
            if alpha >= beta:
                break # Beta cut-off
        return value
    else:
        value = INF
        for move in possible_moves:
            new_board, extra_turn = apply_move(board, move, 1)
            
            if extra_turn:
                score = alphabeta(new_board, depth, alpha, beta, False)
            else:
                score = alphabeta(new_board, depth - 1, alpha, beta, True)
                
            value = min(value, score)
            beta = min(beta, value)
            if beta <= alpha:
                break # Alpha cut-off
        return value

def get_best_move(board, player, depth=MAX_DEPTH):
    """
    Determine the best move for the AI.
    player: 0 (Maximizing, P1) or 1 (Minimizing, P2)
    Returns the best move index.
    """
    possible_moves = legal_moves(board, player)
    if not possible_moves:
        return None
        
    best_move = -1
    
    # Initialize implementation-agnostic best value
    if player == 0:
        best_value = -INF
    else:
        best_value = INF
        
    alpha = -INF
    beta = INF
    
    # Root level search
    for move in possible_moves:
        new_board, extra_turn = apply_move(board, move, player)
        
        # If extra turn, continue with same player
        if extra_turn:
            # We are still at the root level essentially, but depth might decrement?
            # Actually if extra turn, we shouldn't decrement depth usually, 
            # but to prevent infinite loops in bad euristic setups, maybe we should?
            # Standard: Don't decrement depth for extra turn.
            
            # Since we need a score, we call alphabeta appropriately
            score = alphabeta(new_board, depth, alpha, beta, player == 0)
        else:
            # Hand over to opponent
            score = alphabeta(new_board, depth - 1, alpha, beta, player != 0) # if player 0, next is False (1)
        
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
