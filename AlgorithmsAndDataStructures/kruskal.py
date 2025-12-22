class UnionFind:
    def __init__(self, elements):
        self.parent = {e: e for e in elements}
        self.rank = {e: 0 for e in elements}

    def find(self, i):
        if self.parent[i] != i:
            self.parent[i] = self.find(self.parent[i]) # Path compression
        return self.parent[i]

    def union(self, i, j):
        root_i = self.find(i)
        root_j = self.find(j)

        if root_i != root_j:
            if self.rank[root_i] > self.rank[root_j]:
                self.parent[root_j] = root_i
            else:
                self.parent[root_i] = root_j
                if self.rank[root_i] == self.rank[root_j]:
                    self.rank[root_j] += 1
            return True
        return False

def kruskal_mst(graph):
    # graph: list of (u, v, weight)
    # Extract unique nodes
    nodes = set()
    for u, v, w in graph:
        nodes.add(u)
        nodes.add(v)
        
    uf = UnionFind(nodes)
    mst_cost = 0
    mst_edges = []
    
    # Sort edges by weight
    sorted_edges = sorted(graph, key=lambda x: x[2])
    
    for u, v, w in sorted_edges:
        if uf.union(u, v):
            mst_cost += w
            mst_edges.append((u, v, w))
            
    return mst_cost, mst_edges

if __name__ == "__main__":
    print("Testing Kruskal's MST...")
    edges = [
        ('A', 'B', 1),
        ('A', 'C', 3),
        ('B', 'C', 1),
        ('B', 'D', 4),
        ('C', 'D', 2)
    ]
    
    cost, m_edges = kruskal_mst(edges)
    print(f"MST Cost: {cost}")
    print(f"MST Edges: {m_edges}")
    # (A,B,1), (B,C,1), (C,D,2) -> Cost 4
    assert cost == 4
    print("Kruskal's Test Passed!")
