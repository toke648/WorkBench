from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import bs4

# 配置 Chrome 浏览器
options = Options()
options.headless = False  # 设为 False 方便调试
options.add_argument("--disable-blink-features=AutomationControlled")  # 规避 Selenium 检测

driver = webdriver.Chrome(options=options)
wait = WebDriverWait(driver, 10)

# 获取 Pixiv `series` 页面所有作品链接
page_links = []
def get_pixiv_series_images(url):
    driver.get(url)
    time.sleep(3)
    
    for _ in range(2):  # 滚动加载更多内容
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)
    
    soup = bs4.BeautifulSoup(driver.page_source, "html.parser")
    links = soup.find_all("a", class_="sc-d00cb9ca-0 jmvyWD sc-5a760b36-6 bsJslY gtm-gtm-manga-series-thumbnail")
    for link in links:
        href = link.get("href")
        if href and href not in page_links:
            page_links.append("https://www.pixiv.net" + href)

# 获取所有系列页链接
for i in range(1, 6):
    url = f"https://www.pixiv.net/user/14601125/series/217742?p={i}#seriesContents"
    get_pixiv_series_images(url)
    print(f"已获取第 {i} 页的链接")
    time.sleep(2)
print("All links have been collected")

# 获取作品详情页中的图片链接
def get_image_links(url):
    print(url)
    driver.get(url)
    time.sleep(3)
    
    # 点击 "查看全部" 按钮
    try:
        view_all_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), '查看全部')]")))
        view_all_button.click()
        time.sleep(2)
    except Exception:
        print("未找到 '查看全部' 按钮，可能已展开或页面结构变化。")
    
    # 滚动加载全部内容
    for _ in range(5):
        driver.find_element(By.TAG_NAME, "body").send_keys(Keys.PAGE_DOWN)
        time.sleep(1)
    
    # 获取页面 HTML
    soup = bs4.BeautifulSoup(driver.page_source, "html.parser")
    print(soup)
    image_links = [img["src"] for img in soup.find_all("img")]
    print(image_links)
    return image_links

# 获取所有作品详情页图片链接
for link in page_links:
    get_image_links(link)

driver.quit()
