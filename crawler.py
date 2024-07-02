from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import pandas as pd
import time
import random
import urllib.parse

def crawl_news(keyword, num_news):
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Safari/537.36")

    # Streamlit 클라우드의 ChromeDriver 경로
    chrome_options.binary_location = "/usr/bin/chromium-browser"

    driver = webdriver.Chrome(options=chrome_options)
    wait = WebDriverWait(driver, 20)

    news_items = []

    try:
        encoded_keyword = urllib.parse.quote(keyword)
        url = f"https://kr.investing.com/search/?q={keyword}&tab=news"
        driver.get(url)
        print(f"Accessed search results page for keyword: {keyword}")

        # 페이지 로딩 대기
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'div.js-article-item')))

        while len(news_items) < num_news:
            # 현재 페이지의 뉴스 항목 찾기
            articles = driver.find_elements(By.CSS_SELECTOR, 'div.js-article-item')

            for article in articles[len(news_items):]:
                if len(news_items) >= num_news:
                    break

                try:
                    title_element = article.find_element(By.CSS_SELECTOR, 'a.title')
                    title = title_element.text.strip()
                    link = title_element.get_attribute('href')
                    news_items.append({'title': title, 'link': link})
                    print(f"Crawled: {title}")
                except NoSuchElementException:
                    continue

            if len(news_items) >= num_news:
                break

            # 페이지 스크롤
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(random.uniform(2, 4))  # 새로운 컨텐츠 로딩을 기다림

            # 새로운 항목이 로드되었는지 확인
            try:
                wait.until(lambda d: len(d.find_elements(By.CSS_SELECTOR, 'div.js-article-item')) > len(articles))
            except TimeoutException:
                print("No more new articles loaded")
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