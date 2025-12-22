from collections import deque

def bfs(graph, start):
    visited = set()
    queue = deque([start])
    visited.add(start)
    order = []

    while queue:
        vertex = queue.popleft()
        order.append(vertex)

        for neighbor in graph[vertex]:
            if neighbor not in visited:
                visited.add(neighbor)
                queue.append(neighbor)
    return order

if __name__ == "__main__":
    print("Testing BFS...")
    # Graph: 0 -> 1, 2; 1 -> 2; 2 -> 0, 3; 3 -> 3
    g = {
        0: [1, 2],
        1: [2],
        2: [0, 3],
        3: [] # 3 self loop removed for simple list
    }
    
    order = bfs(g, 2)
    print(f"BFS from 2: {order}")
    # 2 -> 0, 3 -> 1 (via 0)
    assert order == [2, 0, 3, 1] or order == [2, 3, 0, 1]
    print("BFS Test Passed!")
