import pygame
import time
import random

# Initialize pygame
pygame.init()

# Define constants
WIDTH = 800
HEIGHT = 600
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)

# Set up the screen
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Countdown Timer Game")

# Set up fonts
font = pygame.font.SysFont("comicsansms", 50)
small_font = pygame.font.SysFont("comicsansms", 30)

# Timer class to manage the countdown
class Timer:
    def __init__(self, time_limit):
        self.time_limit = time_limit
        self.time_left = time_limit
        self.start_time = None

    def start(self):
        self.start_time = time.time()

    def update(self):
        if self.start_time is not None:
            self.time_left = self.time_limit - (time.time() - self.start_time)

    def reset(self):
        self.time_left = self.time_limit
        self.start_time = None

    def get_time_left(self):
        return max(0, self.time_left)

    def draw(self, screen):
        time_text = font.render(f"Time Left: {int(self.get_time_left())}s", True, WHITE)
        screen.blit(time_text, (WIDTH // 2 - time_text.get_width() // 2, HEIGHT // 3))

# Function to display the task
def display_task(screen, task):
    task_text = small_font.render(task, True, WHITE)
    screen.blit(task_text, (WIDTH // 2 - task_text.get_width() // 2, HEIGHT // 2))

# Function to display the result (Win or Lose)
def display_result(screen, result):
    result_text = font.render(result, True, GREEN if result == "You Win!" else RED)
    screen.blit(result_text, (WIDTH // 2 - result_text.get_width() // 2, HEIGHT // 2 + 100))

# Main game loop
def game_loop():
    # Game state variables
    tasks = ["Press 'A'", "Press 'B'", "Press 'C'", "Press 'D'", "Press 'Space'"]
    current_task = random.choice(tasks)
    timer = Timer(30)  # 30 seconds countdown
    timer.start()
    game_over = False
    won = False

    clock = pygame.time.Clock()

    while not game_over:
        screen.fill(BLACK)

        # Update timer
        timer.update()
        timer.draw(screen)

        # Display task
        display_task(screen, current_task)

        # Check if the time is up
        if timer.get_time_left() == 0:
            display_result(screen, "You Lose!")
            game_over = True

        # Check for user input
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                game_over = True
            if event.type == pygame.KEYDOWN:
                if current_task == "Press 'A'" and event.key == pygame.K_a:
                    won = True
                elif current_task == "Press 'B'" and event.key == pygame.K_b:
                    won = True
                elif current_task == "Press 'C'" and event.key == pygame.K_c:
                    won = True
                elif current_task == "Press 'D'" and event.key == pygame.K_d:
                    won = True
                elif current_task == "Press 'Space'" and event.key == pygame.K_SPACE:
                    won = True

        # If the player won, display "You Win!" and end the game
        if won:
            display_result(screen, "You Win!")
            game_over = True

        pygame.display.update()
        clock.tick(60)

    pygame.time.wait(2000)  # Wait for 2 seconds before quitting
    pygame.quit()

# Start the game
if __name__ == "__main__":
    game_loop()
