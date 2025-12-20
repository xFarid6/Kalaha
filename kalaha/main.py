# Ensure we can import modules from the same directory
import sys
import os

# Ensure parent directory is in path for imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

try:
    from kalaha.game_logic import (
        initial_state, legal_moves, apply_move, is_terminal, 
        evaluate, cleanup_board, P1_PITS, P2_PITS, P1_STORE, P2_STORE
    )
    from kalaha.ai_engine import get_best_move
    from kalaha.endgame_db import endgame_db
    import kalaha.gui_app as gui_app
except ImportError:
    # Fallback/Local imports if running from within kalaha/ dir without package structure?
    # Ideally the sys.path append above solves this, making 'kalaha' accessible.
    # But let's keep local fallback just in case, but cleaner.
    from game_logic import (
        initial_state, legal_moves, apply_move, is_terminal, 
        evaluate, cleanup_board, P1_PITS, P2_PITS, P1_STORE, P2_STORE
    )
    from ai_engine import get_best_move
    from endgame_db import endgame_db
    import gui_app

def print_board(board):
    print("\n" + "="*40)
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
            user_input = int(input(f"Player {player+1}, choose pit (1-6): "))
            if 1 <= user_input <= 6:
                if player == 0:
                    idx = user_input - 1
                else:
                    idx = user_input - 1 + 7
                
                if idx in valid_moves:
                    return idx
                else:
                    print("Invalid move (Empty pit).")
            else:
                print("Please enter a number between 1 and 6.")
        except ValueError:
            print("Invalid input.")

def get_player_type(mode: str, current_player: int) -> str:
    """Determine player type based on mode and current player"""
    if mode == 'BvB':
        return 'bot', 'bot'
    
    if mode == 'HvA':
        return ('human', 'agent') if current_player == 0 else ('agent', 'human')
    
    if mode == 'AvB':
        return ('agent', 'bot') if current_player == 0 else ('bot', 'agent')
        
    if mode == 'HvB':
        return ('human', 'bot') if current_player == 0 else ('bot', 'human')
        
    if mode == 'BvH':
        return ('bot', 'human') if current_player == 0 else ('human', 'bot')
        
    return ('human', 'human')  # HvH default

def main():
    print("Welcome to Kalaha!")
    print("[1] Terminal Mode")
    print("[2] Graphical Interface (Beta)")
    
    choice = input("Select interface: ")
    if choice == '2':
        gui_app.run_gui()
        return

    print("\n--- Terminal Mode ---")
    print("1. Human vs Human")
    print("2. Human (P1) vs Bot (P2)")
    print("3. Bot (P1) vs Human (P2)")
    print("4. Bot (P1) vs Bot (P2) (Simulation)")
    print("5. Human vs RL Agent (PPO)")
    print("6. RL Agent vs Bot (Simulation)")
    
    mode_input = input("Select mode: ")
    
    # Mode mapping for cleaner code
    MODE_MAP = {
        '1': 'HvH',
        '2': 'HvB',
        '3': 'BvH',
        '4': 'BvB',
        '5': 'HvA',
        '6': 'AvB'
    }
    
    mode = MODE_MAP.get(mode_input, 'HvH')  # Default to HvH if invalid
        
    # Configuration
    bot_depth = 6
    bot_strategy = 'balanced'
    sim_delay = 0.5
    
    if mode != 'HvH':
        try:
            d_input = input("Enter Bot Depth (1-20, default 6): ")
            if d_input.strip():
                bot_depth = int(d_input)
                
            print(" Strategies: basic, balanced, defensive, aggressive")
            s_input = input("Enter Bot Strategy (default 'balanced'): ")
            if s_input.strip():
                bot_strategy = s_input.strip()

            if mode == 'BvB':
                t_input = input("Simulation Delay (seconds, default 0.5): ")
                if t_input.strip():
                    sim_delay = float(t_input)
                
        except ValueError:
            print("Invalid input, using defaults.")
            
    board = initial_state()
    current_player = 0 
    
    while not is_terminal(board):
        print_board(board)
        
        extra_turn = False
        move = -1
        
        # Determine player types
        p1_type, p2_type = get_player_type(mode, current_player)
        player_type = p1_type if current_player == 0 else p2_type
        
        print(f"Turn: Player {current_player + 1} ({player_type.title()})")
        
        
        # Execute move based on player type
        if player_type == 'agent':
            # RL Agent move
            print("RL Agent is thinking...")
            try:
                import numpy as np
                from sb3_contrib import MaskablePPO
                import os
                
                model_path = os.path.join("models", "kalaha_latest.zip")
                if not os.path.exists(model_path):
                    model_path = os.path.join("..", "models", "kalaha_latest.zip")
                    
                if os.path.exists(model_path):
                    model = MaskablePPO.load(model_path)
                    
                    obs = np.zeros(15, dtype=np.int32)
                    if current_player == 0:
                        obs[0:6] = board[0:6]; obs[6] = board[6]; obs[7:13] = board[7:13]; obs[13] = board[13]; obs[14] = 0
                    else:
                        obs[0:6] = board[7:13]; obs[6] = board[13]; obs[7:13] = board[0:6]; obs[13] = board[6]; obs[14] = 1
                    
                    mask = [False]*6
                    pits = list(range(0,6)) if current_player == 0 else list(range(7,13))
                    for i, p in enumerate(pits):
                        if board[p] > 0: mask[i] = True
                        
                    action, _ = model.predict(obs, action_masks=mask, deterministic=True)
                    move = int(action) if current_player == 0 else int(action + 7)
                    
                    rel_move = move + 1 if current_player == 0 else move - 7 + 1
                    print(f"RL Agent chose pit: {rel_move} (Index {move})")
                else:
                    print("RL model not found! Falling back to random move.")
                    valid = legal_moves(board, current_player)
                    move = valid[0] if valid else None
            except Exception as e:
                print(f"RL Agent error: {e}. Falling back to random move.")
                valid = legal_moves(board, current_player)
                move = valid[0] if valid else None
                
        elif player_type == 'bot':
            print(f"Bot (Strategy: {bot_strategy}, Depth: {bot_depth}) is thinking...")
            
            if mode == 'BvB':
                time.sleep(sim_delay)
                
            move, nodes = get_best_move(board, current_player, depth=bot_depth, strategy=bot_strategy)
            if move is None:
                print("Bot has no legal moves!")
                break
            # Display relative move for readability
            rel_move = move + 1 if current_player == 0 else move - 7 + 1
            print(f"Bot chose pit: {rel_move} (Index {move}) [Analyzed {nodes} nodes]")
        else:  # human
            move = get_human_move(board, current_player)
            
        if move is None:
            break
            
        board, extra_turn = apply_move(board, move, current_player)
        
        if extra_turn:
            print("Extra Turn!")
        else:
            current_player = 1 - current_player
            
    # Game Over
    board = cleanup_board(board)
    print_board(board)
    
    # Save Endgame DB
    endgame_db.save()
    
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
