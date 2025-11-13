"""
知识库管理模块
提供知识库的增删改查、搜索、导入等功能
"""
from typing import List, Dict, Any, Optional
import uuid
import os
from datetime import datetime
from .database import DatabaseManager
from .document_parser import DocumentParser
from config.settings import DatabaseConfig


class KnowledgeBase:
    """知识库管理器"""
    
    def __init__(self, db_manager: DatabaseManager):
        """
        初始化知识库
        
        Args:
            db_manager: 数据库管理器实例
        """
        self.db_manager = db_manager
        self.doc_parser = DocumentParser()
        self._init_default_knowledge()
    
    def _init_default_knowledge(self):
        """初始化默认知识库数据"""
        default_policies = [
            {
                "id": "car_replacement",
                "title": "汽车以旧换新补贴政策",
                "content": "燃油车购置价格10%补贴，最高1万元；新能源车购置价格15%补贴，最高1.5万元。旧车需注册登记满6年，排放标准国三及以下。",
                "source": "商务部【2024】15号文",
                "url": "https://www.mofcom.gov.cn/article/zhengce/202406/2024060345.html",
                "effective_date": "2024-01-01",
                "category": "汽车"
            },
            {
                "id": "appliance_replacement",
                "title": "家电以旧换新补贴政策",
                "content": "冰箱新品价格8%补贴，最高800元；空调新品价格10%补贴，最高1000元；电视新品价格5%补贴，最高500元。需一级能效新品，旧品使用超5年。",
                "source": "发改委【2024】8号文",
                "url": "https://www.ndrc.gov.cn/xxgk/zcfb/tz/202403/t20240315_123456.html",
                "effective_date": "2024-03-15",
                "category": "家电"
            },
            {
                "id": "digital_replacement",
                "title": "数码产品以旧换新政策",
                "content": "手机旧机折价+补贴最高1500元，电脑最高2000元，平板最高1000元。功能完好评估价80%+补贴，屏幕损坏50%+补贴，无法开机固定回收价100元。",
                "source": "工信部【2024】12号文",
                "url": "https://www.miit.gov.cn/jgsj/xxx/202404/t20240420_789012.html",
                "effective_date": "2024-04-20",
                "category": "数码"
            }
        ]
        
        # 只有当数据库为空时才添加默认数据
        existing = self.db_manager.get_all_policies()
        if not existing:
            for policy in default_policies:
                self.db_manager.insert_policy(policy)
    
    def search(self, query: str, category: Optional[str] = None, limit: int = 5) -> List[Dict[str, Any]]:
        """
        搜索知识库
        
        Args:
            query: 查询关键词
            category: 分类筛选
            limit: 返回结果数量限制
            
        Returns:
            搜索结果列表
        """
        results = self.db_manager.search_policies(query, category, limit)
        
        # 计算相关性分数
        query_lower = query.lower()
        keywords = ["汽车", "家电", "数码", "补贴", "以旧换新", "政策", "价格", "申请", "流程"]
        
        for result in results:
            score = 0
            title_lower = result.get("title", "").lower()
            content_lower = result.get("content", "").lower()
            
            # 标题匹配
            if any(keyword in title_lower for keyword in keywords if keyword in query_lower):
                score += 2
            
            # 内容匹配
            for keyword in keywords:
                if keyword in query_lower and keyword in content_lower:
                    score += 1
            
            # 类别匹配
            if category and result.get("category", "").lower() == category.lower():
                score += 1
            
            result["relevance_score"] = score
        
        # 按相关性分数排序
        results.sort(key=lambda x: x.get("relevance_score", 0), reverse=True)
        return results[:limit]
    
    def add_policy(self, policy_data: Dict[str, Any]) -> bool:
        """
        添加政策到知识库
        
        Args:
            policy_data: 政策数据字典
            
        Returns:
            是否成功
        """
        if "id" not in policy_data:
            policy_data["id"] = str(uuid.uuid4())
        
        if "effective_date" not in policy_data:
            policy_data["effective_date"] = datetime.now().strftime("%Y-%m-%d")
        
        return self.db_manager.insert_policy(policy_data)
    
    def import_from_file(self, file_path: str, auto_extract: bool = True) -> Dict[str, Any]:
        """
        从文件导入知识库
        
        Args:
            file_path: 文件路径
            auto_extract: 是否自动提取政策信息
            
        Returns:
            导入结果
        """
        # 解析文档
        parse_result = self.doc_parser.parse(file_path)
        
        if not parse_result["success"]:
            return parse_result
        
        # 保存文档到数据库
        doc_id = str(uuid.uuid4())
        doc_data = {
            "id": doc_id,
            "filename": parse_result["filename"],
            "file_path": parse_result["file_path"],
            "file_type": parse_result["file_type"],
            "content": parse_result["content"],
            "size": parse_result["size"]
        }
        
        self.db_manager.insert_document(doc_data)
        
        # 如果启用自动提取，尝试从文档中提取政策信息
        policy_data = None
        if auto_extract:
            policy_data = self._extract_policy_from_content(
                parse_result["content"],
                parse_result["filename"]
            )
            
            if policy_data:
                policy_data["id"] = str(uuid.uuid4())
                policy_data["source"] = parse_result["filename"]
                policy_data["url"] = f"#file:{doc_id}"
                self.add_policy(policy_data)
        
        return {
            "success": True,
            "document_id": doc_id,
            "policy_data": policy_data,
            "message": f"✅ 已导入文档: {parse_result['filename']}"
        }
    
    def _extract_policy_from_content(self, content: str, filename: str) -> Optional[Dict[str, Any]]:
        """
        从内容中提取政策信息（简单实现，可后续优化）
        
        Args:
            content: 文档内容
            filename: 文件名
            
        Returns:
            提取的政策数据
        """
        # 简单提取：使用文件名作为标题
        title = filename.replace(".txt", "").replace(".pdf", "").replace(".docx", "").replace(".doc", "")
        
        return {
            "title": title,
            "content": content[:5000],  # 限制长度
            "category": "自定义文档",
            "effective_date": datetime.now().strftime("%Y-%m-%d")
        }
    
    def batch_import(self, file_paths: list) -> Dict[str, Dict[str, Any]]:
        """
        批量导入文件
        
        Args:
            file_paths: 文件路径列表
            
        Returns:
            导入结果字典
        """
        results = {}
        for file_path in file_paths:
            result = self.import_from_file(file_path)
            filename = os.path.basename(file_path) if file_path else "unknown"
            results[filename] = result
        return results
    
    def get_all_categories(self) -> List[str]:
        """获取所有分类"""
        policies = self.db_manager.get_all_policies()
        categories = set()
        for policy in policies:
            if policy.get("category"):
                categories.add(policy["category"])
        return sorted(list(categories))
    
    def delete_policy(self, policy_id: str) -> bool:
        """删除政策"""
        # TODO: 实现删除逻辑
        return True

