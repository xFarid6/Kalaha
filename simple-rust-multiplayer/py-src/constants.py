import sys

DEFAULT_PORT = 4000

# Se passiamo --local usiamo localhost
if "--local" in sys.argv:
    MEET_SERVER_IP = "127.0.0.1"
    print("[Config] Modalità LOCAL attiva (127.0.0.1)")
# Se passiamo --ip [INDIRIZZO] usiamo quell'IP
elif "--ip" in sys.argv:
    idx = sys.argv.index("--ip")
    MEET_SERVER_IP = sys.argv[idx + 1]
    print(f"[Config] Uso IP personalizzato: {MEET_SERVER_IP}")
else:
    # IP di default (cambialo con il tuo server se ne hai uno)
    MEET_SERVER_IP = "176.246.73.156"

MEET_SERVER_PORT = 5000

TICK_RATE = 60
WINDOW_SIZE = (800, 600)
DEBUG_MODE = True

CURRENT_VERSION = "1.1.0"
UPDATE_URL = "http://127.0.0.1:8000/version.json"