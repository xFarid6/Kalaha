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
