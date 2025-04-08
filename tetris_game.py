import pygame
import random
import sys

# Initialize pygame
pygame.font.init()

# Constants
SCREEN_WIDTH = 300
SCREEN_HEIGHT = 600
BLOCK_SIZE = 30
BOARD_WIDTH = 10
BOARD_HEIGHT = 20
GAME_WIDTH = SCREEN_WIDTH // BLOCK_SIZE
GAME_HEIGHT = SCREEN_HEIGHT // BLOCK_SIZE
WHITE = (255, 255, 255)
BLUE = (0, 0, 255)
CYAN = (0, 255, 255)
ORANGE = (255, 165, 0)
YELLOW = (255, 255, 0)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
PURPLE = (128, 0, 128)
COLOR_LIST = [CYAN, BLUE, ORANGE, YELLOW, GREEN, RED, PURPLE]

# Shapes (each list of lists represents a shape)
SHAPES = [
    [[1, 1, 1, 1]],  # I shape
    [[1, 1, 0],
     [0, 1, 1]],  # S shape
    [[0, 1, 1],
     [1, 1, 0]],  # Z shape
    [[1, 1],
     [1, 1]],  # O shape
    [[0, 1, 0],
     [1, 1, 1]],  # T shape
    [[1, 0, 0],
     [1, 1, 1]],  # L shape
    [[0, 0, 1],
     [1, 1, 1]],  # J shape
]

# Initialize the screen
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption('Tetris')


# Class to represent a Tetris piece
class Piece(object):
    def __init__(self, shape, color):
        self.shape = shape
        self.color = color
        self.x = GAME_WIDTH // 2 - len(self.shape[0]) // 2
        self.y = 0
        self.rotation = 0


# Class to handle the game logic
class Tetris(object):
    def __init__(self):
        self.board = [[0 for _ in range(BOARD_WIDTH)] for _ in range(BOARD_HEIGHT)]
        self.gameover = False
        self.current_piece = None
        self.next_piece = None
        self.score = 0
        self.font = pygame.font.SysFont("monospace", 30)

    def new_piece(self):
        shape = random.choice(SHAPES)
        color = random.choice(COLOR_LIST)
        self.current_piece = Piece(shape, color)
        self.next_piece = Piece(random.choice(SHAPES), random.choice(COLOR_LIST))

    def rotate_piece(self):
        self.current_piece.shape = [
            [self.current_piece.shape[y][x] for y in range(len(self.current_piece.shape))]
            for x in range(len(self.current_piece.shape[0]) - 1, -1, -1)
        ]

    def valid_move(self, dx=0, dy=0):
        for y, row in enumerate(self.current_piece.shape):
            for x, cell in enumerate(row):
                if cell:
                    new_x = self.current_piece.x + x + dx
                    new_y = self.current_piece.y + y + dy
                    if new_x < 0 or new_x >= BOARD_WIDTH or new_y >= BOARD_HEIGHT:
                        return False
                    if new_y >= 0 and self.board[new_y][new_x]:
                        return False
        return True

    def freeze_piece(self):
        for y, row in enumerate(self.current_piece.shape):
            for x, cell in enumerate(row):
                if cell:
                    self.board[self.current_piece.y + y][self.current_piece.x + x] = self.current_piece.color
        self.clear_lines()
        self.new_piece()

    def clear_lines(self):
        for y in range(BOARD_HEIGHT - 1, -1, -1):
            if all(self.board[y]):
                self.board.pop(y)
                self.board.insert(0, [0 for _ in range(BOARD_WIDTH)])
                self.score += 100

    def draw_board(self):
        for y in range(BOARD_HEIGHT):
            for x in range(BOARD_WIDTH):
                if self.board[y][x]:
                    pygame.draw.rect(screen, self.board[y][x], (x * BLOCK_SIZE, y * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE))

    def draw_piece(self):
        for y, row in enumerate(self.current_piece.shape):
            for x, cell in enumerate(row):
                if cell:
                    pygame.draw.rect(
                        screen, self.current_piece.color,
                        ((self.current_piece.x + x) * BLOCK_SIZE, (self.current_piece.y + y) * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE)
                    )

    def draw(self):
        screen.fill(WHITE)
        self.draw_board()
        self.draw_piece()

        # Draw score
        score_text = self.font.render(f"Score: {self.score}", True, (0, 0, 0))
        screen.blit(score_text, (10, 10))

        if self.gameover:
            game_over_text = self.font.render("Game Over!", True, (255, 0, 0))
            screen.blit(game_over_text, (SCREEN_WIDTH // 2 - game_over_text.get_width() // 2, SCREEN_HEIGHT // 2))

        pygame.display.update()

    def run(self):
        clock = pygame.time.Clock()
        self.new_piece()

        while not self.gameover:
            clock.tick(10)  # Speed of the game
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_LEFT:
                        if self.valid_move(dx=-1):
                            self.current_piece.x -= 1
                    if event.key == pygame.K_RIGHT:
                        if self.valid_move(dx=1):
                            self.current_piece.x += 1
                    if event.key == pygame.K_DOWN:
                        if self.valid_move(dy=1):
                            self.current_piece.y += 1
                    if event.key == pygame.K_UP:
                        self.rotate_piece()
                        if not self.valid_move():
                            self.rotate_piece()
                            self.rotate_piece()
                            self.rotate_piece()

            if self.valid_move(dy=1):
                self.current_piece.y += 1
            else:
                self.freeze_piece()

            self.draw()

            if self.gameover:
                pygame.time.wait(2000)
                self.__init__()  # Restart the game

# Run the game
if __name__ == "__main__":
    game = Tetris()
    game.run()
