import random

class GuessTheNumberGame:
    def __init__(self):
        self.score = 0  # Keeps track of the player's score
        self.best_score = None  # Best score across all rounds
        self.max_attempts = 0  # Variable for the maximum attempts based on difficulty

    def set_difficulty(self):
        """Set the difficulty level for the game."""
        print("Welcome to Guess the Number Game!")
        print("Choose a difficulty level:")
        print("1. Easy (1 to 50) - 10 attempts")
        print("2. Medium (1 to 100) - 7 attempts")
        print("3. Hard (1 to 200) - 5 attempts")
        
        while True:
            choice = input("Enter the number corresponding to your choice (1/2/3): ")
            if choice == "1":
                self.max_attempts = 10
                self.range_start = 1
                self.range_end = 50
                break
            elif choice == "2":
                self.max_attempts = 7
                self.range_start = 1
                self.range_end = 100
                break
            elif choice == "3":
                self.max_attempts = 5
                self.range_start = 1
                self.range_end = 200
                break
            else:
                print("Invalid choice, please choose 1, 2, or 3.")
        
        print(f"Great! You have {self.max_attempts} attempts to guess the number between {self.range_start} and {self.range_end}.")

    def play_round(self):
        """Play a round of the game."""
        number = random.randint(self.range_start, self.range_end)
        attempts_left = self.max_attempts
        attempts = 0
        
        print("\nStart guessing!")
        
        while attempts_left > 0:
            guess = input(f"Attempts left: {attempts_left}. Enter your guess: ")
            if not guess.isdigit():
                print("Please enter a valid number.")
                continue
            guess = int(guess)
            
            attempts += 1
            attempts_left -= 1

            if guess < number:
                print("Too low! Try again.")
            elif guess > number:
                print("Too high! Try again.")
            else:
                print(f"Congratulations! You've guessed the number {number} in {attempts} attempts.")
                self.update_score(attempts)
                break
        else:
            print(f"Sorry! You've run out of attempts. The correct number was {number}.")
            self.update_score(attempts)
    
    def update_score(self, attempts):
        """Update the score based on how many attempts were used."""
        score = max(0, self.max_attempts - attempts + 1)
        print(f"You earned {score} points for this round.")
        self.score += score
        
        if self.best_score is None or self.score > self.best_score:
            self.best_score = self.score
            print("New best score!")
        print(f"Total Score: {self.score}")
    
    def play_game(self):
        """Main game loop to allow multiple rounds."""
        while True:
            self.set_difficulty()
            self.play_round()

            play_again = input("\nDo you want to play another round? (yes/no): ").lower()
            if play_again != "yes":
                print(f"\nThank you for playing! Your total score: {self.score}")
                print(f"Your best score was: {self.best_score}")
                break

if __name__ == "__main__":
    game = GuessTheNumberGame()  # Create an instance of the game
    game.play_game()  # Start the game
