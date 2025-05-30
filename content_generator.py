import os
import json
import glob
import re

def read_markdown_file(file_path):
    """
    Read a markdown file and extract the title and content
    """
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()
    
    # Extract title (first line starting with #)
    title_match = re.search(r'^# (.+)$', content, re.MULTILINE)
    title = title_match.group(1) if title_match else os.path.basename(file_path).replace('-', ' ').replace('.md', '').title()
    
    # Extract content (everything after the title)
    if title_match:
        content_text = content[title_match.end():].strip()
    else:
        content_text = content.strip()
    
    return title, content_text

def convert_to_html_paragraphs(text):
    """
    Convert markdown text to HTML paragraphs
    """
    # Split by double newlines (paragraph breaks)
    paragraphs = [p.strip() for p in text.split('\n\n') if p.strip()]
    
    # Wrap each paragraph in <p> tags
    html_paragraphs = [f"<p>{p}</p>" for p in paragraphs]
    
    # Join with newlines for readability
    return '\n\n'.join(html_paragraphs)

def generate_image_url(file_name):
    """
    Generate image URL based on the file name
    """
    # Keep the filename as is, preserving hyphens
    # Add appropriate extension
    image_url = f"https://affnarayani.github.io/ninetynine_credits_legal_advice_app_content/images/{file_name}.jpg"
    return image_url

def create_content_entry(file_path):
    """
    Create a content entry for a markdown file
    """
    file_name = os.path.basename(file_path).replace('.md', '')
    title, content = read_markdown_file(file_path)
    html_content = convert_to_html_paragraphs(content)
    image_url = generate_image_url(file_name)
    
    return {
        "title": title,
        "description": html_content,
        "image": image_url
    }

def update_content_json():
    """
    Update content.json with entries from processed_articles
    """
    # Get all markdown files in processed_articles
    processed_dir = os.path.join(os.getcwd(), 'processed_articles')
    article_files = glob.glob(os.path.join(processed_dir, '*.md'))
    
    if not article_files:
        print("No markdown files found in the processed_articles directory.")
        return
    
    # Read existing content.json
    content_json_path = os.path.join(os.getcwd(), 'content.json')
    with open(content_json_path, 'r', encoding='utf-8') as file:
        content_data = json.load(file)
    
    # Create new entries
    new_entries = []
    for file_path in article_files:
        try:
            entry = create_content_entry(file_path)
            new_entries.append(entry)
            print(f"Created entry for: {os.path.basename(file_path)}")
        except Exception as e:
            print(f"Error processing {file_path}: {str(e)}")
    
    # Add new entries to the beginning of the content data
    updated_content = new_entries + content_data
    
    # Write back to content.json
    with open(content_json_path, 'w', encoding='utf-8') as file:
        json.dump(updated_content, file, indent=2)
    
    print(f"Added {len(new_entries)} new entries to content.json")

if __name__ == "__main__":
    update_content_json()