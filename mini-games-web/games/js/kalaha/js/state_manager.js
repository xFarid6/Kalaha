/**
 * Game State Manager
 * Handles localStorage persistence, undo/redo, and stats tracking
 */

export class GameStateManager {
    constructor() {
        this.STORAGE_KEY = 'kalaha_game_state';
        this.STATS_KEY = 'kalaha_stats';
        this.HISTORY_KEY = 'kalaha_move_history';
        this.maxUndoSteps = 20;
    }

    /**
     * Save current game state to localStorage
     */
    saveGame(gameState) {
        try {
            const saveData = {
                board: gameState.board,
                currentPlayer: gameState.currentPlayer,
                opponent: gameState.opponent,
                difficulty: gameState.difficulty,
                timestamp: Date.now()
            };

            localStorage.setItem(this.STORAGE_KEY, JSON.stringify(saveData));
            return true;
        } catch (error) {
            console.error('Failed to save game:', error);
            return false;
        }
    }

    /**
     * Load saved game from localStorage
     */
    loadGame() {
        try {
            const data = localStorage.getItem(this.STORAGE_KEY);
            if (!data) return null;

            const saveData = JSON.parse(data);

            // Check if save is recent (within 7 days)
            const daysSinceLastSave = (Date.now() - saveData.timestamp) / (1000 * 60 * 60 * 24);
            if (daysSinceLastSave > 7) {
                this.clearSavedGame();
                return null;
            }

            return saveData;
        } catch (error) {
            console.error('Failed to load game:', error);
            return null;
        }
    }

    /**
     * Check if there's a saved game
     */
    hasSavedGame() {
        return localStorage.getItem(this.STORAGE_KEY) !== null;
    }

    /**
     * Clear saved game
     */
    clearSavedGame() {
        localStorage.removeItem(this.STORAGE_KEY);
        localStorage.removeItem(this.HISTORY_KEY);
    }

    /**
     * Save move history for undo/redo
     */
    saveMoveHistory(history) {
        try {
            localStorage.setItem(this.HISTORY_KEY, JSON.stringify(history));
            return true;
        } catch (error) {
            console.error('Failed to save move history:', error);
            return false;
        }
    }

    /**
     * Load move history
     */
    loadMoveHistory() {
        try {
            const data = localStorage.getItem(this.HISTORY_KEY);
            return data ? JSON.parse(data) : [];
        } catch (error) {
            console.error('Failed to load move history:', error);
            return [];
        }
    }

    /**
     * Get game statistics
     */
    getStats() {
        try {
            const data = localStorage.getItem(this.STATS_KEY);
            if (!data) {
                return {
                    gamesPlayed: 0,
                    wins: 0,
                    losses: 0,
                    draws: 0,
                    vsAI: { wins: 0, losses: 0, draws: 0 },
                    vsHuman: { wins: 0, losses: 0, draws: 0 },
                    byDifficulty: {
                        easy: { wins: 0, losses: 0 },
                        medium: { wins: 0, losses: 0 },
                        hard: { wins: 0, losses: 0 }
                    },
                    totalMoves: 0,
                    averageGameLength: 0
                };
            }
            return JSON.parse(data);
        } catch (error) {
            console.error('Failed to load stats:', error);
            return null;
        }
    }

    /**
     * Update statistics after game
     */
    updateStats(gameResult) {
        const stats = this.getStats();
        if (!stats) return;

        stats.gamesPlayed++;

        // Update overall record
        if (gameResult.winner === 0) {
            stats.wins++;
        } else if (gameResult.winner === 1) {
            stats.losses++;
        } else {
            stats.draws++;
        }

        // Update opponent-specific stats
        const opponentType = gameResult.opponent === 'ai' ? 'vsAI' : 'vsHuman';
        if (gameResult.winner === 0) {
            stats[opponentType].wins++;
        } else if (gameResult.winner === 1) {
            stats[opponentType].losses++;
        } else {
            stats[opponentType].draws++;
        }

        // Update difficulty-specific stats (if vs AI)
        if (gameResult.opponent === 'ai' && gameResult.difficulty) {
            const diff = gameResult.difficulty;
            if (gameResult.winner === 0) {
                stats.byDifficulty[diff].wins++;
            } else if (gameResult.winner === 1) {
                stats.byDifficulty[diff].losses++;
            }
        }

        // Update average game length
        stats.totalMoves += gameResult.moveCount;
        stats.averageGameLength = Math.round(stats.totalMoves / stats.gamesPlayed);

        // Save updated stats
        try {
            localStorage.setItem(this.STATS_KEY, JSON.stringify(stats));
        } catch (error) {
            console.error('Failed to save stats:', error);
        }
    }

    /**
     * Reset all statistics
     */
    resetStats() {
        localStorage.removeItem(this.STATS_KEY);
    }

    /**
     * Export stats as JSON
     */
    exportStats() {
        const stats = this.getStats();
        const blob = new Blob([JSON.stringify(stats, null, 2)], { type: 'application/json' });
        const url = URL.createObjectURL(blob);

        const a = document.createElement('a');
        a.href = url;
        a.download = `kalaha_stats_${Date.now()}.json`;
        a.click();

        URL.revokeObjectURL(url);
    }
}

// Singleton instance
export const gameStateManager = new GameStateManager();
