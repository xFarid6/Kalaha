# Web Deployment Strategy: Kalaha on GitHub Pages

## Overview
This document outlines the process for deploying a **web version** of the Kalaha game to **GitHub Pages**, making it publicly accessible without requiring Python installation.

---

## Why GitHub Pages?

### Advantages
✅ **Free hosting** (unlimited static sites)  
✅ **Custom domain support** (kalaha.yourdomain.com)  
✅ **HTTPS by default** (secure connections)  
✅ **Git-based deployment** (push to deploy)  
✅ **No server management** (fully static)  
✅ **Global CDN** (fast worldwide access)

### Limitations
❌ No Python backend (must transpile or rewrite)  
❌ Static files only (HTML/CSS/JS)  
❌ No server-side AI training  
❌ Model size limits (~100MB recommended)

---

## Architecture Decision

### Option 1: 🥇 **Pure JavaScript Port** (Recommended)

**Convert to Web Stack**:
- **Frontend**: React or Vanilla JS
- **Game Logic**: Port Python → JavaScript
- **AI**: Load pre-trained model (TensorFlow.js or ONNX.js)
- **UI**: Canvas or SVG for board rendering

**Pros**:
- No server required
- Fast client-side inference
- Works offline (PWA)
- Easy to maintain

**Cons**:
- Rewrite game logic (~500 lines)
- Convert neural network (PyTorch → TensorFlow.js)
- JavaScript AI is slower than Python

---

### Option 2: Pyodide (Python in Browser)

**Keep Python Code**:
- Use **Pyodide** (Python compiled to WebAssembly)
- Run actual Python code in browser
- Load `.py` files directly

**Pros**:
- Minimal code changes
- Keep existing logic

**Cons**:
- Large download (~10MB Pyodide runtime)
- Slower startup
- Limited ML library support (no PyTorch)
- Experimental technology

---

### Option 3: Hybrid (API Backend)

**Not Suitable for GitHub Pages** (no backend support)

Alternative: Deploy to Vercel/Netlify with serverless functions, but defeats the purpose of "simple GitHub Pages".

---

## Recommended Approach: JavaScript Port

We will **port the game to JavaScript** for optimal web experience.

---

## Implementation Roadmap

### Phase 1: Core Game Logic (Week 1)

**Tasks**:
1. **Create Repository Structure**
   ```
   kalaha-web/
   ├── index.html
   ├── css/
   │   └── styles.css
   ├── js/
   │   ├── game_logic.js     # Port from Python
   │   ├── ai_engine.js      # Minimax/Alpha-Beta
   │   ├── ui.js             # Board rendering
   │   └── main.js           # Entry point
   └── models/
       └── kalaha_model.json # Pre-trained NN (optional)
   ```

2. **Port Game Logic**
   - Translate `game_logic.py` → `game_logic.js`
   - Functions: `initialState()`, `legalMoves()`, `applyMove()`, etc.
   - Unit tests (Jest or Mocha)

3. **Validate Logic**
   ```bash
   npm test  # Run tests to ensure parity with Python
   ```

**Milestone**: JavaScript game engine works identically to Python version.

---

### Phase 2: UI Development (Week 2)

**Tasks**:
1. **Design Board Layout**
   - Use HTML5 Canvas or SVG
   - Responsive design (mobile + desktop)
   - Brown/gold aesthetic (match desktop app)

2. **Implement Interaction**
   - Click to select pit
   - Animate seed distribution
   - Highlight legal moves

3. **Add Game States**
   - Title screen
   - Settings menu (difficulty, AI type)
   - Game over overlay

**Milestone**: Playable game in browser (human vs human).

---

### Phase 3: AI Integration (Week 3)

**Option A: Minimax/Alpha-Beta (Simpler)**
- Port `ai_engine.py` → `ai_engine.js`
- Keep endgame database (JSON file)
- Fast, no dependencies

**Option B: Neural Network (Advanced)**
1. **Convert Model**
   ```bash
   # PyTorch → ONNX → TensorFlow.js
   python convert_model.py
   tensorflowjs_converter --input_format=keras model.h5 web_model/
   ```

2. **Load in Browser**
   ```javascript
   import * as tf from '@tensorflow/tfjs';
   
   const model = await tf.loadLayersModel('models/kalaha_model.json');
   const prediction = model.predict(tf.tensor(state));
   ```

**Recommendation**: Start with **Minimax** (simpler), add NN later if needed.

**Milestone**: AI opponent works in browser.

---

### Phase 4: GitHub Pages Deployment (Week 4)

**Tasks**:
1. **Setup GitHub Repository**
   ```bash
   git init
   git add .
   git commit -m "Initial web version"
   git remote add origin https://github.com/xFarid6/kalaha-web.git
   git push -u origin main
   ```

2. **Enable GitHub Pages**
   - Go to repository **Settings** → **Pages**
   - Source: `main` branch, `/` (root)
   - Save

3. **Access Site**
   - URL: `https://xfarid6.github.io/kalaha-web/`
   - Custom domain (optional): Add `CNAME` file

