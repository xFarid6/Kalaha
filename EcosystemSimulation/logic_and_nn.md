# Ecosystem Simulation Logic & Neural Network

## 1. Simulation Rules

### The World
- A continuous 2D plane (wrapped or bounded, likely bounded for simplicity).
- Entities behave according to physics (velocity, acceleration).

### Entities
All entities share:
- **Neural Network**: For decision making.
- **Energy**: Life force. Depletes over time (metabolism) and movement.
- **Vision**: Ray-casting sensors.

#### Predators (Red)
- **Goal**: Survive by eating preys.
- **Energy**:
    - Starts at a fixed amount.
    - Decays over time (`DECAY_RATE`).
    - Consumed by movement (`speed * MOVE_COST`).
    - Replenished **ONLY** by eating Preys (`+ENERGY_GAIN`).
- **Mechanics**:
    - **Digestion**: Can only eat if digest timer is 0. Eating sets the timer.
    - **Death**: If energy <= 0.
    - **Reproduction**: No automatic splitting. (Or maybe they replicate if energy is high enough? The prompt says "in order to split predators need to eat", implying they DO split if they consume enough).
- **Vision**: Narrow FOV (e.g., 60 degrees) but Long Range.

#### Preys (Green)
- **Goal**: Survive and reproduce.
- **Energy**:
    - Starts at a fixed amount.
    - Decays over time.
    - Consumed by movement.
    - Replenished by... staying still? (Prompt: "if it reaches 0 they can no longer move and have to stay still to recharge it"). This implies they are effectively "plants" or solar-powered when stopped.
- **Mechanics**:
    - **Death**: Eaten by predators. (Prompt doesn't explicitly say they die of old age/starvation, but usually they do. However, pt 7 says they recharge if 0 energy. So they only die if eaten?). Let's assume they can die if eaten.
    - **Reproduction**: Automatic splitting if `time_alive > SPLIT_TIMER` and `energy > SPLIT_COST`.
- **Vision**: Wide FOV (e.g., 270 degrees) but Short Range.

### Evolution
- **Children** inherit the parent's Neural Network.
- **Mutation**:
    - Small chance to change a weight.
    - Small chance to add a new connection.
    - Small chance to add a new neuron (splitting a connection).

## 2. Neural Network Architecture

We use a flexible Feed-Forward Network (though evolution can make it recurrent or arbitrary if we allow arbitrary node connections). For simplicity, we'll start with a fixed topology that can evolve weights, or a NEAT-lite approach.

Given the requirements (inputs -> outputs), a simple dense network is easier to manage than full NEAT for a demo. Let's use a fixed topology [Inputs -> Hidden -> Outputs] but allow weights to mutate.

### Inputs (Sensors)
Each ray `i` casts into the world.
- `Value = 1.0 - (distance / max_range)`
- If nothing hit, `Value = 0`.
- We distinguish Primitive types? 
    - Maybe Input is just "Entity Proximity". 
    - Or separate inputs for "Prey" and "Predator"?
    - Prompt says "closer the intersection... higher the input".
    - Usually useful to know WHAT you are looking at.
    - Let's give: 
        - `I_type`: 1.0 if Prey, -1.0 if Predator (relative to self?). Or just color channel?
        - Let's keep it simple: Just Proximity. The agent must learn context or we just feed "Proximity to Prey" and "Proximity to Predator" on separate channels?
        - **Decision**: Single channel proximity might be confusing. Let's do **2 values per ray**:
            1. Proximity (0 to 1).
            2. Type (1 for Prey, -1 for Predator, 0 for Wall).

- **Bias**: Always 1.0.
- **Self Energy**: (Current / Max).

### Outputs (Actions)
1. **Thrust**: 0 to 1 (Sigmoid). Controls speed/acceleration.
2. **Turn**: -1 to 1 (Tanh). Controls angular velocity.

## 3. Rendering
- **Soft Body**:
    - Draw a base circle with high alpha.
    - Draw a smaller, solid circle inside.
    - Use glowing sprites if performance allows, or just `pygame.draw.circle` with blending.
- **Eyes**:
    - Two white circles on the "front" vector.
    - Black pupils.
    - **Pupil Logic**:
        - `pupil_radius = base_size * (1.0 - min_ray_distance)`.
        - If clear view (no collision), pupils are small (relaxed).
        - If intersection close, pupils big (dilated/focus).
        - (Prompt says: "vary pupil size based on distance... close-big, far-small").

## 4. Optimization
- **Spatial Hashing**: A grid to quickly query nearby entities for raycasting.
- Raycasting 2400 entities * N rays is heavy.
    - Limit rays (e.g., 3-5 rays).
    - Limit range.
