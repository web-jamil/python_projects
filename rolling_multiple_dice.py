import random
import time
from collections import defaultdict

class DiceGame:
    DICE_ART = {
        1: [
            "┌───────┐",
            "│       │",
            "│   ●   │",
            "│       │",
            "└───────┘"
        ],
        2: [
            "┌───────┐",
            "│ ●     │",
            "│       │",
            "│     ● │",
            "└───────┘"
        ],
        3: [
            "┌───────┐",
            "│ ●     │",
            "│   ●   │",
            "│     ● │",
            "└───────┘"
        ],
        4: [
            "┌───────┐",
            "│ ●   ● │",
            "│       │",
            "│ ●   ● │",
            "└───────┘"
        ],
        5: [
            "┌───────┐",
            "│ ●   ● │",
            "│   ●   │",
            "│ ●   ● │",
            "└───────┘"
        ],
        6: [
            "┌───────┐",
            "│ ●   ● │",
            "│ ●   ● │",
            "│ ●   ● │",
            "└───────┘"
        ]
    }

    def __init__(self):
        self.history = []
        self.stats = defaultdict(int)
        self.running = True

    def roll_dice(self, num_dice=1, sides=6):
        """Roll dice and return results"""
        results = [random.randint(1, sides) for _ in range(num_dice)]
        self.history.extend(results)
        for num in results:
            self.stats[num] += 1
        return results

    def display_dice(self, results):
        """Show ASCII art of dice"""
        dice_faces = []
        for value in results:
            if 1 <= value <= 6:
                dice_faces.append(self.DICE_ART[value])
            else:
                # Generic display for non-standard dice
                generic_die = [
                    f"┌───────┐",
                    f"│       │",
                    f"│  {value:^3}  │",
                    f"│       │",
                    f"└───────┘"
                ]
                dice_faces.append(generic_die)
        
        # Print dice side by side
        for line in zip(*dice_faces):
            print("  ".join(line))

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

    def show_history(self):
        """Display last 10 rolls"""
        print("\n=== Recent Rolls ===")
        for i, roll in enumerate(self.history[-10:], 1):
            print(f"Roll {i}: {roll}")

    def animate_roll(self, duration=1.0, steps=10):
        """Show rolling animation"""
        for _ in range(steps):
            print("\rRolling: " + random.choice(["⚀", "⚁", "⚂", "⚃", "⚄", "⚅"]), end="")
            time.sleep(duration/steps)
        print("\r", end="")

    def show_menu(self):
        """Display game menu"""
        print("\n=== Dice Rolling Simulator ===")
        print("1. Roll single die (6 sides)")
        print("2. Roll multiple dice (6 sides)")
        print("3. Roll custom dice")
        print("4. View statistics")
        print("5. View roll history")
        print("6. Exit")

    def play(self):
        """Main game loop"""
        print("Welcome to the Dice Rolling Simulator!")
        print("You can roll standard 6-sided dice or create custom dice.")
        
        while self.running:
            self.show_menu()
            choice = input("\nEnter your choice (1-6): ").strip()

            if choice == "1":
                self.animate_roll()
                result = self.roll_dice()
                print("\nYou rolled:")
                self.display_dice(result)
                print(f"Total: {result[0]}")

            elif choice == "2":
                try:
                    num = int(input("How many dice? (1-10): "))
                    if 1 <= num <= 10:
                        self.animate_roll()
                        results = self.roll_dice(num)
                        print("\nYou rolled:")
                        self.display_dice(results)
                        print(f"Total: {sum(results)}")
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
                        print("\nYou rolled:")
                        self.display_dice(results)
                        print(f"Total: {sum(results)}")
                    else:
                        print("Invalid input range")
                except ValueError:
                    print("Please enter valid numbers")

            elif choice == "4":
                self.show_stats()

            elif choice == "5":
                self.show_history()

            elif choice == "6":
                self.running = False
                print("\nThanks for playing! Here are your final stats:")
                self.show_stats()

            else:
                print("Invalid choice. Please enter 1-6")

if __name__ == "__main__":
    game = DiceGame()
    game.play()