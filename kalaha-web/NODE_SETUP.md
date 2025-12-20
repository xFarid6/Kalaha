# Node.js Installation (Local to kalaha-web)

## Note on .venv for Node.js

Unlike Python, Node.js doesn't use virtual environments (`.venv`). Instead, Node.js uses:
- **Local `node_modules/`**: Project-specific dependencies
- **Global install**: System-wide Node.js installation

## Option 1: Use System Node.js (Recommended)

Install Node.js globally from: https://nodejs.org/

Then in `kalaha-web/`:
```bash
npm install  # Installs dependencies locally
```

## Option 2: Portable Node.js (Windows)

Download portable Node.js and extract to `kalaha-web/node/`:

1. Download from: https://nodejs.org/dist/v20.11.0/node-v20.11.0-win-x64.zip
2. Extract to: `kalaha-web/node/`
3. Add to PATH temporarily:
   ```powershell
   $env:PATH = "$(pwd)\node;$env:PATH"
   ```

## Option 3: No Node.js Required!

The current implementation uses **pure ES6 modules** which work directly in modern browsers without build tools.

Just open `index.html` in a browser with a local server:

```bash
# Using Python (already installed)
python -m http.server 8000

# Then open: http://localhost:8000
```

## Current Status

✅ **Phase 1 complete**: Game logic validated
✅ **Phase 2 complete**: UI fully implemented

No build step required! The app is ready to run with just a local web server.
