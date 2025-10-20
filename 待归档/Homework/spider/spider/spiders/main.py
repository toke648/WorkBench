"""
基本命令步骤：
pip install scrapy

scrapy startproject spider
cd spider

scrapy genspider tipdm tipdm.com

scrapy crawl main

"""

import scrapy
from scrapy.exporters import CsvItemExporter

class UrlItem(scrapy.Item):
    # 定义一个Item类来存储URL
    url = scrapy.Field()

class MainSpider(scrapy.Spider):
    name = "main"
    allowed_domains = ["www.tipdm.com"]
    start_urls = ["http://www.tipdm.com/gsxw/index_2.jhtml"]  # 修正了初始URL
    
    custom_settings = {
        'FEED_FORMAT': 'csv',          # 导出格式为CSV
        'FEED_URI': 'output_urls.csv',  # 导出文件名
        'FEED_EXPORT_FIELDS': ['url'],  # 指定导出的字段
    }

    def parse(self, response):
        # 提取总页数
        try:
            number = int(response.xpath('//*[@id="t251"]/div[6]/div/a[6]/text()').get())
        except (ValueError, TypeError, IndexError):
            number = 1  # 如果提取失败，默认为1页
        
        # 生成所有页面的URL
        url_all = [f'http://www.tipdm.com/gsxw/index_{i}.jhtml' for i in range(2, number+1)]
        url_all.insert(0, 'http://www.tipdm.com/xwzx/index.jhtml')  # 加入首页

        # 输出当前页面的URL到CSV
        yield UrlItem(url=response.url)
        
        # 请求其他页面
        for url in url_all:
            yield scrapy.Request(url, callback=self.parse_url, dont_filter=True)

    def parse_url(self, response):
        # 将每个页面的URL保存到Item中
        yield UrlItem(url=response.url)