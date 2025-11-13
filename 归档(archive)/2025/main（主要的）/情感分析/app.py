"""
运行Streamlit 应用
streamlit run app.py

"""

# 保存为 app.py
import streamlit as st
from transformers import pipeline
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time
import re
import pandas as pd
from wordcloud import WordCloud
import matplotlib.pyplot as plt
from collections import Counter

# --------------------------
# 工具函数
# --------------------------
def clean_comment(text):
    text = text.strip()
    text = re.sub(r"\s+", " ", text)
    text = re.sub(r"[^\w\s!?.,]", "", text)
    return text

def get_youtube_comments(keyword, max_scroll=10):
    url = f"https://www.youtube.com/results?search_query={keyword}"
    options = webdriver.ChromeOptions()
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--headless=new")
    driver = webdriver.Chrome(options=options)
    driver.get(url)
    time.sleep(2)

    # 点击第一个视频
    video = driver.find_element("id","video-title")
    video.click()
    time.sleep(3)

    # 滚动加载评论
    for _ in range(max_scroll):
        driver.execute_script("window.scrollTo(0, document.documentElement.scrollHeight);")
        time.sleep(2)

    page_source = driver.page_source
    soup = BeautifulSoup(page_source, "html.parser")
    comment_spans = soup.select("#contents span.yt-core-attributed-string.yt-core-attributed-string--white-space-pre-wrap")
    comments = [clean_comment(c.get_text()) for c in comment_spans if c.get_text().strip()]
    driver.quit()
    return comments

# --------------------------
# Streamlit 页面
# --------------------------
st.title("实时舆情分析系统（原型）")
keyword = st.text_input("请输入关键词", "AI")

if st.button("分析"):
    st.info(f"正在抓取与 '{keyword}' 相关的评论，请稍等...")
    comments = get_youtube_comments(keyword, max_scroll=10)
    st.success(f"抓取完成，共 {len(comments)} 条评论")

    if len(comments) == 0:
        st.warning("没有抓取到评论，尝试扩大抓取次数或检查关键词。")
    else:
        # --------------------------
        # 情绪分析
        # --------------------------
        st.info("正在进行情绪分析...")
        classifier = pipeline("sentiment-analysis")
        results = classifier(comments)
        df = pd.DataFrame(results)
        df['comment'] = comments

        st.subheader("情绪分布")
        summary = df['label'].value_counts()
        st.bar_chart(summary)

        # --------------------------
        # 关键词/热词分析
        # --------------------------
        st.subheader("热词云")
        text_all = " ".join(comments)
        wc = WordCloud(width=800, height=400, background_color="white").generate(text_all)
        plt.figure(figsize=(15,7))
        plt.imshow(wc, interpolation="bilinear")
        plt.axis("off")
        st.pyplot(plt)

        # --------------------------
        # 评论表
        # --------------------------
        st.subheader("部分抓取评论示例")
        st.dataframe(df[['comment','label','score']].head(20))
