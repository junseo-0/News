import streamlit as st
import pandas as pd
import plotly.express as px
from streamlit_option_menu import option_menu
from crawler import crawl_news

# 페이지 설정
st.set_page_config(layout="wide", page_title="News Dashboard", page_icon="📰")

# 스타일 적용
st.markdown("""
<style>
    .reportview-container {
        background: #f0f2f6
    }
    .main {
        background: #ffffff;
        padding: 2rem;
        border-radius: 10px;
        box-shadow: 0 0 10px rgba(0,0,0,.1);
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
    if filter_keyword:
        return df[df['title'].str.contains(filter_keyword, case=False, na=False)]
    return df

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
            keyword = st.text_input('Enter keyword to crawl news', '검색')
        with col2:
            num_news = st.slider('Number of news articles', 5, 50, 10)

        if st.button('Crawl News', key='crawl_button'):
            if keyword:
                # 진행 상황을 표시할 상태 표시줄 생성
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                try:
                    df = pd.DataFrame()
                    for i, news_item in enumerate(crawl_news(keyword, num_news)):
                        df = pd.concat([df, pd.DataFrame([news_item])], ignore_index=True)
                        # 진행 상황 업데이트
                        progress = int((i + 1) / num_news * 100)
                        progress_bar.progress(progress)
                        status_text.text(f"Crawling... {i+1}/{num_news} articles")
                        
                    # 크롤링 완료 후 상태 표시줄 제거
                    progress_bar.empty()
                    status_text.empty()
                    
                    if not df.empty:
                        st.success(f"{len(df)} news articles crawled successfully!")
                        
                        # 데이터 표시 (하이퍼링크 포함)
                        st.subheader('📊 Crawled News Data')
                        df['link'] = df['link'].apply(lambda x: f'<a href="{x}" target="_blank">{x}</a>')
                        st.write(df.to_html(escape=False, index=False), unsafe_allow_html=True)
                        
                        # 필터링
                        filter_keyword = st.text_input('Enter keyword to filter news')
                        if filter_keyword:
                            filtered_df = filter_news(df, filter_keyword)
                            st.subheader('🔍 Filtered News Data')
                            st.write(filtered_df.to_html(escape=False, index=False), unsafe_allow_html=True)

                        # 시각화
                        st.subheader('📈 News Title Length Distribution')
                        fig = px.histogram(df, x=df['title'].str.len(), nbins=20,
                                           labels={'x':'Title Length', 'y':'Count'},
                                           title='Distribution of News Title Lengths')
                        fig.update_layout(xaxis_range=[0, max(df['title'].str.len()) + 10])
                        st.plotly_chart(fig, use_container_width=True)

                    else:
                        st.warning('No news articles found.')
                except Exception as e:
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
                st.warning('Please enter a keyword to crawl news.')

    elif selected == "About":
        st.subheader("About this Dashboard")
        st.write("""
        This News Dashboard is designed to crawl and analyze news articles from kr.investing.com.
        It provides a simple interface to search for news based on keywords, visualize the data,
        and filter the results.
        
        Built with Streamlit, Selenium, and Plotly.
        """)

if __name__ == "__main__":
    main()