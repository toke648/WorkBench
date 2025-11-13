import requests
from bs4 import BeautifulSoup
import time
import os
import pandas as pd

def get_html_links(url):
    links_list = []

    response = requests.get(url, headers=headers)
    response.encoding = 'gbk'

    soup = BeautifulSoup(response.text, 'html.parser')
    print(soup)
    links = soup.find('div', class_='article-chapter-list').find_all('a')

    for link in links:
        href = url + link.get('href')
        title = link.text

        links_list.append({'title': title, 'href': href})
        time.sleep(1)

    return links_list

def get_image_urls(page_links):
    for page_link in page_links:
        title = page_link['title']
        url = page_link['href']

        if not os.path.exists(f'Download/chapter/{title}'):
            os.makedirs(f'Download/chapter/{title}')

        print(title)
        print(url)
        response = requests.get(url, headers=headers)
        response.encoding = 'gbk'

        soup = BeautifulSoup(response.text, 'html.parser')
        images = soup.find('div', class_='chapter-content').find_all('img')
        for image in images:
            image_url = image.get('data-original')

            if image_url:
                image_response = requests.get(image_url, headers=headers)
                image_name = image_url.split('/')[-1]
                with open(f'chapter/{title}/{image_name}', 'wb') as f:
                    f.write(image_response.content)
                    time.sleep(1)
        print(f'chapter/{title} 下载完成')

        time.sleep(1)

def search_Anim(url, name='无职转生'):
    search_book_lists = []

    search_url = url + f"/search/{name}/"
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
            page_link = url + page_link

        search_book_lists.append({
            'title': title,
            'intro': intro,
            'img_url': img_url,
            'page_link': page_link
        })
    
    pd_list = pd.DataFrame(search_book_lists)
    pd_list.to_excel('search_book_lists.xlsx', index=False)
    return pd_list

    
if __name__ == '__main__':
    BASE_URL = "https://www.m298.com"

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
    }

    DOWNLOAD_DIR = "Download"

    os.makedirs(DOWNLOAD_DIR, exist_ok=True)

    name = input("请输入要搜索的漫画名：")

    Anim_list = search_Anim(url=BASE_URL, name=name)
    print(Anim_list)

    num = input("请输入要下载的漫画链接 行序号：")

    print(Anim_list.iloc[int(num)])
    print(Anim_list.iloc[int(num)]['page_link'])

    page_links = get_html_links(Anim_list.iloc[int(num)]['page_link'])

    get_image_urls(page_links)

