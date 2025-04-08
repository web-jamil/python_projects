import random

class CoinTossGame:
    def __init__(self):
        self.total_score = 0  # Total score across all rounds
        self.best_streak = 0  # Best streak of consecutive correct guesses
        self.current_streak = 0  # Current streak of correct guesses
        self.rounds_played = 0  # Tracks how many rounds have been played

    def display_intro(self):
        """Displays the game introduction and available options."""
        print("Welcome to the Advanced Coin Toss Game!")
        print("In this game, you need to guess the outcome of a coin toss.")
        print("You can choose the difficulty level, which will affect the number of rounds per game.")
        print("Let's see how well you can predict the coin toss!")

    def set_difficulty(self):
        """Sets the difficulty level based on user input."""
        print("\nChoose a difficulty level:")
        print("1. Easy (1 toss per round)")
        print("2. Medium (3 tosses per round)")
        print("3. Hard (5 tosses per round)")
        
        while True:
            choice = input("Enter your choice (1/2/3): ")
            if choice == "1":
                self.num_tosses = 1
                break
            elif choice == "2":
                self.num_tosses = 3
                break
            elif choice == "3":
                self.num_tosses = 5
                break
            else:
                print("Invalid choice, please choose 1, 2, or 3.")
        
        print(f"Great! You will now guess the outcome of {self.num_tosses} tosses per round.")

    def toss_coin(self):
        """Simulate a coin toss (returns 'Heads' or 'Tails')."""
        return random.choice(['Heads', 'Tails'])

    def play_round(self):
        """Play a round where the player guesses multiple tosses."""
        correct_guesses = 0

        print(f"\nRound {self.rounds_played + 1}:")
        print(f"Guess whether the coin will land on 'Heads' or 'Tails' for each toss.")

        for i in range(self.num_tosses):
            while True:
                guess = input(f"Toss {i + 1} - Your guess (Heads/Tails): ").capitalize()
                if guess in ['Heads', 'Tails']:
                    break
                else:
                    print("Invalid input. Please enter 'Heads' or 'Tails'.")

            outcome = self.toss_coin()
            print(f"Toss {i + 1}: {outcome}")

            if guess == outcome:
                correct_guesses += 1
                print("You guessed correctly!")
            else:
                print("Sorry, wrong guess!")

        self.update_score(correct_guesses)

    def update_score(self, correct_guesses):
        """Update the score and streak based on the player's correct guesses."""
        self.rounds_played += 1
        score_for_round = correct_guesses * 10  # 10 points for each correct guess

        # Update total score
        self.total_score += score_for_round
        print(f"You earned {score_for_round} points this round.")

        # Update the best streak if the player guessed all tosses correctly
        if correct_guesses == self.num_tosses:
            self.current_streak += 1
            print("You've got a streak of correct guesses!")
        else:
            self.current_streak = 0  # Reset the streak if any guess was wrong
        
        if self.current_streak > self.best_streak:
            self.best_streak = self.current_streak
            print("New best streak!")

        print(f"Total Score: {self.total_score}")
        print(f"Current Streak: {self.current_streak}")
        print(f"Best Streak: {self.best_streak}")

    def play_game(self):
        """Main game loop that lets the user play multiple rounds."""
        self.display_intro()

        while True:
            self.set_difficulty()
            self.play_round()

            # Ask if the user wants to play another round
            play_again = input("\nDo you want to play another round? (yes/no): ").lower()
            if play_again != "yes":
                print("\nThank you for playing! Your final score: {}".format(self.total_score))
                print("Your best streak: {}".format(self.best_streak))
                break


if __name__ == "__main__":
    game = CoinTossGame()  # Create an instance of the CoinTossGame class
    game.play_game()  # Start the game
