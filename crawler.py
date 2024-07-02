from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd
import time
import urllib.parse

def crawl_news(keyword, num_news):
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Safari/537.36")

    driver = webdriver.Chrome(ChromeDriverManager().install(), options=chrome_options)
    wait = WebDriverWait(driver, 20)

    news_items = []

    try:
        encoded_keyword = urllib.parse.quote(keyword)
        url = f"https://kr.investing.com/search/?q={keyword}&tab=news"
        driver.get(url)
        print(f"Accessed search results page for keyword: {keyword}")

        while len(news_items) < num_news:
            wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'div.searchSectionMain')))
            news_elements = driver.find_elements(By.CSS_SELECTOR, 'div.searchSectionMain > div > div > div > a')

            for element in news_elements:
                title = element.text
                link = element.get_attribute('href')
                news_items.append({"title": title, "link": link})
                if len(news_items) >= num_news:
                    break
            
            # Scroll down to load more news items
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)  # Adjust sleep time as needed to allow new items to load

    except TimeoutException as e:
        print("Timed out waiting for page to load")
    except NoSuchElementException as e:
        print("No more elements found")
    finally:
        driver.quit()

    return pd.DataFrame(news_items)

if __name__ == "__main__":
    keyword = "example_keyword"
    num_news = 10
    news_df = crawl_news(keyword, num_news)
    print(news_df)
