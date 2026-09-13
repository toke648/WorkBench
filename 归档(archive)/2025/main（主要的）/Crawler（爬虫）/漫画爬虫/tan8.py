import os
import time
import pickle
import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
import bs4

# **1. 浏览器配置**
# options = Options()
# options.headless = False
# driver = webdriver.Chrome(options=options)
options = Options()
options.headless = True     # 无头模式
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=options)

tan8_url = "https://fund.eastmoney.com/data/fundranking.html"

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
# links = soup.find_all("div", class_="swiper-slide swiper-slide-active").find('img')
links = soup.find("div", class_="dbtable").find_all("tr")
# print(links)

for link in links:
    print(link.find_all("td")[0])

# tan8_url = "https://fund.eastmoney.com/data/fundranking.html"

# response = requests.get(tan8_url)   
# response.encoding = 'utf-8'
# print(response.status_code)
# print(response.text)
