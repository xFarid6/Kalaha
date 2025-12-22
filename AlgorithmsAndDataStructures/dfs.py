def dfs(graph, start, visited=None, order=None):
    if visited is None:
        visited = set()
    if order is None:
        order = []

    visited.add(start)
    order.append(start)

    for neighbor in graph[start]:
        if neighbor not in visited:
            dfs(graph, neighbor, visited, order)
    return order

if __name__ == "__main__":
    print("Testing DFS...")
    g = {
        0: [1, 2],
        1: [2],
        2: [0, 3],
        3: []
    }
    
    order = dfs(g, 2)
    print(f"DFS from 2: {order}")
    # 2 -> 0 -> 1 -> 2(skip)
    # Then 2 -> 3
    # Order: 2, 0, 1, 3
    assert order == [2, 0, 1, 3]
    print("DFS Test Passed!")