4. **Optimize for Production**
   ```bash
   # Minify JavaScript
   npm run build
   
   # Compress assets
   gzip -k js/*.js css/*.css
   ```

**Milestone**: Game live on GitHub Pages!

---

### Phase 5: Enhancements (Ongoing)

**Features**:
- [ ] Save game state (localStorage)
- [ ] Undo/redo moves
- [ ] Game replay viewer
- [ ] Stats tracking (wins/losses)
- [ ] Multiplayer (WebRTC or Socket.io) → requires backend
- [ ] PWA (offline play)
- [ ] Leaderboard (Firebase/Supabase)

---

## Technical Stack

### Frontend
- **HTML5**: Structure
- **CSS3**: Styling (Flexbox/Grid)
- **JavaScript (ES6+)**: Logic
- **Canvas/SVG**: Board rendering

### Build Tools (Optional)
- **Vite**: Fast dev server + bundling
- **TypeScript**: Type safety (optional)
- **Tailwind CSS**: Utility-first styling (optional)

### AI Libraries
- **TensorFlow.js**: Neural network inference
- **ONNX.js**: Cross-platform model loading

### Testing
- **Jest**: JavaScript unit tests
- **Cypress**: End-to-end testing

---

## Development Workflow

### Local Development
```bash
# Install dependencies
npm install

# Start dev server
npm run dev

# Open browser
open http://localhost:5173
```

### Deployment
```bash
# Build for production
npm run build

# Push to GitHub
git add dist/
git commit -m "Deploy v1.0"
git push origin main
```

### Automatic Deployment (GitHub Actions)
```yaml
# .github/workflows/deploy.yml
name: Deploy to GitHub Pages

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3
      - run: npm install
      - run: npm run build
      - uses: peaceiris/actions-gh-pages@v3
        with:
          github_token: ${{ secrets.GITHUB_TOKEN }}
          publish_dir: ./dist
```

---

## Why This Process?

### Rationale for JavaScript Port

1. **Performance**: Client-side execution is instant (no network latency)
2. **Accessibility**: Works on any device with a browser
3. **Scalability**: GitHub Pages can serve millions of users
4. **Cost**: Completely free
5. **Portfolio**: Showcase project to recruiters/community

### Why Not Keep Python?

- **Pyodide** is experimental and slow
- **Backend hosting** defeats "simple deployment" goal
- **JavaScript ecosystem** is more mature for web apps

### Trade-offs

**We gain**:
- Universal accessibility
- Zero hosting cost
- Fast loading times

**We lose**:
- Some Python-specific libraries
- Need to rewrite ~1000 lines of code
- Can't use PyTorch directly

**Verdict**: The trade-off is worth it for a **public-facing game**.

---

## Model Conversion Strategy

### If Using Neural Network

**PyTorch → TensorFlow.js Pipeline**:

1. **Export PyTorch to ONNX**
   ```python
   import torch
   import torch.onnx
   
   model.eval()
   dummy_input = torch.randn(1, 15)
   torch.onnx.export(model, dummy_input, "kalaha.onnx")
   ```

2. **ONNX to TensorFlow**
   ```bash
   pip install onnx-tf
   onnx-tf convert -i kalaha.onnx -o kalaha_tf/
   ```

3. **TensorFlow to TensorFlow.js**
   ```bash
   tensorflowjs_converter --input_format=tf_saved_model kalaha_tf/ web_model/
   ```

4. **Load in Browser**
   ```javascript
   const model = await tf.loadGraphModel('web_model/model.json');
   ```

**File Size**: Expect 1-5MB for the model (acceptable for web).

---

## Timeline Summary

| Phase | Duration | Deliverable |
|-------|----------|-------------|
| Core Logic | 1 week | JavaScript game engine |
| UI | 1 week | Playable interface |
| AI | 1 week | Minimax opponent |
| Deployment | 1 week | Live on GitHub Pages |
| **Total** | **1 month** | Public web version |

---

## Success Metrics

After deployment:
- [ ] Game loads in < 3 seconds
- [ ] Works on mobile + desktop
- [ ] AI responds in < 1 second
- [ ] Zero hosting costs
- [ ] >90% Lighthouse score

---

## Future Considerations

### Advanced Features (Post-Launch)
- **Multiplayer**: Requires backend (Firebase, Supabase, or dedicated server)
- **Real-time sync**: WebSockets for live games
- **Tournaments**: Bracket system
- **Analytics**: Track popular strategies

### Monetization (Optional)
- **Ads**: Google AdSense
- **Donations**: Ko-fi/Patreon
- **Premium features**: Advanced AI, themes

---

## Conclusion

**GitHub Pages deployment is ideal** for showcasing Kalaha as a:
- Portfolio project
- Educational tool
- AI demonstration
- Open-source contribution

The **JavaScript port** is the cleanest solution, balancing performance, accessibility, and maintainability. With 1 month of development, we can have a **production-ready web game** available to anyone with a browser.

**Next Step**: Create `kalaha-web` repository and start Phase 1.
