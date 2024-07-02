from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from bs4 import BeautifulSoup
import pandas as pd
import time

def crawl_news(keyword, num_news, max_retries=3):
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')

    driver = webdriver.Chrome(options=options)
    
    search_url = f"https://kr.investing.com/search/?q={keyword}&tab=news"
    driver.get(search_url)

    news_items = []
    
    try:
        while len(news_items) < num_news:
            # 페이지 끝까지 스크롤
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)  # 새로운 내용이 로드될 때까지 대기
            
            # 새로운 기사 찾기
            soup = BeautifulSoup(driver.page_source, 'html.parser')
            articles = soup.select('.js-article-item')
            
            for article in articles:
                if len(news_items) >= num_news:
                    break
                
                title_element = article.select_one('a.title')
                if title_element and {'title': title_element.text.strip(), 'link': "https://kr.investing.com" + title_element['href']} not in news_items:
                    news_items.append({'title': title_element.text.strip(), 'link': "https://kr.investing.com" + title_element['href']})
            
            # 더 이상 새로운 기사가 로드되지 않으면 종료
            if len(news_items) == len(set((item['title'], item['link']) for item in news_items)):
                break
    except Exception as e:
        print(f"An error occurred: {str(e)}")
    finally:
        driver.quit()
    
    return pd.DataFrame(news_items[:num_news])

if __name__ == "__main__":
    print("Crawler module loaded successfully")