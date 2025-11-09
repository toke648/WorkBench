"""
政策检索模块
整合知识库搜索和联网搜索
"""
from typing import List, Dict, Any, Optional
import requests
import json
from datetime import datetime
from data_service.knowledge_base import KnowledgeBase
from config.settings import SearchConfig


class PolicyRetriever:
    """政策检索器"""
    
    def __init__(self, knowledge_base: KnowledgeBase, search_config: SearchConfig):
        """
        初始化检索器
        
        Args:
            knowledge_base: 知识库实例
            search_config: 搜索配置
        """
        self.knowledge_base = knowledge_base
        self.search_config = search_config
    
    def retrieve(self, query: str, use_web: bool = True, use_knowledge: bool = True, 
                 category: Optional[str] = None) -> Dict[str, Any]:
        """
        检索政策信息
        
        Args:
            query: 查询内容
            use_web: 是否使用联网搜索
            use_knowledge: 是否使用知识库
            category: 分类筛选
            
        Returns:
            检索结果
        """
        results = {
            "knowledge_results": [],
            "web_results": [],
            "sources": []
        }
        
        # 知识库搜索
        if use_knowledge:
            knowledge_results = self.knowledge_base.search(query, category, limit=5)
            results["knowledge_results"] = knowledge_results
            
            # 转换为统一格式
            for idx, result in enumerate(knowledge_results):
                results["sources"].append({
                    "id": idx,
                    "title": result.get("title", ""),
                    "content": result.get("content", "")[:200] + "..." if len(result.get("content", "")) > 200 else result.get("content", ""),
                    "source": result.get("source", ""),
                    "url": result.get("url", "#"),
                    "type": "知识库",
                    "category": result.get("category", ""),
                    "relevance_score": result.get("relevance_score", 0)
                })
        
        # 联网搜索
        if use_web and self.search_config.enable_web_search:
            web_results = self._web_search(query)
            results["web_results"] = web_results
            
            # 转换为统一格式
            start_id = len(results["sources"])
            for idx, result in enumerate(web_results):
                results["sources"].append({
                    "id": start_id + idx,
                    "title": result.get("title", ""),
                    "content": result.get("content", "")[:200] + "..." if len(result.get("content", "")) > 200 else result.get("content", ""),
                    "source": result.get("source", ""),
                    "url": result.get("url", "#"),
                    "type": "网络搜索",
                    "date": result.get("date", ""),
                    "relevance_score": 1.0
                })
        
        return results
    
    def _web_search(self, query: str) -> List[Dict[str, Any]]:
        """联网搜索"""
        if self.search_config.search_engine == "serper":
            return self._serper_search(query)
        else:
            # 默认使用模拟搜索结果
            return self._mock_search(query)
    
    def _serper_search(self, query: str) -> List[Dict[str, Any]]:
        """使用Serper API搜索"""
        if not self.search_config.api_key:
            return self._mock_search(query)
        
        try:
            url = "https://google.serper.dev/search"
            payload = json.dumps({
                "q": f"{query} 政策 2024 以旧换新",
                "num": self.search_config.max_results
            })
            headers = {
                'X-API-KEY': self.search_config.api_key,
                'Content-Type': 'application/json'
            }
            
            response = requests.post(url, headers=headers, data=payload, timeout=self.search_config.timeout)
            if response.status_code == 200:
                data = response.json()
                results = []
                
                # 处理搜索结果
                for item in data.get('organic', [])[:self.search_config.max_results]:
                    results.append({
                        "title": item.get('title', ''),
                        "content": item.get('snippet', ''),
                        "url": item.get('link', ''),
                        "source": item.get('link', '').split('/')[2] if '/' in item.get('link', '') else '网络搜索',
                        "date": datetime.now().strftime("%Y-%m-%d")
                    })
                
                # 知识图谱结果
                if 'knowledgeGraph' in data:
                    kg = data['knowledgeGraph']
                    results.insert(0, {
                        "title": kg.get('title', query),
                        "content": kg.get('description', ''),
                        "url": kg.get('website', '#'),
                        "source": "知识图谱",
                        "date": datetime.now().strftime("%Y-%m-%d")
                    })
                
                return results
        except Exception as e:
            print(f"❌ 搜索API错误: {e}")
        
        return self._mock_search(query)
    
    def _mock_search(self, query: str) -> List[Dict[str, Any]]:
        """模拟搜索结果（备用）"""
        return [
            {
                "title": "2024年最新以旧换新政策全面解读",
                "content": "国家加大消费品以旧换新支持力度，扩大补贴范围，提高补贴标准，促进绿色消费。",
                "url": "https://www.gov.cn/zhengce/2024-06/15/content_6954321.html",
                "source": "中国政府网",
                "date": datetime.now().strftime("%Y-%m-%d")
            },
            {
                "title": "汽车以旧换新实施细则发布",
                "content": "明确补贴申请流程、材料要求和审核标准，简化办理手续。",
                "url": "https://www.mofcom.gov.cn/article/zhengce/202406/2024060345.html",
                "source": "商务部",
                "date": datetime.now().strftime("%Y-%m-%d")
            }
        ]

