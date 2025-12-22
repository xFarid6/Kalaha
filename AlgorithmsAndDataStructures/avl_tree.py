class AVLTree:
    class Node:
        def __init__(self, key):
            self.key = key
            self.left = None
            self.right = None
            self.height = 1

    def __init__(self):
        self.root = None

    def insert(self, key):
        self.root = self._insert_node(self.root, key)

    def _insert_node(self, node, key):
        # 1. Standard BST Insert
        if not node:
            return self.Node(key)
        
        if key < node.key:
            node.left = self._insert_node(node.left, key)
        else:
            node.right = self._insert_node(node.right, key)

        # 2. Update Height
        node.height = 1 + max(self._get_height(node.left), self._get_height(node.right))

        # 3. Get Balance
        balance = self._get_balance(node)

        # 4. Rotations based on 4 cases
        
        # Left Left
        if balance > 1 and key < node.left.key:
            return self._right_rotate(node)
            
        # Right Right
        if balance < -1 and key > node.right.key:
            return self._left_rotate(node)
            
        # Left Right
        if balance > 1 and key > node.left.key:
            node.left = self._left_rotate(node.left)
            return self._right_rotate(node)

        # Right Left
        if balance < -1 and key < node.right.key:
            node.right = self._right_rotate(node.right)
            return self._left_rotate(node)

        return node

    def _left_rotate(self, z):
        y = z.right
        T2 = y.left
        
        # Perform rotation
        y.left = z
        z.right = T2
        
        # Update heights
        z.height = 1 + max(self._get_height(z.left), self._get_height(z.right))
        y.height = 1 + max(self._get_height(y.left), self._get_height(y.right))
        
        return y

    def _right_rotate(self, z):
        y = z.left
        T3 = y.right
        
        # Perform rotation
        y.right = z
        z.left = T3
        
        # Update heights
        z.height = 1 + max(self._get_height(z.left), self._get_height(z.right))
        y.height = 1 + max(self._get_height(y.left), self._get_height(y.right))
        
        return y

    def _get_height(self, node):
        if not node: return 0
        return node.height

    def _get_balance(self, node):
        if not node: return 0
        return self._get_height(node.left) - self._get_height(node.right)

    def inorder(self):
        res = []
        self._inorder_helper(self.root, res)
        return res

    def _inorder_helper(self, node, res):
        if node:
            self._inorder_helper(node.left, res)
            res.append(node.key)
            self._inorder_helper(node.right, res)

if __name__ == "__main__":
    print("Testing AVL Tree...")
    avl = AVLTree()
    
    # Insert causing rotations
    keys = [10, 20, 30, 40, 50, 25]
    # 10,20,30 -> RR -> Rotate Left at 10. Root becomes 20.
    
    for k in keys:
        avl.insert(k)
        
    # Check Inorder (Sorted)
    res = avl.inorder()
    print(f"Inorder: {res}")
    assert res == sorted(keys)
    
    # Check Height Balance (Root)
    print(f"Root Height: {avl.root.height}")
    # With 6 nodes, height should be small (3 or 4)
    # 20 Should be root or close
    assert avl.root.height <= 4
    
    print("AVL Tree Test Passed!")
