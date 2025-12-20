/**
 * UI Module - Board Rendering & Interaction (Canvas)
 * Handles all visual aspects of the game
 */

import {
    P1_PITS,
    P1_STORE,
    P2_PITS,
    P2_STORE,
    getSowingPath
} from './game_logic.js';

export class GameUI {
    constructor(canvas) {
        this.canvas = canvas;
        this.ctx = canvas.getContext('2d');
        this.board = null;
        this.currentPlayer = 0;
        this.legalMoves = [];
        this.animating = false;
        this.animationPath = [];
        this.animationIndex = 0;
        this.animationSpeed = 300; // ms per seed
        this.hoveredPit = null;

        // Colors (matching Python desktop app)
        this.colors = {
            bg: 'rgb(40, 26, 13)',
            pit: 'rgb(60, 40, 20)',
            pitHighlight: 'rgb(150, 100, 50)',
            seed: 'rgb(218, 165, 32)',
            text: 'rgb(245, 245, 220)',
            accent: 'rgb(218, 165, 32)',
            border: 'rgb(80, 50, 20)',
            storeBorder: 'rgb(90, 60, 30)'
        };

        // Layout
        this.pitPositions = [];
        this.storePositions = [];

        this.setupCanvas();
        this.setupEventListeners();
    }

    setupCanvas() {
        // Responsive canvas sizing
        const container = this.canvas.parentElement;
        const maxWidth = Math.min(container.clientWidth - 40, 1000);
        const maxHeight = Math.min(container.clientHeight - 40, 600);

        // Maintain aspect ratio (5:3)
        let width = maxWidth;
        let height = maxWidth * 0.6;

        if (height > maxHeight) {
            height = maxHeight;
            width = maxHeight / 0.6;
        }

        this.canvas.width = width;
        this.canvas.height = height;

        this.calculatePositions();
    }

    calculatePositions() {
        const w = this.canvas.width;
        const h = this.canvas.height;
        const padding = 40;

        // Pit dimensions
        const pitRadius = Math.min(w / 20, h / 7);
        const storeWidth = pitRadius * 2.5;
        const storeHeight = h * 0.7;

        // Store positions
        this.storePositions[P1_STORE] = {
            x: w - padding - storeWidth / 2,
            y: h / 2,
            width: storeWidth,
            height: storeHeight
        };

        this.storePositions[P2_STORE] = {
            x: padding + storeWidth / 2,
            y: h / 2,
            width: storeWidth,
            height: storeHeight
        };

        // Pit positions
        const availableWidth = w - (padding * 2 + storeWidth * 2 + 100);
        const pitSpacing = availableWidth / 7;
        const startX = padding + storeWidth + 50 + pitSpacing / 2;

        // P1 pits (bottom row, left to right)
        P1_PITS.forEach((pitIndex, i) => {
            this.pitPositions[pitIndex] = {
                x: startX + i * pitSpacing,
                y: h - padding - pitRadius * 2,
                radius: pitRadius
            };
        });

        // P2 pits (top row, right to left)
        P2_PITS.forEach((pitIndex, i) => {
            this.pitPositions[pitIndex] = {
                x: startX + (5 - i) * pitSpacing,
                y: padding + pitRadius * 2,
                radius: pitRadius
            };
        });
    }

    setupEventListeners() {
        this.canvas.addEventListener('click', (e) => this.handleClick(e));
        this.canvas.addEventListener('mousemove', (e) => this.handleMouseMove(e));
        this.canvas.addEventListener('mouseleave', () => {
            this.hoveredPit = null;
            if (!this.animating) this.draw();
        });

        window.addEventListener('resize', () => {
            this.setupCanvas();
            this.draw();
        });
    }

    handleClick(e) {
        if (this.animating || !this.onPitClick) return;

        const rect = this.canvas.getBoundingClientRect();
        const x = e.clientX - rect.left;
        const y = e.clientY - rect.top;

        const pitIndex = this.getPitAtPosition(x, y);
        if (pitIndex !== null && this.legalMoves.includes(pitIndex)) {
            this.onPitClick(pitIndex);
        }
    }

    handleMouseMove(e) {
        const rect = this.canvas.getBoundingClientRect();
        const x = e.clientX - rect.left;
        const y = e.clientY - rect.top;

        const pitIndex = this.getPitAtPosition(x, y);

        if (pitIndex !== this.hoveredPit) {
            this.hoveredPit = pitIndex;
            if (!this.animating) this.draw();
        }

        // Update cursor
        if (pitIndex !== null && this.legalMoves.includes(pitIndex)) {
            this.canvas.style.cursor = 'pointer';
        } else {
            this.canvas.style.cursor = 'default';
        }
    }

