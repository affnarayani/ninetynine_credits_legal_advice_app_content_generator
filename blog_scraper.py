import requests
from bs4 import BeautifulSoup
import re
import json
import os
import urllib.parse
from urllib.request import urlretrieve
import time

def scrape_and_save_article(article_url, article_id, title):
    """
    Scrape the article content from the given URL and save it as a markdown file.
    
    Format:
    - Article title with ###
    - Article headings with ##
    - Article paragraphs with #
    """
    try:
        # Create raw_articles directory if it doesn't exist
        os.makedirs("raw_articles", exist_ok=True)
        
        # Send HTTP request to the article URL
        response = requests.get(article_url)
        
        # Check if the request was successful
        if response.status_code != 200:
            print(f"Failed to retrieve the article. Status code: {response.status_code}")
            return False
        
        # Parse the HTML content
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Find the main content of the article
        # This selector might need adjustment based on the actual structure of the blog
        article_content = soup.find('div', class_='brxe-block')
        
        if not article_content:
            print(f"Could not find article content for {article_id}")
            return False
        
        # Create markdown content
        markdown_content = f"### {title}\n\n"
        
        # Process headings and paragraphs
        skip_table_of_contents = False
        
        for element in article_content.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'p']):
            # Check if this is a "Table of Contents" heading
            if element.name.startswith('h') and element.text.strip() == "Table of Contents":
                skip_table_of_contents = True
                continue
            
            # If we're in the Table of Contents section, check if we've reached the next heading
            if skip_table_of_contents:
                if element.name.startswith('h'):
                    # We've reached the next heading after Table of Contents
                    skip_table_of_contents = False
                else:
                    # Still in Table of Contents, skip this element
                    continue
            
            # Process normal content
            if element.name.startswith('h') and element.name != 'h3':  # h3 is reserved for the title
                # This is a heading
                heading_text = element.text.strip()
                markdown_content += f"## {heading_text}\n\n"
            elif element.name == 'p':
                # This is a paragraph
                paragraph_text = element.text.strip()
                if paragraph_text:  # Only add non-empty paragraphs
                    markdown_content += f"# {paragraph_text}\n\n"
        
        # Remove any line containing contact@indialaw.in and everything below it
        lines = markdown_content.split('\n')
        filtered_lines = []
        
        for line in lines:
            if "contact@indialaw.in" in line:
                break
            filtered_lines.append(line)
        
        markdown_content = '\n'.join(filtered_lines).strip() + "\n\n"
        
        # Save to file
        file_path = os.path.join("raw_articles", f"{article_id}.md")
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(markdown_content)
        
        print(f"Article saved to {file_path}")
        return True
    
    except Exception as e:
        print(f"Error scraping article: {e}")
        return False

def save_image(img_url, article_id):
    """
    Save an image from a URL to the raw_images directory with the article ID as the filename.
    Preserves the original file extension.
    """
    # Create raw_images directory if it doesn't exist
    raw_images_dir = "raw_images"
    os.makedirs(raw_images_dir, exist_ok=True)
    
    try:
        # Get the file extension from the URL
        parsed_url = urllib.parse.urlparse(img_url)
        path = parsed_url.path
        ext = os.path.splitext(path)[1]
        
        # If no extension is found, default to .jpg
        if not ext:
            ext = ".jpg"
        
        # Create the full path for saving the image
        save_path = os.path.join(raw_images_dir, f"{article_id}{ext}")
        
        # Download and save the image
        response = requests.get(img_url, stream=True)
        if response.status_code == 200:
            with open(save_path, 'wb') as f:
                for chunk in response.iter_content(1024):
                    f.write(chunk)
            print(f"Image saved to {save_path}")
            return save_path
        else:
            print(f"Failed to download image: {response.status_code}")
            return None
    except Exception as e:
        print(f"Error saving image: {e}")
        return None

