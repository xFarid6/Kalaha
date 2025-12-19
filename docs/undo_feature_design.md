# UNDO Feature Design

## Overview
Implement an UNDO button that allows the player to revert to a previous game state, enhancing the learning and experimentation experience.

## Technical Implementation

### Game State History Tracking

**Already Implemented**: `GameScreen` now maintains `self.game_history: List[Dict[str, Any]]`

Each state snapshot contains:
```python
{
    'board': List[int],          # 14-element board state
    'current_player': int,       # 0 or 1
    'move_that_led_here': Optional[int],  # Pit index (None for initial state)
    'timestamp': float           # For debugging/replay
}
```

### Use Cases

#### 1. **Player Learning**
   - Try different moves
   - Explore "what if" scenarios
   - Learn optimal strategies without penalty

#### 2. **Mistake Recovery**
   - Accidental clicks on wrong pit
   - Misunderstanding game rules
   - Experimenting with tactics

#### 3. **Analysis Mode**
   - Review bot reasoning
   - Compare alternative lines
   - Study endgames

## UI Design (Future Implementation)

### Button Placement
- **Location**: Bottom-left of game screen
- **Style**: Consistent with existing UI (brown/gold theme)
- **State**: 
  - Disabled (grayed out) when no history
  - Active when undos available

### Visual Feedback
```
┌─────────────────────┐
│   [←] UNDO MOVE     │  ← Button
│   (3 moves back)    │  ← Counter
└─────────────────────┘
```

### Interaction Flow
1. Click UNDO button
2. Board animates backward (optional)
3. Counter updates
4. Game state restored

## Implementation Constraints

### Allowed Scenarios
✅ Player's own moves (Player 1)
✅ Bot's moves (if human reviews)
✅ Multiple undos in sequence

### Restricted Scenarios
❌ Cannot undo after game over (by design choice)
❌ UNDO during animation (state=ANIMATING)
❌ UNDO during bot thinking (state=THINKING)

**Rationale**: Maintain game state integrity and prevent race conditions.

## Technical Challenges

### 1. Memory Usage
- **Issue**: Storing full board state every move (14 ints × N moves)
- **Solution**: Kalaha has short games (~20-60 moves), negligible memory
- **Optimization** (if needed): Only store deltas

### 2. Animation Reversal
- **Challenge**: Sowing animation plays forward, how to reverse?
- **Options**:
  - A) Instant revert (no animation)
  - B) Reverse animation (seeds hop backward)
  - C) Fade transition
- **Recommended**: Option A (simplest, clearest)

### 3. Bot Interaction
- **Question**: What happens if player undos bot's move?
  - Bot will replay same move (deterministic strategy)
  - Solution: Flush bot's internal state or disable UNDO for bot turns
- **Design Choice**: Allow undo, but inform user bot will replay

### 4. Stats Tracking
- **Issue**: `total_nodes_analyzed` becomes misleading with undos
- **Solutions**:
  - A) Reset stats on UNDO
  - B) Keep stats (shows "wasted" computation)
  - C) Track "net moves" vs "total moves"
- **Recommended**: Option B with visual indicator

## Implementation Steps (Future)

### Phase 1: Core Functionality
```python
class GameScreen:
    def undo_move(self) -> bool:
        """Reverts to previous state. Returns success."""
        if len(self.game_history) <= 1:  # Only initial state
            return False
            
        if self.state != "IDLE":  # Safety check
            return False
            
        # Pop current state
        self.game_history.pop()
        
        # Restore previous
        prev_state = self.game_history[-1]
        self.board = prev_state['board'].copy()
        self.current_player = prev_state['current_player']
        
        return True
```

### Phase 2: UI Integration
- Add UNDO button to `draw()` method
- Handle click in `update()`
- Show undo counter
- Disable button when invalid

### Phase 3: Polish
- Visual feedback (brief flash/highlight)
- Sound effect (optional)
- Keyboard shortcut (Ctrl+Z)
- Undo history limit (e.g., max 10)

## Alternative: Full Game Replay

Instead of selective undo, offer **full game replay**:
- Save entire game on completion
- Replay from start with pause/step controls
- More complex but better for analysis

## Necessity Assessment

### Priority: **MEDIUM-HIGH**

**Pros**:
- Significantly improves user experience
- Enables experimentation without restarting
- Standard feature in strategy games
- Low implementation cost

**Cons**:
- Not critical for core gameplay
- Can be added later
- Requires UI real estate

### When to Implement
- ✅ **Now**: History tracking is already done
- ⏸️ **Later**: UI button and interaction logic
- 🎯 **After**: Animation reversal, advanced features

## Conclusion

The UNDO feature is a valuable quality-of-life improvement. With `game_history` already implemented, adding the UI button is the only remaining task. Recommended implementation:

1. Simple button in bottom bar
2. Instant state revert (no animation)
3. Work for Player 1 moves only initially
4. Keyboard shortcut support

This aligns with modern game design expectations and enhances the learning experience.
