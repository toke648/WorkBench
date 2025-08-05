import requests
from lxml import etree

# 请求网页
url = 'https://www.sdcet.edu.cn/'
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36'
}
response = requests.get(url, headers=headers)
response.encoding = 'utf-8'  # 防止乱码

# 解析网页
tree = etree.HTML(response.text)

# 输出解析后所有网页内容
print(tree.xpath('//*'))

print(tree.xpath('//li[starts-with(@class, "li")]//a/text()'))

# 网页里似乎没有和属性相关的内容
print(tree.xpath('//li[starts-with(@id, "id-")]//a/text()'))

print(tree.xpath('//li[starts-with(@class, "item")]//a/@href'))

print("J2401008 shirundong")
