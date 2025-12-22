# Heaps (Min & Max)

## Concept
A **Binary Heap** is a complete binary tree which satisfies the heap property:
- **Min Heap**: The value of each node is greater than or equal to the value of its parent. The minimum element is at the root.
- **Max Heap**: The value of each node is less than or equal to the value of its parent. The maximum element is at the root.

## Implementation (Array)
Heaps are typically implemented as arrays for cache efficiency.
For a node at index `i`:
- **Parent**: `(i - 1) // 2`
- **Left Child**: `2 * i + 1`
- **Right Child**: `2 * i + 2`

## Operations

### Insert $O(\log n)$
1. Add element to the end of the array.
2. **Bubble Up**: Swap with parent until the heap property is restored.

### Extract Root $O(\log n)$
1. Remove root (index 0).
2. Move last element to root.
3. **Bubble Down**: Swap with smallest (MinHeap) or largest (MaxHeap) child until heap property is restored.

### Peek $O(1)$
- Return element at index 0.
