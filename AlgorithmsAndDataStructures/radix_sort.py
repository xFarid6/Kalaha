def counting_sort(arr, exp):
    """
    The idea of counting sort is to count the number of occurrences of each element in the array.
    Then, we can use this count to determine the position of each element in the sorted array.
    """
    n = len(arr)
    output = [0] * n
    count = [0] * 10

    for i in range(n):
        index = arr[i] // exp
        count[index % 10] += 1

    for i in range(1, 10):
        count[i] += count[i - 1]

    for i in range(n - 1, -1, -1):
        index = arr[i] // exp
        output[count[index % 10] - 1] = arr[i]
        count[index % 10] -= 1

    for i in range(n):
        arr[i] = output[i]

def radix_sort(arr):
    """
    The idea of radix sort is to sort the array by each digit, starting from the least significant digit.
    """
    if not arr: return []
    max1 = max(arr)
    exp = 1
    while max1 // exp > 0:
        counting_sort(arr, exp)
        exp *= 10
    return arr

if __name__ == "__main__":
    import random
    print("Testing Radix Sort...")
    data = [random.randint(0, 1000) for _ in range(20)]
    print(f"Input: {data}")
    
    radix_sort(data)
    
    print(f"Sorted: {data}")
    assert data == sorted(data), "Radix Sort failed!"
    print("Radix Sort Test Passed!")
