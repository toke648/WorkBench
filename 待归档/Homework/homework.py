# import requests
# from selenium import webdriver
# from selenium.webdriver.common.by import By
# from selenium.webdriver.common.action_chains import ActionChains
# import time

# url = 'https://www.ptpress.com.cn/login'

# # headers = {
# #     'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36'
# # }

# # response = requests.get(url=url, headers=headers)

# # print(response.text)

# driver = webdriver.Chrome()
# driver.get(url=url)

# time.sleep(2)

# driver.find_element(By.XPATH, '//*[@id="loginForm"]/div[3]/div[2]/div/img')
# page_source = driver.page_source

# print(page_source)


import requests
from PIL import Image
headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/106.0.0.0 Safari/537.36 '}

kapturl='https://www.ptpress.com.cn/kaptcha.jpg?v=0.20690228450321835'

r=requests.get(kapturl,headers=headers)

with open('J2401008.jpg','wb')as f:f.write(r.content)
im=Image.open('J2401008.jpg')
im.show()

kaptcha=input('请输入验证码：')
print('获取验证码为：',kaptcha)

data = {
    'username': 13661797680,
    'password': 'timsrd_217',
    'verifyCode': f'{kaptcha}'
}

url = 'https://www.ptpress.com.cn/login'

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36'
}

response = requests.post(url=url, headers=headers, data=data)

print(response.text)
print(response.status_code)