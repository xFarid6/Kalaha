class MinHeap:
    def __init__(self):
        self.heap = []
    
    def push(self, val):
        self.heap.append(val)
        self._bubble_up(len(self.heap) - 1)
    
    def pop(self):
        if not self.heap:
            return None
        
        if len(self.heap) == 1:
            return self.heap.pop()
        
        root = self.heap[0]
        self.heap[0] = self.heap.pop()
        self._bubble_down(0)
        return root
    
    def _bubble_up(self, idx):
        """
        This function bubbles up the element at index idx to its correct position in the heap.
        It does this by comparing the element with its parent and swapping if necessary.
        """
        while idx > 0:
            parent = (idx - 1) // 2
            if self.heap[idx] < self.heap[parent]:
                self.heap[idx], self.heap[parent] = self.heap[parent], self.heap[idx]
                idx = parent
            else:
                break
    
    def _bubble_down(self, idx):
        """
        This function bubbles down the element at index idx to its correct position in the heap.
        It does this by comparing the element with its children and swapping if necessary.
        """
        while idx < len(self.heap):
            left = 2 * idx + 1
            right = 2 * idx + 2
            smallest = idx
            
            if left < len(self.heap) and self.heap[left] < self.heap[smallest]:
                smallest = left
            if right < len(self.heap) and self.heap[right] < self.heap[smallest]:
                smallest = right
            
            if smallest != idx:
                self.heap[idx], self.heap[smallest] = self.heap[smallest], self.heap[idx]
                idx = smallest
            else:
                break

def binary_search(arr, val, start, end):
    if start == end:
        if arr[start] > val:
            return start
        else:
            return start + 1
    if start > end:
        return start

    mid = (start + end) // 2
    if arr[mid] < val:
        return binary_search(arr, val, mid + 1, end)
    elif arr[mid] > val:
        return binary_search(arr, val, start, mid - 1)
    else:
        return mid

def binary_insertion_sort(arr):
    for i in range(1, len(arr)):
        val = arr[i]
        j = binary_search(arr, val, 0, i - 1)
        # Shift elements
        arr.pop(i)
        arr.insert(j, val)
    return arr

# let's try doing a selection sort

def selection_sort(arr):
    for i in range(len(arr)):
        min_idx = i
        for j in range(i + 1, len(arr)):
            if arr[j] < arr[min_idx]:
                min_idx = j
        arr[i], arr[min_idx] = arr[min_idx], arr[i]
    return arr

# taking items from a min heap, constructed internally

def selection_sort_min_heap(arr):
    min_heap = MinHeap()
    for x in arr:
        min_heap.push(x)
    for i in range(len(arr)):
        arr[i] = min_heap.pop()
    return arr

if __name__ == "__main__":
    import random
    print("Testing Binary Sort (Binary Insertion)...")
    data = [random.randint(0, 100) for _ in range(20)]
    print(f"Input: {data}")
    
    binary_insertion_sort(data)
    
    print(f"Sorted: {data}")
    assert data == sorted(data), "Binary Sort failed!"
    print("Binary Sort Test Passed!")

    print("Testing Selection Sort (Min Heap)...")
    data = [random.randint(0, 100) for _ in range(20)]
    print(f"Input: {data}")
    selection_sort_min_heap(data)
    
    print(f"Sorted: {data}")
    assert data == sorted(data), "Selection Sort failed!"
    print("Selection Sort Test Passed!")


    # add stress tests for each and time them
    import time
    import random
    for i in range(1, 1000000, 100000):
        data = [random.randint(0, 100) for _ in range(i)]
        data2 = data.copy()

        start = time.time()
        binary_insertion_sort(data)
        end = time.time()
        print(f"Binary Insertion Sort: {i} elements, {end - start} seconds")

        start = time.time()
        selection_sort_min_heap(data2)
        end = time.time()
        print(f"Selection Sort (Min Heap): {i} elements, {end - start} seconds")    

        """
        Binary Insertion Sort: 200001 elements, 14.1382737159729 seconds
        Selection Sort (Min Heap): 200001 elements, 1.0839273929595947 seconds
        
        Binary Insertion Sort: 300001 elements, 51.456604957580566 seconds
        Selection Sort (Min Heap): 300001 elements, 1.8016932010650635 seconds
        """