# Python Interpolation Engine

## Philosophy
This engine is built on a **declarative** philosophy. Instead of manually updating values every frame to create an animation, you simply describe the **instantaneous state** of your object.

You say: *"The position is now X."*
The engine says: *"Okay, I will smoothly transition from where it was to X over the specified duration."*

It is designed to be modular, plug-and-play, and easily integrated into any game loop or application that requires smooth state transitions.

## Usage

### Basic Example

```python
import time
from interpolation import Interpolated, Easing

# 1. Create an interpolated value, starting at 0.
#    Default duration is 0.5s, default easing is Linear.
position = Interpolated(0.0)

# 2. Change the state. Move to 100.
position.set_value(100.0)

# 3. In your game loop:
while True:
    current_pos = position.get_value()
    print(f"Current Position: {current_pos:.2f}")
    
    if current_pos == 100.0:
        break
    time.sleep(0.016)
```

### Customizing Transitions

You can change the duration or easing function at any time.

```python
# Use Elastic easing for a bouncy effect
scale = Interpolated(1.0, duration=1.0, easing=Easing.EASE_OUT_ELASTIC)

# Trigger a scale up
scale.set_value(2.0)
```

### Speed vs Duration

Sometimes you want a movement to always take `0.5s`. Other times, you want an object to move at `50 pixels/second` regardless of distance.

```python
# Set fixed duration
position.set_duration(2.0) # Take 2 seconds

# Set speed (calculates duration based on distance to target)
position.set_value(500)
position.set_speed(100) # Will take 5 seconds (distance 500 / speed 100)
```

## Easing Functions

The engine includes several helper formulas `C = A + delta * function(t)`.

- `LINEAR`: Constant speed.
- `EASE_IN_OUT_EXPONENTIAL`: Slow start, fast middle, slow end.
- `EASE_IN_BACK`: Retracts slightly before shooting forward.
- `EASE_OUT_BACK`: Shoots past the target and settles back.
- `EASE_OUT_ELASTIC`: Wobbly elastic effect at the end.

For more easing functions and visualizations, visit: [easings.net](https://easings.net/)

## Future Improvements
- Add more easing functions (Sine, Quad, Cubic, Quart, Quint).
- specialized support for 2D vectors or colors (currently works if the object supports arithmetic operations).
