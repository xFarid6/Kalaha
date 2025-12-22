import heapq # For comparison in testing, not usage

class MinHeap:
    def __init__(self):
        self.heap = []

    def parent(self, i):
        return (i - 1) // 2

    def left_child(self, i):
        return 2 * i + 1

    def right_child(self, i):
        return 2 * i + 2

    def push(self, val):
        self.heap.append(val)
        self._bubble_up(len(self.heap) - 1)

    def pop(self):
        if not self.heap:
            return None
        if len(self.heap) == 1:
            return self.heap.pop()
        
        root = self.heap[0]
        self.heap[0] = self.heap.pop() # Move last to root
        self._bubble_down(0)
        return root

    def peek(self):
        return self.heap[0] if self.heap else None

    def _bubble_up(self, index):
        while index > 0:
            p = self.parent(index)
            if self.heap[index] < self.heap[p]:
                self.heap[index], self.heap[p] = self.heap[p], self.heap[index]
                index = p
            else:
                break

    def _bubble_down(self, index):
        size = len(self.heap)
        while True:
            left = self.left_child(index)
            right = self.right_child(index)
            smallest = index

            if left < size and self.heap[left] < self.heap[smallest]:
                smallest = left
            
            if right < size and self.heap[right] < self.heap[smallest]:
                smallest = right
            
            if smallest != index:
                self.heap[index], self.heap[smallest] = self.heap[smallest], self.heap[index]
                index = smallest
            else:
                break

if __name__ == "__main__":
    import random
    print("Testing MinHeap...")
    mh = MinHeap()
    data = [random.randint(0, 100) for _ in range(20)]
    
    print(f"Input: {data}")
    for x in data:
        mh.push(x)
        
    sorted_out = []
    while mh.peek() is not None:
        sorted_out.append(mh.pop())
        
    print(f"Heap Sort Output: {sorted_out}")
    assert sorted_out == sorted(data), "MinHeap sort failed!"
    print("MinHeap Test Passed!")
