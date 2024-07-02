from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, WebDriverException
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

    try:
        driver = webdriver.Chrome(options=chrome_options)
    except WebDriverException as e:
        print(f"Failed to initialize WebDriver: {str(e)}")
        return pd.DataFrame()

    wait = WebDriverWait(driver, 20)
    news_items = []

    try:
        encoded_keyword = urllib.parse.quote(keyword)
        url = f"https://kr.investing.com/search/?q={encoded_keyword}&tab=news"
        driver.get(url)
        print(f"Accessed search results page for keyword: {keyword}")

        # 페이지 로딩 대기
        news_container_selector = "#fullColumn > div > div:nth-child(6) > div.searchSectionMain > div"
        try:
            news_container = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, news_container_selector)))
            print("News container found")
        except TimeoutException:
            print("Timed out waiting for news container")
            return pd.DataFrame()

        while len(news_items) < num_news:
            # 현재 페이지의 뉴스 항목 찾기
            articles = news_container.find_elements(By.CSS_SELECTOR, "div > div > a")
            print(f"Found {len(articles)} articles")

            for article in articles[len(news_items):]:
                if len(news_items) >= num_news:
                    break

                try:
                    title = article.text.strip()
                    link = article.get_attribute('href')
                    if title and link:
                        news_items.append({'title': title, 'link': link})
                        print(f"Crawled: {title}")
                    else:
                        print(f"Skipped article (missing title or link)")
                except Exception as e:
                    print(f"Error extracting article info: {str(e)}")
                    continue

            if len(news_items) >= num_news:
                break

            # 페이지 스크롤
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(random.uniform(2, 4))  # 새로운 컨텐츠 로딩을 기다림

            # 새로운 항목이 로드되었는지 확인
            try:
                wait.until(lambda d: len(d.find_elements(By.CSS_SELECTOR, f"{news_container_selector} > div > div > a")) > len(articles))
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