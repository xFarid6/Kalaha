# Fibonacci Heap

## Concept
A **Fibonacci Heap** is a collection of heap-ordered trees. It allows for faster amortized operations compared to binary heaps, particularly for **Decrease Key** and **Merge**.

## Key Properties
1. **Lazy**: Operations like insert and merge just add trees to the root list without consolidating immediately.
2. **Consolidation**: Trees are only consolidated (linked) during an **Extract Min** operation.
3. **Marking**: Nodes are marked if they lose a child. If a marked node loses another child, it is cut from its parent and moved to the root list (Cascading Cut).

## Time Complexity (Amortized)
- **Insert**: $O(1)$
- **Find Min**: $O(1)$
- **Union**: $O(1)$
- **Decrease Key**: $O(1)$
- **Extract Min**: $O(\log n)$
- **Delete**: $O(\log n)$

## Structure
- **Root List**: Doubly linked list of tree roots.
- **Min Pointer**: Points to the root with the minimum key.
- **Nodes**: Store pointers to parent, child, left, right, degree, and mark.
