import pygame
import sys
import math
# Ensure we can import from the same directory if running from elsewhere
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from interpolation import Interpolated, Easing

# Constants
SCREEN_WIDTH = 1024
SCREEN_HEIGHT = 768
CARD_WIDTH = 100
CARD_HEIGHT = 150
GAP = 20
COLS = 6
ROWS = 4
BG_COLOR = (30, 30, 30)
CARD_COLOR_FRONT = (240, 240, 240)
CARD_COLOR_BACK = (200, 100, 100)
TEXT_COLOR = (200, 150, 50)

class Card:
    def __init__(self, index, x, y):
        self.index = index
        self.id = index # Unique ID to track identity
        
        # Interpolated Position (pygame.Vector2 supports + and *)
        self.pos = Interpolated(pygame.Vector2(x, y), duration=0.4, easing=Easing.EASE_OUT_BACK)
        
        # Interpolated Scale (for drag effect)
        self.scale = Interpolated(1.0, duration=0.2, easing=Easing.EASE_OUT_BACK)
        
        # Interpolated Flip (1.0 = Front, -1.0 = Back)
        self.flip = Interpolated(1.0, duration=0.3, easing=Easing.EASE_IN_OUT_EXPONENTIAL)
        
        self.is_dragging = False
        self.drag_offset = pygame.Vector2(0, 0)
        self.rect = pygame.Rect(x, y, CARD_WIDTH, CARD_HEIGHT)

    def update(self):
        # Update rect for hit testing based on CURRENT interpolated position
        # We use the integer version for drawing/rects
        current_pos = self.pos.get_value()
        self.rect.topleft = (int(current_pos.x), int(current_pos.y))

    def draw(self, surface, font):
        current_pos = self.pos.get_value()
        current_scale = self.scale.get_value() 
        current_flip = self.flip.get_value()
        
        # Handle Scaling (visual only)
        # Flip affects X scale: |flip|
        scale_x = current_scale * abs(current_flip)
        scale_y = current_scale
        
        w = int(CARD_WIDTH * scale_x)
        h = int(CARD_HEIGHT * scale_y)
        
        # Center the card on its position
        cx, cy = current_pos.x + CARD_WIDTH / 2, current_pos.y + CARD_HEIGHT / 2
        
        # Determine color/face
        color = CARD_COLOR_FRONT if current_flip >= 0 else CARD_COLOR_BACK
        
        # Only draw if visible
        if w > 0:
            # Create a centered rect
            draw_rect = pygame.Rect(0, 0, w, h)
            draw_rect.center = (cx, cy)
            
            pygame.draw.rect(surface, color, draw_rect, border_radius=10)
            
            # Draw Text (Rotation? No, just flip check)
            # Only show text if facing front and scale is significant
            if current_flip > 0.1 and w > 20: 
                text_surf = font.render(str(self.id), True, TEXT_COLOR)
                text_rect = text_surf.get_rect(center=draw_rect.center)
                surface.blit(text_surf, text_rect)

