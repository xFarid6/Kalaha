/**
 * Test Suite for Kalaha Game Logic
 * Validates parity between JavaScript and Python implementations
 */

import {
    initialState,
    legalMoves,
    isTerminal,
    evaluate,
    cleanupBoard,
    applyMove,
    getSowingPath,
    P1_PITS,
    P1_STORE,
    P2_PITS,
    P2_STORE
} from './game_logic.js';

// Simple test framework
class TestRunner {
    constructor() {
        this.passed = 0;
        this.failed = 0;
        this.tests = [];
    }

    test(name, fn) {
        this.tests.push({ name, fn });
    }

    run() {
        console.log('🧪 Running Kalaha Game Logic Tests\n');
        console.log('='.repeat(60));

        this.tests.forEach(({ name, fn }) => {
            try {
                fn();
                this.passed++;
                console.log(`✓ ${name}`);
            } catch (error) {
                this.failed++;
                console.log(`✗ ${name}`);
                console.log(`  Error: ${error.message}`);
            }
        });

        console.log('='.repeat(60));
        console.log(`\nResults: ${this.passed} passed, ${this.failed} failed`);

        if (this.failed === 0) {
            console.log('🎉 All tests passed!');
        } else {
            console.log('❌ Some tests failed');
        }

        return this.failed === 0;
    }
}

function assert(condition, message) {
    if (!condition) {
        throw new Error(message || 'Assertion failed');
    }
}

function arrayEqual(a, b) {
    return a.length === b.length && a.every((val, i) => val === b[i]);
}

// Test Suite
const runner = new TestRunner();

runner.test('Initial state creates correct board', () => {
    const board = initialState();
    assert(board.length === 14, 'Board should have 14 pits');
    assert(board[P1_STORE] === 0, 'P1 store should be empty');
    assert(board[P2_STORE] === 0, 'P2 store should be empty');
    P1_PITS.forEach(i => {
        assert(board[i] === 6, `P1 pit ${i} should have 6 seeds`);
    });
    P2_PITS.forEach(i => {
        assert(board[i] === 6, `P2 pit ${i} should have 6 seeds`);
    });
});

runner.test('Legal moves returns correct pits for P1', () => {
    const board = initialState();
    const moves = legalMoves(board, 0);
    assert(arrayEqual(moves, [0, 1, 2, 3, 4, 5]), 'All P1 pits should be legal');
});

runner.test('Legal moves excludes empty pits', () => {
    const board = [0, 6, 0, 6, 0, 6, 0, 6, 6, 6, 6, 6, 6, 0];
    const moves = legalMoves(board, 0);
    assert(arrayEqual(moves, [1, 3, 5]), 'Only non-empty pits should be legal');
});

runner.test('Terminal state detection works', () => {
    const activeBoard = initialState();
    assert(!isTerminal(activeBoard), 'Initial board should not be terminal');

    const endBoard = [0, 0, 0, 0, 0, 0, 24, 6, 6, 6, 6, 6, 6, 24];
    assert(isTerminal(endBoard), 'Board with empty P1 side should be terminal');
});

runner.test('Evaluate returns correct score difference', () => {
    const board = [0, 0, 0, 0, 0, 0, 30, 0, 0, 0, 0, 0, 0, 18];
    const score = evaluate(board);
    assert(score === 12, 'Score should be P1 - P2 = 30 - 18 = 12');
});

runner.test('Cleanup board collects remaining seeds', () => {
    const board = [2, 3, 0, 1, 0, 0, 20, 0, 4, 0, 2, 1, 0, 15];
    const cleaned = cleanupBoard(board);

    assert(cleaned[P1_STORE] === 26, 'P1 store should have 20 + 6 = 26');
    assert(cleaned[P2_STORE] === 22, 'P2 store should have 15 + 7 = 22');

    P1_PITS.forEach(i => {
        assert(cleaned[i] === 0, `P1 pit ${i} should be empty`);
    });
    P2_PITS.forEach(i => {
        assert(cleaned[i] === 0, `P2 pit ${i} should be empty`);
    });
});

runner.test('Apply move distributes seeds correctly', () => {
    const board = initialState();
    const result = applyMove(board, 0, 0);

    const expected = [0, 7, 7, 7, 7, 7, 1, 6, 6, 6, 6, 6, 6, 0];
    assert(arrayEqual(result.board, expected), 'Seeds should distribute correctly');
    assert(result.extraTurn === true, 'Landing in own store gives extra turn');
});

runner.test('Apply move handles capture', () => {
    const board = [4, 0, 0, 0, 0, 0, 10, 6, 6, 6, 6, 6, 6, 10];
    const result = applyMove(board, 0, 0);

    // Lands in pit 4 (empty), captures opposite pit 8
    assert(result.board[4] === 0, 'Landing pit should be empty after capture');
    assert(result.board[8] === 0, 'Opposite pit should be empty');
    assert(result.board[P1_STORE] === 10 + 6 + 1, 'Store should receive captured seeds');
});

runner.test('Apply move skips opponent store', () => {
    const board = [0, 0, 0, 0, 0, 10, 0, 6, 6, 6, 6, 6, 6, 0];
    const result = applyMove(board, 5, 0);

    // 10 seeds from pit 5: should go to pits 6,7,8,9,10,11,12,0,1,2
    // Pit 13 (P2 store) should be skipped
    assert(result.board[P2_STORE] === 0, 'P2 store should not receive seeds from P1');
});

runner.test('Sowing path returns correct sequence', () => {
    const board = initialState();
    const path = getSowingPath(board, 0, 0);

    const expected = [1, 2, 3, 4, 5, 6];
    assert(arrayEqual(path, expected), 'Path should skip opponent store');
});

runner.test('Integration: Play through a short game', () => {
    let board = initialState();
    let player = 0;
    let moveCount = 0;
    const maxMoves = 100;

    while (!isTerminal(board) && moveCount < maxMoves) {
        const moves = legalMoves(board, player);
        if (moves.length === 0) break;

        const move = moves[0]; // Always pick first legal move
        const result = applyMove(board, move, player);
        board = result.board;

        if (!result.extraTurn) {
            player = 1 - player;
        }

        moveCount++;
    }

    board = cleanupBoard(board);
    const totalSeeds = board[P1_STORE] + board[P2_STORE];

    assert(totalSeeds === 72, 'All seeds should be accounted for (6*12 = 72)');
    assert(isTerminal(board), 'Game should be terminal');
});

// Run all tests
const success = runner.run();
if (!success) {
    process.exit(1);
}
