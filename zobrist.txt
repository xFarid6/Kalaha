# Zobrist Hashing

## Cos'è
Zobrist Hashing è una tecnica usata nei giochi da tavolo (Scacchi, Go, Kalaha) per rappresentare lo stato di una scacchiera con un singolo numero intero (hash) in modo estremamente efficiente.

## Come funziona
1. **Inizializzazione**:
   - Si crea una tabella di numeri casuali a 64 bit.
   - Dimensioni: `[Numero Celle] x [Numero Possibili Valori per Cella]`.
   - Per Kalaha: 14 celle. Ogni cella può contenere da 0 a N semi (es. 72).
   - In più, si usa un numero casuale per indicare di chi è il turno.

2. **Calcolo dell'Hash**:
   - L'hash della scacchiera è lo XOR (somma bit a bit esclusiva) dei numeri casuali associati a ciascuna cella e al suo contenuto.
   - Hash = `Random[0][semi_in_0] ^ Random[1][semi_in_1] ... ^ Random[Turno]`

3. **Perché è veloce?**:
   - L'operazione XOR è rapidissima per la CPU.
   - **Aggiornamento Incrementale**: Quando si fa una mossa, non serve ricalcolare da zero. Basta fare lo XOR dei valori che cambiano.
     - Togli semi da A: `Hash ^= Random[A][vecchi] ^ Random[A][0]`
     - Aggiungi a B: `Hash ^= Random[B][vecchi] ^ Random[B][nuovi]`

## Perché lo usiamo in Kalaha
- **Transposition Tables (TT)**: Usiamo l'hash come chiave per la dizionario (Map). È molto più veloce cercare un intero che confrontare un intero array di 14 elementi o una tupla.
- **Collisioni**: Le probabilità che due stati diversi abbiano lo stesso hash a 64 bit sono infinitesimali.
