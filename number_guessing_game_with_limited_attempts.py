import random

class NumberGuessingGame:
    def __init__(self):
        self.min_number = 1  # Minimum number in the range
        self.max_number = 100  # Maximum number in the range
        self.max_attempts = 10  # Maximum number of attempts
        self.game_over = False  # Game over flag
        self.number_to_guess = 0  # The number the player needs to guess
        self.attempts_left = self.max_attempts  # Number of attempts remaining

    def generate_number(self):
        """Generates a random number between min_number and max_number."""
        self.number_to_guess = random.randint(self.min_number, self.max_number)

    def display_instructions(self):
        """Displays the instructions for the game."""
        print("Welcome to the Advanced Number Guessing Game!")
        print(f"Guess a number between {self.min_number} and {self.max_number}.")
        print(f"You have {self.max_attempts} attempts to guess the correct number.\n")

    def get_user_guess(self):
        """Prompts the user for their guess and ensures it's a valid number."""
        while True:
            try:
                guess = int(input(f"Guess a number (between {self.min_number} and {self.max_number}): "))
                if guess < self.min_number or guess > self.max_number:
                    print(f"Please enter a number between {self.min_number} and {self.max_number}.")
                else:
                    return guess
            except ValueError:
                print("Invalid input. Please enter a valid number.")

    def check_guess(self, guess):
        """Checks if the guess is correct, too high, or too low."""
        if guess < self.number_to_guess:
            print("Your guess is too low!")
        elif guess > self.number_to_guess:
            print("Your guess is too high!")
        else:
            print(f"Congratulations! You've guessed the number {self.number_to_guess} correctly!")
            return True
        return False

    def update_attempts(self):
        """Decreases the number of attempts left."""
        self.attempts_left -= 1

    def display_attempts_left(self):
        """Displays the number of attempts left."""
        print(f"Attempts left: {self.attempts_left}")

    def check_game_over(self):
        """Checks if the game is over (either guessed correctly or out of attempts)."""
        if self.attempts_left <= 0:
            print(f"Game Over! You've used all {self.max_attempts} attempts. The correct number was {self.number_to_guess}.")
            return True
        return False

    def reset_game(self):
        """Resets the game state for a new round."""
        self.attempts_left = self.max_attempts
        self.game_over = False
        self.generate_number()

    def ask_for_replay(self):
        """Asks if the player wants to play again."""
        while True:
            play_again = input("Do you want to play again? (yes/no): ").lower()
            if play_again == "yes":
                self.reset_game()
                self.play_game()
                break
            elif play_again == "no":
                print("Thank you for playing! Goodbye.")
                break
            else:
                print("Invalid input. Please enter 'yes' or 'no'.")

    def play_game(self):
        """Main game loop for Number Guessing Game."""
        self.display_instructions()
        self.generate_number()

        while not self.game_over:
            guess = self.get_user_guess()
            self.update_attempts()
            self.display_attempts_left()

            if self.check_guess(guess):
                self.game_over = True

            if not self.game_over:
                if self.check_game_over():
                    self.game_over = True

        self.ask_for_replay()


if __name__ == "__main__":
    game = NumberGuessingGame()  # Create an instance of the NumberGuessingGame class
    game.play_game()  # Start the game
