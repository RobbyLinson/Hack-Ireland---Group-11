from flask import Flask, request, jsonify
from flask_cors import CORS
from readability import Document
from bs4 import BeautifulSoup
import requests
import json
import re

app = Flask(__name__)
CORS(app)

def fetch_webpage(url):
    headers = {
        "User-Agent": ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                       "AppleWebKit/537.36 (KHTML, like Gecko) "
                       "Chrome/90.0.4430.93 Safari/537.36")
    }
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()  # Raises HTTPError for bad responses
        return response.text
    except requests.exceptions.RequestException as e:
        print(f"Error fetching URL: {e}")
        return None

def parse_with_readability(html_content):
    # Use readability to extract the main content and title
    doc = Document(html_content)
    summary_html = doc.summary()
    title = doc.title()
    
    # Parse the summary HTML using BeautifulSoup
    soup = BeautifulSoup(summary_html, "lxml")
    text = soup.get_text(separator="\n")
    
    # Clean up the extracted text:
    lines = [line.strip() for line in text.splitlines()]
    clean_lines = [line for line in lines if line]
    clean_text = "\n".join(clean_lines)
    clean_text = re.sub(r'\s{2,}', ' ', clean_text)
    
    # Remove non-ASCII characters (applied to clean_text)
    clean_text = re.sub(r'[^\x00-\x7F]+', '', clean_text)
    
    # Remove all newline characters by replacing them with a space
    clean_text = clean_text.replace('\n', ' ')
    
    return clean_text, title

@app.route('/scrape', methods=['POST'])
def scrape():
    # Get JSON data from the POST request
    data = request.get_json()
    url = data.get("url")
    if not url:
        return jsonify({"error": "Missing URL parameter"}), 400

    # Fetch the webpage content
    html_content = fetch_webpage(url)
    if not html_content:
        return jsonify({"error": "Failed to fetch webpage content"}), 500

    # Parse the webpage content using readability and BeautifulSoup
    parsed_text, title = parse_with_readability(html_content)

    # Prepare the result dictionary
    result = {
        "url": url,
        "title": title,
        "text": parsed_text
    }

    # Save the result to a JSON file
    try:
        with open("scraped_result.json", "w", encoding="utf-8") as f:
            json.dump(result, f, ensure_ascii=False, indent=4)
    except Exception as e:
        print(f"Error writing JSON to file: {e}")

    # Return the result as a JSON response
    return jsonify(result)

if __name__ == "__main__":
    app.run(debug=True)
