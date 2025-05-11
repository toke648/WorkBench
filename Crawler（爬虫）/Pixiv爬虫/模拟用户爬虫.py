# from selenium import webdriver
# from selenium.webdriver.common.by import By
#
# # 创建浏览器操作对象
# # path = 'chromedriver.exe'
# browser= webdriver.Chrome()
#
# # 访问网站
# url = 'https://www.baidu.com'
# browser.get(url)
#
# button = browser.find_element(By.ID, 'su')
# # button = browser.find_elements(By.ID, 'su')
# print(button)


# # 元素定位：首先调用find_element_by_id（元素value）获得元素定位
#
# # 导包
# from time import sleep
# from selenium import webdriver
#
# # 实例化浏览器对象
# driver = webdriver.Chrome()
#
# # 打开网址url
# driver.get('https://www.baidu.com/')
#
# # 需求
# driver.find_element_by_id('kw').send_keys('易烊千玺')
#
# # 观察效果
# sleep(3)
#
# # 关闭网页
# driver.quit()


#
# """
# web 自动化基本代码
# """
# # 1、导包
# from time import sleep
# from selenium import webdriver
#
# # 2、实例化浏览器对象：类名（）
# # driver = webdriver.Chrome()
# driver = webdriver.Edge()
#
# # 3、打开网页包含协议头
# driver.get('https://www.baidu.com/')
#
# driver.find_element_by_id('document.querySelector("#kw")').send_keys('易烊千玺')
#
# # 4、时间轴观察效果
# # # sleep(2)
# #
# # # 5、关闭网页
# # driver.quit()
#

# # 1、导包
# from time import sleep
# from selenium import webdriver
# from selenium.webdriver.common.by import By
# from selenium.webdriver.common.keys import Keys
#
# # 2、实例化浏览器对象：类名（）
# driver = webdriver.Chrome()
#
# # 3、打开网页包含协议头
# driver.get('https://www.baidu.com/')
#
# # 4、找到搜索框并输入内容
# search_box = driver.find_element(By.ID, 'kw')  # 使用 By.ID 查找元素
# search_box.send_keys('python')  # 输入搜索内容
#
# # 5、模拟按下回车键进行搜索
# search_box.send_keys(Keys.RETURN)
#
# # 6、时间轴观察效果
# sleep(5)
#
# # 7、关闭网页
# driver.quit()


# 导包
from time import sleep
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

# 实例化浏览器对象
driver = webdriver.Edge()
# 打开网址url
driver.get('https://www.baidu.com/')
# 搜索
search_box = driver.find_element(By.ID, 'kw')
search_box.send_keys('世界上最大的淡水湖')

search_box.send_keys(Keys.RETURN)
# 观察效果
sleep(3)
# 关闭网页
driver.quit()
