import math
import time
from enum import Enum, auto

class Easing(Enum):
    LINEAR = auto()
    EASE_IN_OUT_EXPONENTIAL = auto()
    EASE_IN_BACK = auto()
    EASE_OUT_BACK = auto()
    EASE_OUT_ELASTIC = auto()

def linear(t):
    return t

def ease_in_out_exponential(t):
    if t == 0: return 0
    if t == 1: return 1
    if t < 0.5:
        return math.pow(2, 20 * t - 10) / 2
    else:
        return (2 - math.pow(2, -20 * t + 10)) / 2

def ease_in_back(t):
    c1 = 1.70158
    c3 = c1 + 1
    return c3 * t * t * t - c1 * t * t

def ease_out_back(t):
    c1 = 1.70158
    c3 = c1 + 1
    return 1 + c3 * math.pow(t - 1, 3) + c1 * math.pow(t - 1, 2)

def ease_out_elastic(t):
    if t == 0: return 0
    if t == 1: return 1
    
    c4 = (2 * math.pi) / 3
    return math.pow(2, -10 * t) * math.sin((t * 10 - 0.75) * c4) + 1

class Interpolated:
    def __init__(self, initial_value, duration=0.5, easing=Easing.LINEAR):
        """
        initial_value: The starting value (can be float, int, or anything supporting + and *).
        duration: Time in seconds for the transition to complete.
        easing: The easing function to use.
        """
        self.start = initial_value
        self.end = initial_value
        self.start_time = time.time()
        self.duration = duration
        self.easing = easing

    def _get_current_time(self):
        return time.time()

    def _get_easing_function(self):
        if self.easing == Easing.LINEAR:
            return linear
        elif self.easing == Easing.EASE_IN_OUT_EXPONENTIAL:
            return ease_in_out_exponential
        elif self.easing == Easing.EASE_IN_BACK:
            return ease_in_back
        elif self.easing == Easing.EASE_OUT_BACK:
            return ease_out_back
        elif self.easing == Easing.EASE_OUT_ELASTIC:
            return ease_out_elastic
        else:
            return linear

    def set_value(self, new_value):
        """
        Updates the target value. The current interpolated value becomes the new start point,
        ensureing a smooth transition from the current state to the new target.
        """
        self.start = self.get_value()
        self.end = new_value
        self.start_time = self._get_current_time()

    def set_duration(self, duration):
        """
        Updates the duration. To ensure continuity, this re-anchors the transition:
        Current value becomes new start, target remains same, timer resets.
        """
        self.start = self.get_value()
        self.start_time = self._get_current_time()
        self.duration = duration

    def set_speed(self, speed):
        """
        Sets duration based on speed. 
        Note: This is context dependent. Speed might mean units per second.
        If we assume the value difference is the distance:
        """
        # Snapshot current state first to ensure we calculate distance from where we ARE
        current_val = self.get_value()
        self.start = current_val
        self.start_time = self._get_current_time()
        
        # Logic: duration = distance / speed
        # We need the current "distance" to target. This is a bit ambiguous if types are generic.
        # For simple numbers:
        try:
            distance = abs(self.end - self.start)
            if speed > 0:
                self.duration = distance / speed
            else:
                 self.duration = 0 # Instant
        except:
            pass # Use existing duration if calculation fails

    def get_value(self):
        now = self._get_current_time()
        elapsed = now - self.start_time
        
        if self.duration <= 0:
            return self.end
            
        t = elapsed / self.duration
        t = max(0.0, min(1.0, t)) # Clamp t between 0 and 1
        
        func = self._get_easing_function()
        delta = func(t)
        
        # C = A + delta * function(t) -> actually C = A + (B - A) * function(t)
        # where (B-A) is the total change.
        return self.start + (self.end - self.start) * delta

    @property
    def value(self):
        return self.get_value()

    @value.setter
    def value(self, new_val):
        self.set_value(new_val)
