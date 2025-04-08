import pygame
import random
import sys

# Initialize pygame
pygame.init()

# Constants
WIDTH, HEIGHT = 800, 600
GRID_SIZE = 10
CELL_SIZE = WIDTH // GRID_SIZE
NUM_MINES = 15

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (169, 169, 169)
RED = (255, 0, 0)
GREEN = (0, 255, 0)

# Set up the display
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Minesweeper")

# Fonts
font = pygame.font.SysFont("arial", 24)

# Cell Class
class Cell:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.revealed = False
        self.flagged = False
        self.mine = False
        self.neighbor_mines = 0

    def draw(self, screen):
        color = WHITE
        if self.revealed:
            color = GRAY
            if self.mine:
                pygame.draw.circle(screen, RED, (self.x * CELL_SIZE + CELL_SIZE // 2, self.y * CELL_SIZE + CELL_SIZE // 2), CELL_SIZE // 3)
            elif self.neighbor_mines > 0:
                number_text = font.render(str(self.neighbor_mines), True, BLACK)
                screen.blit(number_text, (self.x * CELL_SIZE + CELL_SIZE // 4, self.y * CELL_SIZE + CELL_SIZE // 4))
        elif self.flagged:
            pygame.draw.line(screen, BLACK, (self.x * CELL_SIZE, self.y * CELL_SIZE), ((self.x + 1) * CELL_SIZE, (self.y + 1) * CELL_SIZE), 3)
            pygame.draw.line(screen, BLACK, ((self.x + 1) * CELL_SIZE, self.y * CELL_SIZE), (self.x * CELL_SIZE, (self.y + 1) * CELL_SIZE), 3)

        pygame.draw.rect(screen, color, (self.x * CELL_SIZE, self.y * CELL_SIZE, CELL_SIZE, CELL_SIZE))
        pygame.draw.rect(screen, BLACK, (self.x * CELL_SIZE, self.y * CELL_SIZE, CELL_SIZE, CELL_SIZE), 2)

    def reveal(self):
        self.revealed = True
        if self.mine:
            return False
        return True

    def add_mine(self):
        self.mine = True

    def set_neighbor_mines(self, count):
        self.neighbor_mines = count


# Create the grid
def create_grid():
    grid = [[Cell(x, y) for y in range(GRID_SIZE)] for x in range(GRID_SIZE)]

    # Randomly place mines
    mines_placed = 0
    while mines_placed < NUM_MINES:
        x = random.randint(0, GRID_SIZE - 1)
        y = random.randint(0, GRID_SIZE - 1)
        if not grid[x][y].mine:
            grid[x][y].add_mine()
            mines_placed += 1

    # Calculate neighboring mines
    for x in range(GRID_SIZE):
        for y in range(GRID_SIZE):
            if grid[x][y].mine:
                continue
            neighbor_mines = 0
            for dx in range(-1, 2):
                for dy in range(-1, 2):
                    nx, ny = x + dx, y + dy
                    if 0 <= nx < GRID_SIZE and 0 <= ny < GRID_SIZE and grid[nx][ny].mine:
                        neighbor_mines += 1
            grid[x][y].set_neighbor_mines(neighbor_mines)

    return grid


# Reveal the neighboring cells (if the cell has 0 neighboring mines)
def reveal_neighbors(grid, x, y):
    to_reveal = [(x, y)]
    revealed = set()

    while to_reveal:
        cx, cy = to_reveal.pop()
        if (cx, cy) in revealed:
            continue
        revealed.add((cx, cy))
        grid[cx][cy].reveal()

        if grid[cx][cy].neighbor_mines == 0:
            for dx in range(-1, 2):
                for dy in range(-1, 2):
                    nx, ny = cx + dx, cy + dy
                    if 0 <= nx < GRID_SIZE and 0 <= ny < GRID_SIZE and not grid[nx][ny].revealed:
                        to_reveal.append((nx, ny))

    return revealed


# Check if the player has won
def check_win(grid):
    for x in range(GRID_SIZE):
        for y in range(GRID_SIZE):
            if not grid[x][y].mine and not grid[x][y].revealed:
                return False
    return True


# Main game loop
def game_loop():
    grid = create_grid()
    game_over = False
    win = False
    clock = pygame.time.Clock()

    while not game_over:
        screen.fill(WHITE)

        # Draw the grid
        for x in range(GRID_SIZE):
            for y in range(GRID_SIZE):
                grid[x][y].draw(screen)

        # Check for events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                game_over = True
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mx, my = event.pos
                x, y = mx // CELL_SIZE, my // CELL_SIZE

                if event.button == 1:  # Left click
                    if not grid[x][y].revealed:
                        if not grid[x][y].reveal():
                            game_over = True  # Hit a mine
                        elif grid[x][y].neighbor_mines == 0:
                            reveal_neighbors(grid, x, y)

                elif event.button == 3:  # Right click
                    grid[x][y].flagged = not grid[x][y].flagged

        # Check win condition
        if check_win(grid):
            win = True
            game_over = True

        if game_over:
            message = "You Win!" if win else "Game Over!"
            message_text = font.render(message, True, GREEN if win else RED)
            screen.blit(message_text, (WIDTH // 2 - message_text.get_width() // 2, HEIGHT // 2))

        pygame.display.flip()
        clock.tick(30)

    pygame.time.wait(2000)
    pygame.quit()


if __name__ == "__main__":
    game_loop()