    getPitAtPosition(x, y) {
        // Check regular pits
        for (let i = 0; i < this.pitPositions.length; i++) {
            if (i === P1_STORE || i === P2_STORE) continue;

            const pos = this.pitPositions[i];
            const dx = x - pos.x;
            const dy = y - pos.y;
            if (Math.sqrt(dx * dx + dy * dy) <= pos.radius) {
                return i;
            }
        }

        return null;
    }

    updateBoard(board, currentPlayer, legalMoves) {
        this.board = board;
        this.currentPlayer = currentPlayer;
        this.legalMoves = legalMoves || [];
        this.draw();
    }

    draw() {
        if (!this.board) return;

        const ctx = this.ctx;
        const w = this.canvas.width;
        const h = this.canvas.height;

        // Clear canvas
        ctx.fillStyle = this.colors.bg;
        ctx.fillRect(0, 0, w, h);

        // Draw main board area
        ctx.fillStyle = this.colors.border;
        ctx.fillRect(20, 20, w - 40, h - 40);

        // Draw stores
        this.drawStore(P1_STORE, this.board[P1_STORE]);
        this.drawStore(P2_STORE, this.board[P2_STORE]);

        // Draw pits
        [...P1_PITS, ...P2_PITS].forEach(i => {
            this.drawPit(i, this.board[i]);
        });
    }

    drawPit(index, seeds) {
        const pos = this.pitPositions[index];
        const ctx = this.ctx;

        // Highlight logic
        const isLegal = this.legalMoves.includes(index);
        const isHovered = this.hoveredPit === index;
        const isAnimating = this.animationPath.includes(index);

        // Pit background
        ctx.fillStyle = isAnimating ? this.colors.pitHighlight : this.colors.pit;
        ctx.beginPath();
        ctx.arc(pos.x, pos.y, pos.radius, 0, Math.PI * 2);
        ctx.fill();

        // Pit border
        if (isLegal && isHovered) {
            ctx.strokeStyle = this.colors.accent;
            ctx.lineWidth = 4;
        } else if (isLegal) {
            ctx.strokeStyle = this.colors.accent;
            ctx.lineWidth = 2;
        } else {
            ctx.strokeStyle = this.colors.border;
            ctx.lineWidth = 2;
        }
        ctx.stroke();

        // Pit number label
        ctx.fillStyle = this.colors.text;
        ctx.font = `${pos.radius * 0.4}px sans-serif`;
        ctx.textAlign = 'center';
        ctx.textBaseline = 'top';
        const pitNum = index < 7 ? index + 1 : index - 6;
        ctx.fillText(pitNum, pos.x, pos.y + pos.radius + 8);

        // Draw seeds
        this.drawSeeds(pos.x, pos.y, pos.radius * 0.9, seeds);
    }

    drawStore(index, seeds) {
        const pos = this.storePositions[index];
        const ctx = this.ctx;

        // Store background
        ctx.fillStyle = this.colors.pit;
        ctx.fillRect(
            pos.x - pos.width / 2,
            pos.y - pos.height / 2,
            pos.width,
            pos.height
        );

        // Store border
        ctx.strokeStyle = this.colors.storeBorder;
        ctx.lineWidth = 3;
        ctx.strokeRect(
            pos.x - pos.width / 2,
            pos.y - pos.height / 2,
            pos.width,
            pos.height
        );

        // Store label
        ctx.fillStyle = this.colors.text;
        ctx.font = 'bold 18px sans-serif';
        ctx.textAlign = 'center';
        ctx.textBaseline = 'top';
        const label = index === P1_STORE ? 'P1' : 'P2';
        ctx.fillText(label, pos.x, pos.y + pos.height / 2 + 10);

        // Draw seeds
        this.drawSeeds(pos.x, pos.y, Math.min(pos.width, pos.height) * 0.4, seeds);
    }

    drawSeeds(x, y, maxRadius, count) {
        const ctx = this.ctx;

        if (count === 0) return;

        // Seed display logic
        ctx.fillStyle = this.colors.seed;
        ctx.font = 'bold 24px sans-serif';
        ctx.textAlign = 'center';
        ctx.textBaseline = 'middle';
        ctx.fillText(count, x, y);
    }

    async animateMove(board, move, player, animSpeed) {
        this.animating = true;
        this.animationSpeed = animSpeed;
        this.animationPath = getSowingPath(board, move, player);
        this.animationIndex = 0;

        // Animate each seed
        for (let i = 0; i < this.animationPath.length; i++) {
            this.animationIndex = i;
            this.draw();
            await this.delay(this.animationSpeed);
        }

        this.animating = false;
        this.animationPath = [];
        this.draw();
    }

    delay(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
    }

    setOnPitClick(callback) {
        this.onPitClick = callback;
    }

    setAnimationSpeed(speed) {
        this.animationSpeed = speed;
    }
}
