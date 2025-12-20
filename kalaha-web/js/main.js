/**
 * Main Application Module
 * Manages game state, screens, and user interactions
 */

import { initialState, legalMoves, applyMove, isTerminal, cleanupBoard, P1_STORE, P2_STORE } from './game_logic.js';
import { GameUI } from './ui.js';
import { gameStateManager } from './state_manager.js';

class KalahaApp {
    constructor() {
        this.gameState = {
            board: null,
            currentPlayer: 0,
            gameOver: false,
            opponent: 'human',  // 'human' or 'ai'
            difficulty: 'medium',
            animationSpeed: 300
        };

        this.moveHistory = [];  // For undo/redo
        this.moveCount = 0;     // Track game length

        this.screens = {
            title: document.getElementById('title-screen'),
            settings: document.getElementById('settings-screen'),
            game: document.getElementById('game-screen')
        };

        this.overlays = {
            gameOver: document.getElementById('game-over-overlay'),
            howToPlay: document.getElementById('how-to-play-overlay')
        };

        this.gameUI = null;

        this.init();
    }

    init() {
        this.setupEventListeners();
        this.showScreen('title');

        // Check for saved game
        if (gameStateManager.hasSavedGame()) {
            this.promptContinueGame();
        }
    }

    promptContinueGame() {
        const continueBtn = document.createElement('button');
        continueBtn.className = 'btn btn-secondary';
        continueBtn.textContent = 'Continue Saved Game';
        continueBtn.style.marginTop = '1rem';

        continueBtn.addEventListener('click', () => {
            const savedGame = gameStateManager.loadGame();
            if (savedGame) {
                this.gameState.board = savedGame.board;
                this.gameState.currentPlayer = savedGame.currentPlayer;
                this.gameState.opponent = savedGame.opponent;
                this.gameState.difficulty = savedGame.difficulty;
                this.moveHistory = gameStateManager.loadMoveHistory();

                const canvas = document.getElementById('game-canvas');
                this.gameUI = new GameUI(canvas);
                this.gameUI.setAnimationSpeed(this.gameState.animationSpeed);
                this.gameUI.setOnPitClick((pitIndex) => this.handlePitClick(pitIndex));

                this.showScreen('game');
                this.updateGameUI();
            }
            continueBtn.remove();
        });

        const menuButtons = document.querySelector('#title-screen .menu-buttons');
        if (menuButtons) {
            menuButtons.appendChild(continueBtn);
        }
    }

