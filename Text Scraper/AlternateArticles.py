import requests
from bs4 import BeautifulSoup as bs
import nltk
nltk.download('stopwords')
from nltk.corpus import stopwords
import numpy as np
from Scraper import app
import pandas as pd

API_KEY = "69ea4f52545a4750a3c0e49811ffc8d3"
NEWS_API_URL = 'https://newsapi.org/v2/top-headlines'

# Example sentiment dictionary
eg_sentiment_payload = dict({
    "Left":0.2,
    "Middle":0.1,
    "Right":0.7
})

# Example text dict
scraped_payload = dict({
    "text": "blahblahblah",
    "url": "skibidid.",
    "title": "Donald Trump is a great rolemodel"
})

def FindArticleTitle(json_thing):
    
	dic = dict(json_thing)

	title = dic["title"]

	return title

# Sentiment processor
def SentimentProcessor(dic):
    
	# Returning the side thats highest
    return max(dic, key=dic.get)

# Finds keywords init
def KeywordFinder(article_title, stopwords):
    
	# Extracting stop words
    stopwords = set(stopwords.words('english'))
    
	# Tokenizing the article title
    article_tokens = article_title.split()
    
	# Filtering stop words
    keywords = [word for word in article_tokens if word.lower() not in stopwords]
    
    return keywords

# Searching for articles init
def SearchArticle(keyword, api_key):
    
	url = 'https://newsapi.org/v2/top-headlines'
	# api_key = "69ea4f52545a4750a3c0e49811ffc8d3"

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
	
# Main function
def NewsArticleFinder(stopwords, scraped_payload, sentiment_payload, og_article_url,api_key=API_KEY):
    
    # Important endpoints to access our tools
    scrape_endpoint = "http://localhost:5000/scrape"
    nlp_endpoint = "https://driven-gnu-ample.ngrok-free.app/api/analyze/"
    # og_article_url = "https://www.foxnews.com/world/israel-delays-palestinian-prisoner-release-hamas-humiliating-treatment-hostages-netanyahu-says"

    # Scraping the original article
    payload_thing = {"url": og_article_url}
    print("Before thing")
    og_scrape_response = requests.post(scrape_endpoint, json=payload_thing)
    if og_scrape_response.status_code == 200:

        og_scrape_payload = og_scrape_response.json()        
        og_sentiment_response = requests.post(nlp_endpoint, json=og_scrape_payload)

        if og_sentiment_response.status_code == 200:
             
            og_sentiment_payload = og_sentiment_response.json()
    else:
        print("ERORR")

    # Extracting the sentiment of our current article
    current_article_title_raw = FindArticleTitle(og_scrape_payload)
    print("#############")
    print(current_article_title_raw)
    print("################")
    # using pre loaded sentiment for testing while api is down
    # current_article_sentiment = SentimentProcessor(og_sentiment_payload)
    current_article_sentiment = SentimentProcessor(sentiment_payload)
    print

    # Printing the article stuff
    print("#########")
    print(f"Current article sentiment: {current_article_sentiment}")
    print(f"Current article title: {current_article_title_raw}")
    print()

	# Storage
    opp_articles = []
    opp_articles_score = dict({"url":[], "Score":[], "Lean":[]})

	# Isolating the keywords
    keywords = KeywordFinder(current_article_title_raw, stopwords)
    print(f"Isolated keywords: {keywords}")
    print()
    
    # Looping over all keywords
    for keyword in keywords:

        print(f"searching articles for: {keyword}")
        articles = SearchArticle(keyword, api_key)

        for article in articles:
            url = article.get('url')
            if url:
                
                # Making json (dict)
                payload = {"url": url}

				# Send url to Scraper
                scrape_response = requests.post(scrape_endpoint, json=payload)

                #
                if scrape_response.status_code == 200:
                    # print("******* TITLE ********")
                    # print(scrape_response.status_code)
                    # print(scrape_response.json()['title'])
                    # print("******* TITLE ********")

                    # Send Scraped text to NLP
                    nlp_response = requests.post(nlp_endpoint, json=scrape_response.json())

                    if nlp_response.status_code == 200:

                        # print("$$$$$$$$$$$$$$$$$ Sentiment $$$$$$$$$$$$$$")
                        # print(nlp_response.status_code)
                        # print(nlp_response.json())
                        # print("$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$")

                        nlp_sentiment = nlp_response.json()
                        opp_article_sentiment = SentimentProcessor(nlp_sentiment["bias_analysis"])
                        
                
                    else:
                        print(f"NLP API request error: {nlp_response.status_code}")

                else:
                    print(f"Scraping request error: {scrape_response.status_code}")

				# Comparing sentiments
                print()
                # print(f"Current article title: {current_article_title_raw}")
                # print(f"Possible opposing article title: {scrape_response.json()['title']}")
                # print(f"Possible opposing article sentiment: {opp_article_sentiment}")
                # print(f"Original article sentiment: {current_article_sentiment}")
                print()
                if current_article_sentiment != opp_article_sentiment:
                    print(f"Opposite sentiment found: {current_article_sentiment}, {opp_article_sentiment}")
                    opp_articles.append(article)
                    opp_articles_score["url"].append(url)
                    opp_articles_score["Score"].append(nlp_sentiment["bias_analysis"][opp_article_sentiment])
                    opp_articles_score["Lean"].append(opp_article_sentiment)
        print()
    return opp_articles, opp_articles_score

# articles = NewsArticleFinder(API_KEY, stopwords, scraped_payload, eg_sentiment_payload)

# print("_---------_")
# for art in articles:
# 	print(art)
# 	print("-------------------------------------------------")
import time
import threading
def run_flask_app():
	app.run(debug=False, use_reloader=False)

print("BEFORE RUNNING FLASK THREAD")
flask_thread = threading.Thread(target=run_flask_app)
flask_thread.daemon = True
flask_thread.start()
time.sleep(1)
print("AFTER RUNNING FLASK THREAD")
###################################################################################
######################################################### Using stuff                ##############################################################






# endpoint = "http://localhost:5000/scrape"

# # The URL you want to scrape
# payload = {"url": "https://www.foxnews.com/politics/judge-grants-19-ags-preliminary-injunction-against-doge-access-treasury-payment-system"}

# # Send
# print("Before send")
# print()
# response = requests.post(endpoint, json=payload)

# if response.status_code == 200:
# 	data = response.json()
# 	print("Scraped data:", data)
# else:
# 	print("Error:", response.status_code, response.text)
	
# print()
# print()
# print(response.json()["title"])

og_url = "https://www.foxnews.com/world/israel-delays-palestinian-prisoner-release-hamas-humiliating-treatment-hostages-netanyahu-says"

print("STARTING ARTICLE SEARCH")
articles, exp_dic = NewsArticleFinder(API_KEY, stopwords, scraped_payload, eg_sentiment_payload, og_url)
print("DONE ARTICLE SEARCH")

print(f"Number of articles: {len(articles)}")
for article in articles:
    print(article["url"])

print()
print("###### DIc: ######")
print(exp_dic)

df = pd.DataFrame(exp_dic)
df_sorted = df.sort_values(by='Score', ascending=False).reset_index(drop=True)
x = df_sorted.iloc[0].to_dict()



###### output #######
x
# TODO Send this back to chrome extension
