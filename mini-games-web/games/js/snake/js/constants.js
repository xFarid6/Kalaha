/**
 * Snake - Constants
 * All game constants and configuration
 */

// Screen dimensions
export const SCREEN_WIDTH = 800;
export const SCREEN_HEIGHT = 600;
export const FPS = 10;

// Grid settings
export const GRID_SIZE = 20;
export const GRID_WIDTH = SCREEN_WIDTH / GRID_SIZE;
export const GRID_HEIGHT = SCREEN_HEIGHT / GRID_SIZE;

// Colors
export const BLACK = '#000000';
export const WHITE = '#FFFFFF';
export const PURPLE = '#9333ea';
export const PURPLE_LIGHT = '#a855f7';
export const GOLD = '#daa520';
export const GOLD_LIGHT = '#eeb934';
export const GREEN = '#059669';
export const GREEN_LIGHT = '#10b981';
export const RED = '#dc2626';

// Directions
export const UP = { x: 0, y: -1 };
export const DOWN = { x: 0, y: 1 };
export const LEFT = { x: -1, y: 0 };
export const RIGHT = { x: 1, y: 0 };

// Game settings
export const INITIAL_SNAKE_LENGTH = 3;
export const GROWTH_PER_FOOD = 1;
export const POINTS_PER_FOOD = 10;
