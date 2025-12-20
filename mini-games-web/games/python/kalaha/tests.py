import unittest
from game_logic import (
    initial_state, legal_moves, is_terminal, 
    evaluate, cleanup_board, apply_move,
    P1_PITS, P2_PITS, P1_STORE, P2_STORE
)

class TestKalahaLogic(unittest.TestCase):
    
    def test_initial_state(self):
        board = initial_state()
        self.assertEqual(len(board), 14)
        self.assertEqual(board[0], 6)
        self.assertEqual(board[6], 0)
        self.assertEqual(board[7], 6)
        self.assertEqual(board[13], 0)
        
    def test_legal_moves(self):
        board = initial_state()
        moves_p1 = legal_moves(board, 0)
        self.assertEqual(moves_p1, [0, 1, 2, 3, 4, 5])
        
        board[0] = 0
        moves_p1 = legal_moves(board, 0)
        self.assertEqual(moves_p1, [1, 2, 3, 4, 5])
        
    def test_apply_move_basic(self):
        board = initial_state()
        # P1 moves from index 0 (6 seeds)
        # Sowing: 1, 2, 3, 4, 5, 6(Store) - Ends in Store
        new_board, extra_turn = apply_move(board, 0, 0)
        
        self.assertEqual(new_board[0], 0)
        self.assertEqual(new_board[1], 7)
        self.assertEqual(new_board[6], 1) # Landed in store
        self.assertTrue(extra_turn)
        
    def test_apply_move_skip_opponent_store(self):
        # Setup board where P1 has enough seeds to wrap around
        board = [0] * 14
        board[5] = 8 
        # Sowing from 5: 
        # 6(Store), 7, 8, 9, 10, 11, 12, 13(Skip), 0
        
        # Note: Landing in 0 triggers a Capture because:
        # 1. 0 was empty
        # 2. It's P1's pit
        # 3. Opposite pit (12) has 1 seed (just received one)
        
        new_board, extra_turn = apply_move(board, 5, 0)
        
        self.assertEqual(new_board[5], 0)
        # Store gets: 1 (distribution) + 1 (from pit 0) + 1 (from pit 12) = 3
        self.assertEqual(new_board[6], 3) 
        self.assertEqual(new_board[12], 0) # Captured
        self.assertEqual(new_board[13], 0) # P2 Store (Skipped)
        self.assertEqual(new_board[0], 0) # Captured
        self.assertFalse(extra_turn) # Ended in 0 (Pit), not Store
        
    def test_capture(self):
        board = [0] * 14
        board[0] = 1 # P1 has 1 seed in pit 0
        board[1] = 0 # P1 pit 1 is empty (destination)
        board[11] = 5 # Opponent pit opposite to 1 (12-1 = 11) has 5 seeds
        
        # Move from 0 -> lands in 1 (empty) -> Capture 5 from 11 + 1 from 1 = 6 to Store
        new_board, extra_turn = apply_move(board, 0, 0)
        
        self.assertEqual(new_board[0], 0)
        self.assertEqual(new_board[1], 0) # Captured
        self.assertEqual(new_board[11], 0) # Captured
        self.assertEqual(new_board[6], 6) # 5 + 1
        self.assertFalse(extra_turn)

    def test_is_terminal(self):
        board = [0] * 14
        board[0] = 1
        # Need to ensure P2 also has seeds, otherwise it mimics terminal state (one side empty)
        board[7] = 1 
        self.assertFalse(is_terminal(board))
        
        board[0] = 0
        # All P1 pits empty
        self.assertTrue(is_terminal(board))
        
    def test_cleanup_board(self):
        board = [0] * 14
        board[6] = 10
        board[13] = 10
        board[7] = 2 # P2 has seeds left
        
        # P1 empty, so game over usually triggers this
        cleaned_board = cleanup_board(board)
        
        self.assertEqual(cleaned_board[7], 0)
        self.assertEqual(cleaned_board[13], 12) # 10 + 2
        self.assertEqual(cleaned_board[6], 10)

if __name__ == '__main__':
    unittest.main()
