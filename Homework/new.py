# import requests
# from selenium import webdriver
# from selenium.webdriver.common.by import By
# from selenium.webdriver.common.action_chains import ActionChains
# import time
# from PIL import Image

# url = 'https://www.ptpress.com.cn/login'

# driver = webdriver.Chrome()
# driver.get(url=url)

# time.sleep(2)

# # 找到验证码图片元素
# captcha_img = driver.find_element(By.XPATH, '//*[@id="loginForm"]/div[3]/div[2]/div/img')

# # 保存验证码图片（可选）
# captcha_img.screenshot('captcha.png')

# im = Image.open('./captcha.png')
# im.show()


# # 输入用户名、密码和验证码（这里验证码需要手动输入或者使用第三方验证码识别服务）
# username = '13661797680'
# password = 'timsrd_217'
# verify_code = input("请输入验证码: ")

# driver.find_element(By.XPATH, '//*[@id="loginForm"]/div[1]/input').send_keys(username)
# driver.find_element(By.XPATH, '//*[@id="loginForm"]/div[2]/input').send_keys(password)
# driver.find_element(By.XPATH, '//*[@id="loginForm"]/div[3]/div[1]/div/input').send_keys(verify_code)

# # 点击登录按钮
# driver.find_element(By.XPATH, '//*[@id="loginBtn"]').click()

# time.sleep(5)  # 等待登录结果

# page_source = driver.page_source
# print(page_source)

# time.sleep(5)

# driver.quit()

# 图像识别
import requests

url = "https://v2.xxapi.cn/api/ocr?url=https://cdn.xxhzm.cn/api/wenchangdijun/lq_lqwc_1.jpg"

payload = {}
headers = {
'User-Agent': 'xiaoxiaoapi/1.0.0 (https://xxapi.cn)'
}

response = requests.request("GET", url, headers = headers, data = payload)

print(response.text)
