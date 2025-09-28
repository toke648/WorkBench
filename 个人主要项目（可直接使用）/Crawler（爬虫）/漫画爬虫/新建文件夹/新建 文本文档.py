import requests
from bs4 import BeautifulSoup
import time
import os

def get_html_links(url):
    links_list = []

    response = requests.get(url, headers=headers)
    response.encoding = 'gbk'

    soup = BeautifulSoup(response.text, 'html.parser')
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

        if not os.path.exists(f'chapter/{title}'):
            os.makedirs(f'chapter/{title}')

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

if __name__ == '__main__':
    if not os.path.exists('chapter'):
        os.makedirs('chapter')

    url = 'https://www.m298.com/798comic_269544/'

    headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
        }

    page_links = get_html_links(url)

    get_image_urls(page_links)



