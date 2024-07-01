import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, WebDriverException
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd

def get_driver():
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--ignore-certificate-errors")
    chrome_options.add_argument("--ignore-ssl-errors")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--disable-extensions")
    chrome_options.add_argument("--disable-infobars")
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
    service = Service(ChromeDriverManager().install())
    return webdriver.Chrome(service=service, options=chrome_options)

def crawl_news(keyword, num_news, max_retries=3):
    for attempt in range(max_retries):
        try:
            driver = get_driver()
            search_url = f"https://kr.investing.com/search/?q={keyword}&tab=news"
            driver.get(search_url)

            news_items = []
            
            WebDriverWait(driver, 20).until(
                EC.presence_of_element_located((By.XPATH, '//*[@id="fullColumn"]/div/div[4]/div[3]'))
            )

            while len(news_items) < num_news:
                articles = driver.find_elements(By.XPATH, '//*[@id="fullColumn"]/div/div[4]/div[3]/div/div')
                
                for article in articles:
                    if len(news_items) >= num_news:
                        break
                    
                    try:
                        title_element = article.find_element(By.CSS_SELECTOR, 'a.title')
                        title = title_element.text.strip()
                        link = title_element.get_attribute('href')
                        
                        news_items.append({'title': title, 'link': link})
                    except NoSuchElementException:
                        continue

                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(2)
                
                new_articles = driver.find_elements(By.XPATH, '//*[@id="fullColumn"]/div/div[4]/div[3]/div/div')
                if len(new_articles) == len(articles):
                    break

            return pd.DataFrame(news_items)

        except (TimeoutException, WebDriverException) as e:
            print(f"Attempt {attempt + 1} failed: {str(e)}")
            if attempt == max_retries - 1:
                print("Max retries reached. Crawling failed.")
                return pd.DataFrame()
            time.sleep(5)
        finally:
            driver.quit()