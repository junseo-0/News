from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import time
import random

def crawl_news(keyword, num_news):
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Safari/537.36")

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    wait = WebDriverWait(driver, 20)

    try:
        url = f"https://kr.investing.com/search/?q={keyword}&tab=news"
        driver.get(url)
        print(f"Accessed search results page for keyword: {keyword}")

        news_container_selector = "#fullColumn > div > div:nth-child(6) > div.searchSectionMain > div"
        news_container = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, news_container_selector)))
        
        news_items = []
        scroll_attempts = 0
        max_scroll_attempts = 5

        while len(news_items) < num_news and scroll_attempts < max_scroll_attempts:
            articles = news_container.find_elements(By.CSS_SELECTOR, "div > div > a")
            
            for article in articles:
                if len(news_items) >= num_news:
                    break
                try:
                    title = article.text.strip()
                    link = article.get_attribute('href')
                    if title and link and {'title': title, 'link': link} not in news_items:
                        news_items.append({'title': title, 'link': link})
                        yield {'title': title, 'link': link}
                        print(f"Crawled: {title}")
                except Exception as e:
                    print(f"Error extracting article info: {str(e)}")

            if len(news_items) < num_news:
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(random.uniform(2, 4))
                scroll_attempts += 1

        if len(news_items) < num_news:
            print(f"Could only find {len(news_items)} articles. Requested: {num_news}")

    except Exception as e:
        print(f"An error occurred during crawling: {str(e)}")
    finally:
        driver.quit()

if __name__ == "__main__":
    keyword = input("Enter search keyword: ")
    num_news = int(input("Enter number of news articles to crawl: "))
    for item in crawl_news(keyword, num_news):
        print(item)