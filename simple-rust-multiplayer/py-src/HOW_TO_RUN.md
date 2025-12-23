# Istruzioni per il Test del Multiplayer Locale

Questo progetto permette di testare la connessione peer-to-peer (UDP Hole Punching) simulata in locale su un unico PC oppure tra PC diversi attraverso un Meet Server.

## Come avviare il test su un singolo PC

Apri **3 terminali diversi** nella cartella principale del progetto:

### 1. Avvia il Meet Server (Terminale 1)
È il server che mette in contatto i due giocatori.
```bash
python simple-rust-multiplayer/py-src/server.py
```

### 2. Avvia il primo Giocatore (Terminale 2)
Usa il flag `--local` per indicare di connettersi a localhost.
```bash
python simple-rust-multiplayer/py-src/main.py --local
```
- Una volta aperto, premi il tasto **`S`** (Server/Host).
- Premi **`INVIO`** per confermare e iniziare ad attendere l'altro giocatore.

### 3. Avvia il secondo Giocatore (Terminale 3)
```bash
python simple-rust-multiplayer/py-src/main.py --local
```
- Una volta aperto, premi il tasto **`C`** (Client/Guest).
- Premi **`INVIO`** per confermare.

---

## Controlli e Logica di gioco
- **Movimento**: Usa le frecce direzionali (**SU, GIÙ, SINISTRA, DESTRA**).
- **Rettangolo Verde**: Rappresenta la tua posizione locale.
- **Rettangolo Rosso**: Rappresenta la posizione del tuo avversario (ricevuta via rete).
- **Console**: Entrambi i terminali dei giocatori mostreranno log come:
  - `Inviata posizione al peer: x,y`
  - `Ricevuta posizione dal peer: x,y`

## Sistema di Auto-Update

Il progetto ora include un sistema di aggiornamento automatico all'avvio.

### Requisiti
È necessario installare le seguenti librerie:
```bash
pip install aiohttp tqdm
```

### Come testare l'aggiornamento in locale
1.  **Avvia il server di finto aggiornamento**:
    ```bash
    python simple-rust-multiplayer/py-src/mock_update_server.py
    ```
    Questo creerà un file `update.zip` e servirà un `version.json` che indica la versione `1.1.0`.

2.  **Avvia il gioco**:
    ```bash
    python simple-rust-multiplayer/py-src/main.py
    ```
    - Vedrai nella console il messaggio `Nuova versione trovata: 1.1.0`.
    - L'app scaricherà lo zip, estrarrà i file (sostituendo `constants.py`) e si riavvierà automaticamente.
    - Al riavvio, vedrai `Versione corrente: 1.1.0` e `L'app è aggiornata`.

## Visualizzazione
I rettangoli sono stati ingranditi (100x100 pixel) per facilitare la verifica dei movimenti. Se vedi il rettangolo rosso muoversi quando sposti il verde nell'altra finestra, il sistema sta scambiando i dati correttamente.
