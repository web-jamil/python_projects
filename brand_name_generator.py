import random
import string

class BrandNameGenerator:
    def __init__(self, prefix_list=None, suffix_list=None):
        # If no prefix or suffix lists are provided, use default lists
        self.prefix_list = prefix_list or ["Pro", "Tech", "Mega", "Ultra", "Smart", "Velo", "Max"]
        self.suffix_list = suffix_list or ["ify", "verse", "works", "gen", "lab", "ly", "ex", "nova"]
        
        # Create an additional pool of random characters to spice up the brand names
        self.character_pool = string.ascii_uppercase + string.digits

    def generate_random_suffix(self):
        """Generate a random suffix for the brand name."""
        return random.choice(self.suffix_list)
    
    def generate_random_prefix(self):
        """Generate a random prefix for the brand name."""
        return random.choice(self.prefix_list)
    
    def generate_random_brand_name(self, base_name):
        """Generate a brand name by appending a random suffix or prefix to the base name."""
        # Randomly decide to add a prefix or a suffix
        add_prefix = random.choice([True, False])
        
        if add_prefix:
            brand_name = self.generate_random_prefix() + base_name
        else:
            brand_name = base_name + self.generate_random_suffix()
        
        # Add some random characters at the end for uniqueness
        random_chars = ''.join(random.choices(self.character_pool, k=3))  # Adding 3 random characters
        return brand_name + random_chars
    
    def get_user_input(self):
        """Get the base name from the user for brand generation."""
        print("Welcome to the Brand Name Generator Game!")
        print("Please provide a base name (e.g., 'Tech', 'Nova', 'Glide', etc.):")
        base_name = input().strip().capitalize()  # Capitalize to ensure it's properly formatted
        return base_name

    def generate_and_display_brand_names(self, base_name, num_names=5):
        """Generate and display a list of brand names based on the user's input."""
        print("\nHere are some brand name suggestions for you:")
        for _ in range(num_names):
            brand_name = self.generate_random_brand_name(base_name)
            print(f"- {brand_name}")

    def play_game(self):
        """Main game loop."""
        while True:
            base_name = self.get_user_input()
            num_names = input("How many brand names would you like to generate? (default is 5): ").strip()
            
            # Set a default number of names if input is empty or invalid
            if not num_names.isdigit():
                num_names = 5
            else:
                num_names = int(num_names)
            
            self.generate_and_display_brand_names(base_name, num_names)
            
            play_again = input("\nDo you want to generate more brand names? (yes/no): ").strip().lower()
            if play_again != "yes":
                print("Thank you for playing the Brand Name Generator Game!")
                break

if __name__ == "__main__":
    game = BrandNameGenerator()  # Create an instance of the BrandNameGenerator class
    game.play_game()  # Start the game
