import requests

# Cookie
cookie_str = "acw_tc=1a0c63a417469549202682632e00781a8a5a84c44b75f711df6a9b20ead337; JSESSIONID=4C05271B84E6DD4F6E5D90AFDE8A920B"

# 将 Cookie 字符串转换为字典
cookies = {}
for item in cookie_str.strip().split(';'):
    if '=' in item:
        key, value = item.strip().split('=', 1)
        cookies[key] = value

# 请求头
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36'
}

url = 'https://www.ptpress.com.cn/login'

# 发送请求
response = requests.get(url, headers=headers, cookies=cookies)
response = requests.post(url, headers=headers, cookies=cookies)

print(response.text)
print("状态码：", response.status_code)
