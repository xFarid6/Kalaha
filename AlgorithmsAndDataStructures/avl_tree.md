# AVL Tree (Adelson-Velsky and Landis)

## Concept
An **AVL Tree** is a self-balancing Binary Search Tree (BST). It ensures that for every node, the height difference between left and right subtrees (Balance Factor) is at most 1.

$$ \text{BalanceFactor}(node) = \text{Height}(node.left) - \text{Height}(node.right) $$

## Invariant
- `abs(BalanceFactor) <= 1` for all nodes.

## Rotations
To restore balance after Insert/Delete:

1. **Left Rotation (LL Case)**: Right child heavy.
2. **Right Rotation (RR Case)**: Left child heavy.
3. **Left-Right Rotation (LR Case)**: Left child has heavy right subtree.
4. **Right-Left Rotation (RL Case)**: Right child has heavy left subtree.

## Complexity
- **Search**: $O(\log n)$
- **Insert**: $O(\log n)$
- **Delete**: $O(\log n)$
- Strictly balanced (Height $\approx 1.44 \log_2 n$).
