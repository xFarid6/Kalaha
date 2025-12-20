# Kalaha Web

Web-based implementation of Kalaha (Mancala) with AI opponents.

## Quick Start

```bash
# Test game logic
npm test

# Run development server
npm run dev
# Open http://localhost:8000
```

## Project Structure

```
kalaha-web/
├── index.html          # Main HTML file
├── css/
│   └── styles.css      # Styling
├── js/
│   ├── game_logic.js   # Core game rules (ported from Python)
│   ├── game_logic.test.js  # Test suite
│   ├── ai_engine.js    # Minimax AI
│   ├── ui.js           # Board rendering & interaction
│   └── main.js         # Application entry point
├── models/
│   └── kalaha_model/   # TensorFlow.js model (converted from PyTorch)
└── README.md
```

## Development Status

- [x] Phase 1: Game Logic (✓ Validated against Python)
- [ ] Phase 2: Neural Network Conversion
- [ ] Phase 3: UI Development
- [ ] Phase 4: AI Integration
- [ ] Phase 5: Deployment

## Testing

Run `npm test` to validate game logic parity with the Python implementation.

All tests must pass before proceeding to UI development.

## Deployment

Will be hosted on GitHub Pages at: `https://xfarid6.github.io/kalaha-web/`
