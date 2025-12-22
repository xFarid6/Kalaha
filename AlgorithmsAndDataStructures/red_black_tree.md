# Red-Black Tree

## Concept
A **Red-Black Tree** is a self-balancing BST that satisfies specific coloring properties to ensure the tree remains approximately balanced.

## Properties
1. **Color**: Each node is either Red or Black.
2. **Root**: The root is always Black.
3. **Leaves**: All leaves (NIL nodes) are Black.
4. **Red Property**: If a node is Red, both its children are Black (No two Reds in a row).
5. **Depth Property**: Every path from a node to any of its descendant NIL nodes contains the same number of Black nodes.

## Balancing
Violations are fixed using **Recoloring** and **Rotations**.
- **Insert**: New node is Red. Fix Red-Red conflicts.
- **Delete**: Complex cases involving double black nodes.

## Comparison with AVL
- **AVL**: Stricter balance, faster lookups. Slow updates (more rotations).
- **Red-Black**: Looser balance ($h \le 2 \log(n+1)$), faster updates (fewer rotations). Preferred in generic libraries (e.g., C++ std::map, Java TreeMap).
