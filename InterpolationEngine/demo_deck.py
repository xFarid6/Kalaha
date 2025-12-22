import pygame
import sys
import math
import random
import os

# Ensure we can import from the same directory
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from interpolation import Interpolated, Easing

# --- Constants & Config ---
SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 800
BG_COLOR = (20, 20, 25) # Matte black/dark blueish

# Card Visuals
CARD_WIDTH = 100
CARD_HEIGHT = 150
CARD_COLOR_FRONT = (245, 240, 230) # Cream
CARD_COLOR_BACK = (25, 20, 20)     # Dark Charcoal
GOLD_COLOR = (212, 175, 55)
TEXT_COLOR = GOLD_COLOR

# --- Procedural Graphics Helpers ---
def draw_card_front(surface, rect, text):
    # Base
    pygame.draw.rect(surface, CARD_COLOR_FRONT, rect, border_radius=8)
    # Gold Border
    pygame.draw.rect(surface, GOLD_COLOR, rect, width=2, border_radius=8)
    
    # Ornamental Oval
    oval_rect = rect.inflate(-20, -10)
    pygame.draw.ellipse(surface, GOLD_COLOR, oval_rect, width=2)
    
    # Inner decoration (simple dots or lines)
    cy = rect.centery
    cx = rect.centerx
    
    # Draw Text
    if text:
        # We need a font. loading system font.
        font = pygame.font.SysFont("Times New Roman", 60, bold=True, italic=True)
        text_surf = font.render(text, True, GOLD_COLOR)
        text_rect = text_surf.get_rect(center=rect.center)
        surface.blit(text_surf, text_rect)
        
        # Small corner text
        small_font = pygame.font.SysFont("Times New Roman", 18, bold=True)
        # Top Left
        tl_surf = small_font.render(text, True, GOLD_COLOR)
        surface.blit(tl_surf, (rect.x + 8, rect.y + 8))
        # Bottom Right
        br_surf = small_font.render(text, True, GOLD_COLOR)
        br_rect = br_surf.get_rect(bottomright=(rect.right - 8, rect.bottom - 8))
        surface.blit(br_surf, br_rect)

def draw_card_back(surface, rect):
    # Base
    pygame.draw.rect(surface, CARD_COLOR_BACK, rect, border_radius=8)
    # Gold Border
    pygame.draw.rect(surface, GOLD_COLOR, rect, width=2, border_radius=8)
    
    # Rooster/Logo Placeholder (A stylized circle/star)
    center = rect.center
    pygame.draw.circle(surface, GOLD_COLOR, center, 30, width=2)
    # Sun rays
    for i in range(0, 360, 45):
        rad = math.radians(i)
        start = (center[0] + math.cos(rad)*20, center[1] + math.sin(rad)*20)
        end = (center[0] + math.cos(rad)*25, center[1] + math.sin(rad)*25)
        pygame.draw.line(surface, GOLD_COLOR, start, end, 2)
        
    font = pygame.font.SysFont("Times New Roman", 12, italic=True)
    txt = font.render("Rooster", True, GOLD_COLOR)
    txt_rect = txt.get_rect(center=center)
    surface.blit(txt, txt_rect)

