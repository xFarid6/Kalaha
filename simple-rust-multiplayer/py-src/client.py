import asyncio
from datetime import datetime

class GameClient(asyncio.DatagramProtocol):
    def __init__(self, mode="client"):
        self.transport = None
        self.last_data = None
        self.peer_addr = None
        self.mode = mode

    def log(self, message):
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] [{self.mode.upper()}] {message}")

    def connection_made(self, transport):
        self.transport = transport
        local_addr = transport.get_extra_info('sockname')
        self.log(f"Socket creato su {local_addr}")

    def datagram_received(self, data, addr):
        msg = data.decode()
        
        # Normalizzazione indirizzo (per gestire IPv6 mapping o formati diversi)
        # addr[0] è l'IP, addr[1] è la porta
        incoming_ip = addr[0].replace('::ffff:', '') # Rimuove mapping IPv6 se presente
        incoming_addr = (incoming_ip, addr[1])

        # Se non abbiamo ancora un peer, questo potrebbe essere l'indirizzo del peer inviato dal MeetServer
        if self.peer_addr is None:
            try:
                if ':' in msg:
                    ip, port = msg.split(':')
                    self.peer_addr = (ip, int(port))
                    self.log(f"Match ricevuto dal MeetServer {addr}! Peer trovato a {self.peer_addr}")
                else:
                    self.log(f"Ricevuto messaggio dal server: {msg}")
            except Exception as e:
                self.log(f"Errore nel parsing del messaggio del MeetServer: {msg} -> {e}")
        else:
            # Dati di gioco dal peer
            # Confronto IP e Porta (ignorando eventuali altri campi di addr come scope id)
            if incoming_addr == self.peer_addr:
                self.last_data = msg
            else:
                # Logghiamo solo pacchetti inaspettati (evitiamo lo spam del server se invia ancora qualcosa)
                if incoming_addr[0] != "127.0.0.1" and incoming_addr[0] != MEET_SERVER_IP:
                    self.log(f"IGNORATO pacchetto da {incoming_addr} (Aspettavo {self.peer_addr})")

    def send_to_peer(self, data: str):
        if self.transport and self.peer_addr:
            self.transport.sendto(data.encode(), self.peer_addr)

    def register_with_server(self, server_addr):
        self.log(f"Registrazione presso MeetServer {server_addr}...")
        self.transport.sendto(b"HELLO", server_addr)

async def create_client(mode="client"):
    # Usiamo 0 per far scegliere al sistema una porta libera (fondamentale per test locale)
    loop = asyncio.get_running_loop()
    transport, protocol = await loop.create_datagram_endpoint(
        lambda: GameClient(mode),
        local_addr=("0.0.0.0", 0)
    )
    return protocol
