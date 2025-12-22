import heapq

"""
Prims is a greedy algorithm that finds the minimum spanning tree (MST) of a graph.
It does this by starting at a random node and adding the smallest edge to the tree.
It then adds the smallest edge to the tree that connects a node in the tree to a node not in the tree.
This process is repeated until all nodes are in the tree.
"""

def prim_mst(graph, start_node):
    # graph: {node: [(neighbor, weight), ...]}
    mst_cost = 0
    mst_edges = []
    visited = set()
    
    # Priority Queue: (weight, from_node, to_node)
    pq = [(0, start_node, start_node)] # Dummy start edge
    
    count = 0
    n = len(graph)
    
    while pq and count < n:
        weight, u, v = heapq.heappop(pq)
        
        if v in visited:
            continue
            
        visited.add(v)
        mst_cost += weight
        if u != v:
            mst_edges.append((u, v, weight))
        count += 1
        
        for neighbor, w in graph[v]:
            if neighbor not in visited:
                heapq.heappush(pq, (w, v, neighbor))
                
    return mst_cost, mst_edges

if __name__ == "__main__":
    print("Testing Prim's MST...")
    g = {
        'A': [('B', 1), ('C', 3)],
        'B': [('A', 1), ('C', 1), ('D', 4)],
        'C': [('A', 3), ('B', 1), ('D', 2)],
        'D': [('B', 4), ('C', 2)]
    }
    
    cost, edges = prim_mst(g, 'A')
    print(f"MST Cost: {cost}")
    print(f"MST Edges: {edges}")
    # Edges: (A,B,1), (B,C,1), (C,D,2) -> Cost 4
    assert cost == 4
    print("Prim's Test Passed!")
