import streamlit as st
import pandas as pd
from streamlit_option_menu import option_menu
import logging
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import random
import os

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# 페이지 설정
st.set_page_config(layout="wide", page_title="News Dashboard", page_icon="📰")

# 스타일 적용
st.markdown("""
<style>
    .reportview-container { background: #f0f2f6; }
    .main {
        background: #ffffff;
        padding: 2rem;
        border-radius: 10px;
        box-shadow: 0 0 10px rgba(0,0,0,.1);
        overflow-y: auto;
    }
    h1 { color: #1E88E5; }
    .stDataFrame { width: 100%; }
    .error-message {
        color: #D32F2F;
        background-color: #FFCDD2;
        padding: 1rem;
        border-radius: 5px;
        margin-bottom: 1rem;
    }
</style>
""", unsafe_allow_html=True)

def setup_driver():
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Safari/537.36")
    chrome_options.add_argument("--disable-features=IsolateOrigins,site-per-process")
    chrome_options.add_argument("--ignore-certificate-errors")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)

    if 'STREAMLIT_SHARING' in os.environ:
        logger.info("Running on Streamlit Cloud")
        CHROMEDRIVER_PATH = "/usr/local/bin/chromedriver"
        if not os.path.exists(CHROMEDRIVER_PATH):
            logger.error(f"ChromeDriver not found at {CHROMEDRIVER_PATH}")
            raise FileNotFoundError(f"ChromeDriver not found at {CHROMEDRIVER_PATH}")
        chrome_options.binary_location = "/usr/bin/google-chrome-stable"
        return webdriver.Chrome(executable_path=CHROMEDRIVER_PATH, options=chrome_options)
    else:
        logger.info("Running locally")
        from webdriver_manager.chrome import ChromeDriverManager
        from selenium.webdriver.chrome.service import Service
        return webdriver.Chrome(service=Service(ChromeDriverManager(version="114.0.5735.90").install()), options=chrome_options)

@st.cache_data
def crawl_news(keyword, num_news):
    logger.info(f"Starting crawl for keyword: {keyword}, number of news: {num_news}")
    try:
        driver = setup_driver()
    except Exception as e:
        logger.error(f"Failed to setup WebDriver: {str(e)}")
        return []

    wait = WebDriverWait(driver, 20)
    news_items = []

    try:
        url = f"https://kr.investing.com/search/?q={keyword}&tab=news"
        driver.get(url)
        logger.info(f"Accessing URL: {url}")

        news_container_selector = "#fullColumn > div > div:nth-child(6) > div.searchSectionMain > div"
        news_container = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, news_container_selector)))
        
        scroll_attempts = 0
        max_scroll_attempts = 5

        while len(news_items) < num_news and scroll_attempts < max_scroll_attempts:
            articles = news_container.find_elements(By.CSS_SELECTOR, "div > div > a")
            
            for article in articles:
                if len(news_items) >= num_news:
                    break
                try:
                    title = article.text.strip() if article.text else None
                    link = article.get_attribute('href')
                    if title and link and {'title': title, 'link': link} not in news_items:
                        news_items.append({'title': title, 'link': link})
                        logger.info(f"Crawled: {title}")
                except Exception as e:
                    logger.error(f"Error extracting article info: {str(e)}", exc_info=True)

            if len(news_items) < num_news:
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(random.uniform(2, 4))
                scroll_attempts += 1

        if len(news_items) < num_news:
            logger.warning(f"Could only find {len(news_items)} articles. Requested: {num_news}")

    except Exception as e:
        logger.error(f"An error occurred during crawling: {str(e)}", exc_info=True)
    finally:
        driver.quit()
        logger.info("Browser closed")

    return news_items

def display_news(df):
    st.subheader('📊 Crawled News Data')
    df['title'] = df.apply(lambda row: f'<a href="{row["link"]}" target="_blank">{row["title"]}</a>', axis=1)
    df = df.drop(columns=['link'])
    df.index = range(1, len(df) + 1)
    st.write(df.to_html(escape=False, index=True), unsafe_allow_html=True)

def main():
    st.title('📰 경제 뉴스검색')

    with st.sidebar:
        selected = option_menu(
            menu_title="Main Menu",
            options=["Dashboard", "About"],
            icons=["house", "info-circle"],
            menu_icon="cast",
            default_index=0,
        )

    if selected == "Dashboard":
        col1, col2 = st.columns([2,1])
        with col1:
            keyword = st.text_input('Enter keyword to crawl news', '테슬라')
        with col2:
            num_news = st.slider('Number of news articles', 5, 50, 10)

        if st.button('Crawl News', key='crawl_button'):
            if keyword:
                try:
                    with st.spinner('Crawling news...'):
                        news_items = crawl_news(keyword, num_news)
                    
                    if news_items:
                        df = pd.DataFrame(news_items)
                        st.success(f"{len(df)} news articles crawled successfully!")
                        display_news(df)
                    else:
                        st.warning('No news articles found.')
                except Exception as e:
                    logger.error(f"An error occurred during crawling: {str(e)}", exc_info=True)
                    st.error(f"An error occurred during crawling: {str(e)}")
                    st.markdown(
                        """
                        <div class="error-message">
                            <h3>Oops! Something went wrong</h3>
                            <p>We encountered an error while trying to crawl the news. Here are some things you can try:</p>
                            <ul>
                                <li>Check your internet connection</li>
                                <li>Try a different keyword</li>
                                <li>Reduce the number of articles to crawl</li>
                                <li>Wait a few minutes and try again</li>
                            </ul>
                            <p>If the problem persists, please contact support.</p>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )
            else:
                st.warning('Please enter a keyword to crawl news.')

    elif selected == "About":
        st.subheader("About this Dashboard")
        st.write("""
        This News Dashboard is designed to crawl and analyze news articles from kr.investing.com.
        It provides a simple interface to search for news based on keywords, visualize the data,
        and filter the results.
        
        Built with Streamlit and Selenium.
        """)

if __name__ == "__main__":
    main()