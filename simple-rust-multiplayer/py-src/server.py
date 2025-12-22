import asyncio

class MeetServer(asyncio.DatagramProtocol):
    def __init__(self):
        self.clients = []
        self.transport = None

    def datagram_received(self, data, addr):
        if addr not in self.clients:
            self.clients.append(addr)
            print(f"Registrato: {addr}")

        if len(self.clients) >= 2:
            a, b = self.clients[0:2]
            print(f"Match: {a} <-> {b}")
            
            # Inviamo a ciascuno l'indirizzo dell'altro
            self.transport.sendto(f"{b[0]}:{b[1]}".encode(), a)
            self.transport.sendto(f"{a[0]}:{a[1]}".encode(), b)
            
            # Rimuoviamo i primi due
            self.clients = self.clients[2:]

    def connection_made(self, transport):
        self.transport = transport

async def run_meet_server(port):
    loop = asyncio.get_running_loop()
    await loop.create_datagram_endpoint(
        lambda: MeetServer(),
        local_addr=("0.0.0.0", port)
    )
    print(f"Meet server attivo su {port}")
    await asyncio.Future()

if __name__ == "__main__":
    from constants import MEET_SERVER_PORT
    try:
        asyncio.run(run_meet_server(MEET_SERVER_PORT))
    except (KeyboardInterrupt, asyncio.CancelledError):
        print("\nServer interrotto.")
