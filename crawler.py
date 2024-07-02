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

    driver = webdriver.Chrome(options=options)
    
    search_url = f"https://kr.investing.com/search/?q={keyword}&tab=news"
    driver.get(search_url)

    news_items = []
    
    try:
        # 뉴스 섹션이 로드될 때까지 대기
        news_section_selector = "#fullColumn > div > div:nth-child(6) > div.searchSectionMain > div"
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, news_section_selector))
        )

        while len(news_items) < num_news:
            # 뉴스 섹션 내에서 기사 찾기
            news_section = driver.find_element(By.CSS_SELECTOR, news_section_selector)
            articles = news_section.find_elements(By.CSS_SELECTOR, 'div > div > a')
            
            for article in articles:
                if len(news_items) >= num_news:
                    break
                
                try:
                    title = article.text.strip()
                    link = article.get_attribute('href')
                    if {'title': title, 'link': link} not in news_items:
                        news_items.append({'title': title, 'link': link})
                except Exception as e:
                    print(f"Error extracting article info: {str(e)}")
                    continue
            
            # 페이지 끝까지 스크롤
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)  # 새로운 내용이 로드될 때까지 대기
            
            # 새로운 기사가 로드되지 않으면 종료
            new_articles = news_section.find_elements(By.CSS_SELECTOR, 'div > div > a')
            if len(new_articles) == len(articles):
                break

    except Exception as e:
        print(f"An error occurred: {str(e)}")
    finally:
        driver.quit()
    
    return pd.DataFrame(news_items[:num_news])

if __name__ == "__main__":
    print("Crawler module loaded successfully")