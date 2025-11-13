# from selenium import webdriver
# from selenium.webdriver.common.by import By
# from selenium.webdriver.common.action_chains import ActionChains
# import pandas as pd
# import time
#
# class Pixiv:
#     def __init__(self, url):
#         self.url = url
#         self.directory = []
#
#     def ranking_list(self):
#         rank_list = self.url + "/ranking.php"
#         driver.get(rank_list)
#
#         # 等待页面加载
#         time.sleep(2)  # 视情况而定，可以用 WebDriverWait 替代
#
#         # 模拟滚动页面，加载更多内容
#         for _ in range(10):  # 滚动次数根据页面加载深度决定
#             driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
#             time.sleep(1)
#
#         # 获取页面 HTML
#         page_source = driver.page_source
#
#         # 提取需要的数据（示例：图片链接）
#         from bs4 import BeautifulSoup
#         # 使用 BeautifulSoup 解析 HTML
#         soup = BeautifulSoup(page_source, "html.parser")
#
#         # 查找所有符合条件的 <a> 标签
#         links = soup.find_all("a", class_="title")  # 这里 class="title" 是你的目标条件
#         for link in links:
#             href = link.get("href")
#             text = link.text.strip()
#             # print(f"链接: {href}, 标题: {text}")
#             base_url = url + href
#             self.directory.append({"title": text, "url": base_url})
#
#         # 关闭浏览器
#         driver.quit()
#
#         pixiv_table = pd.DataFrame(self.directory)
#         print(pixiv_table)
#         pixiv_table.to_excel("./pixiv.xlsx", index=False)
#
#     def deep_link(self):
#         pass
# if __name__ == '__main__':
#     # 初始化浏览器
#     driver = webdriver.Chrome()  # 确保 ChromeDriver 已安装并设置在 PATH 中
#     url = "https://www.pixiv.net"
#
#     p = Pixiv(url)
#     p.ranking_list()



from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time

# 配置 Chrome 浏览器为无头模式
options = Options()
options.headless = True  # 无头模式
driver = webdriver.Chrome(options=options)

url = "https://www.pixiv.net/ranking.php"
driver.get(url)

# 等待页面加载
time.sleep(5)

# 模拟滚动加载更多内容
for _ in range(5):  # 根据需要调整滚动次数
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(2)

# 获取页面 HTML
html = driver.page_source
print(html)

driver.quit()
