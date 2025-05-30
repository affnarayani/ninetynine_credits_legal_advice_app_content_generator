import os
import shutil

def clean_folders(folders=None):
    """
    Clears the contents of the specified folders without deleting the folders themselves.
    
    Args:
        folders (list): List of folder names to clear. If None, defaults to 
                       ['raw_images', 'raw_articles', 'processed_articles', 'processed_images']
    """
    if folders is None:
        folders = ['raw_images', 'raw_articles', 'processed_articles', 'processed_images']
    
    for folder in folders:
        if os.path.exists(folder):
            print(f"Cleaning folder: {folder}")
            # Get all items in the folder
            for item in os.listdir(folder):
                item_path = os.path.join(folder, item)
                try:
                    if os.path.isfile(item_path):
                        # Remove file
                        os.unlink(item_path)
                        print(f"  Removed file: {item_path}")
                    elif os.path.isdir(item_path):
                        # Remove directory and all its contents
                        shutil.rmtree(item_path)
                        print(f"  Removed directory: {item_path}")
                except Exception as e:
                    print(f"  Error while removing {item_path}: {e}")
        else:
            print(f"Warning: Folder '{folder}' does not exist.")

if __name__ == "__main__":
    print("Starting cleanup process...")
    clean_folders()
    print("Cleanup complete!")