from flask import Flask, request, jsonify
from flask_cors import CORS
from bs4 import BeautifulSoup
import requests
import re
import nltk
from nltk.corpus import stopwords
import time
import urllib.parse

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Download stopwords
nltk.download('stopwords')

BIAS_API_URL = "https://popular-strongly-lemur.ngrok-free.app/api/analyze/"

# Function to fetch webpage content with exponential backoff
def fetch_webpage(url, max_retries=5, backoff_factor=1):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.93 Safari/537.36"
    }
    for attempt in range(1, max_retries + 1):
        try:
            print(f"Fetching URL: {url} (Attempt {attempt})")
            response = requests.get(url, headers=headers, timeout=10)
            if response.status_code == 429:
                raise requests.exceptions.RequestException("429 Too Many Requests")
            response.raise_for_status()
            print("Successfully fetched webpage.")
            return response.text
        except requests.exceptions.RequestException as e:
            print(f"Error fetching URL: {e}")
            if attempt == max_retries or response.status_code != 429:
                return None
            sleep_time = backoff_factor * (2 ** (attempt - 1))
            print(f"Retrying in {sleep_time} seconds...")
            time.sleep(sleep_time)

# Function to parse content using BeautifulSoup
def parse_with_beautifulsoup(html_content):
    soup = BeautifulSoup(html_content, "html.parser")
    title = soup.title.string if soup.title else "No Title Found"
    paragraphs = soup.find_all('p')
    text = ' '.join([para.get_text() for para in paragraphs])
    text = re.sub(r'\s+', ' ', text)  # Remove excessive whitespace
    text = re.sub(r'[^\x00-\x7F]+', '', text)  # Remove non-ASCII characters
    print(f"Extracted title: {title}")
    return text, title

# API endpoint to scrape an article
@app.route('/scrape', methods=['POST'])
def scrape():
    data = request.get_json()
    url = data.get("url")
    if not url:
        return jsonify({"error": "Missing URL parameter"}), 400

    print(f"Scraping article: {url}")
    html_content = fetch_webpage(url)
    if not html_content:
        return jsonify({"error": "Failed to fetch webpage content"}), 500

    parsed_text, title = parse_with_beautifulsoup(html_content)
    result = {"url": url, "title": title, "text": parsed_text}
    print(f"Scrape result: {title}")
    return jsonify(result)

# Function to get the bias of an article
def get_article_bias(article_url):
    # Fetch the article's HTML content
    html_content = fetch_webpage(article_url)
    if not html_content:
        print(f"Failed to fetch content for URL: {article_url}")
        return None

    # Parse the HTML to extract text
    article_text, _ = parse_with_beautifulsoup(html_content)

    # Send the extracted text to the bias analysis API
    try:
        response = requests.post(BIAS_API_URL, json={"text": article_text})
        if response.status_code == 200:
            print(response.json())
            return response.json().get("bias_analysis")  # Returns "Left", "Middle", or "Right"
        else:
            print(f"Bias API returned status code {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"Error fetching bias for {article_url}: {e}")
    return None


# Function to extract keywords from an article title
def extract_keywords(title):
    stop_words = set(stopwords.words('english'))
    words = re.findall(r'\b\w+\b', title.lower())
    keywords = [word for word in words if word not in stop_words]
    print(f"Extracted keywords: {keywords}")
    return keywords

# Function to perform a search and retrieve article URLs
def search_articles(keywords, max_articles=10):
    query = '+'.join(keywords)
    search_url = f"https://www.bing.com/search?q={query}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.93 Safari/537.36"
    }
    
    print(f"Searching for articles with query: {query}")
    response = fetch_webpage(search_url)
    if not response:
        print("Failed to retrieve search results.")
        return []

    soup = BeautifulSoup(response, "html.parser")
    search_results = soup.find_all('a', href=True)

    # Extracting article URLs
    article_urls = []
    ignored_count = 0  

    for result in search_results:
        href = result['href']
        
        # Ignore unnecessary Bing-specific links
        if not href.startswith("http") or "bing.com" in href or "webcache.googleusercontent.com" in href:
            ignored_count += 1
            continue
        
        # Start collecting URLs after ignoring the first 30
        if ignored_count < 30:
            ignored_count += 1
            continue
        
        article_urls.append(href)
        if len(article_urls) >= max_articles:
            break
    
    print(f"Extracted {len(article_urls)} relevant article URLs:")
    return article_urls


# API endpoint to find a single related article with opposing bias
@app.route("/article_finder", methods=["POST"])
def article_finder():
    data = request.get_json()
    original_article_url = data.get("url")
    if not original_article_url:
        return jsonify({"error": "No URL provided"}), 400

    print(f"Finding related articles for: {original_article_url}")

    # Get bias of the original article
    original_bias = get_article_bias(original_article_url)
    if not original_bias:
        return jsonify({"error": "Failed to analyze bias of the original article"}), 500

    # Scrape and extract keywords from the original article
    html_content = fetch_webpage(original_article_url)
    if not html_content:
        return jsonify({"error": "Failed to fetch the original article"}), 500

    _, title = parse_with_beautifulsoup(html_content)
    keywords = extract_keywords(title)
    if not keywords:
        return jsonify({"error": "No keywords extracted from the title"}), 500

    # Search for related articles
    related_articles = search_articles(keywords)
    if not related_articles:
        return jsonify({"error": "No related articles found"}), 404

    # Find an article with an opposing bias
    for article_url in related_articles:
        if article_url != original_article_url:
            article_bias = get_article_bias(article_url)
            if article_bias and article_bias != original_bias:
                print(f"Selected article with opposing bias: {article_url}")
                return jsonify({"message": "Success", "related_article": article_url}), 200

    # If no opposing bias article is found, return the first different article
    for article_url in related_articles:
        if article_url != original_article_url:
            print(f"Selected first alternative article: {article_url}")
            return jsonify({"message": "Success", "related_article": article_url}), 200

    return jsonify({"error": "No valid alternative articles found"}), 404


if __name__ == "__main__":
    app.run(debug=True)