# --- Card Class ---
class Card:
    def __init__(self, text, start_pos):
        self.text = text
        
        # Interpolated Properties
        self.pos = Interpolated(pygame.Vector2(start_pos), duration=1.0, easing=Easing.EASE_OUT_BACK)
        self.rotation = Interpolated(0.0, duration=0.8, easing=Easing.EASE_OUT_BACK)
        self.scale = Interpolated(1.0, duration=0.5, easing=Easing.EASE_OUT_BACK)
        
        # Flip state (1.0 = Front, -1.0 = Back)
        self.flip = Interpolated(-1.0, duration=0.6, easing=Easing.EASE_IN_OUT_EXPONENTIAL)
        
        self.z_index = 0

    def draw(self, surface):
        # 1. Get current values
        c_pos = self.pos.get_value()
        c_rot = self.rotation.get_value()
        c_flip = self.flip.get_value()
        c_scale = self.scale.get_value()
        
        # 2. Setup transformation surface
        # We draw the card unrotated at (0,0) on a temp surface, then rotate/scale it.
        # Size needed: large enough to hold rotated card.
        # Let's keep it simple: Draw to a surface of CARD_WIDTH x CARD_HEIGHT, then transform.
        
        # Visual Scale from flip
        scale_x = abs(c_flip) * c_scale
        scale_y = c_scale
        
        if scale_x < 0.01: return # Invisible when perpendicular
        
        w = int(CARD_WIDTH * scale_x)
        h = int(CARD_HEIGHT * scale_y)
        
        # Temp surface for the card face
        # We need a surface with alpha
        card_surf = pygame.Surface((CARD_WIDTH, CARD_HEIGHT), pygame.SRCALPHA)
        
        rect = pygame.Rect(0, 0, CARD_WIDTH, CARD_HEIGHT)
        if c_flip >= 0:
            draw_card_front(card_surf, rect, self.text)
        else:
            draw_card_back(card_surf, rect)
            
        # Scale
        if scale_x != 1.0 or scale_y != 1.0:
            card_surf = pygame.transform.scale(card_surf, (w, h))
            
        # Rotate
        if abs(c_rot) > 0.1:
            card_surf = pygame.transform.rotate(card_surf, -c_rot) # Negative for clockwise visual
        
        # Blit to screen centered
        surf_rect = card_surf.get_rect(center=(c_pos.x, c_pos.y))
        surface.blit(card_surf, surf_rect)

