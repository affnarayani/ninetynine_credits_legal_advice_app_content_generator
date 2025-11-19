import os
import shutil

# Define directories
RAW_IMAGES_DIR = "raw_images"
PROCESSED_IMAGES_DIR = "processed_images"

def copy_all_images():
    """
    Copies all images from the raw_images directory to the processed_images directory.
    """
    # Create processed_images directory if it doesn't exist
    os.makedirs(PROCESSED_IMAGES_DIR, exist_ok=True)
    
    # Get all files in the raw_images directory
    if not os.path.exists(RAW_IMAGES_DIR):
        print(f"Error: {RAW_IMAGES_DIR} directory does not exist.")
        return
    
    image_files = [f for f in os.listdir(RAW_IMAGES_DIR) 
                  if os.path.isfile(os.path.join(RAW_IMAGES_DIR, f)) and 
                  f.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp', '.webp'))]
    
    if not image_files:
        print(f"No image files found in {RAW_IMAGES_DIR} directory.")
        return
    
    print(f"Found {len(image_files)} images to copy.")
    
    # Copy each image
    copied_count = 0
    for image_file in image_files:
        src_path = os.path.join(RAW_IMAGES_DIR, image_file)
        dest_path = os.path.join(PROCESSED_IMAGES_DIR, image_file)
        
        try:
            shutil.copy2(src_path, dest_path)
            print(f"Copied {image_file} to {PROCESSED_IMAGES_DIR}")
            copied_count += 1
        except Exception as e:
            print(f"Error copying {image_file}: {e}")
            
    print(f"\nCopying complete. Successfully copied {copied_count} out of {len(image_files)} images.")
    print(f"Copied images are in the '{PROCESSED_IMAGES_DIR}' directory.")

if __name__ == "__main__":
    copy_all_images()
