import requests
import bs4
import json
import urllib.parse

def extract_image_urls(page=1):
    """提取图片URL"""
    url = f"https://imgloc.com/rundongshi/?page={page}"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }
    
    try:
        response = requests.get(url, headers=headers)
        soup = bs4.BeautifulSoup(response.text, 'html.parser')
        image_elements = soup.find_all('div', class_='list-item')
        
        image_urls = []
        for element in image_elements:
            data_object = element.get('data-object')
            if data_object:
                try:
                    decoded_data = urllib.parse.unquote(data_object)
                    image_info = json.loads(decoded_data)
                    
                    # 收集不同尺寸的图片URL
                    urls = {
                        'original': image_info.get('url'),
                        'display': image_info.get('display_url'),
                        'thumb': image_info.get('thumb', {}).get('url'),
                        'medium': image_info.get('medium', {}).get('url'),
                        'title': image_info.get('title'),
                        'id': image_info.get('id_encoded')
                    }
                    image_urls.append(urls)
                    
                except json.JSONDecodeError:
                    continue
        
        return image_urls
        
    except Exception as e:
        print(f"错误: {e}")
        return []

# 使用示例
if __name__ == "__main__":
    images = extract_image_urls(page=1)

    data = open("imgs.txt", "w", encoding="utf-8")
    
    for i, img in enumerate(images):  # 只显示前5张
        print(f"\n图片 {i+1}:")
        print(f"  标题: {img.get('title')}")
        print(f"  ID: {img.get('id')}")
        print(f"  原图: {img.get('original')}")
        print(f"  显示图: {img.get('display')}")

        data.write(f"{img.get('original')}\n")


# # collect_images.py
# import requests
# import bs4
# import json
# import urllib.parse
# import time

# def collect_all_images(max_pages=10):
#     """收集所有图片数据"""
#     all_images = []
    
#     for page in range(1, max_pages + 1):
#         print(f"正在收集第 {page} 页...")
        
#         url = f"https://imgloc.com/rundongshi/?page={page}"
#         headers = {
#             "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
#         }
        
#         try:
#             response = requests.get(url, headers=headers)
#             soup = bs4.BeautifulSoup(response.text, 'html.parser')
#             image_elements = soup.find_all('div', class_='list-item')
            
#             page_images = 0
#             for element in image_elements:
#                 data_object = element.get('data-object')
#                 if data_object:
#                     try:
#                         decoded_data = urllib.parse.unquote(data_object)
#                         image_info = json.loads(decoded_data)
                        
#                         image_data = {
#                             'id': image_info.get('id_encoded'),
#                             'title': image_info.get('title', ''),
#                             'url': image_info.get('url', ''),
#                             'display_url': image_info.get('display_url', ''),
#                             'thumb_url': image_info.get('thumb', {}).get('url', ''),
#                             'width': image_info.get('width', 0),
#                             'height': image_info.get('height', 0),
#                             'size': image_info.get('size_formatted', ''),
#                             'user': image_info.get('user', {}).get('username', ''),
#                             'viewer_url': image_info.get('url_viewer', '')
#                         }
                        
#                         if image_data['id']:  # 确保有ID
#                             all_images.append(image_data)
#                             page_images += 1
                            
#                     except json.JSONDecodeError:
#                         continue
            
#             print(f"第 {page} 页找到 {page_images} 张图片")
            
#             if page_images == 0:  # 没有图片了，停止收集
#                 break
                
#             time.sleep(1)  # 避免请求过快
            
#         except Exception as e:
#             print(f"第 {page} 页收集失败: {e}")
#             break
    
#     return all_images

# def save_to_json(images, filename='gallery_images.json'):
#     """保存到JSON文件"""
#     with open(filename, 'w', encoding='utf-8') as f:
#         json.dump(images, f, ensure_ascii=False, indent=2)
    
#     print(f"保存完成！共 {len(images)} 张图片")

# if __name__ == "__main__":
#     images = collect_all_images(max_pages=5)  # 收集5页
#     save_to_json(images)