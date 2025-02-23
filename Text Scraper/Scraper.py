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

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Download stopwords
nltk.download('stopwords')

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

@app.route("/article_finder", methods=["POST"])
def article_finder(api_key="69ea4f52545a4750a3c0e49811ffc8d3"):
    ##################### Mini helper functions ############################
    def find_article_title(json_thing):
        dic = dict(json_thing)
        title = dic["title"]
        return title
    
    # Sentiment processor
    def sentiment_processor(dic):
        # Returning the side that's highest
        return max(dic, key=dic.get)
    
    # Finds keywords init
    def keyword_finder(article_title):
        # Extracting stop words
        stop_words = set(stopwords.words('english'))
        # Tokenizing the article title
        article_tokens = article_title.split()
        # Filtering stop words
        keywords = [word for word in article_tokens if word.lower() not in stop_words]
        return keywords
    
    # Searching for articles init
    def search_article(keyword, api_key):
        url = 'https://newsapi.org/v2/top-headlines'
        # Define parameters for the request (e.g., get US headlines)    
        params = {
            'qInTitle': keyword,
            'q': keyword,
            'country': 'us',
            'pageSize': 10,  # Limit the number of articles returned
            'apiKey': api_key
        }
        # Make the GET request to the News API
        response = requests.get(url, params=params)
        if response.status_code == 200:
            data = response.json()
            return data.get('articles', [])
        else:
            print(f"Error fetching news for keyword '{keyword}':", response.status_code)
            return []

    ####################### Endpoints #####################
    scrape_endpoint = "http://localhost:5000/scrape"
    nlp_endpoint = "https://popular-strongly-lemur.ngrok-free.app/api/analyze/"
    
    # Looking for current article url
    data = request.get_json()
    original_article_url = data.get("url")
    if not original_article_url:
        return jsonify({"error": "No URL provided"}), 400

    print(f"Processing URL: {original_article_url}")
    
    payload = {"url": original_article_url}

    # Further processing can be added here
    og_scrape_response = requests.post(scrape_endpoint, json=payload)
    if og_scrape_response.status_code == 200:

        og_scrape_payload = og_scrape_response.json()
        og_sentiment_response = requests.post(nlp_endpoint, json=og_scrape_payload)

        if og_sentiment_response.status_code == 200:

            og_sentiment_payload = og_sentiment_response.json()

    else:
        print("ERROR")
    
    # Extracting key info
    current_article_title_raw = find_article_title(og_scrape_payload)
    current_article_sentiment = sentiment_processor(og_sentiment_payload['bias_analysis'])
    print(f"############ {current_article_title_raw} ############")
    print(f"$$$$$$$$$$$$ {current_article_sentiment} $$$$$$$$$$$$")

    # Storage
    opp_articles = []
    opp_articles_score = dict({"url":[], "Score":[], "Lean":[]})

    # Isolating the keywords
    keywords = keyword_finder(current_article_title_raw)
    print(f"Isolated keywords from title: {keywords}")
    print()

    for keyword in keywords:

        print(f"Searching articles for: {keyword}")
        articles = search_article(keyword, api_key)

        for article in articles:
            url = article.get("url")
            if url:

                # Making json dict
                article_search_payload = {"url": url}

                # Sending the url to scraper
                scrape_response = requests.post(scrape_endpoint, json=article_search_payload)
                if scrape_response.status_code == 200:

                    print(f"Searched article title: {scrape_response.json()['title']}")

                    nlp_response = requests.post(nlp_endpoint, json=scrape_response.json())

                    if nlp_response.status_code == 200:

                        nlp_sentiment = nlp_response.json()
                        opp_article_sentiment = sentiment_processor(nlp_sentiment['bias_analysis'])

                    else:
                        print(f"NLP API request error: {nlp_response.status_code}")

                else:
                    print(f"Scraping request error: {scrape_response.status_code}")


                print()

                if current_article_sentiment != opp_article_sentiment:
                    print(f"Opposite sentiment found: {current_article_sentiment}, {opp_article_sentiment}")
                    opp_articles.append(article)
                    opp_articles_score["url"].append(url)
                    opp_articles_score["Score"].append(nlp_sentiment["bias_analysis"][opp_article_sentiment])
                    opp_articles_score["Lean"].append(opp_article_sentiment)
        
    df = pd.DataFrame(opp_articles_score)
    df_sorted = df.sort_values(by="Score", ascending=False).reset_index(drop=True)
    final = df_sorted.iloc[0].to_dict()

    return jsonify({"message": "Success", "details": final}), 200

if __name__ == "__main__":
    app.run(debug=True)
