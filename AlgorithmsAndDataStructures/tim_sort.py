RUN = 32

def insertion_sort(arr, left, right):
    for i in range(left + 1, right + 1):
        temp = arr[i]
        j = i - 1
        while j >= left and arr[j] > temp:
            arr[j + 1] = arr[j]
            j -= 1
        arr[j + 1] = temp

def merge(arr, l, m, r):
    len1, len2 = m - l + 1, r - m
    left = arr[l : m + 1]
    right = arr[m + 1 : r + 1]

    i, j, k = 0, 0, l
    while i < len1 and j < len2:
        if left[i] <= right[j]:
            arr[k] = left[i]
            i += 1
        else:
            arr[k] = right[j]
            j += 1
        k += 1

    while i < len1:
        arr[k] = left[i]
        k += 1
        i += 1
    while j < len2:
        arr[k] = right[j]
        k += 1
        j += 1

def tim_sort(arr):
    n = len(arr)
    # Sort individual subarrays of size RUN
    for i in range(0, n, RUN):
        insertion_sort(arr, i, min(i + 31, n - 1))

    # Merge subarrays
    size = RUN
    while size < n:
        for left in range(0, n, 2 * size):
            mid = left + size - 1
            right = min(left + 2 * size - 1, n - 1)
            if mid < right:
                merge(arr, left, mid, right)
        size *= 2
    return arr

if __name__ == "__main__":
    import random
    print("Testing TimSort...")
    data = [random.randint(0, 1000) for _ in range(500)]
    # Timsort shines on partially sorted data
    data.extend(range(100)) 
    
    tim_sort(data)
    
    assert data == sorted(data), "TimSort failed!"
    print("TimSort Test Passed!")
