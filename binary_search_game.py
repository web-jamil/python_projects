# Function to perform binary search on a sorted list
def binary_search(arr, target):
    low = 0
    high = len(arr) - 1
    
    while low <= high:
        mid = (low + high) // 2  # Find the middle index
        
        # Check if the target is at the mid index
        if arr[mid] == target:
            return mid  # Element found, return the index
        
        # If target is greater than mid element, discard the left half
        elif arr[mid] < target:
            low = mid + 1
        
        # If target is smaller than mid element, discard the right half
        else:
            high = mid - 1
    
    return -1  # Element is not present in the list

# Function to take user input and find the target using binary search
def main():
    # Example sorted array
    arr = [2, 4, 6, 8, 10, 12, 14, 16, 18, 20, 22, 24, 26]
    
    # Take the target element input from the user
    target = int(input("Enter the number you want to search for: "))
    
    # Perform binary search
    result = binary_search(arr, target)
    
    # Print the result
    if result != -1:
        print(f"Element {target} is present at index {result}.")
    else:
        print(f"Element {target} is not present in the list.")

# Run the main function
if __name__ == "__main__":
    main()
