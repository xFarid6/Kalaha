# Interpolation in C++ with SFML

## Theory
Implementing this interpolation engine in C++ follows the exact same philosophy as the Python version: **Declarative State**.

In a typical C++ game loop (like with SFML), you have a `update(dt)` and `render()` phase. 
The `Interpolated` object holds the state (`start`, `end`, `start_time`).
- `start_time` is best managed using a monotonic clock (like `sf::Clock` or `std::chrono`).
- Templates (`typename T`) allow this to work for `float`, `sf::Vector2f`, or even `sf::Color` (as long as operators `+`, `-`, `*` are overloaded).

## Implementation Details

### The Struct
As suggested, a struct/class template `Interpolated<T>` acts as a wrapper around any value you want to animate.

```cpp
template <typename T>
struct Interpolated {
    T start;
    T end;
    float startTime;
    float duration;
    // ...
};
```

### Implicit Conversion
By overloading `operator T()`, you can treat the object *as if* it were the underlying value.
`float currentX = myInterpolatedX;` calls the getter automatically.

## SFML Integration
 SFML provides `sf::Clock` which is perfect for tracking `startTime`.

### Example Usage
```cpp
sf::Clock globalClock;
Interpolated<float> opacity(255.0f);

// In update loop
sprite.setColor(sf::Color(255, 255, 255, (sf::Uint8)opacity));

// Trigger fade out
opacity.setValue(0.0f);
```

See the `cpp_sfml_example` folder for a concrete implementation.
