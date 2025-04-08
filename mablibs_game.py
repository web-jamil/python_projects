def get_user_input():
    # Ask the user for different types of words
    noun1 = input("Enter a noun: ")
    verb1 = input("Enter a verb (past tense): ")
    adjective1 = input("Enter an adjective: ")
    noun2 = input("Enter another noun: ")
    verb2 = input("Enter another verb (past tense): ")
    adjective2 = input("Enter another adjective: ")
    place = input("Enter a place: ")
    number = input("Enter a number: ")
    noun3 = input("Enter a third noun: ")

    return noun1, verb1, adjective1, noun2, verb2, adjective2, place, number, noun3

def create_story(noun1, verb1, adjective1, noun2, verb2, adjective2, place, number, noun3):
    # Create a story by plugging the user inputs into a predefined template
    story = f"""
    Once upon a time in a {place}, there was a {noun1} who loved to {verb1}. It was the most {adjective1} {noun1} 
    anyone had ever seen. One day, it met a {noun2} who {verb2} in a very {adjective2} way. The {noun2} told the {noun1}, 
    "I have {number} ideas to make this place better, and we need a {noun3} to help!"
    """
    return story

def main():
    print("Welcome to Mad Libs!")
    # Get the user's input
    noun1, verb1, adjective1, noun2, verb2, adjective2, place, number, noun3 = get_user_input()

    # Generate the story
    story = create_story(noun1, verb1, adjective1, noun2, verb2, adjective2, place, number, noun3)

    # Print the resulting story
    print("\nHere's your Mad Libs story!\n")
    print(story)

# Run the game
if __name__ == "__main__":
    main()
