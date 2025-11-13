# dm5_downloader.py
import os
import time
import re
import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import logging

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

# 常量定义
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36"
DEFAULT_WAIT_TIME = 3
DEFAULT_DELAY = 0.6

class DM5Downloader:
    def __init__(self, headless=True, download_dir="downloads"):
        self.headless = headless
        self.download_dir = download_dir
        self.driver = None
        self.session = None
        
    def __enter__(self):
        self.driver = self._make_driver()
        self.session = self._selenium_cookies_to_requests()
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.driver:
            self.driver.quit()
    
    def _make_driver(self):
        """创建并配置 Chrome 驱动"""
        options = Options()
        if self.headless:
            options.add_argument('--headless=new')
        options.add_argument(f'user-agent={USER_AGENT}')
        options.add_argument('--disable-gpu')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        return webdriver.Chrome(options=options)
    
    def _selenium_cookies_to_requests(self):
        """将 Selenium cookies 转换为 requests session"""
        session = requests.Session()
        session.headers.update({'User-Agent': USER_AGENT})
        for cookie in self.driver.get_cookies():
            session.cookies.set(cookie['name'], cookie['value'])
        return session
    
    def _sanitize_filename(self, name):
        """清理文件名中的非法字符"""
        return re.sub(r'[\\/:*?"<>|]', '_', name)
    
    def _wait_for_element(self, by, value, timeout=DEFAULT_WAIT_TIME):
        """等待元素加载"""
        return WebDriverWait(self.driver, timeout).until(
            EC.presence_of_element_located((by, value))
        )
    
    def get_chapter_list(self, comic_url):
        """获取漫画章节列表"""
        logger.info(f"获取章节列表: {comic_url}")
        
        response = requests.get(comic_url, headers={'User-Agent': USER_AGENT})
        response.encoding = 'utf-8'
        soup = BeautifulSoup(response.text, 'html.parser')
        
        chapter_div = soup.find('div', id='chapterlistload')
        if not chapter_div:
            logger.error("未找到章节列表")
            return {}
        
        chapters = {}
        for link in chapter_div.find_all('a', href=True):
            title = link.get_text(strip=True)
            href = urljoin("https://m.dm5.cn", link['href'])
            chapters[href] = title
        
        # 按从新到旧排序
        return dict(reversed(list(chapters.items())))
    
    def get_total_pages(self, chapter_url):
        """获取章节总页数"""
        self.driver.get(chapter_url)
        time.sleep(DEFAULT_WAIT_TIME)
        
        soup = BeautifulSoup(self.driver.page_source, 'html.parser')
        pager = soup.find('div', id='chapterpager')
        
        if not pager:
            return 1, chapter_url.rstrip('/')
        
        # 从分页器中提取最大页数
        last_link = pager.find_all('a', href=True)[-1] if pager.find_all('a') else None
        if last_link and (match := re.search(r'-p(\d+)/', last_link['href'])):
            total_pages = int(match.group(1))
        else:
            total_pages = 1
        
        base_url = chapter_url.rstrip('/')
        return total_pages, base_url
    
    def get_image_url(self, page_url):
        """获取页面中的图片URL"""
        self.driver.get(page_url)
        self._wait_for_element(By.ID, 'cp_image')
        
        try:
            img_element = self.driver.find_element(By.ID, 'cp_image')
            return img_element.get_attribute('src')
        except Exception as e:
            logger.warning(f"通过元素获取图片失败: {e}, 尝试备用方法")
            soup = BeautifulSoup(self.driver.page_source, 'html.parser')
            img = soup.find('img', id='cp_image')
            return img.get('src') if img else None
    
    def download_image(self, img_url, referer, output_path):
        """下载图片到指定路径"""
        headers = {'Referer': referer, 'User-Agent': USER_AGENT}
        
        response = self.session.get(img_url, headers=headers, stream=True, timeout=30)
        response.raise_for_status()
        
        with open(output_path, 'wb') as file:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    file.write(chunk)
    
    def download_chapter(self, chapter_url, delay=DEFAULT_DELAY):
        """下载整个章节"""
        logger.info(f"开始下载章节: {chapter_url}")
        
        try:
            total_pages, base_url = self.get_total_pages(chapter_url)
            logger.info(f"检测到 {total_pages} 页")
            
            # 创建章节目录
            chapter_id = base_url.split('/')[-1]
            chapter_folder = os.path.join(
                self.download_dir, 
                self._sanitize_filename(chapter_id)
            )
            os.makedirs(chapter_folder, exist_ok=True)
            
            # 下载每一页
            for page_num in range(1, total_pages + 1):
                page_url = f"{base_url}/" if page_num == 1 else f"{base_url}-p{page_num}/"
                logger.info(f"处理页面 {page_num}/{total_pages}")
                
                img_url = self.get_image_url(page_url)
                if not img_url:
                    logger.warning(f"无法获取图片URL: {page_url}")
                    continue
                
                # 构建完整图片URL
                full_img_url = urljoin(page_url, img_url)
                
                # 生成输出文件名
                file_ext = os.path.splitext(full_img_url.split('?')[0])[1] or '.jpg'
                output_file = os.path.join(chapter_folder, f"{page_num:03d}{file_ext}")
                
                # 下载图片
                try:
                    self.download_image(full_img_url, page_url, output_file)
                    logger.info(f"已保存: {output_file}")
                except Exception as e:
                    logger.error(f"下载失败: {full_img_url} -> {e}")
                
                time.sleep(delay)  # 请求间隔
                
            logger.info(f"章节下载完成: {chapter_url}")
            
        except Exception as e:
            logger.error(f"下载章节时出错: {e}")
    
    def download_comic(self, comic_url, start_chapter=None, end_chapter=None):
        """下载整部漫画"""
        chapters = self.get_chapter_list(comic_url)
        
        if not chapters:
            logger.error("未找到任何章节")
            return
        
        # 筛选章节范围
        chapter_urls = list(chapters.keys())
        if start_chapter:
            chapter_urls = [url for url in chapter_urls if chapter_urls.index(url) >= start_chapter - 1]
        if end_chapter:
            chapter_urls = chapter_urls[:end_chapter]
        
        logger.info(f"准备下载 {len(chapter_urls)} 个章节")
        
        for i, chapter_url in enumerate(chapter_urls, 1):
            title = chapters[chapter_url]
            logger.info(f"进度: {i}/{len(chapter_urls)} - {title}")
            
            try:
                self.download_chapter(chapter_url)
            except Exception as e:
                logger.error(f"下载章节失败 {title}: {e}")
                continue

def main():
    """主函数"""
    COMIC_URL = "https://m.dm5.cn/manhua-dongfangzuidiehua/"
    DOWNLOAD_DIR = "downloads"
    
    with DM5Downloader(headless=True, download_dir=DOWNLOAD_DIR) as downloader:
        # 方式1: 下载整部漫画
        downloader.download_comic(COMIC_URL)
        
        # 方式2: 下载指定章节范围 (例如第1-3章)
        # downloader.download_comic(COMIC_URL, start_chapter=1, end_chapter=3)
        
        # 方式3: 下载单个章节
        # chapter_url = "https://m.dm5.cn/m943770/"
        # downloader.download_chapter(chapter_url)

if __name__ == "__main__":
    main()