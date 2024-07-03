import streamlit as st
import pandas as pd
import plotly.express as px
from streamlit_option_menu import option_menu
from crawler import crawl_news
import logging

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 페이지 설정
logger.info("Setting up page configuration")
st.set_page_config(layout="wide", page_title="News Dashboard", page_icon="📰")

# 스타일 적용
logger.info("Applying styles")
st.markdown("""
<style>
    .reportview-container {
        background: #f0f2f6;
    }
    .main {
        background: #ffffff;
        padding: 2rem;
        border-radius: 10px;
        box-shadow: 0 0 10px rgba(0,0,0,.1);
        overflow-y: auto;
    }
    h1 {
        color: #1E88E5;
    }
    .stDataFrame {
        width: 100%;
    }
    .error-message {
        color: #D32F2F;
        background-color: #FFCDD2;
        padding: 1rem;
        border-radius: 5px;
        margin-bottom: 1rem;
    }
</style>
""", unsafe_allow_html=True)

def filter_news(df, filter_keyword):
    logger.info(f"Filtering news with keyword: {filter_keyword}")
    if filter_keyword:
        return df[df['title'].str.contains(filter_keyword, case=False, na=False)]
    return df

def main():
    logger.info("Starting main function")
    st.title('📰 경제 뉴스검색')

    with st.sidebar:
        logger.info("Setting up sidebar")
        selected = option_menu(
            menu_title="Main Menu",
            options=["Dashboard", "About"],
            icons=["house", "info-circle"],
            menu_icon="cast",
            default_index=0,
        )

    if selected == "Dashboard":
        logger.info("Dashboard selected")
        col1, col2 = st.columns([2,1])
        
        with col1:
            keyword = st.text_input('Enter keyword to crawl news', '테슬라')
        with col2:
            num_news = st.slider('Number of news articles', 5, 50, 10)

        if st.button('Crawl News', key='crawl_button'):
            logger.info(f"Crawl button clicked. Keyword: {keyword}, Number of articles: {num_news}")
            if keyword:
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                try:
                    logger.info("Starting news crawling")
                    df = pd.DataFrame()
                    for i, news_item in enumerate(crawl_news(keyword, num_news)):
                        df = pd.concat([df, pd.DataFrame([news_item])], ignore_index=True)
                        progress = int((i + 1) / num_news * 100)
                        progress_bar.progress(progress)
                        status_text.text(f"Crawling... {i+1}/{num_news} articles")
                    
                    progress_bar.empty()
                    status_text.empty()
                    
                    if not df.empty:
                        logger.info(f"Crawling completed. {len(df)} articles found.")
                        st.success(f"{len(df)} news articles crawled successfully!")
                        
                        st.subheader('📊 Crawled News Data')
                        df['title'] = df.apply(lambda row: f'<a href="{row["link"]}" target="_blank">{row["title"]}</a>', axis=1)
                        df = df.drop(columns=['link'])  # link 열 제거
                        df.index = range(1, len(df) + 1)  # 인덱스를 1부터 시작하는 번호로 설정
                        st.write(df.to_html(escape=False, index=True), unsafe_allow_html=True)
                        
                    else:
                        logger.warning('No news articles found.')
                        st.warning('No news articles found.')
                except Exception as e:
                    logger.error(f"An error occurred during crawling: {str(e)}", exc_info=True)
                    st.error(f"An error occurred during crawling: {str(e)}")
                    st.markdown(
                        f"""
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
                logger.warning('No keyword entered for crawling.')
                st.warning('Please enter a keyword to crawl news.')

    elif selected == "About":
        logger.info("About page selected")
        st.subheader("About this Dashboard")
        st.write("""
        This News Dashboard is designed to crawl and analyze news articles from kr.investing.com.
        It provides a simple interface to search for news based on keywords, visualize the data,
        and filter the results.
        
        Built with Streamlit, Selenium, and Plotly.
        """)

if __name__ == "__main__":
    logger.info("Starting the application")
    main()