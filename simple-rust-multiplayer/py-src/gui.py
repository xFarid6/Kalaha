import pygame
from enum import Enum
from constants import WINDOW_SIZE, MEET_SERVER_IP, MEET_SERVER_PORT
import asyncio
from client import create_client
from datetime import datetime

class AppState(Enum):
    SELECT_MODE = 0
    NETWORK_SETUP = 1
    IN_GAME = 2

class GUI:
    def __init__(self, screen):
        self.screen = screen
        self.state = AppState.SELECT_MODE
        self.mode = None
        self.client = None
        self.networking_started = False

        self.my_pos = pygame.Vector2(300, 300)
        self.remote_pos = pygame.Vector2(500, 300)
        self.speed = 300

        self.font = pygame.font.SysFont(None, 32)
        
    def log(self, message):
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] [GUI] {message}")

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if self.state == AppState.SELECT_MODE:
                if event.key == pygame.K_s:
                    self.mode = "server"
                    self.log("Selezionata modalità SERVER (S)")
                    self.state = AppState.NETWORK_SETUP
                if event.key == pygame.K_c:
                    self.mode = "client"
                    self.log("Selezionata modalità CLIENT (C)")
                    self.state = AppState.NETWORK_SETUP

            elif self.state == AppState.NETWORK_SETUP:
                if event.key == pygame.K_RETURN:
                    self.log("Avvio gioco...")
                    self.state = AppState.IN_GAME

    def update(self, dt):
        if self.state == AppState.IN_GAME:
            # Inizializzazione controllata del networking
            if not self.networking_started:
                self.networking_started = True
                asyncio.create_task(self.start_networking())
                return

            if self.client is None:
                return

            # Movimento Locale
            keys = pygame.key.get_pressed()
            moved = False
            if keys[pygame.K_LEFT]:
                self.my_pos.x -= self.speed * dt
                moved = True
            if keys[pygame.K_RIGHT]:
                self.my_pos.x += self.speed * dt
                moved = True
            if keys[pygame.K_UP]:
                self.my_pos.y -= self.speed * dt
                moved = True
            if keys[pygame.K_DOWN]:
                self.my_pos.y += self.speed * dt
                moved = True

            # Invio posizione al peer
            if self.client.peer_addr:
                if moved or (pygame.time.get_ticks() % 500 < 20):
                    pos_str = f"{self.my_pos.x:.1f},{self.my_pos.y:.1f}"
                    self.client.send_to_peer(pos_str)

            # Ricezione posizione dal peer
            if self.client.last_data:
                try:
                    x_str, y_str = self.client.last_data.split(',')
                    self.remote_pos.x = float(x_str)
                    self.remote_pos.y = float(y_str)
                    self.client.last_data = None
                except ValueError:
                    self.log(f"Errore parsing dati peer: {self.client.last_data}")

    async def start_networking(self):
        self.log(f"Inizializzazione networking in modalità {self.mode}...")
        self.client = await create_client(self.mode)
        # Registrazione al MeetServer
        self.client.register_with_server((MEET_SERVER_IP, MEET_SERVER_PORT))

    def draw(self):
        self.screen.fill((30, 30, 30))

        if self.state == AppState.SELECT_MODE:
            self.draw_text("Premi S per SERVER, C per CLIENT", 200)

        elif self.state == AppState.NETWORK_SETUP:
            self.draw_text(f"Modalità: {self.mode.upper() if self.mode else '?'}", 200)
            self.draw_text("Premi INVIO per connetterti al MeetServer", 250)

        elif self.state == AppState.IN_GAME:
            # Rettangoli più grandi: 100x100
            pygame.draw.rect(self.screen, (0, 255, 0), (*self.my_pos, 100, 100))
            pygame.draw.rect(self.screen, (255, 0, 0), (*self.remote_pos, 100, 100))

            self.draw_text("IO (Verde)", self.my_pos.y - 30, self.my_pos.x)
            
            peer_status = "Peer Connesso" if self.client and self.client.peer_addr else "In attesa di peer..."
            self.draw_text(peer_status, self.remote_pos.y - 30, self.remote_pos.x - 20)
            
            if self.client and self.client.peer_addr:
                self.draw_text(f"Peer: {self.client.peer_addr}", 20)
                self.draw_text("PEER (Rosso)", self.remote_pos.y + 110, self.remote_pos.x)

    def draw_text(self, text, y, x=200):
        surface = self.font.render(text, True, (200, 200, 200))
        self.screen.blit(surface, (x, y))
