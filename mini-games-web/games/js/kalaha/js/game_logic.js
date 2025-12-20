/**
 * Kalaha Game Logic (JavaScript Port)
 * Ported from Python implementation in kalaha/game_logic.py
 */

// Constants
const P1_PITS = [0, 1, 2, 3, 4, 5];
const P1_STORE = 6;
const P2_PITS = [7, 8, 9, 10, 11, 12];
const P2_STORE = 13;
const TOTAL_PITS = 14;
const SEEDS_PER_PIT = 6;

/**
 * Create initial board state
 * @returns {number[]} Array of 14 integers representing the board
 */
export function initialState() {
    const board = new Array(TOTAL_PITS).fill(0);
    [...P1_PITS, ...P2_PITS].forEach(i => {
        board[i] = SEEDS_PER_PIT;
    });
    return board;
}

/**
 * Get legal moves for the current player
 * @param {number[]} board - Current board state
 * @param {number} player - Current player (0 or 1)
 * @returns {number[]} Array of valid pit indices
 */
export function legalMoves(board, player) {
    const pits = player === 0 ? P1_PITS : P2_PITS;
    return pits.filter(i => board[i] > 0);
}

/**
 * Check if the game is over
 * @param {number[]} board - Current board state
 * @returns {boolean} True if game is over
 */
export function isTerminal(board) {
    const p1Empty = P1_PITS.every(i => board[i] === 0);
    const p2Empty = P2_PITS.every(i => board[i] === 0);
    return p1Empty || p2Empty;
}

/**
 * Evaluate board from P1 perspective
 * @param {number[]} board - Current board state
 * @returns {number} Score difference (P1 - P2)
 */
export function evaluate(board) {
    return board[P1_STORE] - board[P2_STORE];
}

/**
 * Clean up board at game end (collect remaining seeds)
 * @param {number[]} board - Current board state
 * @returns {number[]} Cleaned board
 */
export function cleanupBoard(board) {
    const newBoard = [...board];

    // Collect P1 remaining seeds
    P1_PITS.forEach(i => {
        newBoard[P1_STORE] += newBoard[i];
        newBoard[i] = 0;
    });

    // Collect P2 remaining seeds
    P2_PITS.forEach(i => {
        newBoard[P2_STORE] += newBoard[i];
        newBoard[i] = 0;
    });

    return newBoard;
}

/**
 * Apply a move to the board
 * @param {number[]} board - Current board state
 * @param {number} move - Pit index to play
 * @param {number} player - Current player (0 or 1)
 * @returns {{board: number[], extraTurn: boolean}} New board state and extra turn flag
 */
export function applyMove(board, move, player) {
    const newBoard = [...board];
    let seeds = newBoard[move];
    newBoard[move] = 0;

    let currentIdx = move;

    // Distribute seeds
    while (seeds > 0) {
        currentIdx = (currentIdx + 1) % TOTAL_PITS;

        // Skip opponent's store
        if (player === 0 && currentIdx === P2_STORE) continue;
        if (player === 1 && currentIdx === P1_STORE) continue;

        newBoard[currentIdx]++;
        seeds--;
    }

    // Check for extra turn
    if (player === 0 && currentIdx === P1_STORE) {
        return { board: newBoard, extraTurn: true };
    }
    if (player === 1 && currentIdx === P2_STORE) {
        return { board: newBoard, extraTurn: true };
    }

    // Check for capture
    const wasEmpty = newBoard[currentIdx] === 1;

    if (wasEmpty) {
        if (player === 0 && P1_PITS.includes(currentIdx)) {
            const oppositeIdx = 12 - currentIdx;
            if (newBoard[oppositeIdx] > 0) {
                const capturedSeeds = newBoard[oppositeIdx] + 1;
                newBoard[P1_STORE] += capturedSeeds;
                newBoard[currentIdx] = 0;
                newBoard[oppositeIdx] = 0;
            }
        } else if (player === 1 && P2_PITS.includes(currentIdx)) {
            const oppositeIdx = 12 - currentIdx;
            if (newBoard[oppositeIdx] > 0) {
                const capturedSeeds = newBoard[oppositeIdx] + 1;
                newBoard[P2_STORE] += capturedSeeds;
                newBoard[currentIdx] = 0;
                newBoard[oppositeIdx] = 0;
            }
        }
    }

    return { board: newBoard, extraTurn: false };
}

/**
 * Get the sowing path (for animations)
 * @param {number[]} board - Current board state
 * @param {number} move - Pit index to play
 * @param {number} player - Current player (0 or 1)
 * @returns {number[]} Array of pit indices that receive seeds
 */
export function getSowingPath(board, move, player) {
    const path = [];
    let seeds = board[move];
    let currentIdx = move;

    while (seeds > 0) {
        currentIdx = (currentIdx + 1) % TOTAL_PITS;

        // Skip opponent's store
        if (player === 0 && currentIdx === P2_STORE) continue;
        if (player === 1 && currentIdx === P1_STORE) continue;

        path.push(currentIdx);
        seeds--;
    }

    return path;
}

// Export constants for use in other modules
export {
    P1_PITS,
    P1_STORE,
    P2_PITS,
    P2_STORE,
    TOTAL_PITS,
    SEEDS_PER_PIT
};
