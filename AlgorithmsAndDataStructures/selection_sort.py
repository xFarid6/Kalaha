def selection_sort(arr):
    """
    The idea of selection sort is to divide the input into a sorted and an unsorted region.
    The sorted region starts empty and the unsorted region starts with the entire array.
    In each iteration, the algorithm finds the minimum element in the unsorted region and swaps it with the first element of the unsorted region.
    This process is repeated until the unsorted region is empty, resulting in a sorted array.
    """
    n = len(arr)
    for i in range(n):
        min_idx = i
        for j in range(i+1, n):
            if arr[j] < arr[min_idx]:
                min_idx = j
        arr[i], arr[min_idx] = arr[min_idx], arr[i]
    return arr

if __name__ == "__main__":
    import random
    print("Testing Selection Sort...")
    data = [random.randint(0, 100) for _ in range(20)]
    print(f"Input: {data}")
    
    selection_sort(data)
    
    print(f"Sorted: {data}")
    assert data == sorted(data), "Selection Sort failed!"
    print("Selection Sort Test Passed!")
