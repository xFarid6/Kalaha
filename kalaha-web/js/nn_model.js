/**
 * Neural Network Model Interface (TensorFlow.js)
 * Provides interface for loading and using trained PyTorch models converted to TensorFlow.js
 */

// Model manager class
export class NeuralNetAI {
    constructor() {
        this.model = null;
        this.isLoaded = false;
        this.modelPath = 'models/kalaha_tfjs/model.json';
    }

    /**
     * Load the TensorFlow.js model
     */
    async loadModel() {
        if (this.isLoaded) {
            return true;
        }

        try {
            console.log(`Loading neural network model from ${this.modelPath}...`);

            // Check if TensorFlow.js is available
            if (typeof tf === 'undefined') {
                console.error('TensorFlow.js not loaded. Please include the TensorFlow.js script.');
                return false;
            }

            // Load model
            this.model = await tf.loadLayersModel(this.modelPath);
            this.isLoaded = true;

            console.log('✓ Neural network model loaded successfully');
            return true;

        } catch (error) {
            console.warn(`Could not load neural network model: ${error.message}`);
            console.warn('Falling back to Minimax AI');
            this.isLoaded = false;
            return false;
        }
    }

    /**
     * Get move prediction from neural network
     * @param {number[]} board - Current board state
     * @param {number} player - Current player (0 or 1)
     * @param {boolean[]} actionMask - Legal moves mask
     * @returns {number} - Pit index to play
     */
    async predict(board, player, actionMask) {
        if (!this.isLoaded) {
            throw new Error('Model not loaded. Call loadModel() first.');
        }

        // Prepare observation (canonical view)
        const obs = new Float32Array(15);

        if (player === 0) {
            // P1 view: [P1 pits, P1 store, P2 pits, P2 store, player]
            obs[0] = board[0]; obs[1] = board[1]; obs[2] = board[2];
            obs[3] = board[3]; obs[4] = board[4]; obs[5] = board[5];
            obs[6] = board[6];
            obs[7] = board[7]; obs[8] = board[8]; obs[9] = board[9];
            obs[10] = board[10]; obs[11] = board[11]; obs[12] = board[12];
            obs[13] = board[13];
            obs[14] = 0;
        } else {
            // P2 view: rotate board
            obs[0] = board[7]; obs[1] = board[8]; obs[2] = board[9];
            obs[3] = board[10]; obs[4] = board[11]; obs[5] = board[12];
            obs[6] = board[13];
            obs[7] = board[0]; obs[8] = board[1]; obs[9] = board[2];
            obs[10] = board[3]; obs[11] = board[4]; obs[12] = board[5];
            obs[13] = board[6];
            obs[14] = 1;
        }

        // Create tensor
        const inputTensor = tf.tensor2d([obs], [1, 15]);

        // Get prediction
        const prediction = this.model.predict(inputTensor);
        const policy = await prediction.data();

        // Clean up tensors
        inputTensor.dispose();
        prediction.dispose();

        // Apply action mask (zero out illegal moves)
        const maskedPolicy = new Float32Array(6);
        for (let i = 0; i < 6; i++) {
            maskedPolicy[i] = actionMask[i] ? policy[i] : -Infinity;
        }

        // Get best action
        let bestAction = 0;
        let bestValue = maskedPolicy[0];
        for (let i = 1; i < 6; i++) {
            if (maskedPolicy[i] > bestValue) {
                bestValue = maskedPolicy[i];
                bestAction = i;
            }
        }

        // Convert to board index
        return player === 0 ? bestAction : bestAction + 7;
    }

    /**
     * Get action mask for current player
     * @param {number[]} board - Current board state
     * @param {number} player - Current player (0 or 1)
     * @returns {boolean[]} - Mask of legal moves
     */
    getActionMask(board, player) {
        const mask = new Array(6).fill(false);
        const pits = player === 0
            ? [0, 1, 2, 3, 4, 5]
            : [7, 8, 9, 10, 11, 12];

        for (let i = 0; i < 6; i++) {
            if (board[pits[i]] > 0) {
                mask[i] = true;
            }
        }

        return mask;
    }
}

// Singleton instance
export const neuralNetAI = new NeuralNetAI();

/**
 * Try to load model on module import (optional)
 */
if (typeof window !== 'undefined') {
    // Attempt to load model when page is ready
    window.addEventListener('load', () => {
        neuralNetAI.loadModel().catch(err => {
            console.log('Neural network model not available, using Minimax AI');
        });
    });
}
