import os
import glob
import google.generativeai as genai
from dotenv import load_dotenv
import re
import time

# Load environment variables
load_dotenv()

# Configure the Gemini API
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

def summarize_article(content):
    """
    Summarize an article using Gemini API
    """
    model = genai.GenerativeModel('gemini-2.5-flash')
    
    # Extract the title from the content if it exists
    title = ""
    lines = content.strip().split('\n')
    for line in lines:
        if line.startswith('# ') or line.startswith('## ') or line.startswith('### '):
            title = line.lstrip('#').strip()
            break
    
    prompt = f"""
    Summarize the following article.
    Maintain the key points and professional tone.
    Keep the summary informative and concise.
    Format the output as proper Markdown with:
    1. A main heading (H1) with the article title
    2. Well-structured paragraphs
    3. Proper Markdown syntax
    
    Article:
    {content}
    """
    
    response = model.generate_content(prompt)
    summary = response.text
    
    # If the summary doesn't start with a heading and we have a title, add it
    if not summary.startswith('#') and title:
        summary = f"# {title}\n\n{summary}"
    
    return summary

def process_article(file_path):
    """
    Process a single article file
    """
    # Read the article content
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()
    
    # Get the filename without extension
    filename = os.path.basename(file_path)
    name_without_ext = os.path.splitext(filename)[0]
    
    # Create the output directory if it doesn't exist
    output_dir = os.path.join(os.path.dirname(os.path.dirname(file_path)), 'processed_articles')
    os.makedirs(output_dir, exist_ok=True)
    
    # Generate the summary
    summary = summarize_article(content)
    
    # Ensure the summary follows Markdown standards
    if not summary.strip():
        # If summary is empty, create a basic markdown structure
        title = name_without_ext.replace('-', ' ').title()
        summary = f"# {title}\n\nNo summary available for this article."
    elif not any(line.startswith('#') for line in summary.split('\n')):
        # If no headings are found, add a title based on the filename
        title = name_without_ext.replace('-', ' ').title()
        summary = f"# {title}\n\n{summary}"
    
    # Save the summary to a new file
    output_path = os.path.join(output_dir, f"{name_without_ext}.md")
    with open(output_path, 'w', encoding='utf-8') as file:
        file.write(summary)
    
    print(f"Processed: {filename} -> {output_path}")
    return output_path

def main():
    # Process the article from raw_articles folder
    raw_articles_dir = os.path.join(os.getcwd(), 'raw_articles')
    
    # Get all markdown files
    article_files = glob.glob(os.path.join(raw_articles_dir, '*.md'))
    
    if not article_files:
        print("No markdown files found in the raw_articles directory.")
        return
    
    # Process each article
    for i, file_path in enumerate(article_files):
        try:
            # Add a delay between API requests (except for the first one)
            if i > 0:
                print(f"Waiting 15 seconds before processing the next article...")
                time.sleep(15)
                
            output_path = process_article(file_path)
            print(f"Successfully processed and saved to: {output_path}")
        except Exception as e:
            print(f"Error processing {file_path}: {str(e)}")

if __name__ == "__main__":
    main()