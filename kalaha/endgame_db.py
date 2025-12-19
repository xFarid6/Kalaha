import json
import os
try:
    from zobrist_hashing import zobrist
except ImportError:
    from kalaha.zobrist_hashing import zobrist

DB_FILE = "endgame_db.json"

class EndgameDB:
    def __init__(self):
        self.db = {} # Hash (str) -> Score (int)
        self.max_seeds = 0
        self.load()

    def load(self):
        if os.path.exists(DB_FILE):
            try:
                with open(DB_FILE, 'r') as f:
                    data = json.load(f)
                    self.db = data.get("positions", {})
                    self.max_seeds = data.get("max_seeds", 0)
                    print(f"Loaded {len(self.db)} solved positions from {DB_FILE}. Max seeds: {self.max_seeds}")
            except Exception as e:
                print(f"Error loading {DB_FILE}: {e}")
                self.db = {}
        else:
            print("No endgame database found. Starting fresh.")

    def save(self):
        try:
            with open(DB_FILE, 'w') as f:
                data = {
                    "max_seeds": self.max_seeds,
                    "positions": self.db
                }
                json.dump(data, f)
            print(f"Saved {len(self.db)} positions to {DB_FILE}.")
        except Exception as e:
            print(f"Error saving {DB_FILE}: {e}")

    def lookup(self, board, player):
        """
        Returns exact score if position is solved, else None.
        """
        # Dictionary keys in JSON are strings
        h = str(zobrist.compute_hash(board, player))
        return self.db.get(h)

    def add(self, board, player, score):
        """
        Adds a solved position.
        """
        h = str(zobrist.compute_hash(board, player))
        self.db[h] = score
        
        # Update max_seeds statistics if needed
        # Note: Ideally we track the seed count of this board
        current_seeds = sum(board)
        # We only want to increase max_seeds threshold if we are confident 
        # we are solving this "tier" of seeds. 
        # For now, we update it simply to track what we've seen on specific solutions.
        if current_seeds > self.max_seeds:
            self.max_seeds = current_seeds

endgame_db = EndgameDB()
