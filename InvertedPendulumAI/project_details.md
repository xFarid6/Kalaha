# Inverted Pendulum AI Project Details

## 1. Physics Model
We simulate a classic Cart-Pole system (inverted pendulum).
- **Cart**: Mass $M$, confined to x-axis.
- **Pole**: Mass $m$, Length $L$, attached to cart pivot.
- **Forces**:
    - Gravity $g$ acting on pole.
    - Control Force $F$ applied to cart (AI output).
    - Friction (optional, usually ignored for simplicity initially).

### Dynamics (Simplified Euler)
At each step $dt$:
1. Calculate angular acceleration $\ddot{\theta}$ based on gravity and cart acceleration.
2. Calculate cart acceleration $\ddot{x}$ based on Force.
3. $x \leftarrow x + \dot{x} \cdot dt$
4. $\dot{x} \leftarrow \dot{x} + \ddot{x} \cdot dt$
5. $\theta \leftarrow \theta + \dot{\theta} \cdot dt$
6. $\dot{\theta} \leftarrow \dot{\theta} + \ddot{\theta} \cdot dt$

## 2. Neural Network
- **Architecture**: Feed Forward.
- **Inputs (4)**:
    1. Cart Position ($x / \text{limit}$)
    2. Pole Direction X ($\sin \theta$)
    3. Pole Direction Y ($\cos \theta$)
    4. Angular Velocity ($\dot{\theta}$)
- **Hidden Layer**: 8 Neurons, ReLU activation.
- **Output Layer**: 1 Neuron, Tanh activation (-1 to 1).
    - Output mapped to Force (e.g., $F = \text{out} \cdot F_{max}$).

## 3. Fitness Function
Score calculates how well the agent balances the pole.
$$ Score = \sum_{t=0}^{T} (R_{alive} - P_{shake} - P_{center}) $$

- $R_{alive}$: +1 point per second if pole tip $y > \text{threshold}$.
- $P_{shake}$: Penalty proportional to $|\dot{\theta}|$. Discourages violent wobbling.
- $P_{center}$: Penalty proportional to $|x|$. Encourages staying near center.

## 4. Genetic Algorithm (Trainer)
- **Population**: e.g., 100 agents.
- **Evaluation**: Run simulation for 100 seconds (or until failure).
- **Selection**: Sort by fitness, keep top % (Elitism).
- **Reproduction**:
    - **Crossover**: Mix weights of two parents.
    - **Mutation**: Randomly perturb weights with Gaussian noise.
- **Multithreading**: Since physics is independent per agent, we use a `ThreadPool` to update the population in parallel batches.
