import pygame
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
YELLOW = (255, 255, 0)

# Set up the screen
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Space Invaders")

# Set up fonts
font = pygame.font.SysFont("comicsansms", 30)

# Load images
player_image = pygame.image.load('spaceship.png')
player_rect = player_image.get_rect()

# Player class to represent the spaceship
class Player:
    def __init__(self):
        self.x = WIDTH // 2 - player_rect.width // 2
        self.y = HEIGHT - player_rect.height - 10
        self.speed = 10

    def move(self, left, right):
        keys = pygame.key.get_pressed()
        if keys[left] and self.x > 0:
            self.x -= self.speed
        if keys[right] and self.x < WIDTH - player_rect.width:
            self.x += self.speed

    def draw(self, screen):
        screen.blit(player_image, (self.x, self.y))

# Bullet class to represent the bullets fired by the player
class Bullet:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = 5
        self.height = 10
        self.speed = 10

    def move(self):
        self.y -= self.speed

    def draw(self, screen):
        pygame.draw.rect(screen, YELLOW, (self.x + 20, self.y, self.width, self.height))

# Enemy class to represent the alien invaders
class Enemy:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = 50
        self.height = 50
        self.speed = 2

    def move(self):
        self.y += self.speed

    def draw(self, screen):
        pygame.draw.rect(screen, RED, (self.x, self.y, self.width, self.height))

# Function to display the score
def display_score(score):
    score_text = font.render(f"Score: {score}", True, WHITE)
    screen.blit(score_text, (10, 10))

# Main game loop
def game_loop():
    player = Player()
    bullets = []
    enemies = []
    score = 0

    # Create enemies
    for i in range(5):
        for j in range(3):
            enemy = Enemy(100 + i * 100, 50 + j * 50)
            enemies.append(enemy)

    clock = pygame.time.Clock()

    game_over = False
    while not game_over:
        screen.fill(BLACK)

        # Draw player and enemies
        player.draw(screen)

        for enemy in enemies:
            enemy.move()
            enemy.draw(screen)

        for bullet in bullets:
            bullet.move()
            bullet.draw(screen)

        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                game_over = True
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    bullet = Bullet(player.x, player.y)
                    bullets.append(bullet)

        # Move the player
        player.move(pygame.K_LEFT, pygame.K_RIGHT)

        # Check for collisions with enemies
        for bullet in bullets:
            for enemy in enemies:
                if enemy.x < bullet.x + bullet.width and enemy.x + enemy.width > bullet.x and \
                   enemy.y < bullet.y + bullet.height and enemy.y + enemy.height > bullet.y:
                    bullets.remove(bullet)
                    enemies.remove(enemy)
                    score += 10

        # Remove bullets that go off-screen
        for bullet in bullets[:]:
            if bullet.y < 0:
                bullets.remove(bullet)

        # Check if any enemy reaches the bottom
        for enemy in enemies:
            if enemy.y >= HEIGHT - enemy.height:
                game_over = True
                break

        # Display score
        display_score(score)

        pygame.display.update()

        clock.tick(60)

    # Display game over screen
    game_over_text = font.render("Game Over!", True, WHITE)
    screen.blit(game_over_text, (WIDTH // 2 - game_over_text.get_width() // 2, HEIGHT // 2))

    pygame.display.update()
    pygame.time.wait(2000)

    pygame.quit()

# Start the game
if __name__ == "__main__":
    game_loop()
