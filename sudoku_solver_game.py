# Function to print the Sudoku grid
def print_board(board):
    for row in board:
        print(" ".join(str(num) if num != 0 else "." for num in row))
        
# Function to check if placing num in (row, col) is valid
def is_valid(board, num, row, col):
    # Check if num is in the current row
    if num in board[row]:
        return False
    
    # Check if num is in the current column
    for i in range(9):
        if board[i][col] == num:
            return False
    
    # Check if num is in the current 3x3 box
    start_row, start_col = 3 * (row // 3), 3 * (col // 3)
    for i in range(start_row, start_row + 3):
        for j in range(start_col, start_col + 3):
            if board[i][j] == num:
                return False
                
    return True

# Function to solve the Sudoku puzzle using backtracking
def solve_sudoku(board):
    # Find the next empty spot (denoted by 0)
    for row in range(9):
        for col in range(9):
            if board[row][col] == 0:
                # Try possible numbers from 1 to 9
                for num in range(1, 10):
                    if is_valid(board, num, row, col):
                        board[row][col] = num
                        
                        # Recursively try to solve with this number placed
                        if solve_sudoku(board):
                            return True
                        
                        # If placing num doesn't work, reset the spot
                        board[row][col] = 0
                        
                return False  # No valid number was found, backtrack
    return True  # All cells are filled, puzzle is solved

# Function to solve and print the Sudoku board
def main():
    # Example Sudoku board (0 represents empty cells)
    board = [
        [5, 3, 0, 0, 7, 0, 0, 0, 0],
        [6, 0, 0, 1, 9, 5, 0, 0, 0],
        [0, 9, 8, 0, 0, 0, 0, 6, 0],
        [8, 0, 0, 0, 6, 0, 0, 0, 3],
        [4, 0, 0, 8, 0, 3, 0, 0, 1],
        [7, 0, 0, 0, 2, 0, 0, 0, 6],
        [0, 6, 0, 0, 0, 0, 2, 8, 0],
        [0, 0, 0, 4, 1, 9, 0, 0, 5],
        [0, 0, 0, 0, 8, 0, 0, 7, 9]
    ]
    
    print("Original Sudoku Board:")
    print_board(board)
    
    # Solve the Sudoku puzzle
    if solve_sudoku(board):
        print("\nSolved Sudoku Board:")
        print_board(board)
    else:
        print("\nNo solution exists for this Sudoku puzzle.")

# Run the main function to start the solver
if __name__ == "__main__":
    main()
