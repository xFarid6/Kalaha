/**
 * Snake - Main Game Loop
 * Entry point and game loop
 */

import * as C from './constants.js';
import { TitleScene } from './scenes.js';

class Game {
    constructor() {
        this.canvas = document.getElementById('game-canvas');
        this.ctx = this.canvas.getContext('2d');

        // Set canvas size
        this.canvas.width = C.SCREEN_WIDTH;
        this.canvas.height = C.SCREEN_HEIGHT;

        // Scene stack
        this.sceneStack = [];
        this.pushScene(new TitleScene(this));

        // Input tracking
        this.keys = {};
        this.setupInput();

        // Game loop timing
        this.lastTime = 0;
        this.accumulator = 0;
        this.fixedTimeStep = 1000 / C.FPS;  // ms per frame

        // Start game loop
        this.running = true;
        requestAnimationFrame((time) => this.gameLoop(time));
    }

    setupInput() {
        window.addEventListener('keydown', (e) => {
            this.keys[e.key] = true;
            // Prevent scrolling
            if (['ArrowUp', 'ArrowDown', 'ArrowLeft', 'ArrowRight', ' '].includes(e.key)) {
                e.preventDefault();
            }
        });

        window.addEventListener('keyup', (e) => {
            this.keys[e.key] = false;
        });
    }

    pushScene(scene) {
        this.sceneStack.push(scene);
    }

    popScene() {
        if (this.sceneStack.length > 1) {
            this.sceneStack.pop();
        }
    }

    gameLoop(currentTime) {
        if (!this.running || this.sceneStack.length === 0) {
            return;
        }

        // Calculate delta time
        const deltaTime = currentTime - this.lastTime;
        this.lastTime = currentTime;
        this.accumulator += deltaTime;

        // Fixed timestep updates
        while (this.accumulator >= this.fixedTimeStep) {
            const currentScene = this.sceneStack[this.sceneStack.length - 1];

            // Handle input
            currentScene.handleInput(this.keys);

            // Update
            currentScene.update(this.fixedTimeStep / 1000);

            this.accumulator -= this.fixedTimeStep;
        }

        // Render
        const currentScene = this.sceneStack[this.sceneStack.length - 1];
        currentScene.draw(this.ctx);

        // Continue loop
        requestAnimationFrame((time) => this.gameLoop(time));
    }
}

// Start game when page loads
document.addEventListener('DOMContentLoaded', () => {
    new Game();
});
