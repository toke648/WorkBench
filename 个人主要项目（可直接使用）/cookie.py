import requests
from PIL import Image
import http.cookiejar as cookielib

# 使用 Session 对象维持会话状态（如 Cookie）
session = requests.Session()

# 设置 cookie 存储位置
cookie_file = 'cookie.txt'

# 如果 Cookie 文件存在，则从文件中加载 Cookies
session.cookies = cookielib.LWPCookieJar(cookie_file)

try:
    session.cookies.load(cookie_file, ignore_discard=True)  # 尝试加载保存的 Cookie
    print("成功加载 Cookie")
except FileNotFoundError:
    print("Cookie 文件未找到，将会进行登录")

# 请求头
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/106.0.0.0 Safari/537.36'
}

# 获取验证码图片
kapturl = 'https://www.ptpress.com.cn/kaptcha.jpg?v=0.20690228450321835'
response = session.get(kapturl, headers=headers)

# 保存并显示验证码图片
with open('captcha.jpg', 'wb') as f:
    f.write(response.content)

# 使用 PIL 显示验证码图片
im = Image.open('captcha.jpg')
im.show()

# 用户输入验证码
kaptcha = input('请输入验证码：')
print('获取验证码为：', kaptcha)

# 登录数据
data = {
    'username': '',  # 用户名
    'password': '',   # 密码
    'verifyCode': kaptcha       # 输入的验证码
}

login_url = 'https://www.ptpress.com.cn/login'

# 发起登录请求
login_response = session.post(url=login_url, headers=headers, data=data)

# 输出响应内容和状态码
print('登录响应状态码：', login_response.status_code)
# print('登录响应内容：\n', login_response.text)

# 判断登录是否成功并保存 Cookie
if login_response.status_code == 200:
    print("登录成功，保存 Cookie 到文件")

    # 将当前会话中的 Cookie 保存到文件
    session.cookies.save(cookie_file, ignore_discard=True)
    print(f"Cookie 已保存到 {cookie_file}")
    
    # 假设登录后你想访问会员页面或其他需要登录的页面
    protected_url = 'https://www.ptpress.com.cn/login'  # 登录后需要访问的页面URL
    
    # 使用会话进行 GET 请求，携带自动存储的 Cookie
    protected_response = session.get(protected_url, headers=headers)

    # 打印登录后页面内容和状态码
    print("登录后页面状态码：", protected_response.status_code)
    # print("登录后页面内容：\n", protected_response.text)
else:
    print("登录失败，请检查用户名、密码或验证码。")
