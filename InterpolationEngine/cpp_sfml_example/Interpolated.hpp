#pragma once
#include <cmath>
#include <functional>
#include <algorithm>

enum class Easing {
    Linear,
    EaseOutElastic,
    // Add others...
};

// Simple easing function implementation
inline float applyEasing(float t, Easing easing) {
    if (t < 0.0f) return 0.0f;
    if (t > 1.0f) return 1.0f;
    
    switch (easing) {
        case Easing::Linear: return t;
        case Easing::EaseOutElastic: {
             if (t == 0) return 0;
             if (t == 1) return 1;
             float c4 = (2 * 3.14159f) / 3;
             return std::pow(2, -10 * t) * std::sin((t * 10 - 0.75f) * c4) + 1;
        }
        default: return t;
    }
}

template <typename T>
class Interpolated {
private:
    T start{};
    T end{};
    float startTime{};
    float duration{};
    Easing easingType{Easing::Linear};
    
    // Function to get current time globally or passed in. 
    // For simplicity, we assume the user updates a static time, or passes it.
    // Here we'll use a fast, simple approach: rely on the user passing 'now' or having a global accessor.
    // Let's assume a global accessor for this example context.
    static float (*timeProvider)(); 

public:
    explicit Interpolated(T const& initial_value = {}, float dur = 1.0f)
        : start{initial_value}
        , end{initial_value}
        , duration{dur}
    {
        if (timeProvider) startTime = timeProvider();
    }

    static void setTimeProvider(float (*provider)()) {
        timeProvider = provider;
    }

    void setValue(T const& new_value) {
        if (timeProvider) {
            start = getValue(); // Capture current state
            end = new_value;
            startTime = timeProvider();
        }
    }

    T getValue() const {
        if (!timeProvider) return end;
        
        float now = timeProvider();
        float elapsed = now - startTime;
        
        if (duration <= 0) return end;
        
        float t = elapsed / duration;
        float delta = applyEasing(t, easingType);
        
        // T must support + and * (and -)
        // C = A + (B - A) * t
        return start + (end - start) * delta;
    }

    void setDuration(float dur) { duration = dur; }
    void setEasing(Easing e) { easingType = e; }
    
    // Implicit conversion
    operator T() const { return getValue(); }

    // Assignment operator to trigger transition
    void operator=(T const& new_value) { setValue(new_value); }
};

// Initialize static member
template<typename T>
float (*Interpolated<T>::timeProvider)() = nullptr;
