/**
 * AI Engine - Minimax with Alpha-Beta Pruning
 * Ported from Python (kalaha/ai_engine.py)
 */

import {
    legalMoves,
    applyMove,
    isTerminal,
    evaluate,
    P1_STORE,
    P2_STORE,
    P1_PITS,
    P2_PITS
} from './game_logic.js';

// Constants
const MAX_DEPTH = 6;
const INF = Infinity;

// Transposition Table
const TT = new Map();

// Global counter
let NODES_VISITED = 0;

/**
 * Heuristic evaluation with multiple strategies
 */
export function evaluateHeuristic(board, player, strategy = 'balanced') {
    const storeDiff = board[P1_STORE] - board[P2_STORE];

    if (strategy === 'basic') {
        return storeDiff;
    }

    const p1SideSeeds = P1_PITS.reduce((sum, i) => sum + board[i], 0);
    const p2SideSeeds = P2_PITS.reduce((sum, i) => sum + board[i], 0);
    const sideDiff = p1SideSeeds - p2SideSeeds;

    let score = storeDiff;

    if (strategy === 'balanced') {
        score += 0.5 * sideDiff;
    } else if (strategy === 'defensive') {
        score += 0.8 * sideDiff;
        const emptyP1 = P1_PITS.filter(i => board[i] === 0).length;
        score -= 2.0 * emptyP1;
    } else if (strategy === 'aggressive') {
        score += 0.3 * sideDiff;
    }

    return score;
}

/**
 * Order moves for better Alpha-Beta pruning
 */
function orderMoves(board, moves, player) {
    const scored = moves.map(move => {
        const result = applyMove(board, move, player);
        const simBoard = result.board;
        const extraTurn = result.extraTurn;

        const scoreDiff = player === 0
            ? (simBoard[P1_STORE] - simBoard[P2_STORE])
            : (simBoard[P2_STORE] - simBoard[P1_STORE]);
        const prevDiff = player === 0
            ? (board[P1_STORE] - board[P2_STORE])
            : (board[P2_STORE] - board[P1_STORE]);

        const captured = (scoreDiff - prevDiff) > 1;

        let priority = 0;
        if (extraTurn) priority += 1000;
        if (captured) priority += 500;
        priority += Math.random();

        return { move, priority };
    });

    scored.sort((a, b) => b.priority - a.priority);
    return scored.map(s => s.move);
}

/**
 * Simple hash function for board state
 */
function hashBoard(board) {
    return board.join(',');
}

/**
 * Minimax with Alpha-Beta Pruning
 */
function alphabeta(board, depth, alpha, beta, maximizing, strategy = 'balanced') {
    NODES_VISITED++;

    // Check transposition table
    const hash = hashBoard(board);
    if (TT.has(hash)) {
        const cached = TT.get(hash);
        if (cached.depth >= depth) {
            if (cached.flag === 'EXACT') return cached.value;
            if (cached.flag === 'LOWER' && cached.value > alpha) alpha = cached.value;
            if (cached.flag === 'UPPER' && cached.value < beta) beta = cached.value;
            if (alpha >= beta) return cached.value;
        }
    }

    // Terminal or depth limit
    if (isTerminal(board) || depth === 0) {
        const value = evaluateHeuristic(board, 0, strategy);
        TT.set(hash, { value, depth, flag: 'EXACT' });
        return value;
    }

    const player = maximizing ? 0 : 1;
    const moves = legalMoves(board, player);

    if (moves.length === 0) {
        const value = evaluateHeuristic(board, 0, strategy);
        TT.set(hash, { value, depth, flag: 'EXACT' });
        return value;
    }

    const orderedMoves = orderMoves(board, moves, player);

    if (maximizing) {
        let maxEval = -INF;

        for (const move of orderedMoves) {
            const result = applyMove(board, move, player);
            const newBoard = result.board;
            const extraTurn = result.extraTurn;

            const evalScore = alphabeta(newBoard, depth - 1, alpha, beta, !extraTurn, strategy);
            maxEval = Math.max(maxEval, evalScore);
            alpha = Math.max(alpha, evalScore);

            if (beta <= alpha) break; // Beta cutoff
        }

        const flag = maxEval <= alpha ? 'UPPER' : (maxEval >= beta ? 'LOWER' : 'EXACT');
        TT.set(hash, { value: maxEval, depth, flag });

        return maxEval;
    } else {
        let minEval = INF;

        for (const move of orderedMoves) {
            const result = applyMove(board, move, player);
            const newBoard = result.board;
            const extraTurn = result.extraTurn;

            const evalScore = alphabeta(newBoard, depth - 1, alpha, beta, extraTurn, strategy);
            minEval = Math.min(minEval, evalScore);
            beta = Math.min(beta, evalScore);

            if (beta <= alpha) break; // Alpha cutoff
        }

        const flag = minEval <= alpha ? 'UPPER' : (minEval >= beta ? 'LOWER' : 'EXACT');
        TT.set(hash, { value: minEval, depth, flag });

        return minEval;
    }
}

/**
 * Get best move for AI
 */
export function getBestMove(board, player, depth = MAX_DEPTH, strategy = 'balanced') {
    NODES_VISITED = 0;
    TT.clear();

    const moves = legalMoves(board, player);

    if (moves.length === 0) {
        return { move: null, nodes: NODES_VISITED };
    }

    if (moves.length === 1) {
        return { move: moves[0], nodes: NODES_VISITED };
    }

    const orderedMoves = orderMoves(board, moves, player);
    let bestMove = orderedMoves[0];
    let bestValue = player === 0 ? -INF : INF;

    for (const move of orderedMoves) {
        const result = applyMove(board, move, player);
        const newBoard = result.board;
        const extraTurn = result.extraTurn;

        const maximizing = player === 0 ? !extraTurn : extraTurn;
        const value = alphabeta(newBoard, depth - 1, -INF, INF, maximizing, strategy);

        if (player === 0) {
            if (value > bestValue) {
                bestValue = value;
                bestMove = move;
            }
        } else {
            if (value < bestValue) {
                bestValue = value;
                bestMove = move;
            }
        }
    }

    return { move: bestMove, nodes: NODES_VISITED };
}

/**
 * Get difficulty settings
 */
export function getDifficultySettings(difficulty) {
    const settings = {
        'easy': { depth: 2, strategy: 'basic' },
        'medium': { depth: 6, strategy: 'balanced' },
        'hard': { depth: 10, strategy: 'aggressive' }
    };

    return settings[difficulty] || settings['medium'];
}
