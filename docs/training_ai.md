# Allenare una "Vera" AI (Machine Learning) per Kalaha

## 1. Stack Tecnologico
- **Libreria**: **Stable-Baselines3 (SB3)** con **Shimmy/Gymnasium**.
- **Algoritmo**: **PPO (Proximal Policy Optimization)**.
- **Metodologia**: **Self-Play**.

### Perché PPO + Self-Play?
Kalaha è un gioco **Zero-Sum Deterministico a Informazione Perfetta**.
- **DQN** soffre in questo ambiente a causa della natura "turn-based" e del reward sparso, richiedendo enormi replay buffer.
- **PPO** è più stabile. Sebbene impari policy "medie", combinato con il **Self-Play** (l'agente gioca contro versioni precedenti di se stesso) può raggiungere livelli sovrumani (stile OpenAI Five).

## 2. Modellazione dell'Ambiente (Gymnasium)

### Observation Space: `Box(15)`
Non usare l'array grezzo da 14. È fondamentale fornire una vista **Canonicale** (sempre dal punto di vista di chi deve muovere).
- **Size**: 15 input interi.
- **Struttura**: `[Miei 6 Pozzi] + [Mio Granaio] + [Avversario 6 Pozzi] + [Avversario Granaio] + [Turno/ExtraInfo]`.
- **Note**: Ruotare la scacchiera quando tocca a P2, in modo che la rete impari una sola logica (i "miei" pezzi sono sempre nei primi indici).

### Action Space: `Discrete(6)` + Action Masking
- L'agente sceglie un indice da 0 a 5.
- **Cruciale**: Implementare **Action Masking**.
    - Se l'agente sceglie un pozzo vuoto, la mossa è illegale.
    - SB3 supporta `ActionMasker` (tramite `sb3-contrib` o wrapper custom) per forzare logit a -inf per mosse illegali. Senza questo, il training sarà lentissimo perché l'AI dovrà imparare le regole a tentativi.

### Reward Function
- **Sparso**: +1 (Vittoria), -1 (Sconfitta), 0 (Pareggio) solo a fine partita.
- **Shaping (Opzionale ma rischioso)**: Piccoli reward per catture o turni extra possono accelerare l'apprendimento iniziale ma rischiano di creare agenti miopi che "farmano" punti invece di vincere. Meglio stick to +1/-1.

## 3. Pipeline di Training (Self-Play)
1.  **Inizializzazione**: Agente `Current` (PPO) vs `Opponent` (Random o Minimax Debole).
2.  **Loop di Training**:
    - Fai giocare `Current` contro `Opponent` per N step (es. 100k).
    - Aggiorna i pesi di `Current`.
    - Ogni K step, valuta `Current` vs `Opponent`.
    - Se WinRate > 55%, promuovi `Current` a nuovo `Opponent`.
3.  **Salvataggio**: Salva checkpoint regolari.


## 4. Scaffold Implementativo
Verranno creati:
- `kalaha/training/kalaha_env.py`: Classe Environment.
- `train_scaffold.py`: Script per avviare il training loop base.

## 5. Endgame Database: Should the AI Agent Access It?

### Current Implementation
The `endgame_db.py` module stores **exact solutions** for terminal and near-terminal board positions. Currently used by:
- **Alpha-Beta AI** (`ai_engine.py`): Lookup during tree search
- **Automatic population**: Terminal states are saved during games

### Question: Should the RL Agent (PPO) Use the Endgame DB?

#### Option A: ✅ **YES - Agent Uses DB**

**How**: Modify `KalahaEnv.step()` to inject exact values from DB when available.

```python
def step(self, action):
    # ... apply move ...
    
    if is_terminal(self.board):
        # Normal terminal reward
        reward = compute_reward()
    else:
        # Check endgame DB
        db_value = endgame_db.lookup(self.board, self.current_player)
        if db_value is not None:
            # Inject "ground truth" reward early
            reward = normalize(db_value)  # Map to [-1, 1]
            terminated = True  # Treat as solved
```

**PROS**:
1. ⚡ **Faster Convergence**: Agent learns endgames instantly (no trial-and-error)
2. 🎯 **Perfect Endgame Play**: Guaranteed optimal moves in solved positions
3. 📉 **Reduced Training Time**: Less wasted exploration in known territory
4. 🧠 **Focus on Opening/Middlegame**: Agent spends compute on unsolved positions

**CONS**:
1. ⚠️ **Data Dependency**: DB must be comprehensive (otherwise partial benefit)
2. 🔀 **Distribution Shift**: Agent never experiences natural endgames → might not generalize
3. 🐛 **Reward Hacking Risk**: If DB has errors, agent learns wrong patterns
4. 📊 **Evaluation Difficulty**: Hard to measure "true" agent strength vs DB-assisted

#### Option B: ❌ **NO - Agent Learns Independently**

**How**: Keep DB separate, only use for:
- Evaluation (compare agent vs perfect play)
- Alpha-Beta search opponent

**PROS**:
1. ✨ **Pure RL Learning**: Agent discovers strategies naturally
2. 🔬 **Research Clarity**: Easier to understand what agent actually learned
3. 🌐 **Better Generalization**: Agent experiences full game distribution
4. 🎓 **Educational Value**: Shows RL can solve Kalaha from scratch

**CONS**:
1. 🐌 **Slower Training**: Agent wastes time rediscovering known solutions
2. ⚠️ **Suboptimal Endgames**: May never learn perfect 20-seed endgames
3. 💰 **Higher Compute Cost**: More episodes needed for same performance

### Hybrid Approach: 🔀 **Progressive DB Integration**

**Strategy**: Start pure RL, gradually introduce DB.

1. **Phase 1** (0-500k steps): No DB → Agent explores freely
2. **Phase 2** (500k-1M steps): DB for positions with ≤10 total seeds
3. **Phase 3** (1M+ steps): Full DB access

**Benefits**:
- Agent learns fundamentals naturally
- DB accelerates later optimization
- Best of both worlds

### Recommendation: **HYBRID (Progressive)**

**Rationale**:
- Early training: Agent needs to learn core mechanics (sowing, capturing, extra turns)
- Late training: DB provides "curriculum" for difficult endgames
- Evaluation: Can compare "pure RL" vs "RL+DB" variants

**Implementation**:
```python
class KalahaEnv:
    def __init__(self, use_endgame_db=False, db_seed_threshold=10):
        self.use_endgame_db = use_endgame_db
        self.db_threshold = db_seed_threshold
        
    def step(self, action):
        # ... normal step ...
        
        if self.use_endgame_db:
            total_seeds = sum(self.board)
            if total_seeds <= self.db_threshold:
                db_val = endgame_db.lookup(self.board, self.current_player)
                if db_val is not None:
                    # Inject solution
                    reward = db_val / 48.0  # Normalize
                    terminated = True
                    
        return obs, reward, terminated, truncated, info
```

**Training Schedule**:
```python
# Phase 1: Pure RL
model.learn(500_000, env=make_env(use_endgame_db=False))

# Phase 2: Light DB assistance
model.learn(500_000, env=make_env(use_endgame_db=True, db_seed_threshold=10))

# Phase 3: Full DB
model.learn(1_000_000, env=make_env(use_endgame_db=True, db_seed_threshold=48))
```

### Alternative: DB as Curriculum Generator

Instead of injecting rewards, use DB to:
1. Generate "hard" starting positions (near-optimal lines)
2. Sample positions where agent performs poorly
3. Create targeted training scenarios

This avoids distribution shift while accelerating learning.

### Conclusion

**For Kalaha**: Recommend **progressive DB integration** with careful evaluation. The small state space means agent can likely solve it independently, but DB can act as a "teacher" for tricky endgames. Always maintain a "pure RL" baseline for comparison.

