import pygame
import sys
import math

# Initialize pygame
pygame.init()

# Constants for the game
ROW_COUNT = 6
COLUMN_COUNT = 7
SQUARESIZE = 100
RADIUS = int(SQUARESIZE / 2 - 5)
MY_BLUE = (0, 0, 255)
MY_RED = (255, 0, 0)
MY_YELLOW = (255, 255, 0)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
FONT = pygame.font.SysFont("monospace", 75)

# Create the game board
def create_board():
    board = [[0 for _ in range(COLUMN_COUNT)] for _ in range(ROW_COUNT)]
    return board

# Drop a piece in the board
def drop_piece(board, row, col, piece):
    board[row][col] = piece

# Check if the column is full
def is_valid_location(board, col):
    return board[ROW_COUNT - 1][col] == 0

# Get the next available row in the given column
def get_next_open_row(board, col):
    for r in range(ROW_COUNT):
        if board[r][col] == 0:
            return r

# Print the board (used for debugging)
def print_board(board):
    for r in range(ROW_COUNT):
        print(board[r])

# Check for a winning move
def winning_move(board, piece):
    # Check horizontal locations for win
    for c in range(COLUMN_COUNT - 3):
        for r in range(ROW_COUNT):
            if board[r][c] == piece and board[r][c + 1] == piece and board[r][c + 2] == piece and board[r][c + 3] == piece:
                return True

    # Check vertical locations for win
    for c in range(COLUMN_COUNT):
        for r in range(ROW_COUNT - 3):
            if board[r][c] == piece and board[r + 1][c] == piece and board[r + 2][c] == piece and board[r + 3][c] == piece:
                return True

    # Check positively sloped diagonals
    for c in range(COLUMN_COUNT - 3):
        for r in range(ROW_COUNT - 3):
            if board[r][c] == piece and board[r + 1][c + 1] == piece and board[r + 2][c + 2] == piece and board[r + 3][c + 3] == piece:
                return True

    # Check negatively sloped diagonals
    for c in range(COLUMN_COUNT - 3):
        for r in range(3, ROW_COUNT):
            if board[r][c] == piece and board[r - 1][c + 1] == piece and board[r - 2][c + 2] == piece and board[r - 3][c + 3] == piece:
                return True

# Draw the board
def draw_board(board, screen):
    for c in range(COLUMN_COUNT):
        for r in range(ROW_COUNT):
            pygame.draw.rect(screen, MY_BLUE, (c * SQUARESIZE, r * SQUARESIZE + SQUARESIZE, SQUARESIZE, SQUARESIZE))
            pygame.draw.circle(screen, BLACK, (int(c * SQUARESIZE + SQUARESIZE / 2), int(r * SQUARESIZE + SQUARESIZE + SQUARESIZE / 2)), RADIUS)

            if board[r][c] == 1:
                pygame.draw.circle(screen, MY_RED, (int(c * SQUARESIZE + SQUARESIZE / 2), int(r * SQUARESIZE + SQUARESIZE + SQUARESIZE / 2)), RADIUS)
            elif board[r][c] == 2:
                pygame.draw.circle(screen, MY_YELLOW, (int(c * SQUARESIZE + SQUARESIZE / 2), int(r * SQUARESIZE + SQUARESIZE + SQUARESIZE / 2)), RADIUS)
    pygame.display.update()

# Main game function
def main():
    board = create_board()
    print_board(board)

    # Set up the Pygame screen
    width = COLUMN_COUNT * SQUARESIZE
    height = (ROW_COUNT + 1) * SQUARESIZE
    size = (width, height)
    screen = pygame.display.set_mode(size)
    pygame.display.set_caption("Connect Four")

    draw_board(board, screen)

    game_over = False
    turn = 0  # 0 for Player 1 (Red), 1 for Player 2 (Yellow)

    # Game loop
    while not game_over:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()

            if event.type == pygame.MOUSEMOTION:
                pygame.draw.rect(screen, BLACK, (0, 0, width, SQUARESIZE))
                posx = event.pos[0]
                if turn == 0:
                    pygame.draw.circle(screen, MY_RED, (posx, int(SQUARESIZE / 2)), RADIUS)
                else:
                    pygame.draw.circle(screen, MY_YELLOW, (posx, int(SQUARESIZE / 2)), RADIUS)
            pygame.display.update()

            if event.type == pygame.MOUSEBUTTONDOWN:
                pygame.draw.rect(screen, BLACK, (0, 0, width, SQUARESIZE))
                # Ask for Player 1 Input
                if turn == 0:
                    posx = event.pos[0]
                    col = int(math.floor(posx / SQUARESIZE))

                    if is_valid_location(board, col):
                        row = get_next_open_row(board, col)
                        drop_piece(board, row, col, 1)

                        if winning_move(board, 1):
                            label = FONT.render("Player 1 Wins!!", 1, MY_RED)
                            screen.blit(label, (40, 10))
                            game_over = True

                # Ask for Player 2 Input
                else:
                    posx = event.pos[0]
                    col = int(math.floor(posx / SQUARESIZE))

                    if is_valid_location(board, col):
                        row = get_next_open_row(board, col)
                        drop_piece(board, row, col, 2)

                        if winning_move(board, 2):
                            label = FONT.render("Player 2 Wins!!", 1, MY_YELLOW)
                            screen.blit(label, (40, 10))
                            game_over = True

                draw_board(board, screen)
                turn += 1
                turn = turn % 2

                if game_over:
                    pygame.time.wait(3000)

if __name__ == "__main__":
    main()
