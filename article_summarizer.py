import os
import glob
from google import genai  # Naya import structure
from dotenv import load_dotenv
import re
import time

# Load environment variables
load_dotenv()

# Client initialize karein (genai.configure ki jagah)
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

def summarize_article(content):
    """
    Summarize an article using the new Google Gen AI SDK
    """
    # Model name updated to latest stable version
    model_id = 'gemini-2.5-flash' 
    
    # Title extraction logic (vahi rahega)
    title = ""
    lines = content.strip().split('\n')
    for line in lines:
        if line.startswith('# ') or line.startswith('## ') or line.startswith('### '):
            title = line.lstrip('#').strip()
            break
    
    prompt = f"""
    Summarize the following article in maximum 2000 characters.
    Maintain the key points and professional tone.
    Keep the summary informative and concise.
    Format the output as proper Markdown with:
    1. A main heading (H1) with the article title
    2. Well-structured paragraphs
    3. Proper Markdown syntax
    
    Article:
    {content}
    """
    
    # Naya syntax: client.models.generate_content
    response = client.models.generate_content(
        model=model_id,
        contents=prompt
    )
    
    summary = response.text
    
    if not summary.startswith('#') and title:
        summary = f"# {title}\n\n{summary}"
    
    return summary

# Baki functions (process_article aur main) same rahenge
# Bas summarize_article ke andar ka API call badla hai.

def process_article(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()
    
    filename = os.path.basename(file_path)
    name_without_ext = os.path.splitext(filename)[0]
    
    output_dir = os.path.join(os.path.dirname(os.path.dirname(file_path)), 'processed_articles')
    os.makedirs(output_dir, exist_ok=True)
    
    summary = summarize_article(content)
    
    if not summary.strip():
        title = name_without_ext.replace('-', ' ').title()
        summary = f"# {title}\n\nNo summary available for this article."
    elif not any(line.startswith('#') for line in summary.split('\n')):
        title = name_without_ext.replace('-', ' ').title()
        summary = f"# {title}\n\n{summary}"
    
    output_path = os.path.join(output_dir, f"{name_without_ext}.md")
    with open(output_path, 'w', encoding='utf-8') as file:
        file.write(summary)
    
    return output_path

def main():
    raw_articles_dir = os.path.join(os.getcwd(), 'raw_articles')
    article_files = glob.glob(os.path.join(raw_articles_dir, '*.md'))
    
    if not article_files:
        print("No markdown files found.")
        return
    
    for i, file_path in enumerate(article_files):
        try:
            if i > 0:
                print(f"Waiting 15 seconds...")
                time.sleep(15)
                
            output_path = process_article(file_path)
            print(f"Success: {output_path}")
        except Exception as e:
            print(f"Error processing {file_path}: {str(e)}")

if __name__ == "__main__":
    main()