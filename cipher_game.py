import random
import string

# Caesar Cipher Function
def caesar_cipher(text, shift, mode='encrypt'):
    result = ""
    for char in text:
        if char.isalpha():
            # Get ASCII value of character
            shift_amount = shift if mode == 'encrypt' else -shift
            start = ord('A') if char.isupper() else ord('a')
            # Apply Caesar cipher formula
            new_char = chr((ord(char) - start + shift_amount) % 26 + start)
            result += new_char
        else:
            result += char  # Non-alphabet characters are not encrypted
    return result


# Substitution Cipher Function
def substitution_cipher(text, key, mode='encrypt'):
    alphabet = string.ascii_lowercase
    key_dict = dict(zip(alphabet, key))
    
    if mode == 'decrypt':
        key_dict = {v: k for k, v in key_dict.items()}  # Invert the key for decryption

    result = ""
    for char in text:
        if char.isalpha():
            new_char = key_dict[char.lower()]
            # Preserve the case (uppercase or lowercase)
            if char.isupper():
                result += new_char.upper()
            else:
                result += new_char
        else:
            result += char  # Non-alphabet characters are not encrypted
    return result


# Generate random substitution key
def generate_substitution_key():
    alphabet = list(string.ascii_lowercase)
    random.shuffle(alphabet)
    return ''.join(alphabet)


# Display the Cipher Game Menu
def display_menu():
    print("\n==== Cipher Game ====")
    print("1. Caesar Cipher")
    print("2. Substitution Cipher")
    print("3. Exit")
    choice = input("Choose a cipher (1/2/3): ")
    return choice


# Function for handling the Caesar Cipher Game
def caesar_game():
    text = input("Enter the text you want to encrypt/decrypt: ")
    shift = int(input("Enter the shift value (1-25): "))
    mode = input("Do you want to Encrypt or Decrypt? (e/d): ").lower()

    if mode == 'e':
        result = caesar_cipher(text, shift, 'encrypt')
        print(f"Encrypted Text: {result}")
    elif mode == 'd':
        result = caesar_cipher(text, shift, 'decrypt')
        print(f"Decrypted Text: {result}")
    else:
        print("Invalid choice! Please choose either 'e' for encrypt or 'd' for decrypt.")


# Function for handling the Substitution Cipher Game
def substitution_game():
    text = input("Enter the text you want to encrypt/decrypt: ")
    mode = input("Do you want to Encrypt or Decrypt? (e/d): ").lower()

    key = input("Enter the substitution key (26 characters, without repeating letters): ").lower()

    if len(key) != 26 or len(set(key)) != 26 or not key.isalpha():
        print("Invalid key! The key must contain exactly 26 characters and no repeating letters.")
        return

    if mode == 'e':
        result = substitution_cipher(text, key, 'encrypt')
        print(f"Encrypted Text: {result}")
    elif mode == 'd':
        result = substitution_cipher(text, key, 'decrypt')
        print(f"Decrypted Text: {result}")
    else:
        print("Invalid choice! Please choose either 'e' for encrypt or 'd' for decrypt.")


# Main function to run the Cipher Game
def run_cipher_game():
    while True:
        choice = display_menu()
        if choice == '1':
            caesar_game()
        elif choice == '2':
            substitution_game()
        elif choice == '3':
            print("Exiting Cipher Game. Goodbye!")
            break
        else:
            print("Invalid choice! Please choose a valid option.")

# Start the game
if __name__ == "__main__":
    run_cipher_game()
