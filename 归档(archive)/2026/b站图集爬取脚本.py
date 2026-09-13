import os
import time
import pickle
import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
import bs4
import pandas as pd

os.makedirs("img", exist_ok=True)

# **1. 浏览器配置**
# options = Options()
# options.headless = False
# driver = webdriver.Chrome(options=options)
options = Options()
options.headless = True     # 无头模式
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=options)

tan8_url = "https://www.bilibili.com/read/cv24768778/?opus_fallback=1"

driver.get(tan8_url)
# 等待页面加载
time.sleep(2)

# ------------------------------------------------------------------------------------

# 渐进式滚动 - 确保中间内容被加载
scroll_step = 500  # 每次滚动的像素距离
total_scrolls = 1000  # 最大滚动次数

for i in range(total_scrolls):
    # 计算当前滚动位置
    current_scroll = driver.execute_script("return window.pageYOffset")
    viewport_height = driver.execute_script("return window.innerHeight")
    document_height = driver.execute_script("return document.body.scrollHeight")
    
    # 如果已经滚动到底部，停止滚动
    if current_scroll + viewport_height >= document_height:
        print("已滚动到页面底部")
        break
    
    # 渐进式滚动：每次滚动一定距离
    scroll_to = current_scroll + scroll_step
    driver.execute_script(f"window.scrollTo(0, {scroll_to});")
    
    print(f"第 {i+1} 次滚动，位置: {scroll_to}/{document_height}")
    time.sleep(0.1)  # 等待内容加载
    
    # 检查是否有新内容加载
    new_document_height = driver.execute_script("return document.body.scrollHeight")
    if new_document_height > document_height:
        print(f"检测到新内容加载，页面高度从 {document_height} 增加到 {new_document_height}")
        document_height = new_document_height

# ----------------------------------------------------------------------------------------------

soup = bs4.BeautifulSoup(driver.page_source, "html.parser")
# print(soup.prettify()) # 格式化输出HTML

driver.quit()

result = soup.find_all("figure", class_="img-box loaded")
print(len(result))

n = 0

for item in result:
    n += 1
    # https://i0.hdslb.com/bfs/article/76a77d6905c803f03ba2f46f94dcdb64a9e625a7.jpg@1256w_554h_!web-article-pic.avif
    img_url = "https:" + item.find("img").get("data-src").split("@")[0]
    print(img_url)
    img_name = str(n) + "." + img_url.split("@")[0].split(".")[-1]
    img_path = os.path.join("img", img_name)
    img_data = requests.get(img_url).content
    with open(img_path, "wb") as f:
        f.write(img_data)
    print(f"Downloaded {img_name}")