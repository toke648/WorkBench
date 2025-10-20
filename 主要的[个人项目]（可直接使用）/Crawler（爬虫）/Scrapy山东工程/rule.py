import scrapy

"""
# 安装依赖
pip install scrapy

# 创建项目
scrapy startproject spider

# 创建一个爬虫程序 
scrapy genspider main sdcet.edu.cn

# 进入项目路径
# cd spider

# 执行代码
scrapy crawl main

# 指定输出文件
如果想覆盖默认的存储方式，可以直接指定输出格式：
# 保存为 JSON
scrapy crawl main -o output.json  

# 保存为 CSV
scrapy crawl main -o output.csv  
 
# 保存为 XML
scrapy crawl main -o output.xml   

# 日志级别
控制终端输出的详细程度：
scrapy crawl main --loglevel=INFO  # 只显示 INFO 及以上级别日志
scrapy crawl main --loglevel=DEBUG # 显示所有调试信息

# 找不到模块错误
确保在项目根目录下执行
scrapy crawl main

或使用 Python 直接运行
python -m scrapy crawl main

"""

class MainSpider(scrapy.Spider):
    name = "main"
    allowed_domains = ["sdcet.edu.cn"]
    start_urls = ["https://www.sdcet.edu.cn/tzgg/list.htm"]
    
    custom_settings = {
        'USER_AGENT': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36',
        'DOWNLOAD_DELAY': 1,  # 控制爬取速度
    }

    def parse(self, response):
        print('start : ' + '——' * 30)
        self.logger.info(f"当前页面：{response.url}")
        
        # 提取总页数并校验
        number = response.xpath('//*[@id="wp_paging_w6"]/ul/li[3]/span[1]/em[2]/text()').get()
        if not number:
            self.logger.error("未提取到总页数，终止爬取")
            return

        try:
            total_pages = int(number)
            self.logger.info(f"总页数：{total_pages}")
        except ValueError:
            self.logger.error(f"总页数格式错误：{number}")
            return

        # 生成所有页面链接
        links = []
        for page in range(1, total_pages + 1):
            if page == 1:
                url = "https://www.sdcet.edu.cn/tzgg/list.htm"
            else:
                url = f"https://www.sdcet.edu.cn/tzgg/list{page}.htm"
            links.append(url)

        self.logger.info(f"生成 {len(links)} 个页面链接")

        # 遍历列表页链接并发起请求
        for link in links:
            print(f"正在爬取列表页：{link}")
            yield scrapy.Request(
                url=link,
                callback=self.parse_list_page,  # 解析列表页的方法
                meta={"page": link.split("list")[-1].split(".")[0] or "1"}
            )

        print('end : ' + '——' * 30)

    def parse_list_page(self, response):
        """解析列表页，提取每条新闻的链接并继续爬取"""
        page = response.meta.get("page", "1")
        self.logger.info(f"解析第 {page} 页列表：{response.url}")

        # 提取所有新闻条目的链接
        news_links = response.xpath('//ul[@class="news_list list2"]/li//span[@class="news_title"]/a/@href').getall()
        
        self.logger.info(f"从第 {page} 页提取到 {len(news_links)} 条新闻链接")
        
        # 遍历新闻链接并发起请求
        for rel_url in news_links:
            # 将相对URL转换为绝对URL
            abs_url = response.urljoin(rel_url)
            yield scrapy.Request(
                url=abs_url,
                callback=self.parse_news_page,  # 解析新闻详情页的方法
                meta={"list_page": page}  # 传递列表页信息，便于追踪
            )

    def parse_news_page(self, response):
        """解析新闻详情页，提取完整内容"""
        list_page = response.meta.get("list_page", "未知")
        self.logger.info(f"解析新闻详情页：{response.url}")

        # 提取新闻标题（假设在 <div class="article-title"> 下的 <h1> 中）
        title = response.xpath('//div[contains(@class, "article-title")]/h1/text()').get()
        if not title:
            title = response.xpath('//h1[@class="arti_title"]/text()').get()  # 备用选择器
            
        # 提取发布时间（假设格式为 "发布时间：2025-05-26"）
        time = response.xpath('//*[@id="d-container"]/div/div/div/p/span[1]/text()').get()
            
        # 提取正文内容（合并段落，保留排版）
        content = response.xpath('//div[@class="wp_articlecontent"]//text()[normalize-space()]').getall()
        content = "\n".join([p.strip() for p in content])  # 用换行符分隔段落
        
        # # 提取浏览量（假设在 <div class="arti_metas"> 下的 <span class="WP_VisitCount"> 中）
        # views = response.xpath('//div[contains(@class, "arti_metas")]//span[@class="WP_VisitCount"]/text()').get()

        yield {
            "标题": title,
            "发布时间": time,
            # "内容": content,
            # "浏览量": views,
            # "来源列表页": list_page,
            # "链接": response.url
        }