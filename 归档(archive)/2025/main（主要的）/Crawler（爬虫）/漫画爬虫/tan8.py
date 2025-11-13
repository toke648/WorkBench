from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.chrome.options import Options
import requests
import pickle
import time
import bs4
import os

# 浏览器设置
options = Options()
options.headless = True  # 头模式，表示是否显示浏览器窗口
driver = webdriver.Chrome(options=options)

tan8_url = "https://www.tan8.com/yuepu-90966.html"

driver.get(tan8_url)
# 等待页面加载
time.sleep(3)

# # 模拟滚动加载更多内容
# for _ in range(2):  # 根据需要调整滚动次数
#     driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
#     time.sleep(2)

# 获取页面 HTML
page_source = driver.page_source

soup = bs4.BeautifulSoup(page_source, "html.parser")
links = soup.find_all("div", class_="swiper-slide swiper-slide-active").find('img')

print(links)

