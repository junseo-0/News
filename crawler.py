from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import pandas as pd
import time
import random
import urllib.parse

def crawl_news(keyword, num_news):
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-blink-features=AutomationControlled')
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    
    driver = webdriver.Chrome(options=options)
    driver.execute_cdp_cmd('Network.setUserAgentOverride', {"userAgent": 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Safari/537.36'})
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    
    wait = WebDriverWait(driver, 30)
    
    news_items = []
    
    try:
        # 검색 URL로 직접 이동
        encoded_keyword = urllib.parse.quote(keyword)
        search_url = f"https://kr.investing.com/search/?q={encoded_keyword}&tab=news"
        driver.get(search_url)
        print(f"Accessed search results page for keyword: {keyword}")
        
        # 페이지 로딩 완료 대기
        wait.until(lambda d: d.execute_script('return document.readyState') == 'complete')
        print("Page loading complete")
        
        # 명시적으로 뉴스 섹션 대기
        news_section = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '#fullColumn')))
        print("News section found")
        
        retry_count = 0
        while len(news_items) < num_news and retry_count < 5:
            # 뉴스 항목 찾기
            news_elements = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'div.js-article-item')))
            print(f"Found {len(news_elements)} news elements")
            
            if not news_elements:
                retry_count += 1
                print(f"No news elements found. Retrying... (Attempt {retry_count}/5)")
                time.sleep(5)
                continue
            
            for element in news_elements:
                if len(news_items) >= num_news:
                    break
                
                try:
                    title = element.find_element(By.CSS_SELECTOR, 'a.title').text.strip()
                    link = element.find_element(By.CSS_SELECTOR, 'a.title').get_attribute('href')
                    news_items.append({'title': title, 'link': link})
                    print(f"Crawled: {title}")
                except NoSuchElementException:
                    print("Failed to extract article info")
                    continue
            
            # 페이지 스크롤
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(random.uniform(3, 5))  # 랜덤 대기 시간 증가
            
            # 새로운 기사가 로드되지 않으면 종료
            if len(news_items) == len(set((item['title'], item['link']) for item in news_items)):
                print("No new articles loaded, breaking loop")
                break
        
    except Exception as e:
        print(f"An error occurred: {str(e)}")
    finally:
        driver.quit()
    
    print(f"Total articles crawled: {len(news_items)}")
    return pd.DataFrame(news_items[:num_news])

if __name__ == "__main__":
    keyword = input("Enter search keyword: ")
    num_news = int(input("Enter number of news articles to crawl: "))
    df = crawl_news(keyword, num_news)
    print(df)