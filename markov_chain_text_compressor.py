import random
import re

# Function to clean and prepare the text (tokenization)
def clean_text(text):
    # Remove non-alphabetical characters and split the text into words
    text = re.sub(r'[^A-Za-z0-9\s]+', '', text)  # remove punctuation
    words = text.lower().split()
    return words

# Function to build the Markov Chain model
def build_markov_chain(words, n):
    markov_chain = {}
    
    # Iterate through the words and build the chain of n-grams
    for i in range(len(words) - n):
        key = tuple(words[i:i + n])
        next_word = words[i + n]
        
        # Add the next word to the list of words that follow the n-gram
        if key not in markov_chain:
            markov_chain[key] = [next_word]
        else:
            markov_chain[key].append(next_word)
    
    return markov_chain

# Function to generate text based on the Markov Chain
def generate_text(markov_chain, length, n):
    # Start with a random key (n-gram) from the chain
    start_key = random.choice(list(markov_chain.keys()))
    result = list(start_key)

    # Generate the text by repeatedly selecting the next word based on the n-gram
    for _ in range(length - n):
        current_key = tuple(result[-n:])  # Get the last n words to form the n-gram
        if current_key in markov_chain:
            next_word = random.choice(markov_chain[current_key])
            result.append(next_word)
        else:
            break  # Stop if we encounter a key that doesn't have a continuation
    
    return ' '.join(result)

# Main function to run the program
def main():
    # Load text file
    file_path = input("Enter the path of the text file: ")
    
    try:
        with open(file_path, 'r') as file:
            text = file.read()
    except Exception as e:
        print(f"Error reading file: {e}")
        return
    
    # Clean and prepare the text
    words = clean_text(text)
    
    # Build the Markov Chain model (choose n-gram size)
    n = int(input("Enter the n-gram size (e.g., 2 for bigrams, 3 for trigrams): "))
    markov_chain = build_markov_chain(words, n)
    
    # Generate text
    length = int(input("Enter the length of the generated text (number of words): "))
    generated_text = generate_text(markov_chain, length, n)
    
    print("\nGenerated Text:")
    print(generated_text)

if __name__ == "__main__":
    main()
