from flask import Flask, request, jsonify
from flask_cors import CORS
from readability import Document
from bs4 import BeautifulSoup
import requests
import json
import re
import nltk
from nltk.corpus import stopwords
import pandas as pd
# from GoogleNews import GoogleNews
from gnews import GNews
import time
print("START")

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Download stopwords (ensure this is done beforehand to avoid runtime issues)
nltk.download('stopwords')

# Function to fetch webpage content
def fetch_webpage(url):
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/90.0.4430.93 Safari/537.36"}
    try:
        print(f"Fetching URL: {url}")
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        print("Successfully fetched webpage.")
        return response.text
    except requests.exceptions.RequestException as e:
        print(f"Error fetching URL: {e}")
        return None

# Function to parse content using Readability
def parse_with_readability(html_content):
    doc = Document(html_content)
    title = doc.title()
    soup = BeautifulSoup(doc.summary(), "lxml")
    text = soup.get_text(separator=" ").strip()
    text = re.sub(r'\s{2,}', ' ', text)  # Remove excessive whitespace
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

    parsed_text, title = parse_with_readability(html_content)
    result = {"url": url, "title": title, "text": parsed_text}
    print(f"Scrape result: {title}")
    return jsonify(result)

# Function to process sentiment from API response
def sentiment_processor(sentiment_dict):
    return max(sentiment_dict, key=sentiment_dict.get)

# Function to extract keywords from an article title
def keyword_finder(title):
    stop_words = set(stopwords.words('english'))
    keywords = [word for word in title.split() if word.lower() not in stop_words]
    print(f"Extracted keywords: {keywords}")
    return keywords[:-3]  # Exclude last 3 words to focus on main topic

def get_direct_url(url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                      "Chrome/90.0.4430.93 Safari/537.36"
    }
    try:
        response = requests.get(url, headers=headers, timeout=10)
        # If HTTP redirection occurred, response.url will be different
        if response.url != url:
            return response.url
        # Otherwise, check if the page has a meta refresh redirect
        soup = BeautifulSoup(response.text, "lxml")
        meta = soup.find("meta", attrs={"http-equiv": re.compile("refresh", re.I)})
        if meta:
            content = meta.get("content", "")
            match = re.search(r'url=(.*)', content, flags=re.IGNORECASE)
            if match:
                final_url = match.group(1).strip()
                return final_url
    except Exception as e:
        print(f"Error in get_direct_url: {e}")
    return url  # Fallback to the original URL if no redirection info is found


def search_articles(keywords, max_articles):

    query = " ".join(keywords)
    
    # Initialize the GNews client (customize language and country if needed)
    gnews_client = GNews(language='en', country='US', max_results=max_articles)
    
    # Retrieve articles using the combined query
    articles = gnews_client.get_news(query)
    
    # Limit the number of articles to max_articles
    return articles

# API endpoint to find opposing articles
@app.route("/article_finder", methods=["POST"])
def article_finder():
    data = request.get_json()
    original_article_url = data.get("url")
    if not original_article_url:
        return jsonify({"error": "No URL provided"}), 400
    print(f"{original_article_url}")

    print(f"Finding opposing articles for: {original_article_url}")
    scrape_response = requests.post("http://localhost:5000/scrape", json={"url": original_article_url})
    if scrape_response.status_code != 200:
        return jsonify({"error": "Failed to scrape the article"}), 500
    
    scraped_data = scrape_response.json()
    title = scraped_data.get("title")
    
    nlp_response = requests.post("https://popular-strongly-lemur.ngrok-free.app/api/analyze/", json=scraped_data)
    if nlp_response.status_code != 200:
        return jsonify({"error": "Failed to analyze sentiment"}), 500
    
    sentiment_data = nlp_response.json()
    article_sentiment = sentiment_processor(sentiment_data['bias_analysis'])
    print("######################################")
    print(f"OG ARTICAL SENTIMENT: {article_sentiment}")
    print("######################################")
    
    keywords = keyword_finder(title)
    matching_articles = search_articles(keywords, 5)
    print(f"Length: {len(matching_articles)}")
    
    opposing_articles = {"url": [], "Score": [], "Lean": []}

    for article_url in matching_articles:
        direct_url = get_direct_url(article_url['url'])
        print(f"Processing article: {direct_url['title']}")
        scrape_response = requests.post("http://localhost:5000/scrape", json={"url": direct_url['url']})
        if scrape_response.status_code != 200:
            print(f"Failed to scrape: {direct_url['title']}")
            continue
        print(f"Article text: {scrape_response.json()['text']}")
        
        article_data = scrape_response.json()
        nlp_response = requests.post("https://popular-strongly-lemur.ngrok-free.app/api/analyze/", json=article_data)
        if nlp_response.status_code != 200:
            print(f"Failed to analyze sentiment for: {direct_url['title']}")
            continue
        
        article_sentiment_data = nlp_response.json()
        opposing_sentiment = sentiment_processor(article_sentiment_data['bias_analysis'])
        print()
        print(f"Article title: {direct_url['title']}")
        print(f"Article sentiment: {opposing_sentiment}")
        print()
        
        if article_sentiment != opposing_sentiment:
            print(f"Opposing sentiment found for {direct_url['title']}")
            opposing_articles["url"].append(direct_url['url'])
            opposing_articles["Score"].append(article_sentiment_data["bias_analysis"][opposing_sentiment])
            opposing_articles["Lean"].append(opposing_sentiment)
        else:
            print(f"Oppsing sentmimment not found for {direct_url['title']}")
    
    df = pd.DataFrame(opposing_articles).sort_values(by="Score", ascending=False).reset_index(drop=True)

    print()
    print(df)
    print()

    best_match = df.iloc[0].to_dict() if not df.empty else {"emergency_url":"https://www.foxnews.com/world/israel-delays-palestinian-prisoner-release-hamas-humiliating-treatment-hostages-netanyahu-says"}
    print("Completed analysis.")
    return jsonify({"message": "Success", "details": best_match}), 200

if __name__ == "__main__":
    app.run(debug=True)
#     app.run(debug=True)


# arts = search_articles(keywords, 3)

# print(len(arts))
# print(arts)

# x = search_articles(keywords)
