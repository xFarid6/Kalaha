import asyncio
import pygame
from gui import GUI, AppState
from constants import WINDOW_SIZE, TICK_RATE

async def main():
    # Controllo aggiornamenti all'avvio
    try:
        from updater import run_updater
        await run_updater()
    except (ImportError, Exception) as e:
        print(f"[Main] Salto controllo aggiornamenti: {e}")

    pygame.init()
    screen = pygame.display.set_mode(WINDOW_SIZE)
    clock = pygame.time.Clock()

    gui = GUI(screen)

    running = True
    while running:
        dt = clock.tick(TICK_RATE) / 1000.0

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            gui.handle_event(event)

        gui.update(dt)
        gui.draw()

        pygame.display.flip()
        await asyncio.sleep(0)

    pygame.quit()

if __name__ == "__main__":
    asyncio.run(main())
