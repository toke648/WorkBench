import requests
from bs4 import BeautifulSoup
import time
import os
import pandas as pd
from tqdm import tqdm
from urllib.parse import urljoin

BASE_URL = "https://www.m298.com"
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
}
DOWNLOAD_DIR = "chapter"
RETRY_TIMES = 3
SLEEP_BETWEEN_REQUESTS = 1.5


def safe_request(url, retries=RETRY_TIMES, sleep=SLEEP_BETWEEN_REQUESTS):
    for attempt in range(retries):
        try:
            response = requests.get(url, headers=HEADERS, timeout=10)
            response.raise_for_status()
            return response
        except Exception as e:
            print(f"⚠️ 请求失败 {attempt + 1}/{retries} 次：{e}")
            time.sleep(sleep)
    return None


def search_manga(name='无职转生'):
    print(f"🔍 正在搜索漫画：{name}")
    search_url = f"{BASE_URL}/search/{name}/"
    response = safe_request(search_url)
    if not response:
        return pd.DataFrame()

    response.encoding = 'gbk'
    soup = BeautifulSoup(response.text, 'html.parser')
    result_area = soup.find('div', class_='search-result-page')
    if not result_area:
        return pd.DataFrame()

    search_results = []
    for item in result_area.find_all('div', class_='cart-item'):
        title_tag = item.select_one('div.cart-info p a')
        intro_tag = item.select_one('div.cart-info span')
        img_tag = item.select_one('a.cart-cover img')
        link_tag = item.select_one('a.cart-cover')

        title = title_tag.text.strip() if title_tag else "未知标题"
        intro = intro_tag.text.strip() if intro_tag else ""
        img_url = img_tag.get('src') if img_tag else ""
        page_link = urljoin(BASE_URL, link_tag.get('href') if link_tag else "")

        search_results.append({
            'title': title,
            'intro': intro,
            'img_url': img_url,
            'page_link': page_link
        })

    df = pd.DataFrame(search_results)
    df.to_excel('search_book_lists.xlsx', index=False)
    return df


def get_html_links(comic_url):
    print("📄 正在获取章节列表...")
    response = safe_request(comic_url)
    if not response:
        return []

    response.encoding = 'gbk'
    soup = BeautifulSoup(response.text, 'html.parser')
    links = soup.find('div', class_='article-chapter-list').find_all('a')
    links_list = []

    for link in links:
        href = urljoin(BASE_URL, link.get('href'))
        title = link.text.strip().replace("/", "_")
        links_list.append({'title': title, 'href': href})
    
    return links_list


def get_image_urls(page_links, comic_title):
    print(f"📥 开始下载漫画：《{comic_title}》")

    for page_link in page_links:
        title = page_link['title']
        url = page_link['href']

        chapter_path = os.path.join(DOWNLOAD_DIR, comic_title, title)
        os.makedirs(chapter_path, exist_ok=True)

        print(f"\n📘 章节：{title}")
        print(f"🔗 链接：{url}")

        response = safe_request(url)
        if not response:
            print(f"❌ 请求失败，跳过章节：{title}")
            continue

        response.encoding = 'gbk'
        soup = BeautifulSoup(response.text, 'html.parser')
        images = soup.find('div', class_='chapter-content').find_all('img')

        for image in images:
            image_url = image.get('data-original')
            if not image_url:
                continue

            image_name = image_url.split('/')[-1]
            img_path = os.path.join(chapter_path, image_name)

            if os.path.exists(img_path):
                continue  # 已下载跳过

            img_data = safe_request(image_url)
            if img_data:
                with open(img_path, 'wb') as f:
                    f.write(img_data.content)
                    print(f"✅ 下载成功：{image_name}")
                    time.sleep(1)

        print(f"📁 章节《{title}》下载完成")
        time.sleep(1.5)


if __name__ == '__main__':
    manga_name = input("📚 请输入要搜索的漫画名：").strip()
    manga_list = search_manga(manga_name)

    if manga_list.empty:
        print("❌ 没有找到相关漫画。")
    else:
        print("\n🔎 搜索结果：")
        print(manga_list[['title', 'intro']].to_string(index=True))

        try:
            idx = int(input("\n📌 请输入要下载的漫画行号："))
            selected = manga_list.iloc[idx]
            comic_title = selected['title'].replace("/", "_")
            comic_url = selected['page_link']

            chapters = get_html_links(comic_url)
            get_image_urls(chapters, comic_title)
        except Exception as e:
            print(f"⚠️ 操作失败：{e}")
