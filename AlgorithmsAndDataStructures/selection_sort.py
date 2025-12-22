def selection_sort(arr):
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
