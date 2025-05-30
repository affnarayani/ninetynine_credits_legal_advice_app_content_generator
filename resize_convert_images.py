import os
from PIL import Image
import glob

def resize_and_convert_images(folder_path='raw_images'):
    """
    Converts all images in the specified folder to JPG format and resizes them to 1024x1024.
    Saves the output to the same folder with the same name, replacing the original files.
    
    Args:
        folder_path (str): Path to the folder containing images to process
    """
    # Ensure the folder path exists
    if not os.path.exists(folder_path):
        print(f"Error: The folder '{folder_path}' does not exist.")
        return

    # Get all image files in the folder
    image_extensions = ['*.png', '*.jpg', '*.jpeg', '*.bmp', '*.gif', '*.tiff', '*.webp']
    image_files = []

    for ext in image_extensions:
        image_files.extend(glob.glob(os.path.join(folder_path, ext)))

    if not image_files:
        print(f"No image files found in '{folder_path}'.")
        return

    print(f"Found {len(image_files)} images to process.")

    # Process each image
    for img_path in image_files:
        try:
            # Open the image
            with Image.open(img_path) as img:
                # Convert to RGB mode (required for JPG format)
                if img.mode != 'RGB':
                    img = img.convert('RGB')

                # Resize the image to 1024x1024
                resized_img = img.resize((1024, 1024), Image.Resampling.LANCZOS)

                # Get the output path (same name but with .jpg extension)
                output_path = os.path.splitext(img_path)[0] + '.jpg'

                # Save the resized image
                resized_img.save(output_path, 'JPEG', quality=95)

                print(f"Processed: {img_path} -> {output_path}")

                # If the original file is not a jpg and has a different path, remove it
                if img_path != output_path:
                    os.remove(img_path)
                    print(f"Removed original: {img_path}")

        except Exception as e:
            print(f"Error processing {img_path}: {e}")

if __name__ == "__main__":
    resize_and_convert_images()
    print("Image processing complete!")