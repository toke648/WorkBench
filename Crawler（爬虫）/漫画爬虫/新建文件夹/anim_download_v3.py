import requests
from bs4 import BeautifulSoup
import time
import os
import pandas as pd

BASE_URL = "https://www.m298.com"
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
}
DOWNLOAD_DIR = "Download"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

def get_html_links(comic_url):
    """获取漫画章节链接列表"""
    links_list = []
    try:
        response = requests.get(comic_url, headers=headers)
        response.encoding = 'gbk'
        soup = BeautifulSoup(response.text, 'html.parser')
        links = soup.find('div', class_='article-chapter-list').find_all('a')

        for link in links:
            href = BASE_URL + link.get('href')
            title = link.text.strip()
            links_list.append({'title': title, 'href': href})
            time.sleep(1)
    except Exception as e:
        print(f"⚠️ 获取章节列表失败：{e}")

    return links_list

def get_image_urls(page_links, comic_title):
    """根据章节链接下载图片"""
    for page_link in page_links:
        title = page_link['title']
        url = page_link['href']
        chapter_dir = os.path.join(DOWNLOAD_DIR, comic_title, title.replace("/", "_"))
        os.makedirs(chapter_dir, exist_ok=True)

        print(f"📥 正在下载章节：{title}")
        try:
            response = requests.get(url, headers=headers)
            response.encoding = 'gbk'
            soup = BeautifulSoup(response.text, 'html.parser')
            images = soup.find('div', class_='chapter-content').find_all('img')

            for image in images:
                image_url = image.get('data-original')
                if image_url:
                    image_name = image_url.split('/')[-1]
                    img_path = os.path.join(chapter_dir, image_name)

                    img_data = requests.get(image_url, headers=headers).content
                    with open(img_path, 'wb') as f:
                        f.write(img_data)
                    time.sleep(1)
        except Exception as e:
            print(f"⚠️ 下载章节失败：{e}")
            continue

        print(f"✅ 章节「{title}」下载完成\n")
        time.sleep(1)

def search_manga(name='无职转生'):
    """搜索漫画并返回搜索结果列表"""
    search_url = BASE_URL + f"/search/{name}/"
    search_results = []

    try:
        response = requests.get(search_url, headers=headers)
        response.encoding = 'gbk'
        soup = BeautifulSoup(response.text, 'html.parser')
        result_area = soup.find('div', class_='search-result-page')
        cart_items = result_area.find_all('div', class_='cart-item')

        for item in cart_items:
            title_tag = item.select_one('div.cart-info p a')
            intro_tag = item.select_one('div.cart-info span')
            img_tag = item.select_one('a.cart-cover img')
            link_tag = item.select_one('a.cart-cover')

            title = title_tag.text.strip() if title_tag else "未知标题"
            intro = intro_tag.text.strip() if intro_tag else ""
            img_url = img_tag.get('src') if img_tag else ""
            page_link = link_tag.get('href') if link_tag else ""

            if not page_link.startswith("http"):
                page_link = BASE_URL + page_link

            search_results.append({
                'title': title,
                'intro': intro,
                'img_url': img_url,
                'page_link': page_link
            })

        df = pd.DataFrame(search_results)
        df.to_excel('search_book_lists.xlsx', index=False)
        return df

    except Exception as e:
        print(f"⚠️ 搜索失败：{e}")
        return pd.DataFrame()

if __name__ == '__main__':
    manga_name = input("请输入要搜索的漫画名：")
    manga_list = search_manga(name=manga_name)

    if manga_list.empty:
        print("❌ 没有找到相关漫画。")
    else:
        print(manga_list[['title', 'intro']])
        try:
            idx = int(input("请输入要下载的漫画行号："))
            selected = manga_list.iloc[idx]
            comic_title = selected['title']
            comic_url = selected['page_link']

            chapters = get_html_links(comic_url)
            get_image_urls(chapters, comic_title)
        except Exception as e:
            print(f"⚠️ 下载过程出错：{e}")
