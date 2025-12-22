def bubble_sort(arr):
    n = len(arr)
    for i in range(n):
        swapped = False
        for j in range(0, n-i-1):
            if arr[j] > arr[j+1]:
                arr[j], arr[j+1] = arr[j+1], arr[j]
                swapped = True
        if not swapped:
            break
    return arr

if __name__ == "__main__":
    import random
    print("Testing Bubble Sort...")
    data = [random.randint(0, 100) for _ in range(20)]
    print(f"Input: {data}")
    
    bubble_sort(data)
    
    print(f"Sorted: {data}")
    assert data == sorted(data), "Bubble Sort failed!"
    print("Bubble Sort Test Passed!")
