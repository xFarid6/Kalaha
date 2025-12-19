# Funzione di Valutazione (Evaluation Function)

## Stato Attuale
Attualmente usiamo una funzione euristica semplice ma efficace:
```python
Score = (Miei Semi nel Granaio - Semi Avversari nel Granaio)
        + 0.5 * (Semi sul mio lato - Semi sul lato avversario)
```
- **Materiale**: Priorità assoluta ai punti già incassati.
- **Controllo**: Leggero premio per avere pezzi sul proprio lato (potenziale di difesa e attacco).

## Possibili Miglioramenti
1. **Mobilità**:
   - Contare quante mosse legali ho. Più opzioni = più flessibilità per evitare "Kalaha Starvation" (rimanere senza mosse).

2. **Minaccia di Cattura**:
   - Rilevare se ho buche vuote minacciate (con pezzi opposti di fronte).
   - Premiare stati dove *io* minaccio di catturare (ho buca vuota e l'avversario ha tanti semi di fronte).

3. **Turni Extra**:
   - Premiare configurazioni che permettono turni extra immediati (buca con N semi distante N dal granaio).

4. **Difesa**:
   - Penalizzare se l'avversario ha mosse di cattura facili.

5. **Hoarding (Accumulo)**:
   - Verso fine partita, avere tanti semi sul proprio lato è fortissimo perché se il gioco finisce (lato vuoto), catturo tutto il resto. Bisognerebbe aumentare il peso dei semi sul proprio lato man mano che i semi totali diminuiscono.

## Tuning
I pesi (0.5, 1.0, etc.) vanno calibrati. Idealmente si usano tornei automatici (l'AI gioca contro se stessa con pesi diversi) per trovare la combinazione ottimale (es. usando algoritmo genetico o SPSA).
