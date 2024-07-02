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
    chrome_options.add_argument("--headless")  # Headless 모드 활성화
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Safari/537.36")

    driver = None
    news_items = []

    try:
        driver = webdriver.Chrome(options=chrome_options)
        wait = WebDriverWait(driver, 20)

        encoded_keyword = urllib.parse.quote(keyword)
        url = f"https://kr.investing.com/search/?q={encoded_keyword}&tab=news"
        driver.get(url)
        print(f"Accessed search results page for keyword: {keyword}")

        news_container_selector = "#fullColumn > div > div:nth-child(6) > div.searchSectionMain > div"
        news_container = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, news_container_selector)))
        print("News container found")

        while len(news_items) < num_news:
            articles = news_container.find_elements(By.CSS_SELECTOR, "div > div > a")
            print(f"Found {len(articles)} articles")

            for article in articles:
                if len(news_items) >= num_news:
                    break

                try:
                    title = article.text.strip()
                    link = article.get_attribute('href')
                    if title and link and {'title': title, 'link': link} not in news_items:
                        news_items.append({'title': title, 'link': link})
                        print(f"Crawled: {title}")
                    else:
                        print(f"Skipped article (duplicate or missing info)")
                except Exception as e:
                    print(f"Error extracting article info: {str(e)}")
                    continue

            if len(news_items) >= num_news:
                break

            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(random.uniform(2, 4))

            try:
                wait.until(lambda d: len(d.find_elements(By.CSS_SELECTOR, f"{news_container_selector} > div > div > a")) > len(articles))
            except TimeoutException:
                print("No more new articles loaded")
                break

        print(f"Total unique articles crawled: {len(news_items)}")

    except Exception as e:
        print(f"An error occurred: {str(e)}")
    finally:
        if driver:
            driver.quit()

    return pd.DataFrame(news_items[:num_news])

# Streamlit 앱에서 직접 호출할 함수
def get_news(keyword, num_news):
    return crawl_news(keyword, num_news)