    setupEventListeners() {
        // Title screen
        document.getElementById('btn-play').addEventListener('click', () => {
            this.showScreen('settings');
        });

        document.getElementById('btn-how-to-play').addEventListener('click', () => {
            this.showOverlay('howToPlay');
        });

        // Settings
        document.getElementById('btn-start-game').addEventListener('click', () => {
            this.startGame();
        });

        document.getElementById('btn-back-to-title').addEventListener('click', () => {
            this.showScreen('title');
        });

        // Settings options
        document.querySelectorAll('.btn-option').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const setting = e.target.dataset.setting;
                const value = e.target.dataset.value;

                // Update active state
                document.querySelectorAll(`[data-setting="${setting}"]`).forEach(b => {
                    b.classList.remove('active');
                });
                e.target.classList.add('active');

                // Update game state
                if (setting === 'opponent') {
                    this.gameState.opponent = value;
                    const aiGroup = document.getElementById('ai-difficulty-group');
                    aiGroup.style.display = value === 'ai' ? 'block' : 'none';
                } else if (setting === 'difficulty') {
                    this.gameState.difficulty = value;
                }
            });
        });

        // Animation speed slider
        const animSlider = document.getElementById('anim-speed');
        const animLabel = document.getElementById('anim-speed-label');
        animSlider.addEventListener('input', (e) => {
            const value = parseInt(e.target.value);
            this.gameState.animationSpeed = value;
            animLabel.textContent = `${value}ms`;
        });

        // Game controls
        document.getElementById('btn-menu').addEventListener('click', () => {
            if (confirm('Return to main menu? (Game will be lost)')) {
                this.showScreen('title');
            }
        });

        document.getElementById('btn-undo').addEventListener('click', () => {
            this.undoMove();
        });

        document.getElementById('btn-hint').addEventListener('click', () => {
            // TODO: Implement hint
            console.log('Hint clicked');
        });

        // Game over overlay
        document.getElementById('btn-play-again').addEventListener('click', () => {
            this.hideOverlay('gameOver');
            this.startGame();
        });

        document.getElementById('btn-back-to-menu').addEventListener('click', () => {
            this.hideOverlay('gameOver');
            this.showScreen('title');
        });

        // How to play overlay
        document.getElementById('btn-close-rules').addEventListener('click', () => {
            this.hideOverlay('howToPlay');
        });
    }

    showScreen(screenName) {
        Object.values(this.screens).forEach(screen => screen.classList.add('hidden'));
        this.screens[screenName].classList.remove('hidden');
    }

    showOverlay(overlayName) {
        this.overlays[overlayName].classList.remove('hidden');
    }

    hideOverlay(overlayName) {
        this.overlays[overlayName].classList.add('hidden');
    }

    startGame() {
        // Initialize game state
        this.gameState.board = initialState();
        this.gameState.currentPlayer = 0;
        this.gameState.gameOver = false;
        this.moveHistory = [{ board: [...this.gameState.board], currentPlayer: 0 }];
        this.moveCount = 0;

        // Clear any previous saved game
        gameStateManager.clearSavedGame();

        // Setup canvas UI
        const canvas = document.getElementById('game-canvas');
        this.gameUI = new GameUI(canvas);
        this.gameUI.setAnimationSpeed(this.gameState.animationSpeed);
        this.gameUI.setOnPitClick((pitIndex) => this.handlePitClick(pitIndex));

        // Show game screen
        this.showScreen('game');

        // Update UI
        this.updateGameUI();
    }

    async handlePitClick(pitIndex) {
        if (this.gameState.gameOver) return;

        const board = this.gameState.board;
        const player = this.gameState.currentPlayer;

        // Animate move
        await this.gameUI.animateMove(board, pitIndex, player, this.gameState.animationSpeed);

        // Apply move
        const result = applyMove(board, pitIndex, player);
        this.gameState.board = result.board;
        this.moveCount++;

        // Save to move history
        this.moveHistory.push({ board: [...this.gameState.board], currentPlayer: this.gameState.currentPlayer, move: pitIndex });
        if (this.moveHistory.length > 21) this.moveHistory.shift();

        // Check for extra turn
        if (!result.extraTurn) {
            this.gameState.currentPlayer = 1 - this.gameState.currentPlayer;
        }

        // Auto-save
        gameStateManager.saveGame(this.gameState);
        gameStateManager.saveMoveHistory(this.moveHistory);

        // Check for game over
        if (isTerminal(this.gameState.board)) {
            this.endGame();
        } else {
            this.updateGameUI();

            // Handle AI turn
            if (this.gameState.opponent === 'ai' && this.gameState.currentPlayer === 1) {
                await this.delay(500); // AI "thinking" delay
                this.makeAIMove();
            }
        }
    }

    async makeAIMove() {
        // Use Minimax AI
        const { getBestMove, getDifficultySettings } = await import('./ai_engine.js');

        const settings = getDifficultySettings(this.gameState.difficulty);
        const result = getBestMove(
            this.gameState.board,
            this.gameState.currentPlayer,
            settings.depth,
            settings.strategy
        );

        if (result.move !== null) {
            console.log(`AI chose pit ${result.move + 1} (analyzed ${result.nodes} nodes)`);
            this.handlePitClick(result.move);
        }
    }


    undoMove() {
        if (this.moveHistory.length <= 1) return;

        if (this.gameState.opponent === 'ai') {
            if (this.moveHistory.length <= 2) return;
            this.moveHistory.pop();
            this.moveHistory.pop();
        } else {
            this.moveHistory.pop();
        }

        const previousState = this.moveHistory[this.moveHistory.length - 1];
        this.gameState.board = [...previousState.board];
        this.gameState.currentPlayer = previousState.currentPlayer;

        gameStateManager.saveGame(this.gameState);
        gameStateManager.saveMoveHistory(this.moveHistory);
        this.updateGameUI();
    }

    updateGameUI() {
        const board = this.gameState.board;
        const player = this.gameState.currentPlayer;
        const moves = legalMoves(board, player);

        // Update canvas
        this.gameUI.updateBoard(board, player, moves);

        // Update player indicators
        const p1Indicator = document.getElementById('p1-indicator');
        const p2Indicator = document.getElementById('p2-indicator');

        p1Indicator.classList.toggle('active', player === 0);
        p2Indicator.classList.toggle('active', player === 1);

        // Update status text
        const statusText = document.getElementById('status-text');
        const playerName = player === 0 ? 'Player 1' : (this.gameState.opponent === 'ai' ? 'AI' : 'Player 2');
        statusText.textContent = `${playerName}'s Turn`;

        // Update undo button
        const undoBtn = document.getElementById('btn-undo');
        const canUndo = this.gameState.opponent === 'ai' ? this.moveHistory.length > 2 : this.moveHistory.length > 1;
        undoBtn.disabled = !canUndo;
        const undoCount = Math.max(0, this.moveHistory.length - 1);
        undoBtn.textContent = `↶ Undo (${undoCount})`;
    }

    endGame() {
        this.gameState.gameOver = true;

        // Cleanup board
        this.gameState.board = cleanupBoard(this.gameState.board);
        this.gameUI.updateBoard(this.gameState.board, this.gameState.currentPlayer, []);

        // Determine winner
        const p1Score = this.gameState.board[P1_STORE];
        const p2Score = this.gameState.board[P2_STORE];

        let winner, winnerText;
        if (p1Score > p2Score) {
            winner = 0;
            winnerText = 'Player 1 Wins!';
        } else if (p2Score > p1Score) {
            winner = 1;
            winnerText = this.gameState.opponent === 'ai' ? 'AI Wins!' : 'Player 2 Wins!';
        } else {
            winner = 2;
            winnerText = "It's a Draw!";
        }

        // Update stats
        gameStateManager.updateStats({ winner, opponent: this.gameState.opponent, difficulty: this.gameState.difficulty, moveCount: this.moveCount });
        gameStateManager.clearSavedGame();

        // Update overlay
        document.getElementById('winner-text').textContent = winnerText;
        document.getElementById('final-score-p1').textContent = p1Score;
        document.getElementById('final-score-p2').textContent = p2Score;

        // Show stats
        const stats = gameStateManager.getStats();
        if (stats) {
            const statsHtml = `<div style="margin-top: 1rem; padding: 1rem; background: rgba(0,0,0,0.2); border-radius: 8px;"><h3 style="color: var(--accent-color); margin-bottom: 0.5rem;">Your Stats</h3><p>Games: ${stats.gamesPlayed} | Win Rate: ${stats.gamesPlayed > 0 ? Math.round((stats.wins / stats.gamesPlayed) * 100) : 0}%</p><p>Avg Game Length: ${stats.averageGameLength} moves</p></div>`;
            const overlay = document.querySelector('#game-over-overlay .overlay-content');
            const existing = overlay.querySelector('.stats-display');
            if (existing) existing.remove();
            const div = document.createElement('div');
            div.className = 'stats-display';
            div.innerHTML = statsHtml;
            overlay.appendChild(div);
        }

        // Show overlay
        setTimeout(() => {
            this.showOverlay('gameOver');
        }, 1000);
    }

    delay(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
    }
}

// Start app when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new KalahaApp();
});
