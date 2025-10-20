import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
import time
from PIL import Image

url = 'https://www.ptpress.com.cn/login'

# 无头浏览器配置
options = webdriver.ChromeOptions()
options.add_argument('--headless')  # 无头模式
options.add_argument('--disable-gpu')
options.add_argument('--no-sandbox')

driver = webdriver.Chrome(options=options) # options:  无头模式
driver.get(url=url)

time.sleep(2)

# 找到验证码图片元素
captcha_img = driver.find_element(By.XPATH, '//*[@id="loginForm"]/div[3]/div[2]/div/img')

# 保存验证码图片（可选）
captcha_img.screenshot('captcha.png')

im = Image.open('./captcha.png')
im.show()

# ----------------------------------------------------
# 图像识别
import recognition

# 请求接口
REQUEST_URL = "https://gjbsb.market.alicloudapi.com/ocrservice/advanced"

# 配置信息
appcode = "95eaaede7e784cb0a87ab55c8445a766"
img_file = "./captcha.png"
params = {
    # 是否需要识别结果中每一行的置信度，默认不需要。 true：需要 false：不需要
    "prob": False,
    # 是否需要单字识别功能，默认不需要。 true：需要 false：不需要
    "charInfo": False,
    # 是否需要自动旋转功能，默认不需要。 true：需要 false：不需要
    "rotate": False,
    # 是否需要表格识别功能，默认不需要。 true：需要 false：不需要
    "table": False,
    # 字块返回顺序，false表示从左往右，从上到下的顺序，true表示从上到下，从左往右的顺序，默认false
    "sortPage": False,
    # 是否需要去除印章功能，默认不需要。true：需要 false：不需要
    "noStamp": False,
    # 是否需要图案检测功能，默认不需要。true：需要 false：不需要
    "figure": False,
    # 是否需要成行返回功能，默认不需要。true：需要 false：不需要
    "row": False,
    # 是否需要分段功能，默认不需要。true：需要 false：不需要
    "paragraph": False,
    # 图片旋转后，是否需要返回原始坐标，默认不需要。true：需要  false：不需要
    "oricoord": True
}

data = recognition.request(appcode, img_file, params)

import json
data = json.loads(data)['content']
print(data)

# -----------------------------------------------------

# 输入用户名、密码和验证码（这里验证码需要手动输入或者使用第三方验证码识别服务）
username = '13661797680'
password = 'timsrd_217'
# verify_code = input('请输入验证码：') # 手动输入验证码

driver.find_element(By.XPATH, '//*[@id="loginForm"]/div[1]/input').send_keys(username)
driver.find_element(By.XPATH, '//*[@id="loginForm"]/div[2]/input').send_keys(password)
driver.find_element(By.XPATH, '//*[@id="loginForm"]/div[3]/div[1]/div/input').send_keys(data)

# 点击登录按钮
driver.find_element(By.XPATH, '//*[@id="loginBtn"]').click()

time.sleep(3)  # 等待登录结果

page_source = driver.page_source
print(page_source)

driver.quit()

