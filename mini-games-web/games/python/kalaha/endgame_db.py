import json
import os
from typing import Dict, Optional, List, Union

try:
    from zobrist_hashing import zobrist
except ImportError:
    from kalaha.zobrist_hashing import zobrist

DB_FILE = "endgame_db.json"

class EndgameDB:
    def __init__(self) -> None:
        self.db: Dict[str, int] = {} # Hash (str) -> Score (int)
        self.max_seeds: int = 0
        self.load()

    def load(self) -> None:
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

    def save(self) -> None:
        try:
            with open(DB_FILE, 'w') as f:
                data = {
                    "max_seeds": self.max_seeds,
                    "positions": self.db
                }
                json.dump(data, f, indent=4)
            print(f"Saved {len(self.db)} positions to {DB_FILE}.")
        except Exception as e:
            print(f"Error saving {DB_FILE}: {e}")

    def lookup(self, board: List[int], player: int) -> Optional[int]:
        """
        Returns exact score if position is solved, else None.
        """
        h = str(zobrist.compute_hash(board, player))
        return self.db.get(h)

    def add(self, board: List[int], player: int, score: int) -> None:
        """
        Adds a solved position.
        """
        h = str(zobrist.compute_hash(board, player))
        self.db[h] = score
        
        current_seeds = sum(board)
        if current_seeds > self.max_seeds:
            self.max_seeds = current_seeds

endgame_db = EndgameDB()
