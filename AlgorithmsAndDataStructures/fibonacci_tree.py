import math

class FibonacciHeap:
    class Node:
        def __init__(self, key):
            self.key = key
            self.parent = None
            self.child = None
            self.left = self
            self.right = self
            self.degree = 0
            self.mark = False

    def __init__(self):
        self.min_node = None
        self.total_nodes = 0

    def insert(self, key):
        node = self.Node(key)
        if self.min_node:
            self._add_to_root_list(node)
            if node.key < self.min_node.key:
                self.min_node = node
        else:
            self.min_node = node
        self.total_nodes += 1
        return node

    def find_min(self):
        return self.min_node.key if self.min_node else None

    def extract_min(self):
        z = self.min_node
        if z:
            if z.child:
                # Add children to root list
                children = []
                curr = z.child
                while True:
                    children.append(curr)
                    curr = curr.right
                    if curr == z.child:
                        break
                
                for kid in children:
                    self._add_to_root_list(kid)
                    kid.parent = None
            
            self._remove_from_root_list(z)
            
            if z == z.right:
                self.min_node = None
            else:
                self.min_node = z.right
                self._consolidate()
            
            self.total_nodes -= 1
            return z.key
        return None

    def decrease_key(self, x, k):
        if k > x.key:
            raise ValueError("New key > current key")
        x.key = k
        y = x.parent
        if y and x.key < y.key:
            self._cut(x, y)
            self._cascading_cut(y)
        if x.key < self.min_node.key:
            self.min_node = x

    def _add_to_root_list(self, node):
        if not self.min_node:
            node.left = node
            node.right = node
            self.min_node = node
        else:
            node.right = self.min_node.right
            node.left = self.min_node
            self.min_node.right.left = node
            self.min_node.right = node

    def _remove_from_root_list(self, node):
        node.left.right = node.right
        node.right.left = node.left

    def _consolidate(self):
        max_degree = int(math.log(self.total_nodes, (1 + math.sqrt(5))/2)) + 1
        A = [None] * (max_degree + 1)
        
        # Iterate root list
        roots = []
        curr = self.min_node
        if not curr: return
        while True:
            roots.append(curr)
            curr = curr.right
            if curr == self.min_node:
                break
                
        for w in roots:
            x = w
            d = x.degree
            while A[d]:
                y = A[d]
                if x.key > y.key:
                    x, y = y, x
                self._link(y, x)
                A[d] = None
                d += 1
            A[d] = x
            
        self.min_node = None
        for i in range(len(A)):
            if A[i]:
                if not self.min_node:
                    self.min_node = A[i]
                    self.min_node.left = self.min_node
                    self.min_node.right = self.min_node
                else:
                    self._add_to_root_list(A[i])
                    if A[i].key < self.min_node.key:
                        self.min_node = A[i]

    def _link(self, y, x):
        self._remove_from_root_list(y)
        y.parent = x
        if not x.child:
            x.child = y
            y.right = y
            y.left = y
        else:
            y.left = x.child
            y.right = x.child.right
            x.child.right.left = y
            x.child.right = y
        x.degree += 1
        y.mark = False

    def _cut(self, x, y):
        self._remove_from_child_list(y, x)
        y.degree -= 1
        self._add_to_root_list(x)
        x.parent = None
        x.mark = False

    def _cascading_cut(self, y):
        z = y.parent
        if z:
            if not y.mark:
                y.mark = True
            else:
                self._cut(y, z)
                self._cascading_cut(z)

    def _remove_from_child_list(self, parent, node):
        if parent.child == parent.child.right:
            parent.child = None
        elif parent.child == node:
            parent.child = node.right
            node.right.parent = parent
        
        node.left.right = node.right
        node.right.left = node.left

if __name__ == "__main__":
    print("Testing Fibonacci Heap...")
    fh = FibonacciHeap()
    nodes = []
    
    # Insert
    for i in range(10, 0, -1):
        nodes.append(fh.insert(i))
        
    assert fh.find_min() == 1
    
    # Extract Min
    m = fh.extract_min()
    assert m == 1
    assert fh.find_min() == 2
    
    # Decrease Key
    # Node with key 10 is at index 0
    node_10 = nodes[0] 
    fh.decrease_key(node_10, 0)
    assert fh.find_min() == 0
    assert fh.extract_min() == 0
    
    print("Fibonacci Heap Test Passed!")
