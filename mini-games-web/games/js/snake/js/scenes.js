/**
 * Snake - Game Scenes
 * Scene classes for different game states
 */

import * as C from './constants.js';
import { Snake, Food } from './entities.js';

export class Scene {
    constructor(game) {
        this.game = game;
    }

    handleInput(keys) { }
    update(dt) { }
    draw(ctx) { }
}

export class TitleScene extends Scene {
    constructor(game) {
        super(game);
        this.selected = 0;
        this.menuItems = ['Play', 'Quit'];
    }

    handleInput(keys) {
        if (keys['Enter']) {
            keys['Enter'] = false;  // Consume key
            if (this.selected === 0) {
                this.game.pushScene(new GameScene(this.game));
            } else {
                // Quit - reload page
                window.location.reload();
            }
        }
        if (keys['ArrowUp'] || keys['w']) {
            keys['Arrow Up'] = keys['w'] = false;
            this.selected = (this.selected - 1 + this.menuItems.length) % this.menuItems.length;
        }
        if (keys['ArrowDown'] || keys['s']) {
            keys['ArrowDown'] = keys['s'] = false;
            this.selected = (this.selected + 1) % this.menuItems.length;
        }
    }

    draw(ctx) {
        ctx.fillStyle = C.BLACK;
        ctx.fillRect(0, 0, C.SCREEN_WIDTH, C.SCREEN_HEIGHT);

        // Title
        ctx.fillStyle = C.GREEN_LIGHT;
        ctx.font = 'bold 80px Arial';
        ctx.textAlign = 'center';
        ctx.fillText('SNAKE', C.SCREEN_WIDTH / 2, 150);

        // Subtitle
        ctx.fillStyle = C.PURPLE_LIGHT;
        ctx.font = '24px Arial';
        ctx.fillText('Classic Arcade • Modern Style', C.SCREEN_WIDTH / 2, 200);

        // Menu
        this.menuItems.forEach((item, i) => {
            const y = 350 + i * 70;
            const color = i === this.selected ? C.GOLD_LIGHT : C.WHITE;

            ctx.fillStyle = color;
            ctx.font = 'bold 40px Arial';
            ctx.fillText(item, C.SCREEN_WIDTH / 2, y);

            // Selection box
            if (i === this.selected) {
                ctx.strokeStyle = C.PURPLE;
                ctx.lineWidth = 3;
                const metrics = ctx.measureText(item);
                ctx.strokeRect(
                    C.SCREEN_WIDTH / 2 - metrics.width / 2 - 10,
                    y - 35,
                    metrics.width + 20,
                    50
                );
            }
        });
    }
}

export class GameScene extends Scene {
    constructor(game) {
        super(game);
        this.snake = new Snake();
        this.food = new Food(this.snake);
        this.score = 0;
        this.paused = false;

        // Show score overlay
        document.getElementById('ui-overlay').classList.remove('hidden');
        document.getElementById('score').textContent = '0';
    }

    handleInput(keys) {
        if (keys['Escape']) {
            keys['Escape'] = false;
            this.game.popScene();
            document.getElementById('ui-overlay').classList.add('hidden');
        }
        if (keys[' ']) {
            keys[' '] = false;
            this.paused = !this.paused;
        }

        // Snake direction
        if (keys['ArrowUp'] || keys['w']) {
            this.snake.setDirection(C.UP);
        }
        if (keys['ArrowDown'] || keys['s']) {
            this.snake.setDirection(C.DOWN);
        }
        if (keys['ArrowLeft'] || keys['a']) {
            this.snake.setDirection(C.LEFT);
        }
        if (keys['ArrowRight'] || keys['d']) {
            this.snake.setDirection(C.RIGHT);
        }
    }

    update(dt) {
        if (this.paused) return;

        this.snake.update();

        // Check if ate food
        if (this.snake.getHead().equals(this.food.pos)) {
            this.snake.grow();
            this.food.respawn(this.snake);
            this.score += C.POINTS_PER_FOOD;
            document.getElementById('score').textContent = this.score;
        }

        // Check game over
        if (this.snake.checkSelfCollision() || this.snake.checkWallCollision()) {
            document.getElementById('ui-overlay').classList.add('hidden');
            this.game.pushScene(new GameOverScene(this.game, this.score));
        }
    }

