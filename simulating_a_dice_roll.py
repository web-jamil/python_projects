import random
import time
from collections import defaultdict

class DiceGame:
    def __init__(self):
        self.history = []
        self.stats = defaultdict(int)
        self.running = True

    def roll_dice(self, num_dice=1, sides=6):
        """Simulate rolling dice and return results"""
        results = [random.randint(1, sides) for _ in range(num_dice)]
        self.history.extend(results)
        for num in results:
            self.stats[num] += 1
        return results

    def show_stats(self):
        """Display rolling statistics"""
        print("\n=== Statistics ===")
        total_rolls = len(self.history)
        print(f"Total rolls: {total_rolls}")
        
        if total_rolls > 0:
            print("\nNumber frequencies:")
            for num, count in sorted(self.stats.items()):
                percentage = (count / total_rolls) * 100
                print(f"{num}: {count} rolls ({percentage:.1f}%)")
            
            print(f"\nAverage roll: {sum(self.history)/total_rolls:.2f}")
            print(f"Highest roll: {max(self.history)}")
            print(f"Lowest roll: {min(self.history)}")

    def show_menu(self):
        """Display game menu"""
        print("\n=== Dice Rolling Simulator ===")
        print("1. Roll one 6-sided die")
        print("2. Roll multiple 6-sided dice")
        print("3. Roll custom dice (choose sides)")
        print("4. View statistics")
        print("5. Exit")

    def animate_roll(self):
        """Show rolling animation"""
        for _ in range(3):
            print(".", end="", flush=True)
            time.sleep(0.3)
        print("")

    def play(self):
        """Main game loop"""
        while self.running:
            self.show_menu()
            choice = input("Enter your choice (1-5): ")

            if choice == "1":
                self.animate_roll()
                result = self.roll_dice()
                print(f"\nYou rolled: {result[0]}")
            elif choice == "2":
                try:
                    num = int(input("How many dice? (1-10): "))
                    if 1 <= num <= 10:
                        self.animate_roll()
                        results = self.roll_dice(num)
                        print(f"\nYou rolled: {results} (Total: {sum(results)})")
                    else:
                        print("Please enter between 1 and 10")
                except ValueError:
                    print("Please enter a valid number")
            elif choice == "3":
                try:
                    sides = int(input("How many sides? (2-100): "))
                    num = int(input("How many dice? (1-10): "))
                    if 2 <= sides <= 100 and 1 <= num <= 10:
                        self.animate_roll()
                        results = self.roll_dice(num, sides)
                        print(f"\nYou rolled: {results} (Total: {sum(results)})")
                    else:
                        print("Invalid input range")
                except ValueError:
                    print("Please enter valid numbers")
            elif choice == "4":
                self.show_stats()
            elif choice == "5":
                self.running = False
            else:
                print("Invalid choice. Please enter 1-5")

        print("\nThanks for playing!")

if __name__ == "__main__":
    game = DiceGame()
    game.play()