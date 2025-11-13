"""
爬虫模块
支持从网页爬取政策文档并导入知识库
"""
import requests
from typing import List, Dict, Any, Optional
import time
from urllib.parse import urljoin, urlparse
from config.settings import CrawlerConfig

try:
    from bs4 import BeautifulSoup
    BS4_AVAILABLE = True
except ImportError:
    BS4_AVAILABLE = False
    print("⚠️ beautifulsoup4未安装，爬虫功能不可用")


class PolicyCrawler:
    """政策爬虫"""
    
    def __init__(self, config: CrawlerConfig):
        """
        初始化爬虫
        
        Args:
            config: 爬虫配置
        """
        self.config = config
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': config.user_agent
        })
        self.visited_urls = set()
    
    def crawl(self, url: str, max_depth: Optional[int] = None) -> Dict[str, Any]:
        """
        爬取指定URL的政策内容
        
        Args:
            url: 起始URL
            max_depth: 最大爬取深度
            
        Returns:
            爬取结果
        """
        if not self.config.enable_crawler:
            return {
                "success": False,
                "error": "爬虫功能未启用"
            }
        
        if max_depth is None:
            max_depth = self.config.max_depth
        
        try:
            # 检查域名是否允许
            parsed_url = urlparse(url)
            domain = parsed_url.netloc
            
            if self.config.allowed_domains and domain not in self.config.allowed_domains:
                return {
                    "success": False,
                    "error": f"域名 {domain} 不在允许列表中"
                }
            
            # 爬取内容
            content = self._fetch_page(url)
            if not content:
                return {
                    "success": False,
                    "error": "无法获取页面内容"
                }
            
            # 解析内容
            parsed_content = self._parse_content(content, url)
            
            return {
                "success": True,
                "url": url,
                "title": parsed_content.get("title", ""),
                "content": parsed_content.get("content", ""),
                "links": parsed_content.get("links", [])
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"爬取失败: {str(e)}"
            }
    
    def _fetch_page(self, url: str) -> Optional[str]:
        """获取网页内容"""
        if url in self.visited_urls:
            return None
        
        try:
            time.sleep(self.config.delay)
            response = self.session.get(url, timeout=self.config.timeout)
            response.raise_for_status()
            response.encoding = response.apparent_encoding
            self.visited_urls.add(url)
            return response.text
        except Exception as e:
            print(f"❌ 获取页面失败 {url}: {e}")
            return None
    
    def _parse_content(self, html: str, base_url: str) -> Dict[str, Any]:
        """解析HTML内容"""
        if not BS4_AVAILABLE:
            return {
                "title": "",
                "content": html[:1000],  # 简单截取
                "links": []
            }
        soup = BeautifulSoup(html, 'html.parser')
        
        # 提取标题
        title = ""
        if soup.title:
            title = soup.title.string
        elif soup.find('h1'):
            title = soup.find('h1').get_text()
        
        # 提取正文内容（移除脚本和样式）
        for script in soup(["script", "style", "nav", "footer", "header"]):
            script.decompose()
        
        # 尝试提取主要内容区域
        main_content = soup.find('main') or soup.find('article') or soup.find('div', class_='content')
        if main_content:
            content = main_content.get_text(separator='\n', strip=True)
        else:
            content = soup.get_text(separator='\n', strip=True)
        
        # 提取链接
        links = []
        for link in soup.find_all('a', href=True):
            href = link['href']
            absolute_url = urljoin(base_url, href)
            if self._is_valid_policy_link(absolute_url):
                links.append({
                    "url": absolute_url,
                    "text": link.get_text(strip=True)
                })
        
        return {
            "title": title,
            "content": content,
            "links": links[:10]  # 限制链接数量
        }
    
    def _is_valid_policy_link(self, url: str) -> bool:
        """判断是否是有效的政策链接"""
        policy_keywords = ['政策', '通知', '公告', '办法', '规定', '条例', '意见']
        url_lower = url.lower()
        return any(keyword in url_lower for keyword in policy_keywords)
    
    def crawl_policy_site(self, base_url: str, keywords: List[str]) -> List[Dict[str, Any]]:
        """
        爬取政策网站
        
        Args:
            base_url: 基础URL
            keywords: 关键词列表
            
        Returns:
            爬取结果列表
        """
        results = []
        # TODO: 实现更复杂的爬取逻辑
        return results