    draw(ctx) {
        ctx.fillStyle = C.BLACK;
        ctx.fillRect(0, 0, C.SCREEN_WIDTH, C.SCREEN_HEIGHT);

        // Draw grid
        ctx.strokeStyle = '#1e1e1e';
        ctx.lineWidth = 1;
        for (let x = 0; x < C.SCREEN_WIDTH; x += C.GRID_SIZE) {
            ctx.beginPath();
            ctx.moveTo(x, 0);
            ctx.lineTo(x, C.SCREEN_HEIGHT);
            ctx.stroke();
        }
        for (let y = 0; y < C.SCREEN_HEIGHT; y += C.GRID_SIZE) {
            ctx.beginPath();
            ctx.moveTo(0, y);
            ctx.lineTo(C.SCREEN_WIDTH, y);
            ctx.stroke();
        }

        // Draw game entities
        this.food.draw(ctx);
        this.snake.draw(ctx);

        // Paused message
        if (this.paused) {
            ctx.fillStyle = 'rgba(0, 0, 0, 0.7)';
            ctx.fillRect(0, 0, C.SCREEN_WIDTH, C.SCREEN_HEIGHT);

            ctx.fillStyle = C.PURPLE_LIGHT;
            ctx.font = 'bold 48px Arial';
            ctx.textAlign = 'center';
            ctx.fillText('PAUSED', C.SCREEN_WIDTH / 2, C.SCREEN_HEIGHT / 2);
        }
    }
}

export class GameOverScene extends Scene {
    constructor(game, finalScore) {
        super(game);
        this.finalScore = finalScore;
        this.selected = 0;
        this.menuItems = ['Play Again', 'Main Menu'];
    }

    handleInput(keys) {
        if (keys['Enter']) {
            keys['Enter'] = false;
            if (this.selected === 0) {
                this.game.popScene();  // Remove game over
                this.game.popScene();  // Remove old game
                this.game.pushScene(new GameScene(this.game));  // New game
            } else {
                this.game.popScene();  // Remove game over
                this.game.popScene();  // Remove old game
            }
        }
        if (keys['ArrowUp'] || keys['w']) {
            keys['ArrowUp'] = keys['w'] = false;
            this.selected = (this.selected - 1 + this.menuItems.length) % this.menuItems.length;
        }
        if (keys['ArrowDown'] || keys['s']) {
            keys['ArrowDown'] = keys['s'] = false;
            this.selected = (this.selected + 1) % this.menuItems.length;
        }
    }

    draw(ctx) {
        ctx.fillStyle = C.BLACK;
        ctx.fillRect(0, 0, C.SCREEN_WIDTH, C.SCREEN_HEIGHT);

        // Game Over
        ctx.fillStyle = C.RED;
        ctx.font = 'bold 64px Arial';
        ctx.textAlign = 'center';
        ctx.fillText('GAME OVER', C.SCREEN_WIDTH / 2, 150);

        // Score
        ctx.fillStyle = C.GOLD_LIGHT;
        ctx.font = 'bold 48px Arial';
        ctx.fillText(`Score: ${this.finalScore}`, C.SCREEN_WIDTH / 2, 230);

        // Menu
        this.menuItems.forEach((item, i) => {
            const y = 360 + i * 60;
            const color = i === this.selected ? C.GREEN_LIGHT : C.WHITE;

            ctx.fillStyle = color;
            ctx.font = 'bold 32px Arial';
            ctx.fillText(item, C.SCREEN_WIDTH / 2, y);

            if (i === this.selected) {
                ctx.strokeStyle = C.PURPLE;
                ctx.lineWidth = 3;
                const metrics = ctx.measureText(item);
                ctx.strokeRect(
                    C.SCREEN_WIDTH / 2 - metrics.width / 2 - 10,
                    y - 30,
                    metrics.width + 20,
                    45
                );
            }
        });
    }
}