# --- Main Demo ---
class DemoDeck:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Interpolation Deck Demo")
        self.clock = pygame.time.Clock()
        
        self.deck_pos = pygame.Vector2(100, 150)
        self.cards = []
        
        # Define the message
        self.message_lines = [
            "THANKS",
            "FOR",
            "WATCHING!"
        ]
        
        # Create all cards at deck position
        msg_chars = "".join(self.message_lines)
        for char in msg_chars:
            c = Card(char, self.deck_pos)
            c.rotation.set_value(random.uniform(-5, 5)) # Slight random rotation in pile
            self.cards.append(c)
            
        # Reverse list so first char is at top of deck (for dealing logic if we popped)
        # But for rendering, we want the LAST in list to be on TOP.
        # Let's say we deal from the "top" (end of list).
        self.cards.reverse() 
        
        self.state = "DECK"
        self.timer = 0
        
    def start_deal(self):
        self.state = "DEALING"
        
        # Layout Config
        start_y = 150
        line_height = 160
        gap = 10
        
        # We need to distribute cards to their target positions.
        # We'll pop from our list (which is currently reversed message)
        # So the last item is 'T', then 'H', etc.
        
        # Let's organize the target positions first
        targets = []
        
        # Line 1: THANKS
        l1_y = 150
        l1_len = len("THANKS")
        l1_width = l1_len * CARD_WIDTH + (l1_len-1)*gap
        l1_start_x = (SCREEN_WIDTH - l1_width) / 2 + CARD_WIDTH/2
        
        for i, char in enumerate("THANKS"):
            pos = pygame.Vector2(l1_start_x + i*(CARD_WIDTH+gap), l1_y)
            targets.append((char, pos, 0)) # Char, Pos, Rotation
            
        # Line 2: FOR
        l2_y = l1_y + line_height
        l2_len = len("FOR")
        l2_width = l2_len * CARD_WIDTH + (l2_len-1)*gap
        l2_start_x = (SCREEN_WIDTH - l2_width) / 2 + CARD_WIDTH/2
        
        for i, char in enumerate("FOR"):
             pos = pygame.Vector2(l2_start_x + i*(CARD_WIDTH+gap), l2_y)
             targets.append((char, pos, 0))

        # Line 3: WATCHING! (Arc?)
        l3_y = l2_y + line_height + 50 # Bit lower
        word_3 = "WATCHING!"
        
        # Arc logic
        center_arc_x = SCREEN_WIDTH / 2
        center_arc_y = l3_y + 400 # Radius point far below
        radius = 400
        angle_span = 60 # degrees
        start_angle = -angle_span / 2 - 90 # -90 is up. 
        step = angle_span / (len(word_3) - 1)
        
        for i, char in enumerate(word_3):
            # Angle in degrees. 0 is Right, -90 is Up.
            # We want an arc centered around Up.
            # Let's map i to an angle.
            # Center is index len/2.
            mid = (len(word_3)-1) / 2
            diff = i - mid
            angle_deg = diff * 8 # 8 degrees per card
            angle_rad = math.radians(angle_deg - 90) # -90 to orient up
            
            x = center_arc_x + radius * math.cos(angle_rad)
            y = center_arc_y + radius * math.sin(angle_rad)
            
            # Rotation: The card should point out from center.
            # Angle of normal is angle_deg.
            targets.append((char, pygame.Vector2(x, y), angle_deg))

        # Now apply targets to cards
        # Our cards list is reversed message: [!, G, N... S, K, N...]
        # We need to match them.
        
        # Let's sort cards back to message order to make assignment easy?
        # Or just search for matching char?
        # Let's just assume we have the right count and chars in reverse order.
        
        available_cards = list(self.cards) # Copy
        
        # Animate sequentially
        self.deal_sequence = []
        
        # We want "THANKS" first.
        # targets has "THANKS" first.
        
        for t_char, t_pos, t_rot in targets:
            # Find a card with this char
            # Prefer one from the top (end) if possible?
            found = None
            for i in range(len(available_cards)-1, -1, -1):
                if available_cards[i].text == t_char:
                    found = available_cards.pop(i)
                    break
            
            if found:
                self.deal_sequence.append((found, t_pos, t_rot))
    
    def update(self):
        # Draw Deck Placeholder
        # pygame.draw.rect(self.screen, (50, 40, 40), (self.deck_pos.x, self.deck_pos.y, CARD_WIDTH, CARD_HEIGHT), 2)
        
        if self.state == "DECK":
            self.timer += 1
            if self.timer > 60: # Wait 1 sec then start
                self.start_deal()
                self.timer = 0
                
        elif self.state == "DEALING":
            self.timer += 1
            if self.timer % 10 == 0 and self.deal_sequence: # Deal every 10 frames
                card, target_pos, target_rot = self.deal_sequence.pop(0)
                
                # Animate!
                card.pos.set_value(target_pos)
                card.flip.set_value(1.0) # Flip to Front
                card.rotation.set_value(target_rot)
                
                # Bring to top of draw list (which is self.cards)
                # We need to ensure it draws locally on top.
                self.cards.remove(card)
                self.cards.append(card)

    def draw(self):
        self.screen.fill(BG_COLOR)
        
        # Draw "Deck" placeholder rect
        deck_rect = pygame.Rect(0, 0, CARD_WIDTH, CARD_HEIGHT)
        deck_rect.center = (self.deck_pos.x, self.deck_pos.y)
        pygame.draw.rect(self.screen, GOLD_COLOR, deck_rect, width=2, border_radius=8)
        font = pygame.font.SysFont("Times New Roman", 20, italic=True)
        txt = font.render("Deck", True, GOLD_COLOR)
        self.screen.blit(txt, txt.get_rect(midtop=(deck_rect.centerx, deck_rect.bottom + 10)))

        # Draw Cards
        for c in self.cards:
            c.draw(self.screen)
            
        pygame.display.flip()

    def run(self):
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.MOUSEBUTTONDOWN:
                     # Reset on click
                     self.__init__()
            
            self.update()
            self.draw()
            self.clock.tick(60)

if __name__ == "__main__":
    DemoDeck().run()
