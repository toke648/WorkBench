# # 静态网页爬取
# import requests
# import json
#
# url = 'https://www.pixiv.net/ranking.php'
#
# headers = {
#     'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
# }
#
# response = requests.get(url, headers=headers, proxies={'http': 'http://127.0.0.1:7897'})
# print(response.text)

#
# import requests
# from bs4 import BeautifulSoup
# import json
#
# url = "https://www.pixiv.net/ranking.php"
# headers = {
#     "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
# }
#
# response = requests.get(url, headers=headers, proxies={'http': 'http://127.0.0.1:7897'})
# soup = BeautifulSoup(response.text, "html.parser")
#
# # 查找内嵌的 JSON 数据
# script_tag = soup.find("script", text=lambda t: "globalInitData" in t if t else False)
# if script_tag:
#     json_data = json.loads(script_tag.string.split('=', 1)[1].strip(";"))
#     print(json_data)  # 分析并提取需要的数据
# else:
#     print("未找到内嵌数据")


from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
import time

# 初始化浏览器
driver = webdriver.Chrome()  # 确保 ChromeDriver 已安装并设置在 PATH 中
url = "https://www.pixiv.net"

rank_list = url + "/ranking.php"
driver.get(rank_list)

# 等待页面加载
time.sleep(2)  # 视情况而定，可以用 WebDriverWait 替代

# 模拟滚动页面，加载更多内容
for _ in range(10):  # 滚动次数根据页面加载深度决定
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(1)

# 获取页面 HTML
page_source = driver.page_source

# 提取需要的数据（示例：图片链接）
from bs4 import BeautifulSoup
# 使用 BeautifulSoup 解析 HTML
soup = BeautifulSoup(page_source, "html.parser")

# 查找所有符合条件的 <a> 标签
links = soup.find_all("a", class_="title")  # 这里 class="title" 是你的目标条件
for link in links:
    href = link.get("href")
    text = link.text.strip()
    # print(f"链接: {href}, 标题: {text}")
    base_url = url + href
    print(text)
    print(base_url)

# 关闭浏览器
driver.quit()




