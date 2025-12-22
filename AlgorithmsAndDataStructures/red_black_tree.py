class RedBlackTree:
    class Node:
        def __init__(self, key, color='RED'):
            self.key = key
            self.color = color # 'RED' or 'BLACK'
            self.left = None
            self.right = None
            self.parent = None

    def __init__(self):
        self.TNULL = self.Node(0, 'BLACK')
        self.root = self.TNULL

    def insert(self, key):
        node = self.Node(key)
        node.parent = None
        node.left = self.TNULL
        node.right = self.TNULL
        node.color = 'RED'

        y = None
        x = self.root

        while x != self.TNULL:
            y = x
            if node.key < x.key:
                x = x.left
            else:
                x = x.right

        node.parent = y
        if y == None:
            self.root = node
        elif node.key < y.key:
            y.left = node
        else:
            y.right = node

        if node.parent == None:
            node.color = 'BLACK'
            return

        if node.parent.parent == None:
            return

        self._fix_insert(node)

    def _fix_insert(self, k):
        while k.parent.color == 'RED':
            if k.parent == k.parent.parent.right:
                u = k.parent.parent.left
                if u.color == 'RED':
                    u.color = 'BLACK'
                    k.parent.color = 'BLACK'
                    k.parent.parent.color = 'RED'
                    k = k.parent.parent
                else:
                    if k == k.parent.left:
                        k = k.parent
                        self._right_rotate(k)
                    k.parent.color = 'BLACK'
                    k.parent.parent.color = 'RED'
                    self._left_rotate(k.parent.parent)
            else:
                u = k.parent.parent.right
                if u.color == 'RED':
                    u.color = 'BLACK'
                    k.parent.color = 'BLACK'
                    k.parent.parent.color = 'RED'
                    k = k.parent.parent
                else:
                    if k == k.parent.right:
                        k = k.parent
                        self._left_rotate(k)
                    k.parent.color = 'BLACK'
                    k.parent.parent.color = 'RED'
                    self._right_rotate(k.parent.parent)
            if k == self.root:
                break
        self.root.color = 'BLACK'

    def _left_rotate(self, x):
        y = x.right
        x.right = y.left
        if y.left != self.TNULL:
            y.left.parent = x
        y.parent = x.parent
        if x.parent == None:
            self.root = y
        elif x == x.parent.left:
            x.parent.left = y
        else:
            x.parent.right = y
        y.left = x
        x.parent = y

    def _right_rotate(self, x):
        y = x.left
        x.left = y.right
        if y.right != self.TNULL:
            y.right.parent = x
        y.parent = x.parent
        if x.parent == None:
            self.root = y
        elif x == x.parent.right:
            x.parent.right = y
        else:
            x.parent.left = y
        y.right = x
        x.parent = y

    def inorder(self):
        res = []
        self._inorder_helper(self.root, res)
        return res

    def _inorder_helper(self, node, res):
        if node != self.TNULL:
            self._inorder_helper(node.left, res)
            res.append(node.key)
            self._inorder_helper(node.right, res)

if __name__ == "__main__":
    print("Testing Red-Black Tree...")
    rbt = RedBlackTree()
    
    keys = [10, 20, 30, 15, 25, 5, 1]
    for k in keys:
        rbt.insert(k)
        
    res = rbt.inorder()
    print(f"Inorder: {res}")
    assert res == sorted(keys), "Inorder traversal failed"
    
    assert rbt.root.color == 'BLACK', "Root must be black"
    print("Red-Black Tree Test Passed!")
