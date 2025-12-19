# Allenare una "Vera" AI (Machine Learning)

## Fattibilità
Kalaha è un candidato eccellente per il Reinforcement Learning (RL) per vari motivi:
- **Regole Fisse e Determinisiche**: Ambiente perfetto.
- **Informazione Perfetta**: Niente carte nascoste.
- **Spazio di Stati Gestibile**: ~10^10 stati, piccolo per standard moderni (Go è 10^170), ma abbastanza grande da richiedere generalizzazione.
- **Durata Partita**: Breve, permette milioni di partite di training in poco tempo.

## Approcci Possibili

### 1. Tabular Q-Learning
- **Idea**: Creare una tabella Q[Stato][Mossa] = Valore atteso.
- **Problema**: 10^10 righe sono troppe per la RAM.
- **Soluzione**: Approssimazione lineare o reti neurali.

### 2. Deep Q-Network (DQN)
- **Idea**: Una rete neurale prende in input la scacchiera (14 numeri) e restituisce il valore Q per ogni mossa (6 output).
- **Training**:
  - L'AI gioca contro se stessa o contro il nostro bot Minimax.
  - Ricompensa: +1 per vittoria, -1 per sconfitta, 0 per pareggio (o diff punti).
  - Loss function: Minimizzare errore tra predizione e risultato reale (Bellman equation).

### 3. AlphaZero (MCTS + Neural Network)
- **Idea**: Usare una rete per guidare il Monte Carlo Tree Search.
- **Stato dell'arte**: Sarebbe l'approccio più forte. La rete impara sia la "Policy" (che mossa fare) che il "Value" (quanto sono messo bene).
- **Risorse**: Richiede più potenza di calcolo, ma per Kalaha è fattibilissimo su un PC consumer.

## Piano di Azione
1. Creare ambiente "Gym" (interfaccia standard OpenAI).
2. Implementare un loop di training semplice (es. PPO o DQN con PyTorch/TensorFlow).
3. Far giocare l'AI contro il nostro Minimax per vedere quando lo supera.
4. Salvare il modello (pesi della rete) e usarlo nel gioco principale.
