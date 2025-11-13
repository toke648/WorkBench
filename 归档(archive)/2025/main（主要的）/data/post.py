import requests

# url = 'https://www.kongsoft.cn/login'  # 替换为实际的登录URL

# # 设置请求头，模拟浏览器访问
# headers = {
#     'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
# }

# data = {
#     'username': 'admin',
#     'password': '123456'
# }

# response = requests.post(url, headers=headers, data=data)

# print(response.text)  # 打印响应内容
# print(response.status_code)  # 打印响应状态码

# 直接使用登录接口的URL和参数进行POST请求
import requests




def login():
    data = {
    'username': 'admin',
    'password': '123456'
    }

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3',
    }

    url = f'https://www.kongsoft.cn/api/user/login?username={data["username"]}&password={data["password"]}'

    response = requests.post(url, headers=headers, data=data)

    # print(response.text)  # 打印响应内容
    print(response.status_code)  # 打印响应状态码
    print(response.json())  # 打印响应的JSON内容


usernames = open('../爆破/username-CN-top500.txt', 'r')
passwords = open('../爆破/passwd-top1000.txt', 'r')

print(usernames)
print(passwords)
