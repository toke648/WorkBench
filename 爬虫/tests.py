import pickle
import time
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options

# 浏览器设置
options = Options()
options.headless = False  # 关闭无头模式，避免被检测
driver = webdriver.Chrome(options=options)

# Pixiv 主页
pixiv_url = "https://www.pixiv.net/"

# **1. 加载 cookies**
def load_cookies():
    if os.path.exists("cookies.pkl"):
        driver.get(pixiv_url)
        time.sleep(3)  # 等待页面加载
        with open("cookies.pkl", "rb") as f:
            cookies = pickle.load(f)
            for cookie in cookies:
                driver.add_cookie(cookie)
        print("✅ Cookies 加载成功！")
        driver.refresh()  # 刷新页面，使 cookies 生效
        time.sleep(5)
        return True
    return False

# **2. 登录并保存 cookies**
def login_and_save_cookies():
    driver.get("https://accounts.pixiv.net/login")
    print("🔑 请手动登录 Pixiv...")
    time.sleep(30)  # 给用户足够时间登录

    # 登录后，保存 cookies
    cookies = driver.get_cookies()
    with open("cookies.pkl", "wb") as f:
        pickle.dump(cookies, f)
    print("✅ 登录成功，Cookies 已保存！")

# **3. 主运行逻辑**
if not load_cookies():
    login_and_save_cookies()
else:
    print("✅ 已使用 Cookies 登录，无需手动输入密码！")

# **4. 爬取 Pixiv 页面**
driver.get(pixiv_url)
time.sleep(5)
print("🎉 已成功进入 Pixiv！")

# 关闭浏览器
driver.quit()
