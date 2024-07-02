from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import pandas as pd
import time

def crawl_news(keyword, num_news, max_retries=3):
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--ignore-certificate-errors')
    options.add_argument('--ignore-ssl-errors')
    
    driver = webdriver.Chrome(options=options)
    
    search_url = f"https://kr.investing.com/search/?q={keyword}&tab=news"
    driver.get(search_url)
    print(f"Navigating to URL: {search_url}")

    news_items = []
    
    try:
        # Wait for page to load completely
        WebDriverWait(driver, 20).until(
            lambda d: d.execute_script('return document.readyState') == 'complete'
        )
        print("Page loaded completely")

        # Wait for news section to be present
        news_section_selector = "#fullColumn > div > div:nth-child(6) > div.searchSectionMain > div"
        try:
            news_section = WebDriverWait(driver, 20).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, news_section_selector))
            )
            print("News section found")
        except TimeoutException:
            print("News section not found")
            print("Page source:")
            print(driver.page_source)
            return pd.DataFrame()

        while len(news_items) < num_news:
            # Find articles
            articles = news_section.find_elements(By.CSS_SELECTOR, 'div > div > a')
            print(f"Found {len(articles)} articles")
            
            for article in articles:
                if len(news_items) >= num_news:
                    break
                
                try:
                    title = article.text.strip()
                    link = article.get_attribute('href')
                    if {'title': title, 'link': link} not in news_items:
                        news_items.append({'title': title, 'link': link})
                        print(f"Added article: {title}")
                except Exception as e:
                    print(f"Error extracting article info: {str(e)}")
                    continue
            
            # Scroll to bottom of page
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            print("Scrolled to bottom of page")
            time.sleep(2)  # Wait for new content to load
            
            # Check if new articles have been loaded
            new_articles = news_section.find_elements(By.CSS_SELECTOR, 'div > div > a')
            if len(new_articles) == len(articles):
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