# manga_utils.py
import os
import time
import requests
from bs4 import BeautifulSoup

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
}

BASE_URL = "https://www.m298.com"
SEARCH_URL = BASE_URL + "/search/"
DOWNLOAD_DIR = "Download"

os.makedirs(DOWNLOAD_DIR, exist_ok=True)

def search_manga(keyword, max_results=10):
    url = SEARCH_URL + keyword
    res = requests.get(url, headers=headers)
    res.encoding = 'gbk'
    soup = BeautifulSoup(res.text, 'html.parser')

    results = []
    books = soup.select('ul.common-comic-list li')
    for book in books[:max_results]:
        a_tag = book.find('a')
        img_tag = book.find('img')
        title_tag = book.find('p', class_='book-name')
        desc_tag = book.find('p', class_='book-detail')

        if not all([a_tag, img_tag, title_tag]):
            continue

        title = title_tag.text.strip()
        href = BASE_URL + a_tag.get('href')
        cover = img_tag.get('data-src') or img_tag.get('src')
        desc = desc_tag.text.strip() if desc_tag else ""

        results.append({
            'title': title,
            'href': href,
            'cover': cover,
            'desc': desc
        })

    return results

def download_manga(manga_info):
    title = manga_info['title']
    url = manga_info['href']
    save_dir = os.path.join(DOWNLOAD_DIR, title)
    os.makedirs(save_dir, exist_ok=True)

    log = f"开始下载《{title}》\n"

    try:
        res = requests.get(url, headers=headers)
        res.encoding = 'gbk'
        soup = BeautifulSoup(res.text, 'html.parser')

        chapters = soup.select('div.article-chapter-list a')
        for i, chap in enumerate(chapters):
            chap_title = chap.text.strip().replace('/', '_')
            chap_href = BASE_URL + chap.get('href')
            chap_dir = os.path.join(save_dir, chap_title)
            os.makedirs(chap_dir, exist_ok=True)
            
            log += f"  - 正在下载章节：{chap_title}\n"

            chapter_page = requests.get(chap_href, headers=headers)
            chapter_page.encoding = 'gbk'
            chap_soup = BeautifulSoup(chapter_page.text, 'html.parser')
            images = chap_soup.select('div.chapter-content img')

            for img in images:
                img_url = img.get('data-original') or img.get('src')
                if not img_url:
                    continue

                img_name = img_url.split('/')[-1]
                img_path = os.path.join(chap_dir, img_name)

                try:
                    img_data = requests.get(img_url, headers=headers, timeout=10).content
                    with open(img_path, 'wb') as f:
                        f.write(img_data)
                    time.sleep(0.5)
                except Exception as e:
                    log += f"    ⚠️ 下载失败：{img_url}，原因：{e}\n"

            log += f"    ✅ 章节「{chap_title}」下载完成，共{len(images)}张图\n"
            time.sleep(1)

    except Exception as e:
        log += f"❌ 下载失败：{e}\n"

    return log