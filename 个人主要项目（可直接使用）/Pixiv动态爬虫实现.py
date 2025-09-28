import os
import time
import pickle
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import bs4

# **1. 浏览器配置**
options = Options()
options.headless = False
driver = webdriver.Chrome(options=options)

# **Pixiv 主页**
pixiv_url = "https://www.pixiv.net/"
cookies_file = "cookies.pkl"

# **2. 读取 Cookies**
def load_cookies():
    driver.get(pixiv_url)
    time.sleep(1)
    if os.path.exists(cookies_file):
        with open(cookies_file, "rb") as f:
            cookies = pickle.load(f)
            for cookie in cookies:
                driver.add_cookie(cookie)
        driver.refresh()
        time.sleep(3)
        print("✅ Cookies 加载成功！")
        return True
    return False

# **3. 登录并保存 Cookies**
def login_and_save_cookies():
    driver.get("https://accounts.pixiv.net/login")
    print("🔑 请手动登录 Pixiv...")
    time.sleep(30)  # 预留时间

    cookies = driver.get_cookies()
    with open(cookies_file, "wb") as f:
        pickle.dump(cookies, f)
    print("✅ 登录成功，Cookies 已保存！")

# **4. 自动登录**
if not load_cookies():
    login_and_save_cookies()

# **5. 获取 Pixiv 作品系列的链接**
page_links = []

def get_pixiv_series_images(url):
    try:
        driver.get(url)
        time.sleep(1)

        for _ in range(1):
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(1)

        soup = bs4.BeautifulSoup(driver.page_source, "html.parser")
        links = soup.find_all("a", class_="gtm-expand-full-size-illust")
        for link in links:
            href = link.get("src")
            if href not in page_links:
                page_links.append("https://www.pixiv.net" + href)
    except Exception as e:
        print(f"⚠️ 错误: {e}")

for i in range(1, 5 + 1):
    url = f"https://www.pixiv.net/user/14601125/series/217742?p={i}#seriesContents"
    get_pixiv_series_images(url)
    print(f"✅ 已获取第 {i} 页的链接")
    time.sleep(1)

print("✅ 所有作品页面链接已获取！")

# **6. 使用 requests 下载图片**
def download_image(url, filename):
    headers = {
        "Referer": "https://www.pixiv.net/",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36"
    }
    
    session = requests.Session()
    for cookie in driver.get_cookies():
        session.cookies.set(cookie["name"], cookie["value"])
    
    response = session.get(url, headers=headers, stream=True)
    
    if response.status_code == 200:
        with open(filename, "wb") as f:
            for chunk in response.iter_content(1024):
                f.write(chunk)
        print(f"✅ 下载完成: {filename}")
    else:
        print(f"❌ 下载失败: {url}, 状态码: {response.status_code}")

# **7. 获取作品页面的所有图片**
def get_image_links(url, save_path):
    print(f"📌 访问页面: {url}")
    driver.get(url)
    time.sleep(1)

    try:
        driver.find_element(By.XPATH, '//*[@id="root"]/div[2]/div/div[3]/div/div/div[1]/main/section/div[1]/div/div[5]/div/div/button/div[2]').click()
        time.sleep(1)
    except Exception:
        print("⚠️ 没有找到 '阅读作品' 按钮，可能该页面不需要点击")

    for _ in range(1):  
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(1)

    soup = bs4.BeautifulSoup(driver.page_source, "html.parser")
    links = soup.find_all("a", class_="gtm-expand-full-size-illust")

    if not links:
        print("⚠️ 没有找到图片链接，可能需要调整 XPATH 或者手动检查 HTML 结构")
        return

    print(f"🔍 发现 {len(links)} 张图片，开始下载...")

    # **创建目录**
    if not os.path.exists(save_path):
        os.makedirs(save_path)

    for i, link in enumerate(links):
        img_url = link.get("href")
        filename = os.path.join(save_path, img_url.split("/")[-1])

        download_image(img_url, filename)
        time.sleep(1)

    print(f"✅ 章节 {save_path} 下载完成！")

# **8. 处理所有作品页面**
total_chapters = len(page_links)
for i, link in enumerate(page_links):
    chapter_number = total_chapters - i + 1  # 让最早的章节排在最前
    save_folder = f"Blue Archive/Chapter {chapter_number}"
    
    get_image_links(link, save_folder)

driver.quit()
