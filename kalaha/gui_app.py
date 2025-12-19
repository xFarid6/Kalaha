import pygame
import sys

# Constants
WIDTH, HEIGHT = 800, 600
BG_COLOR = (30, 30, 30)
TEXT_COLOR = (240, 240, 240)

def run_gui():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Kalaha (Mancala)")
    clock = pygame.time.Clock()
    
    font = pygame.font.SysFont("Arial", 48, bold=True)
    
    # Render Text
    text_surface = font.render("Kalaha", True, TEXT_COLOR)
    text_rect = text_surface.get_rect(center=(WIDTH//2, HEIGHT//2 - 30))
    
    sub_font = pygame.font.SysFont("Arial", 32)
    sub_text = sub_font.render("(Mancala)", True, TEXT_COLOR)
    sub_rect = sub_text.get_rect(center=(WIDTH//2, HEIGHT//2 + 30))

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                
        # Draw
        screen.fill(BG_COLOR)
        screen.blit(text_surface, text_rect)
        screen.blit(sub_text, sub_rect)
        
        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    run_gui()
