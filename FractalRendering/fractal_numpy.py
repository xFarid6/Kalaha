import numpy as np
import math

def compute_julia_set(width, height, x_min, x_max, y_min, y_max, c, max_iter=50):
    # 1. Setup Grid
    # Complex plane
    x = np.linspace(x_min, x_max, width, dtype=np.float32)
    y = np.linspace(y_min, y_max, height, dtype=np.float32)
    X, Y = np.meshgrid(x, y)
    Z = X + 1j * Y
    
    # Output arrays
    # We use float for smooth coloring
    iterations = np.zeros(Z.shape, dtype=np.float32)
    mask = np.ones(Z.shape, dtype=bool) # Process all initially
    
    # 2. Iterate
    # Optimization: Z[mask] indexing is sometimes slower than full array ops if mask is large.
    # But for fractals, points escape.
    
    escape_radius_sq = 4.0
    
    for i in range(max_iter):
        if not np.any(mask): break
        
        # Update only active Z
        # Z[mask] = Z[mask]**2 + C
        # Note: In-place update restricted with boolean index on LHS in some versions/shapes, 
        # but standard numpy allows it.
        
        Zs = Z[mask]
        Zs = Zs * Zs + c
        Z[mask] = Zs
        
        # Check escape
        # abs(z)**2 = real**2 + imag**2
        abs_sq = Z.real**2 + Z.imag**2
        
        # Points that just escaped
        escaped_now = (abs_sq > escape_radius_sq) & mask
        
        # Update iterations for escaped points
        # Smooth coloring formula requires |Z| after escape? 
        # Usually we do a couple more iterations to reduce error, or use current |Z|.
        # Formula: nu = log2(log2(|z|))
        # iter = i + 1 - nu
        
        # We save 'i' for now, smooth later?
        # Or compute smooth right here for escaped.
        # Let's save the exact |Z| or iteration count.
        # Actually simplest: store 'i' and current |Z|?
        # Let's just store 'i' and refine post-loop if possible, but Z is mutated.
        # Correct way for vectorization: 
        # Store Z for smoothing *before* it blows up too huge?
        # Actually, |Z| needs to be > 2 for the log formula math to work well.
        
        if np.any(escaped_now):
            # Apply smooth coloring to escaped points
            # log_zn = np.log(abs_sq[escaped_now]) / 2.0  # log(|z|)
            # nu = np.log(log_zn / np.log(2.0)) / np.log(2.0)
            # iterations[escaped_now] = i + 1 - nu
            
            # Simplified for speed/safety:
            # Avoid log(0)
            
            z_abs = np.sqrt(abs_sq[escaped_now])
            # log_z = np.log(z_abs)
            # nu = np.log(log_z) / np.log(2) 
            # val = i + 1 - nu
            
            # Vectorized math
            # We use a simpler approx or the full one.
            # Full one:
            # i + 1 - log2(log2(|z|))
            
            # Safety: z_abs > 2 guaranteed by escape condition
            # np.log2 requires recent numpy, use log / log2
            
            log_z = np.log(z_abs)
            nu = np.log(log_z) / np.log(2.0)
            
            iterations[escaped_now] = i + 1 - nu
            
            # Remove from mask
            mask[escaped_now] = False
            
    # Points inside set (mask is True) get max_iter
    iterations[mask] = 0 # Black usually
    
    return iterations

def map_to_color(iterations, max_iter):
    # Map 0..max_iter to 0..255 (Grayscale or Color)
    # Simple Grayscale:
    # 0 -> 0 (Black)
    # 0.1 -> Gray
    
    # Normalize
    # Handle mask=0 (Interior) separate?
    # Interior is 0.
    
    # Linear:
    # val = (iterations / max_iter) * 255
    
    # Cyclic Cosine Palette (e.g. JohnBuffer style)
    # t = iter * freq
    # r = 0.5 + 0.5*cos(t + r_phase)
    
    freq = 0.1
    t = iterations * freq
    
    r = (0.5 + 0.5 * np.cos(t)).astype(np.float32) * 255
    g = (0.5 + 0.5 * np.cos(t + 2.0)).astype(np.float32) * 255
    b = (0.5 + 0.5 * np.cos(t + 4.0)).astype(np.float32) * 255
    
    # Interior to Black
    # Interior has iterations approx 0 (if we set it) or max_iter
    # In compute function we set it to 0. 
    # But small iterations (0.1) can also be 0.
    # Let's say exactly 0 is black.
    
    img = np.stack((r, g, b), axis=-1).astype(np.uint8)
    
    # Fix Iteration 0 (Interior) to Black (0,0,0)
    # We need a mask for exact 0
    # Floating point comparison safety?
    mask_zero = iterations < 0.001
    img[mask_zero] = 0
    
    # Swap axes for Pygame (Width, Height) -> Pygame expects (W, H, 3) ?
    # Pygame surfarray.make_surface expects [x, y, 3].
    # Numpy meshgrid (y, x) order implies Z is [y, x] usually?
    # np.meshgrid(x, y) returns X[y, x].
    # So img is [Height, Width, 3].
    # Pygame expects [Width, Height, 3].
    # We transpose.
    
    img = np.transpose(img, (1, 0, 2))
    
    return img
