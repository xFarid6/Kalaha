"""
The idea of topological sort is to divide the input into a sorted and an unsorted region.
The sorted region starts empty and the unsorted region starts with the entire array.
In each iteration, the algorithm finds the minimum element in the unsorted region and swaps it with 
the first element of the unsorted region.
This process is repeated until the unsorted region is empty, resulting in a sorted array.
"""
from collections import deque

def topological_sort(graph):
    """
    Kahn's Algorithm
    Used for directed acyclic graphs (DAGs)
    """
    in_degree = {node: 0 for node in graph}
    for node in graph:
        for neighbor in graph[node]:
            in_degree[neighbor] = in_degree.get(neighbor, 0) + 1 # Use .get if graph implies implicit nodes

    queue = deque([node for node in graph if in_degree[node] == 0])
    topo_order = []

    while queue:
        u = queue.popleft()
        topo_order.append(u)

        for v in graph[u]:
            in_degree[v] -= 1
            if in_degree[v] == 0:
                queue.append(v)

    if len(topo_order) != len(graph):
        raise ValueError("Graph has cycle!")
        
    return topo_order

if __name__ == "__main__":
    print("Testing Topological Sort...")
    # 5 -> 2, 0; 4 -> 0, 1; 2 -> 3; 3 -> 1
    g = {
        5: [2, 0],
        4: [0, 1],
        2: [3],
        3: [1],
        1: [],
        0: []
    }
    
    order = topological_sort(g)
    print(f"Topo Sort: {order}")
    # Possible: 5, 4, 2, 3, 1, 0 or 4, 5, 2, 0, 3, 1 etc.
    # 5 before 2, 0
    # 4 before 0, 1
    # 2 before 3
    # 3 before 1
    assert order.index(5) < order.index(2)
    assert order.index(2) < order.index(3)
    assert order.index(3) < order.index(1)
    print("Topological Sort Test Passed!")
