import qrcode
import cv2

# Function to create a QR code
def create_qr_code(message):
    # Generate QR Code
    qr = qrcode.QRCode(
        version=1,  # size of the QR code
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,  # size of each box in the QR code
        border=4,  # thickness of the border
    )
    qr.add_data(message)
    qr.make(fit=True)

    # Create an image from the QR code
    img = qr.make_image(fill='black', back_color='white')
    img.show()  # This will display the generated QR code image

    # Save the QR code as a PNG file
    img.save("generated_qr_code.png")
    print("QR Code has been generated and saved as 'generated_qr_code.png'.")

# Function to decode a QR code from an image file
def decode_qr_code():
    # Read the image file
    img = cv2.imread('generated_qr_code.png')  # Assume the generated QR code is saved as 'generated_qr_code.png'
    detector = cv2.QRCodeDetector()

    # Detect and decode the QR code
    value, pts, qr_code = detector(img)
    
    if value:
        print(f"Decoded message from QR Code: {value}")
    else:
        print("Failed to decode the QR code.")

# Display the game menu to the user
def display_menu():
    print("\n==== QR Code Encoder and Decoder Game ====")
    print("1. Generate QR Code from Message")
    print("2. Decode QR Code from Image")
    print("3. Exit")
    choice = input("Choose an option (1/2/3): ")
    return choice

# Main game loop
def run_qr_game():
    while True:
        choice = display_menu()
        
        if choice == '1':
            message = input("Enter the message you want to encode into a QR Code: ")
            create_qr_code(message)
        elif choice == '2':
            print("Decoding QR Code from the file 'generated_qr_code.png'...")
            decode_qr_code()
        elif choice == '3':
            print("Exiting the game. Goodbye!")
            break
        else:
            print("Invalid choice! Please choose a valid option.")

# Start the game
if __name__ == "__main__":
    run_qr_game()
