import sys
import time

# Ensure we can import modules from the same directory
try:
    from game_logic import (
        initial_state, legal_moves, apply_move, is_terminal, 
        evaluate, cleanup_board, P1_PITS, P2_PITS, P1_STORE, P2_STORE
    )
    from ai_engine import get_best_move
except ImportError:
    # If running from parent directory
    from kalaha.game_logic import (
        initial_state, legal_moves, apply_move, is_terminal, 
        evaluate, cleanup_board, P1_PITS, P2_PITS, P1_STORE, P2_STORE
    )
    from kalaha.ai_engine import get_best_move

def print_board(board):
    print("\n" + "="*40)
    # Player 2 (Top) - Indices 12, 11, 10, 9, 8, 7
    # Reverse order for display purposes so 7 is on left? 
    # Usually: Store P2 (Left) -- Pits -- Store P1 (Right)?
    # User said: "Granaio è alla destra del giocatore"
    # So P1 Store is Right of P1.
    # P2 Store is Right of P2 -> So Left of P1 from P1 pov.
    
    # Text Layout:
    #       [12][11][10][ 9][ 8][ 7]
    # (13)                          ( 6)
    #       [ 0][ 1][ 2][ 3][ 4][ 5]
    
    p2_row = [board[i] for i in reversed(P2_PITS)]
    p1_row = [board[i] for i in P1_PITS]
    
    print(f"      {'  '.join(f'{x:2}' for x in p2_row)}")
    print(f"({board[P2_STORE]:2})                        ({board[P1_STORE]:2})")
    print(f"      {'  '.join(f'{x:2}' for x in p1_row)}")
    print("="*40 + "\n")

def get_human_move(board, player):
    valid_moves = legal_moves(board, player)
    if not valid_moves:
        return None
    
    while True:
        try:
            # Map input 1-6 to indices 0-5 or 7-12
            user_input = int(input(f"Player {player+1}, choose pit (1-6): "))
            if 1 <= user_input <= 6:
                if player == 0:
                    idx = user_input - 1
                else:
                    # Player 2 input: 1 corresponds to 7? or 1 corresponds to 12?
                    # Usually intuitive to map Left-to-Right from player perspective?
                    # But P2 is on top.
                    # Let's assume global indexing or simple 'first pit'.
                    # Let's map 1->7, 2->8... for consistency
                    idx = user_input - 1 + 7
                
                if idx in valid_moves:
                    return idx
                else:
                    print("Invalid move (Empty pit).")
            else:
                print("Please enter a number between 1 and 6.")
        except ValueError:
            print("Invalid input.")

def main():
    print("Welcome to Kalaha!")
    print("1. Human vs Human")
    print("2. Human (P1) vs Bot (P2)")
    print("3. Bot (P1) vs Human (P2)")
    
    mode_input = input("Select mode: ")
    mode = 'HvH'
    if mode_input == '2':
        mode = 'HvB'
    elif mode_input == '3':
        mode = 'BvH'
        
    board = initial_state()
    current_player = 0 # Player 1 starts
    
    while not is_terminal(board):
        print_board(board)
        
        extra_turn = False
        move = -1
        
        # Determine who is moving
        is_bot = False
        if (mode == 'HvB' and current_player == 1) or \
           (mode == 'BvH' and current_player == 0):
            is_bot = True
            
        print(f"Turn: Player {current_player + 1} ({'Bot' if is_bot else 'Human'})")
        
        if is_bot:
            print("Bot is thinking...")
            # Artificial delay?
            # time.sleep(1)
            move = get_best_move(board, current_player, depth=6)
            if move is None:
                print("Bot has no legal moves!") # Should be terminal usually
                break
            print(f"Bot chose pit: {move} ({move if current_player==0 else move-7} relative)")
        else:
            move = get_human_move(board, current_player)
            
        if move is None:
            break
            
        board, extra_turn = apply_move(board, move, current_player)
        
        if extra_turn:
            print("Extra Turn!")
            # Player stays the same
        else:
            current_player = 1 - current_player
            
    # Game Over
    board = cleanup_board(board)
    print_board(board)
    
    score_p1 = board[P1_STORE]
    score_p2 = board[P2_STORE]
    
    print(f"Game Over!")
    print(f"Score P1: {score_p1}")
    print(f"Score P2: {score_p2}")
    
    if score_p1 > score_p2:
        print("Player 1 Wins!")
    elif score_p2 > score_p1:
        print("Player 2 Wins!")
    else:
        print("Draw!")

if __name__ == "__main__":
    main()