class Demo:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Interpolation Engine Demo")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("Arial", 32, bold=True)
        
        self.cards = []
        self._init_cards()
        
        self.dragging_card = None

    def _init_cards(self):
        start_x = (SCREEN_WIDTH - (COLS * (CARD_WIDTH + GAP))) / 2
        start_y = (SCREEN_HEIGHT - (ROWS * (CARD_HEIGHT + GAP))) / 2
        
        for i in range(ROWS * COLS):
            r = i // COLS
            c = i % COLS
            x = start_x + c * (CARD_WIDTH + GAP)
            y = start_y + r * (CARD_HEIGHT + GAP)
            self.cards.append(Card(i, x, y))

    def _get_grid_pos(self, index):
        start_x = (SCREEN_WIDTH - (COLS * (CARD_WIDTH + GAP))) / 2
        start_y = (SCREEN_HEIGHT - (ROWS * (CARD_HEIGHT + GAP))) / 2
        r = index // COLS
        c = index % COLS
        x = start_x + c * (CARD_WIDTH + GAP)
        y = start_y + r * (CARD_HEIGHT + GAP)
        return pygame.Vector2(x, y)

    def handle_input(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1: # Left Click
                    mouse_pos = pygame.Vector2(event.pos)
                    # Check collision (reverse order to pick top card)
                    for card in reversed(self.cards):
                        if card.rect.collidepoint(event.pos):
                            self.dragging_card = card
                            self.dragging_card.is_dragging = True
                            self.dragging_card.scale.set_value(1.2) # Scale up
                            # Drag offset
                            current_pos = self.dragging_card.pos.get_value()
                            self.drag_offset = current_pos - mouse_pos
                            
                            # Move to end of list to render on top
                            self.cards.remove(card)
                            self.cards.append(card)
                            break
                elif event.button == 3: # Right Click
                     for card in reversed(self.cards):
                        if card.rect.collidepoint(event.pos):
                            # Trigger Flip
                            current_flip = card.flip.get_value()
                            # Toggle between 1 and -1
                            target = -1.0 if current_flip > 0 else 1.0
                            card.flip.set_value(target)
                            break

            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1 and self.dragging_card:
                    # Drop
                    self.dragging_card.is_dragging = False
                    self.dragging_card.scale.set_value(1.0) # Scale down
                    
                    # Snap to nearest grid slot mechanism?
                    # The user prompt said: "when dragging a card it's position in the array is swpped with the one below."
                    # This implies we are constantly swapping while dragging, OR we swap on drop.
                    # "swapped with the one below" usually implies interaction with the card UNDER the mouse.
                    
                    # Let's find if we dropped ON another card
                    dropped_on = None
                    for card in self.cards:
                        if card != self.dragging_card and card.rect.collidepoint(event.pos):
                            dropped_on = card
                            break
                    
                    if dropped_on:
                        # Swap their logical indices in the grid layout (not the list order, which is for Z-index)
                        # Actually, the user said "all the cards are stored sequentially in a 1D array".
                        # Let's re-sort the visual list to match grid order for logic, or keep a separate grid state.
                        
                        # Simpler approach: Just swap their TARGET positions.
                        # We need to find the INDEX of the card we dropped on in the logical grid.
                        # But wait, self.cards is just a list. 
                        # We need to maintain the "slot" each card belongs to.
                        pass # Logic handled in drag update or here?
                    
                    # Realignment: Setup all cards to go to their assigned slots
                    # We can recalculate all slots based on current order if we want, or swap.
                    # Let's settle for: Swap positions with the card we are over.
                    
                    self._realign_cards()
                    self.dragging_card = None

            elif event.type == pygame.MOUSEMOTION:
                if self.dragging_card:
                    mouse_pos = pygame.Vector2(event.pos)
                    # Immediate follow mouse (no interpolation for the drag itself? 
                    # OR update target constantly? Immediate is better for responsiveness)
                    # But the prompt says "use the created interpolation object for the cards position".
                    # So we update the target to the mouse position.
                    
                    target_pos = mouse_pos + self.drag_offset
                    self.dragging_card.pos.set_value(target_pos)
                    # Make it instant for responsiveness or keep small duration?
                    # If duration is 0.4, it will lag behind mouse.
                    # We can set duration to 0.05 or similar for strict follow.
                    self.dragging_card.pos.set_duration(0.05)
                    
                    # Check for swap
                    # Find card under mouse
                    hovered_card = None
                    for card in self.cards:
                         if card != self.dragging_card and card.rect.collidepoint(event.pos):
                             hovered_card = card
                             break
                    
                    if hovered_card:
                        # Swap indices in the list? 
                        # We need to know 'slot index' vs 'card object'.
                        # Let's assign a 'slot_index' to each card.
                        pass 

    def _realign_cards(self):
        # This function puts cards back to their grid positions.
        # But we need to know WHICH slot they belong to.
        # Let's assume the order in self.cards dictates the slot?
        # But we changed order for Z-sorting (render on top).
        
        # Issue: If we sort by Z-index, we lose grid order.
        # Solution: Keep a separate 'grid_slots' list of cards.
        pass

    def run(self):
        # We need a robust list that represents the GRID state: `self.grid_cards`
        # `self.cards` will be used for rendering order.
        self.grid_cards = list(self.cards)
        
        while True:
            self.handle_input()
            
            # Logic for swapping
            if self.dragging_card:
                # Find which slot (index in grid_cards) the mouse is over
                mouse_pos = pygame.mouse.get_pos()
                
                # Check intersection with the calculated grid slots, NOT the cards themselves 
                # (since cards are moving)
                target_index = -1
                
                # Simple distance check to slot centers
                min_dist = 99999
                closest_index = -1
                
                for i in range(len(self.grid_cards)):
                    pos = self._get_grid_pos(i)
                    center = pos + pygame.Vector2(CARD_WIDTH/2, CARD_HEIGHT/2)
                    dist = center.distance_to(pygame.Vector2(mouse_pos))
                    
                    if dist < min_dist:
                        min_dist = dist
                        closest_index = i
                
                # If we are close enough to a slot
                if min_dist < CARD_WIDTH / 2:
                    # Find where the dragging card CURRENTLY is in the grid
                    current_index = self.grid_cards.index(self.dragging_card)
                    
                    if current_index != closest_index:
                        # Swap in grid
                        other_card = self.grid_cards[closest_index]
                        self.grid_cards[closest_index] = self.dragging_card
                        self.grid_cards[current_index] = other_card
                        
                        # Trigger interpolation for the OTHER card to move to the old slot
                        # The dragging card is controlled by mouse, so it won't snap yet.
                        old_pos = self._get_grid_pos(current_index)
                        other_card.pos.set_duration(0.5) # Smooth sway
                        other_card.pos.set_value(old_pos)

            # Update loop
            for i, card in enumerate(self.grid_cards):
                # If it's the dragging card, we don't snap it to grid yet (handled in mouse move)
                if card != self.dragging_card:
                    # Ensure it's moving to its slot
                    target_pos = self._get_grid_pos(i)
                    # Only update if target changed (check rough dist to not spam set_value?)
                    # card.pos.end is the target.
                    if card.pos.end != target_pos:
                         card.pos.set_duration(0.5)
                         card.pos.set_value(target_pos)
                
                card.update()

            # Render
            self.screen.fill(BG_COLOR)
            
            # Draw in order of self.cards (Z-Index)
            # We need self.cards to effectively be "grid_cards" but with dragging card last.
            draw_order = [c for c in self.grid_cards if c != self.dragging_card]
            if self.dragging_card:
                draw_order.append(self.dragging_card)
                
            for card in draw_order:
                card.draw(self.screen, self.font)
            
            pygame.display.flip()
            self.clock.tick(60)

if __name__ == "__main__":
    Demo().run()