def scrape_indialaw_blog():
    # URL to scrape
    url = "https://www.indialaw.in/blog/"
    
    # Load history file to check for already processed article IDs
    history_file = "history.json"
    processed_ids = []
    
    if os.path.exists(history_file):
        try:
            with open(history_file, 'r') as f:
                history_data = json.load(f)
                # Extract IDs from history data
                for item in history_data:
                    if "id" in item:
                        processed_ids.append(item["id"])
        except Exception as e:
            print(f"Error loading history file: {e}")
    
    # Send HTTP request to the URL
    response = requests.get(url)
    
    # Check if the request was successful
    if response.status_code != 200:
        print(f"Failed to retrieve the webpage. Status code: {response.status_code}")
        return
    
    # Parse the HTML content
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Find the element with id="brxe-dae79b"
    target_element = soup.find(id="brxe-dae79b")
    
    if not target_element:
        print("Could not find the element with id='brxe-dae79b'")
        # As a fallback, let's try to find all blog posts
        print("Attempting to find all blog posts instead...")
        
        # Find all article elements or similar containers that might contain blog posts
        blog_posts = soup.find_all('a', href=re.compile(r'/blog/'))
        
        if not blog_posts:
            print("Could not find any blog posts.")
            return
        
        # Extract image links and titles
        article_count = 0
        
        for post in blog_posts:
            # Find image within the post
            img = post.find('img')
            img_link = img.get('src') if img else None
            
            # Find title within the post
            title_elem = post.find('h3')
            title_text = title_elem.text.strip() if title_elem else None
            
            # Remove "→" character from title
            if title_text:
                title_text = title_text.replace("→", "").strip()
            
            # Get the link URL
            link_url = post.get('href')
            
            # Skip articles that are missing either image OR title
            if not img_link or not title_text:
                continue
            
            # Extract ID from the URL
            # URL format: https://www.indialaw.in/blog/category/id/
            id_match = re.search(r'/blog/[^/]+/([^/]+)/?', link_url)
            article_id = id_match.group(1) if id_match else "unknown-id"
            
            # Skip articles that are already in history
            if article_id in processed_ids:
                continue
                
            # Save the image
            saved_image_path = save_image(img_link, article_id)
            
            # Scrape and save the article content
            article_saved = scrape_and_save_article(link_url, article_id, title_text)
            
            article_count += 1
            print(f"\nArticle {article_count}:")
            print("----------")
            print(f"ID: {article_id}")
            print(f"Link: {link_url}")
            print(f"Title: {title_text}")
            print(f"Image: {img_link}")
            if saved_image_path:
                print(f"Saved image to: {saved_image_path}")
            if article_saved:
                print(f"Saved article to: raw_articles/{article_id}.md")
            
            # If both image and article were saved successfully, add to history
            if saved_image_path and article_saved:
                processed_ids.append(article_id)
                # Update history file
                history_data = []
                for id in processed_ids:
                    history_data.append({"id": id})
                with open(history_file, 'w') as f:
                    json.dump(history_data, f, indent=4)
                print(f"Added {article_id} to history.json")

            # Add a small delay to avoid overwhelming the server
            time.sleep(1)
        
        if article_count == 0:
            print("No new articles found with both image and title.")
        
        return
    
    # If we found the target element, extract all images and titles within it
    articles = target_element.find_all('a', href=re.compile(r'/blog/'))
    
    # Print the results in the requested format
    article_count = 0
    
    for article in articles:
        # Find image within the article
        img = article.find('img')
        img_link = img.get('src') if img else None
        
        # Find title within the article
        title_elem = article.find('h3')
        title_text = title_elem.text.strip() if title_elem else None
        
        # Remove "→" character from title
        if title_text:
            title_text = title_text.replace("→", "").strip()
        
        # Get the link URL
        link_url = article.get('href')
        
        # Skip articles that are missing either image OR title
        if not img_link or not title_text:
            continue
        
        # Extract ID from the URL
        # URL format: https://www.indialaw.in/blog/category/id/
        id_match = re.search(r'/blog/[^/]+/([^/]+)/?', link_url)
        article_id = id_match.group(1) if id_match else "unknown-id"
        
        # Skip articles that are already in history
        if article_id in processed_ids:
            continue
            
        # Save the image
        saved_image_path = save_image(img_link, article_id)
        
        # Scrape and save the article content
        article_saved = scrape_and_save_article(link_url, article_id, title_text)
        
        article_count += 1
        print(f"\nArticle {article_count}:")
        print("----------")
        print(f"ID: {article_id}")
        print(f"Link: {link_url}")
        print(f"Title: {title_text}")
        print(f"Image: {img_link}")
        if saved_image_path:
            print(f"Saved image to: {saved_image_path}")
        if article_saved:
            print(f"Saved article to: raw_articles/{article_id}.md")
        
        # If both image and article were saved successfully, add to history
        if saved_image_path and article_saved:
            processed_ids.append(article_id)
            # Update history file
            history_data = []
            for id in processed_ids:
                history_data.append({"id": id})
            with open(history_file, 'w') as f:
                json.dump(history_data, f, indent=4)
            print(f"Added {article_id} to history.json")

        # Add a small delay to avoid overwhelming the server
        time.sleep(1)
    
    if article_count == 0:
        print("No new articles found.")

if __name__ == "__main__":
    scrape_indialaw_blog()