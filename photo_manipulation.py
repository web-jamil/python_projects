from PIL import Image, ImageEnhance, ImageFilter
import os

# Function to open an image
def open_image(image_path):
    try:
        image = Image.open(image_path)
        return image
    except Exception as e:
        print(f"Error: {e}")
        return None

# Function to save an image
def save_image(image, output_path):
    try:
        image.save(output_path)
        print(f"Image saved at {output_path}")
    except Exception as e:
        print(f"Error saving image: {e}")

# Function to resize an image
def resize_image(image, width, height):
    return image.resize((width, height))

# Function to crop an image
def crop_image(image, left, top, right, bottom):
    return image.crop((left, top, right, bottom))

# Function to rotate an image
def rotate_image(image, angle):
    return image.rotate(angle)

# Function to flip an image horizontally
def flip_image_horizontal(image):
    return image.transpose(Image.FLIP_LEFT_RIGHT)

# Function to flip an image vertically
def flip_image_vertical(image):
    return image.transpose(Image.FLIP_TOP_BOTTOM)

# Function to apply a blur filter to the image
def apply_blur(image):
    return image.filter(ImageFilter.GaussianBlur(5))

# Function to adjust image brightness
def adjust_brightness(image, factor):
    enhancer = ImageEnhance.Brightness(image)
    return enhancer.enhance(factor)

# Function to adjust image contrast
def adjust_contrast(image, factor):
    enhancer = ImageEnhance.Contrast(image)
    return enhancer.enhance(factor)

# Function to apply sharpen filter
def sharpen_image(image):
    enhancer = ImageEnhance.Sharpness(image)
    return enhancer.enhance(2.0)  # Sharpening by a factor of 2.0

# Main function to manipulate the image
def main():
    image_path = input("Enter the path to the image you want to manipulate: ")
    
    # Open image
    image = open_image(image_path)
    if image is None:
        return

    print("Select the manipulation to perform:")
    print("1. Resize")
    print("2. Crop")
    print("3. Rotate")
    print("4. Flip (Horizontal)")
    print("5. Flip (Vertical)")
    print("6. Apply Blur")
    print("7. Adjust Brightness")
    print("8. Adjust Contrast")
    print("9. Apply Sharpen")

    choice = input("Enter your choice (1-9): ")

    if choice == '1':  # Resize
        width = int(input("Enter the new width: "))
        height = int(input("Enter the new height: "))
        image = resize_image(image, width, height)
    elif choice == '2':  # Crop
        left = int(input("Enter the left coordinate: "))
        top = int(input("Enter the top coordinate: "))
        right = int(input("Enter the right coordinate: "))
        bottom = int(input("Enter the bottom coordinate: "))
        image = crop_image(image, left, top, right, bottom)
    elif choice == '3':  # Rotate
        angle = int(input("Enter the angle to rotate: "))
        image = rotate_image(image, angle)
    elif choice == '4':  # Flip Horizontal
        image = flip_image_horizontal(image)
    elif choice == '5':  # Flip Vertical
        image = flip_image_vertical(image)
    elif choice == '6':  # Apply Blur
        image = apply_blur(image)
    elif choice == '7':  # Adjust Brightness
        factor = float(input("Enter brightness factor (e.g., 1.2 for brighter): "))
        image = adjust_brightness(image, factor)
    elif choice == '8':  # Adjust Contrast
        factor = float(input("Enter contrast factor (e.g., 1.2 for more contrast): "))
        image = adjust_contrast(image, factor)
    elif choice == '9':  # Sharpen Image
        image = sharpen_image(image)
    else:
        print("Invalid choice")
        return

    # Show manipulated image
    image.show()

    # Save manipulated image
    output_path = input("Enter the path to save the manipulated image (e.g., 'output.jpg'): ")
    save_image(image, output_path)

if __name__ == "__main__":
    main()
