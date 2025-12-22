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

if __name__ == "__main__":
    import random
    print("Testing Binary Sort (Binary Insertion)...")
    data = [random.randint(0, 100) for _ in range(20)]
    print(f"Input: {data}")
    
    binary_insertion_sort(data)
    
    print(f"Sorted: {data}")
    assert data == sorted(data), "Binary Sort failed!"
    print("Binary Sort Test Passed!")
