"""
基本命令步骤：
pip install scrapy

scrapy startproject spider
cd spider

scrapy genspider tipdm tipdm.com

scrapy crawl main

"""

import scrapy

class NewsItem(scrapy.Item):
    url = scrapy.Field()
    title = scrapy.Field()
    date = scrapy.Field()
    views = scrapy.Field()

class MainSpider(scrapy.Spider):
    name = "main"
    allowed_domains = ["www.sdcet.edu.cn"]
    start_urls = ["https://www.sdcet.edu.cn/xwzx/924/list1.htm"]
    
    custom_settings = {
        'FEED_FORMAT': 'csv',
        'FEED_URI': 'news_output.csv',
        'FEED_EXPORT_FIELDS': ['url', 'title', 'date', 'views'],
    }

def parse(self, response):
    try:
        number = int(response.xpath('//*[@id="wp_paging_w6"]/ul/li[3]/span[1]/em[2]/text()').get())
    except (ValueError, TypeError, IndexError):
        number = 1

    url_all = [f'https://www.sdcet.edu.cn/xwzx/924/list{i}.htm' for i in range(1, number+1)]

    for url in url_all:
        yield scrapy.Request(url, callback=self.parse_list, dont_filter=True)

def parse_list(self, response):
    links = response.class_name('list-title').get()
    for link in links:
        full_link = response.urljoin(link)
        yield scrapy.Request(full_link, callback=self.parse_detail)

    def parse_detail(self, response):
        item = NewsItem()
        item['url'] = response.url
        # 提取标题
        item['title'] = response.xpath('//*[@id="d-container"]/div/div/div/h1/text()').get(default='').strip()
        # 提取时间
        item['date'] = response.xpath('//*[@id="d-container"]/div/div/div/p/span[2]/text()').get(default='').strip()
        # 提取浏览量（你可能需要根据实际网页结构调整XPath）
        item['views'] = response.xpath('//*[@id="d-container"]/div/div/div/p/span[3]/span/text()').get(default='').strip()
        yield item
