import requests
from PIL import Image

# 使用 Session 对象维持会话状态（如 Cookie）
session = requests.Session()

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/106.0.0.0 Safari/537.36'
}

# 获取验证码图片
kapturl = 'https://www.ptpress.com.cn/kaptcha.jpg?v=0.20690228450321835'
response = session.get(kapturl, headers=headers) # 使用 Session 对象发送请求

# 保存并显示验证码图片
with open('captcha.jpg', 'wb') as f:
    f.write(response.content)

im = Image.open('captcha.jpg')
im.show()

# 用户输入验证码
kaptcha = input('请输入验证码：')
print('获取验证码为：', kaptcha)

# 登录数据
data = {
    'username': '13661797680',  # 注意用户名需要为字符串
    'password': 'timsrd_217',
    'verifyCode': kaptcha
}

login_url = 'https://www.ptpress.com.cn/login'

# 发起登录请求
login_response = session.post(url=login_url, headers=headers, data=data)

# 输出响应内容和状态码
print('响应状态码：', login_response.status_code)
print('响应内容：\n', login_response.text)
