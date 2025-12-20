# Kalaha Project To-Do List

## High Priority

### Model Conversion & Integration
- [ ] Install required packages: `pip install tensorflowjs onnx onnx-tf onnxscript`
- [ ] Convert PyTorch model to ONNX format
- [ ] Convert ONNX to TensorFlow.js
- [ ] Test model loading in browser
- [ ] Compare NN model vs Minimax performance
- [ ] Add model switching UI (Minimax vs Neural Network)

### Web Deployment
- [ ] Create GitHub repository for `kalaha-web`
- [ ] Configure GitHub Pages
- [ ] Add custom domain (optional)
- [ ] Optimize assets for production
- [ ] Add loading screen for model download
- [ ] Test on mobile devices (iOS/Android)

## Medium Priority

### Performance Optimization
- [ ] Profile AI engine performance
- [ ] Optimize Canvas rendering (use requestAnimationFrame)
- [ ] Add Web Worker for AI computation (prevent UI blocking)
- [ ] Implement progressive loading for large models

### Documentation
- [ ] Add README with installation instructions
- [ ] Create CONTRIBUTING.md
- [ ] Document API for game logic
- [ ] Add inline code comments
- [ ] Create gameplay tutorial overlay

### Testing
- [ ] Add unit tests for game logic (Jest/Vitest)
- [ ] Add integration tests for AI engine
- [ ] Cross-browser testing (Chrome, Firefox, Safari, Edge)
- [ ] Accessibility audit (WCAG compliance)
- [ ] Performance benchmarking

## Low Priority

### UI/UX Improvements
- [ ] Add sound effects for moves
- [ ] Add background music (toggleable)
- [ ] Improve mobile touch interactions
- [ ] Add dark/light theme toggle
- [ ] Add confetti animation for wins
- [ ] Add move history timeline

### Advanced Features
- [ ] Export endgame database to JSON for web
- [ ] Add AI personality modes (cautious, balanced, aggressive)
- [ ] Add tournament mode (best of 3/5/7)
- [ ] Add spectator mode for two AIs playing
- [ ] Add game analysis mode (review moves with suggestions)

### Analytics
- [ ] Add privacy-friendly analytics (no tracking)
- [ ] Track most popular difficulty levels
- [ ] Track average game length
- [ ] Track AI win rates by difficulty

## Completed ✅

- [x] Port game logic to JavaScript
- [x] Create responsive UI with Canvas
- [x] Port Minimax/Alpha-Beta AI
- [x] Add difficulty levels
- [x] Create TensorFlow.js model interface
- [x] Browser testing (human vs human)
- [x] Browser testing (human vs AI)
