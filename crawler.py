import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import random
import urllib.parse

def crawl_news(keyword, num_news):
    news_items = []
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Safari/537.36'
    }

    try:
        encoded_keyword = urllib.parse.quote(keyword)
        url = f"https://kr.investing.com/search/?q={encoded_keyword}&tab=news"
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        
        print(f"Accessed search results page for keyword: {keyword}")
        
        soup = BeautifulSoup(response.text, 'html.parser')
        news_container = soup.select_one("#fullColumn > div > div:nth-child(6) > div.searchSectionMain > div")
        
        if not news_container:
            print("News container not found")
            return pd.DataFrame()
        
        articles = news_container.select("div > div > a")
        print(f"Found {len(articles)} articles")
        
        for article in articles[:num_news]:
            try:
                title = article.text.strip()
                link = article.get('href')
                if link:
                    if link.startswith('/'):
                        link = "https://kr.investing.com" + link
                    news_items.append({'title': title, 'link': link})
                    print(f"Crawled: {title}")
                else:
                    print(f"Skipped article (no link): {title}")
            except Exception as e:
                print(f"Error extracting article info: {str(e)}")
                continue
            
            if len(news_items) >= num_news:
                break
        
    except requests.RequestException as e:
        print(f"An error occurred while fetching the page: {str(e)}")
    except Exception as e:
        print(f"An unexpected error occurred: {str(e)}")

    print(f"Total articles crawled: {len(news_items)}")
    return pd.DataFrame(news_items)

if __name__ == "__main__":
    keyword = input("Enter search keyword: ")
    num_news = int(input("Enter number of news articles to crawl: "))
    df = crawl_news(keyword, num_news)
    print(df)