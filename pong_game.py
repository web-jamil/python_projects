import pygame
import random

# Initialize pygame
pygame.init()

# Define constants
WIDTH = 800
HEIGHT = 600
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
PADDLE_WIDTH = 15
PADDLE_HEIGHT = 100
BALL_SIZE = 20

# Set up the screen
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Pong Game")

# Set up fonts
font = pygame.font.SysFont("comicsansms", 30)

# Paddle class to represent each paddle
class Paddle:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = PADDLE_WIDTH
        self.height = PADDLE_HEIGHT
        self.speed = 15

    def move(self, up, down):
        keys = pygame.key.get_pressed()
        if keys[up] and self.y > 0:
            self.y -= self.speed
        if keys[down] and self.y < HEIGHT - self.height:
            self.y += self.speed

    def draw(self, screen):
        pygame.draw.rect(screen, WHITE, (self.x, self.y, self.width, self.height))

# Ball class to represent the ball
class Ball:
    def __init__(self):
        self.x = WIDTH // 2 - BALL_SIZE // 2
        self.y = HEIGHT // 2 - BALL_SIZE // 2
        self.size = BALL_SIZE
        self.speed_x = random.choice([5, -5])
        self.speed_y = random.choice([5, -5])

    def move(self):
        self.x += self.speed_x
        self.y += self.speed_y

    def draw(self, screen):
        pygame.draw.circle(screen, WHITE, (self.x, self.y), self.size)

    def reset(self):
        self.x = WIDTH // 2 - BALL_SIZE // 2
        self.y = HEIGHT // 2 - BALL_SIZE // 2
        self.speed_x = random.choice([5, -5])
        self.speed_y = random.choice([5, -5])

# Function to display the score
def display_score(left_score, right_score):
    score_text = font.render(f"{left_score} - {right_score}", True, WHITE)
    screen.blit(score_text, (WIDTH // 2 - score_text.get_width() // 2, 20))

# Main game loop
def game_loop():
    left_score = 0
    right_score = 0

    left_paddle = Paddle(30, HEIGHT // 2 - PADDLE_HEIGHT // 2)
    right_paddle = Paddle(WIDTH - 30 - PADDLE_WIDTH, HEIGHT // 2 - PADDLE_HEIGHT // 2)
    ball = Ball()

    clock = pygame.time.Clock()

    game_over = False
    while not game_over:
        screen.fill(BLACK)

        # Draw paddles and ball
        left_paddle.draw(screen)
        right_paddle.draw(screen)
        ball.draw(screen)

        # Display score
        display_score(left_score, right_score)

        # Move paddles
        left_paddle.move(pygame.K_w, pygame.K_s)
        right_paddle.move(pygame.K_UP, pygame.K_DOWN)

        # Move the ball
        ball.move()

        # Ball collision with top and bottom
        if ball.y <= 0 or ball.y >= HEIGHT - BALL_SIZE:
            ball.speed_y = -ball.speed_y

        # Ball collision with paddles
        if (ball.x <= left_paddle.x + PADDLE_WIDTH and left_paddle.y < ball.y < left_paddle.y + PADDLE_HEIGHT) or \
           (ball.x >= right_paddle.x - BALL_SIZE and right_paddle.y < ball.y < right_paddle.y + PADDLE_HEIGHT):
            ball.speed_x = -ball.speed_x

        # Scoring system
        if ball.x <= 0:
            right_score += 1
            ball.reset()
        if ball.x >= WIDTH - BALL_SIZE:
            left_score += 1
            ball.reset()

        # Check if the game is over
        if left_score == 5 or right_score == 5:
            game_over = True
            winner = "Left Player" if left_score > right_score else "Right Player"
            message = font.render(f"{winner} wins!", True, WHITE)
            screen.blit(message, (WIDTH // 2 - message.get_width() // 2, HEIGHT // 2))

        pygame.display.update()
        clock.tick(60)

    # Wait for a moment before quitting
    pygame.time.wait(3000)
    pygame.quit()

# Start the game
if __name__ == "__main__":
    game_loop()
