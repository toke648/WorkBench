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
    allowed_domains = ["suet.edu.cn"]
    start_urls = ["https://www.suet.edu.cn/xxyw/1.htm"]
    
    custom_settings = {
        'USER_AGENT': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36',
        'DOWNLOAD_DELAY': 1,  # 控制爬取速度
    }

    def parse(self, response):
        print('start : ' + '——' * 30)
        self.logger.info(f"当前页面：{response.url}")
        
        # 提取总页数并校验
        number = response.xpath('/html/body/div[4]/div/div[2]/div[2]/div/span/span[9]/text()').get()
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
                url = "https://www.suet.edu.cn/xxyw/1.htm"
            else:
                url = f"https://www.suet.edu.cn/xxyw/{page}.htm"
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
        # page = response.meta.get("page", "1") 
        # page 返回内容为 https://www 是怎么回事？
        # 可能是因为在 meta 中传递的 page 值不正确，导致后续解析时获取到的是完整的 URL
        # 如果没有传递 page，则默认为 "1"
        # 如果需要获取列表页的页码，可以从 response.url 中提取
        # 例如：page = response.url.split("/")[-1].split(".")[0]  # 获取 URL 中的页码部分
        page = response.url.split("/")[-1].split(".")[0]

        self.logger.info(f"解析第 {page} 页列表：{response.url}")

        
        """
            # 提取所有新闻条目的链接

            三种情况：
            1. 链接以 "../" 开头，表示相对路径，需要拼接完整的域名
            2. 直接 如 1.htm 或 2.htm，表示当前域名下的页面
            3. 完整的绝对链接，如 https://mp.weixin.qq.com/s/awUoY5xPknq22H2B9oAZ3A

            对于三种情况，我们需要统一处理为绝对链接。
        """
        news_links = response.xpath('//div[@class="newlist2"]//a/@href').getall()

        self.logger.info(f"从第 {page} 页提取到 {len(news_links)} 条新闻链接")
        
        # 遍历新闻链接并发起请求
        for rel_url in news_links:
            # 将相对URL转换为绝对URL         关键  当页number + 页面相对链接
            abs_url = response.urljoin(rel_url)

            print(f"正在爬取新闻详情页：{abs_url}")
            yield scrapy.Request(
                url=abs_url,
                callback=self.parse_news_page,  # 解析新闻详情页的方法
                meta={"list_page": page}  # 传递列表页信息，便于追踪
            )

    def parse_news_page(self, response):
        """解析新闻详情页，提取完整内容"""
        list_page = response.meta.get("list_page", "未知")
        self.logger.info(f"解析新闻详情页：{response.url}")

        title = response.xpath('/html/body/div[4]/div/div[1]/div[2]/form/h2/text()').get()
            
        time = response.xpath('/html/body/div[4]/div/div[1]/div[2]/form/div[1]/span[2]/text()').get()
            
        content = response.xpath('//*[@id="vsb_content"]/div//text()').getall() # getall() 返回一个列表
        content = "\n".join([p.strip() for p in content])  # 用换行符分隔段落
        
        views = response.xpath('//span[contains(@id, "dynclicks_wbnews_2655_")]/text()').get()
        
        yield {
            "标题": title,
            "发布时间": time,
            "内容": content,
            "浏览量": views,
            "来源列表页": list_page,
            "链接": response.url
        }