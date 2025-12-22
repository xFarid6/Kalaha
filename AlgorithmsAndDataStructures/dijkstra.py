import heapq

"""
Dijkstra's algorithm is a greedy algorithm that finds the shortest path from a source node to all other nodes in a graph.
It does this by maintaining a **priority queue** of nodes to visit and their current shortest distance from the source.
It then **visits the node with the smallest distance**, updates the distances of its neighbors, and adds them to the queue.
This process is repeated until all nodes are visited.
"""

def dijkstra(graph, start):
    # graph: {node: [(neighbor, weight), ...]}
    pq = [(0, start)]
    distances = {node: float('inf') for node in graph}
    distances[start] = 0
    visited = set()

    while pq:
        curr_dist, u = heapq.heappop(pq)

        if u in visited:
            continue
        visited.add(u)

        if curr_dist > distances[u]:
            continue

        for v, weight in graph[u]:
            dist = curr_dist + weight
            if dist < distances[v]:
                distances[v] = dist
                heapq.heappush(pq, (dist, v))
                
    return distances

if __name__ == "__main__":
    print("Testing Dijkstra...")
    g = {
        'A': [('B', 1), ('C', 4)],
        'B': [('A', 1), ('C', 2), ('D', 5)],
        'C': [('A', 4), ('B', 2), ('D', 1)],
        'D': [('B', 5), ('C', 1)]
    }
    
    dists = dijkstra(g, 'A')
    print(f"Shortest paths from A: {dists}")
    # A->B (1), A->C via B (1+2=3), A->D via C (3+1=4)
    assert dists['A'] == 0
    assert dists['B'] == 1
    assert dists['C'] == 3
    assert dists['D'] == 4
    print("Dijkstra Test Passed!")
