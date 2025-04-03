from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.chrome.options import Options
import time
import bs4

# 配置 Chrome 浏览器为无头模式
options = Options()
options.headless = True  # 无头模式
driver = webdriver.Chrome(options=options)

# page_links = []
# def get_pixiv_series_images(url = "https://www.pixiv.net/user/14601125/series/217742?p=1#seriesContents"):

#     driver.get(url)

#     # 等待页面加载
#     time.sleep(3)

#     # 模拟滚动加载更多内容
#     for _ in range(2):  # 根据需要调整滚动次数
#         driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
#         time.sleep(2)

#     # 获取页面 HTML
#     page_source = driver.page_source

#     # 使用 BeautifulSoup 解析 HTML
#     soup = bs4.BeautifulSoup(page_source, "html.parser")
#     links = soup.find_all("a", class_="sc-d00cb9ca-0 jmvyWD sc-5a760b36-6 bsJslY gtm-gtm-manga-series-thumbnail")
#     for link in links:
#         href = link.get("href")
#         if href not in page_links:
#             page_links.append("https://www.pixiv.net" + href)
#             print(page_links)

# for i in range(1, 5 + 1):
#     url = f"https://www.pixiv.net/user/14601125/series/217742?p={i}#seriesContents"
#     get_pixiv_series_images(url)

# driver.quit()


url = "https://www.pixiv.net/artworks/117861374"

driver.get(url)
time.sleep(3)
page_source = driver.page_source
print(page_source)