import random

class HangmanGame:
    def __init__(self):
        self.word_list = self.load_word_list()  # List of words for the game
        self.max_attempts = 6  # Maximum number of incorrect guesses allowed
        self.word_to_guess = ""  # The word the player has to guess
        self.guessed_letters = []  # List to store the letters guessed so far
        self.incorrect_guesses = 0  # Tracks the number of incorrect guesses
        self.display_word = ""  # The word to display with guessed letters and underscores
        self.game_over = False

    def load_word_list(self):
        """Load a list of words from a text file. If not available, use a predefined list."""
        try:
            with open('words.txt', 'r') as file:
                return [line.strip() for line in file.readlines()]
        except FileNotFoundError:
            # Fallback to a hardcoded list if the file isn't found
            return ["python", "hangman", "developer", "algorithm", "challenge", "machine", "learning"]

    def choose_word(self):
        """Randomly choose a word from the word list."""
        self.word_to_guess = random.choice(self.word_list)
        self.display_word = "_" * len(self.word_to_guess)  # Initialize display with underscores

    def display_hangman(self):
        """Display the graphical hangman representation based on incorrect guesses."""
        hangman_graphics = [
            '''
               ------
               |    |
                    |
                    |
                    |
                    |
              =========''',  # 0 incorrect guesses
            '''
               ------
               |    |
               O    |
                    |
                    |
                    |
              =========''',  # 1 incorrect guess
            '''
               ------
               |    |
               O    |
               |    |
                    |
                    |
              =========''',  # 2 incorrect guesses
            '''
               ------
               |    |
               O    |
              /|    |
                    |
                    |
              =========''',  # 3 incorrect guesses
            '''
               ------
               |    |
               O    |
              /|\\   |
                    |
                    |
              =========''',  # 4 incorrect guesses
            '''
               ------
               |    |
               O    |
              /|\\   |
              /     |
                    |
              =========''',  # 5 incorrect guesses
            '''
               ------
               |    |
               O    |
              /|\\   |
              / \\   |
                    |
              ========='''  # 6 incorrect guesses
        ]
        print(hangman_graphics[self.incorrect_guesses])

    def get_guess(self):
        """Get the player's guess, ensuring it's a single letter and hasn't been guessed before."""
        while True:
            guess = input(f"Current word: {self.display_word}\nGuessed letters: {', '.join(self.guessed_letters)}\nGuess a letter: ").lower()
            if len(guess) != 1 or not guess.isalpha():
                print("Please enter a valid letter.")
            elif guess in self.guessed_letters:
                print("You've already guessed that letter. Try a different one.")
            else:
                return guess

    def update_display_word(self, guess):
        """Update the display word with the correct guess."""
        new_display_word = list(self.display_word)
        for i, letter in enumerate(self.word_to_guess):
            if letter == guess:
                new_display_word[i] = guess
        self.display_word = "".join(new_display_word)

    def check_game_over(self):
        """Check if the game is over, either by win or loss."""
        if "_" not in self.display_word:
            print(f"Congratulations! You've guessed the word '{self.word_to_guess}' correctly!")
            return True
        elif self.incorrect_guesses >= self.max_attempts:
            print(f"Game over! The word was '{self.word_to_guess}'.")
            return True
        return False

    def play_game(self):
        """Main game loop for Hangman."""
        self.choose_word()
        while not self.game_over:
            self.display_hangman()
            guess = self.get_guess()

            self.guessed_letters.append(guess)

            if guess in self.word_to_guess:
                print(f"Good guess! The letter '{guess}' is in the word.")
                self.update_display_word(guess)
            else:
                print(f"Oops! The letter '{guess}' is not in the word.")
                self.incorrect_guesses += 1

            self.game_over = self.check_game_over()

        print(f"Game Over. Your final word was '{self.word_to_guess}'.")
        self.ask_for_replay()

    def ask_for_replay(self):
        """Ask the player if they want to play again."""
        play_again = input("Do you want to play again? (yes/no): ").lower()
        if play_again == "yes":
            self.reset_game()
            self.play_game()
        else:
            print("Thank you for playing! Goodbye.")

    def reset_game(self):
        """Reset game variables for a new round."""
        self.incorrect_guesses = 0
        self.guessed_letters = []
        self.game_over = False
        self.display_word = ""


if __name__ == "__main__":
    game = HangmanGame()
    game.play_game()
