import pygame
import time
import random

# Initialize pygame
pygame.init()

# Define colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (213, 50, 80)
GREEN = (0, 255, 0)
BLUE = (50, 153, 213)

# Set up display
WIDTH = 600
HEIGHT = 400
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Snake Game")

# Set up the clock for controlling the speed of the game
clock = pygame.time.Clock()

# Set up the font for text rendering
font_style = pygame.font.SysFont("bahnschrift", 25)
score_font = pygame.font.SysFont("comicsansms", 35)

# Function to display the score
def your_score(score):
    value = score_font.render("Your Score: " + str(score), True, WHITE)
    screen.blit(value, [0, 0])

# Function to render the snake
def our_snake(snake_block, snake_list):
    for x in snake_list:
        pygame.draw.rect(screen, GREEN, [x[0], x[1], snake_block, snake_block])

# Function to display a message (like "Game Over")
def message(msg, color):
    mesg = font_style.render(msg, True, color)
    screen.blit(mesg, [WIDTH / 6, HEIGHT / 3])

# Main game loop
def gameLoop():
    game_over = False
    game_close = False

    # Snake settings
    snake_block = 10
    snake_speed = 15

    # Initial position of the snake
    x1 = WIDTH / 2
    y1 = HEIGHT / 2

    # Initial movement direction
    x1_change = 0
    y1_change = 0

    # Snake body
    snake_List = []
    Length_of_snake = 1

    # Food generation
    foodx = round(random.randrange(0, WIDTH - snake_block) / 10.0) * 10.0
    foody = round(random.randrange(0, HEIGHT - snake_block) / 10.0) * 10.0

    while not game_over:

        while game_close == True:
            screen.fill(BLUE)
            message("You Lost! Press Q-Quit or C-Play Again", RED)
            your_score(Length_of_snake - 1)
            pygame.display.update()

            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_q:
                        game_over = True
                    if event.key == pygame.K_c:
                        gameLoop()

        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                game_over = True
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    x1_change = -snake_block
                    y1_change = 0
                elif event.key == pygame.K_RIGHT:
                    x1_change = snake_block
                    y1_change = 0
                elif event.key == pygame.K_UP:
                    y1_change = -snake_block
                    x1_change = 0
                elif event.key == pygame.K_DOWN:
                    y1_change = snake_block
                    x1_change = 0

        # Check if snake goes out of bounds (collision with borders)
        if x1 >= WIDTH or x1 < 0 or y1 >= HEIGHT or y1 < 0:
            game_close = True

        x1 += x1_change
        y1 += y1_change
        screen.fill(BLUE)

        # Draw food
        pygame.draw.rect(screen, RED, [foodx, foody, snake_block, snake_block])

        # Snake body mechanics
        snake_Head = []
        snake_Head.append(x1)
        snake_Head.append(y1)
        snake_List.append(snake_Head)
        if len(snake_List) > Length_of_snake:
            del snake_List[0]

        # Check if snake collides with itself
        for x in snake_List[:-1]:
            if x == snake_Head:
                game_close = True

        # Draw the snake
        our_snake(snake_block, snake_List)
        your_score(Length_of_snake - 1)

        pygame.display.update()

        # Check if snake eats food
        if x1 == foodx and y1 == foody:
            foodx = round(random.randrange(0, WIDTH - snake_block) / 10.0) * 10.0
            foody = round(random.randrange(0, HEIGHT - snake_block) / 10.0) * 10.0
            Length_of_snake += 1

        # Set the speed of the snake
        clock.tick(snake_speed)

    pygame.quit()
    quit()

# Start the game
gameLoop()
