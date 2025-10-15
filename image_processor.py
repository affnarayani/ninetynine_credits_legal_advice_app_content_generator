import os
import sys
import time
from dotenv import load_dotenv
from google import genai
from google.genai import types
from PIL import Image
from io import BytesIO

# Define directories
RAW_IMAGES_DIR = "raw_images"
PROCESSED_IMAGES_DIR = "processed_images"

# Load environment variables
load_dotenv()

# Get API key from environment variable
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    print("Error: GEMINI_API_KEY not found in .env file")
    sys.exit(1)

# Initialize the Gemini client
client = genai.Client(api_key=api_key)

def generate_similar_image(image_path, output_path):
    """
    Generate a similar image using Gemini Flash 2.0 model and save it to the output path.
    The generated image will have a 1:1 aspect ratio (square).
    
    Args:
        image_path (str): Path to the input image
        output_path (str): Path to save the generated image
    
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        # Open the image
        image = Image.open(image_path)
        
        # Prepare the prompt
        text_input = ("Generate a similar image to this one, but with some creative variations "
                     "while maintaining the same style and theme. Make the image square with a 1:1 aspect ratio. "
                     "Important: Do not include any human fingers, hands, or partial human limbs in the image.",)
        
        # Generate content using Gemini model
        response = client.models.generate_content(
            model="gemini-2.5-flash-image",
            contents=[text_input, image],
            config=types.GenerateContentConfig(
                response_modalities=['TEXT', 'IMAGE']
            )
        )
        
        # Process the response
        for part in response.candidates[0].content.parts:
            if part.text is not None:
                print(part.text)
            elif part.inline_data is not None:
                generated_image = Image.open(BytesIO(part.inline_data.data))
                
                # Ensure the image has a 1:1 aspect ratio by stretching if necessary
                width, height = generated_image.size
                if width != height:
                    # Create a square size (1024x1024 is a common size for AI-generated images)
                    target_size = (1024, 1024)
                    
                    # Resize the image to fill the square completely (stretching it)
                    square_image = generated_image.resize(target_size, Image.LANCZOS)
                    
                    # Use the stretched square image
                    generated_image = square_image
                
                # Save the final 1:1 aspect ratio image
                generated_image.save(output_path)
                print(f"Successfully generated similar image for {os.path.basename(image_path)} with 1:1 aspect ratio")
                return True
        
        print(f"No image was generated for {os.path.basename(image_path)}")
        return False
        
    except Exception as e:
        print(f"Error generating similar image for {os.path.basename(image_path)}: {str(e)}")
        return False

def process_all_images():
    """
    Process all images in the raw_images directory and save generated similar images
    to the processed_images directory.
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
    
    print(f"Found {len(image_files)} images to process.")
    
    # Process each image
    successful_generations = 0
    for i, image_file in enumerate(image_files):
        input_path = os.path.join(RAW_IMAGES_DIR, image_file)
        output_path = os.path.join(PROCESSED_IMAGES_DIR, image_file)
        
        # Replace if the processed image already exists
        if os.path.exists(output_path):
            print(f"Processed image already exists at {output_path}. Replacing with new one.")
        
        # Generate similar image
        if generate_similar_image(input_path, output_path):
            successful_generations += 1
        
        # Add a 15-second delay between API calls (except after the last image)
        if i < len(image_files) - 1:
            print(f"Waiting 15 seconds before processing the next image...")
            time.sleep(15)
    
    print(f"\nProcessing complete. Successfully generated {successful_generations} out of {len(image_files)} images.")
    print(f"Generated images are saved in the '{PROCESSED_IMAGES_DIR}' directory.")

if __name__ == "__main__":
    process_all_images()