# Tabelle di Fine Gioco (Endgame Tablebases)

## Cosa sono
Le tabelle di fine gioco (Endgame Tablebases) sono database precalcolati che contengono la valutazione perfetta (vittoria, sconfitta, pareggio, o punteggio esatto) per ogni possibile configurazione di gioco quando rimangono pochi pezzi sulla scacchiera.

In Kalaha, quando il numero totale di semi in gioco diminuisce (perché catturati e messi nei granai), lo spazio degli stati si riduce drasticamente. Questo permette di risolvere completamente il gioco per queste situazioni.

## Come funzionano
Invece di calcolare la mossa migliore in avanti (come Minimax), le tablebase vengono spesso generate all'indietro (**Retrograde Analysis**):
1. Si identificano gli stati terminali (vittoria/sconfitta immediata).
2. Si risale agli stati precedenti: se da uno stato X posso muovere in uno stato vincente, allora X è vincente. Se da uno stato Y tutte le mosse portano a stati perdenti, allora Y è perdente.

## Come usarle nel nostro programma
Durante la ricerca Minimax, prima di avviare la ricorsione o valutare euristicamente un nodo:
1. Controlliamo se la configurazione attuale esiste nella Tablebase.
2. Se sì, restituiamo immediatamente il valore salvato (Mossa Perfetta).
3. Se no, procediamo con Minimax/Alpha-Beta.

## Formato e Compressione
Per rendere le tablebase utilizzabili (veloci da leggere e contenute in memoria):
- **Indicizzazione**: Mappare ogni configurazione di scacchiera a un indice univoco (Perfect Hashing). Dato che le palline sono indistinguibili, si usa la combinatoria.
- **Compressione**: Memorizzare solo 2 bit per stato (Vinto/Perso/Pari/Ignoto) o valore intero compresso.

Idee per implementazione futura:
- File binario indicizzato.
- Cache LRU in memoria per le posizioni più frequenti.
- Popolamento dinamico: "Memorize" delle posizioni risolte durante le partite (Transposition Table persistente).
