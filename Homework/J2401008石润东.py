# import requests
# import chardet

# # 目标URL
# url = 'https://www.sdcet.edu.cn/'  # httpbin 是一个可以用来测试 HTTP 请求的服务

# # 设置请求头
# headers = {
#     'Connection': 'keep-alive',
#     'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36 Edg/135.0.0.0'
# }

# # 请求体数据（可以是字典或 JSON 格式）
# data = {
#     'name': 'SHIRUNDONG',
#     'num': '08',
# }

# # 发送 POST 请求
# response = requests.post(url, headers=headers, data=data)

# # 请求头：打印请求头内容
# print("Request Headers:")
# print(headers)

# # 请求体：查看发送的数据（POST 请求的数据）
# print("\nRequest Body (Data Sent):")
# print(data)

# # 响应体：获取并打印响应内容
# print("\nResponse Status Code:")
# print(response.status_code)  # HTTP响应状态码

# # print("\nResponse Headers:")
# # print(response.headers)  # 响应头

# # # print("\nResponse Body:")
# # # print(response.text)  # 响应体内容（文本格式）

# # # 如果响应是JSON格式，可以直接解析
# # if response.headers.get('Content-Type') == 'application/json':
# #     print("\nResponse JSON Body:")
# #     print(response.json())

# # print(f"该网页的响应格式为：{chardet.detect(response.content)['encoding']}")



import requests
import chardet
import bs4

# 目标URL
url = 'https://www.sdcet.edu.cn/'

headers = {
    'Connection': 'keep-alive',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36 Edg/135.0.0.0'
}

# 获取网页内容
response = requests.get(url, headers=headers)
response.encoding = 'utf-8'

print(f"该网页的响应格式为：{chardet.detect(response.content)['encoding']}")

print(f"该网页的响应格式为：{response.encoding}")

# 对网页内容进行解析
soup = bs4.BeautifulSoup(response.text, "html.parser")

# 获取新闻列表
paper = soup.find('ul', class_='news_list list2 clearfix')
div_list = paper.find_all('li', class_='news n4')

# 遍历新闻列表，获取标题和链接
for i in div_list:
    title = i.find('a').get_text()
    link = i.find('a')['href']
    print(f"标题: {title}")
    print(f"链接: {link}")