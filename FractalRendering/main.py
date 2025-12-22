import pygame
import sys
import numpy as np
import threading
import queue
import time
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from fractal_numpy import compute_julia_set, map_to_color

# Config
WIDTH = 800
HEIGHT = 600
RENDER_SCALE = 0.5 # Render at 50% res for speed, scale up?
# Or render full res if Numpy is fast enough. 800x600 is 480k pixels. 
# Numpy is fast. Let's try full res first.

class RenderTask:
    def __init__(self, rect, c):
        self.rect = rect # (x_min, x_max, y_min, y_max)
        self.c = c

class FractalRenderer:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Julia Set Explorer")
        self.clock = pygame.time.Clock()
        
        # Camera (Complex Plane)
        self.center_x = 0.0
        self.center_y = 0.0
        self.zoom = 1.0 # Larger = Zoomed In? Or Scale?
        # Let's use Scale: Units per Pixel. 
        # width_units = WIDTH * scale
        self.scale = 4.0 / WIDTH # Initial: 4 units across 800 pixels
        
        self.c = -0.4 + 0.6j
        
        # Double Buffering Sync
        self.last_surface = None
        self.last_rect = None # (x_min, y_min, w_units, h_units)
        
        self.render_queue = queue.Queue(maxsize=1)
        self.result_queue = queue.Queue()
        
        self.rendering = False
        
        # Start Thread
        self.thread = threading.Thread(target=self.render_worker, daemon=True)
        self.thread.start()
        
        # Trigger initial render
        self.request_render()

    def get_view_rect(self):
        w_units = WIDTH * self.scale
        h_units = HEIGHT * self.scale
        x_min = self.center_x - w_units / 2
        y_min = self.center_y - h_units / 2
        return (x_min, x_min + w_units, y_min, y_min + h_units)

    def request_render(self):
        # Only request if queue empty (throttle)
        if not self.rendering:
            rect = self.get_view_rect()
            task = RenderTask(rect, self.c)
            self.render_queue.put(task)
            self.rendering = True

    def render_worker(self):
        while True:
            task = self.render_queue.get()
            
            # Compute
            # Note: Pygame surfaces must be created on main thread? 
            # PixelArray/Numpy conversions are CPU ops, fine.
            # But creating Surface? Safer to return numpy array.
            
            x_min, x_max, y_min, y_max = task.rect
            
            # Use lower res?
            rw, rh = WIDTH, HEIGHT
            
            try:
                iters = compute_julia_set(rw, rh, x_min, x_max, y_min, y_max, task.c)
                arr = map_to_color(iters, 50)
                
                self.result_queue.put((arr, task.rect))
            except Exception as e:
                print(f"Render Error: {e}")
            
            self.render_queue.task_done()

    def run(self):
        running = True
        
        font = pygame.font.SysFont("Consolas", 16)
        
        while running:
            # Input
            moved = False
            zoom_changed = False
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                
                # Mouse Pan
                if event.type == pygame.MOUSEMOTION:
                    if event.buttons[0]: # Left Click Drag
                        dx, dy = event.rel
                        # Pixel delta to Complex delta
                        # dx pixels * scale units/pixel
                        self.center_x -= dx * self.scale
                        self.center_y -= dy * self.scale
                        moved = True
                        
                # Mouse Zoom
                if event.type == pygame.MOUSEWHEEL:
                    zoom_factor = 0.9 if event.y > 0 else 1.1
                    self.scale *= zoom_factor
                    moved = True
                    zoom_changed = True
                    # Zoom toward mouse? 
                    # Complex math: 
                    # mouse_z = center + (mouse_pos - screen_center) * old_scale
                    # center = mouse_z - (mouse_pos - screen_center) * new_scale
                    
                    mx, my = pygame.mouse.get_pos()
                    off_x = mx - WIDTH//2
                    off_y = my - HEIGHT//2
                    
                    # Correction to keep mouse fixed
                    # shift = offset * (1 - factor) ?
                    # Let's keep it simple center zoom for now
            
            # Key C Control
            keys = pygame.key.get_pressed()
            c_speed = 0.005
            if keys[pygame.K_LEFT]: self.c -= c_speed; moved = True
            if keys[pygame.K_RIGHT]: self.c += c_speed; moved = True
            if keys[pygame.K_UP]: self.c -= c_speed * 1j; moved = True
            if keys[pygame.K_DOWN]: self.c += c_speed * 1j; moved = True
            
            # Check Results
            try:
                while not self.result_queue.empty():
                    arr, rect = self.result_queue.get_nowait()
                    self.rendering = False
                    
                    # Create Surface
                    surf = pygame.surfarray.make_surface(arr)
                    self.last_surface = surf
                    self.last_rect = rect
            except:
                pass
            
            # Trigger new render if idle and moved
            if moved or not self.rendering:
                # Continuous update check?
                # If we moved, we want a new frame.
                # If we are strictly idle, we don't spam.
                if self.render_queue.empty():
                     rect = self.get_view_rect()
                     # If rect differs significantly from last job?
                     # Just request. Worker throttles naturally by queue size 1 loop.
                     self.request_render()

            # DRAW
            self.screen.fill((0,0,0))
            
            if self.last_surface:
                if zoom_changed or moved:
                    # Digital Zoom / Pan Trick
                    # We have last_surface covering last_rect.
                    # We want to draw it onto screen which represents current_view_rect.
                    
                    # Map:
                    # Screen (0,0) -> view_rect.min
                    # last_rect.min -> Screen Coords?
                    
                    # x_screen = (x_world - view_min) / scale
                    
                    lx_min, lx_max, ly_min, ly_max = self.last_rect
                    vx_min, vx_max, vy_min, vy_max = self.get_view_rect()
                    
                    # Determine where last_surface's top-left is on current screen
                    # pos_x = (lx_min - vx_min) / self.scale
                    # pos_y = (ly_min - vy_min) / self.scale
                    
                    pos_x = (lx_min - vx_min) / self.scale
                    pos_y = (ly_min - vy_min) / self.scale
                    
                    # Determine size
                    # last_width_units = lx_max - lx_min
                    # width_pixels = last_width_units / self.scale
                    
                    last_w_units = lx_max - lx_min
                    last_h_units = ly_max - ly_min
                    
                    new_w = int(last_w_units / self.scale)
                    new_h = int(last_h_units / self.scale)
                    
                    # Scale and Blit
                    # transform.scale is somewhat expensive but faster than fractal gen
                    # Optimization: rough scale?
                    
                    # If scale difference is small, maybe visually negligible?
                    # But for zoom it is large.
                    
                    scaled = pygame.transform.scale(self.last_surface, (new_w, new_h))
                    self.screen.blit(scaled, (int(pos_x), int(pos_y)))
                else:
                    # Perfect match
                    self.screen.blit(self.last_surface, (0, 0))
            
            # UI
            info = f"C: {self.c.real:.3f} + {self.c.imag:.3f}i"
            self.screen.blit(font.render(info, True, (255, 255, 255)), (10, 10))
            
            help_txt = "Arrows: Adjust C | Drag: Pan | Scroll: Zoom"
            self.screen.blit(font.render(help_txt, True, (200, 200, 200)), (10, HEIGHT - 30))

            pygame.display.flip()
            self.clock.tick(60)

        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    FractalRenderer().run()
