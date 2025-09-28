import requests
import bs4
import pandas as pd
import time

def get_links():
    links_list = []

    url = "https://www.qu05.cc/html/38889/"

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
    }

    response = requests.get(url, headers=headers)

    soup = bs4.BeautifulSoup(response.text, "html.parser")
    # print(soup.prettify()) # 输出格式化后的 HTML
    links = soup.find("div", class_="listmain").find_all("dd")

    for link in links:
        # print(link.a.get("href"))
        lk = "https://www.qu05.cc" + link.a.get("href")
        name = link.a.text
        links_list.append({"name": name, "link": lk})

    book = pd.DataFrame(links_list)
    # book.to_excel("book.xlsx", index=False)
    return book

def get_content(book):
    for i in range(len(book)):
        try:     
            url = book.iloc[i, 1]

            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
            }

            response = requests.get(url, headers=headers)
            soup = bs4.BeautifulSoup(response.text, "html.parser")
            text = soup.find("div", class_="Readarea ReadAjax_content").get_text(separator="\n")
            title = book.iloc[i, 0]

            # open() 追加使用文本
            with open("飘飘欲仙狼太郎.txt", "a", encoding="utf-8") as f:
                f.write(title + "\n")
                f.write(text + "\n")

            print(f'{title} complete')
            time.sleep(1)
        except Exception as e:
            print(f"Error occurred: {e}")
            continue
    print("all complete")

if __name__ == "__main__":
    book = get_links()
    get_content(book)
