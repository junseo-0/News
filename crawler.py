import requests
from bs4 import BeautifulSoup
import pandas as pd

def crawl_news(keyword, num_news, max_retries=3):
    search_url = f"https://kr.investing.com/search/?q={keyword}&tab=news"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }

    news_items = []
    
    for attempt in range(max_retries):
        try:
            response = requests.get(search_url, headers=headers)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            articles = soup.select('.js-article-item')
            
            for article in articles[:num_news]:
                title_element = article.select_one('a.title')
                if title_element:
                    title = title_element.text.strip()
                    link = "https://kr.investing.com" + title_element['href']
                    news_items.append({'title': title, 'link': link})
                
                if len(news_items) >= num_news:
                    break
            
            break  # 성공적으로 크롤링했다면 루프 종료
        
        except requests.RequestException as e:
            print(f"Attempt {attempt + 1} failed: {str(e)}")
            if attempt == max_retries - 1:
                print("Max retries reached. Crawling failed.")
    
    return pd.DataFrame(news_items)

if __name__ == "__main__":
    print("Crawler module loaded successfully")