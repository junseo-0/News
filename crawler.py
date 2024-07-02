import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import random
import urllib.parse

def crawl_news(keyword, num_news):
    news_items = []
    page = 1
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Safari/537.36'
    }

    while len(news_items) < num_news:
        try:
            encoded_keyword = urllib.parse.quote(keyword)
            url = f"https://kr.investing.com/search/?q={encoded_keyword}&tab=news&page={page}"
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            articles = soup.select('div.js-article-item')
            
            if not articles:
                print(f"No more articles found on page {page}")
                break
            
            for article in articles:
                if len(news_items) >= num_news:
                    break
                
                title_element = article.select_one('a.title')
                if title_element:
                    title = title_element.text.strip()
                    link = "https://kr.investing.com" + title_element['href']
                    news_items.append({'title': title, 'link': link})
                    print(f"Crawled: {title}")
            
            page += 1
            time.sleep(random.uniform(1, 3))  # 요청 간 대기 시간
            
        except requests.RequestException as e:
            print(f"An error occurred: {str(e)}")
            break

    print(f"Total articles crawled: {len(news_items)}")
    return pd.DataFrame(news_items[:num_news])

if __name__ == "__main__":
    keyword = input("Enter search keyword: ")
    num_news = int(input("Enter number of news articles to crawl: "))
    df = crawl_news(keyword, num_news)
    print(df)