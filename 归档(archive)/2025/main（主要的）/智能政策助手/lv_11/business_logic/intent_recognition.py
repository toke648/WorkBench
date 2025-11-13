"""
意图识别模块
识别用户查询的意图，用于优化检索和回答生成
"""
from typing import Dict, List, Any
import re


class IntentRecognizer:
    """意图识别器"""
    
    def __init__(self):
        """初始化意图识别器"""
        # 意图关键词映射
        self.intent_keywords = {
            "查询补贴标准": ["补贴", "标准", "金额", "多少钱", "多少元"],
            "查询申请流程": ["申请", "流程", "怎么", "如何", "步骤", "办理"],
            "查询适用条件": ["条件", "要求", "资格", "符合", "适用"],
            "查询产品范围": ["产品", "范围", "哪些", "什么", "包括"],
            "查询政策文件": ["文件", "政策", "通知", "公告", "原文"],
            "对比政策": ["对比", "区别", "差异", "哪个", "更好"],
            "时间相关": ["时间", "日期", "什么时候", "多久", "期限"],
            "地点相关": ["地点", "哪里", "什么地方", "区域", "城市"]
        }
        
        # 实体类型
        self.entity_types = {
            "category": ["汽车", "家电", "数码", "手机", "电脑", "平板"],
            "product": ["燃油车", "新能源车", "冰箱", "空调", "电视"],
            "amount": ["元", "万元", "百分比", "%"]
        }
    
    def recognize(self, query: str) -> Dict[str, Any]:
        """
        识别用户意图
        
        Args:
            query: 用户查询
            
        Returns:
            意图识别结果
        """
        query_lower = query.lower()
        
        # 识别意图
        intent_scores = {}
        for intent, keywords in self.intent_keywords.items():
            score = sum(1 for keyword in keywords if keyword in query_lower)
            if score > 0:
                intent_scores[intent] = score
        
        # 获取主要意图
        primary_intent = max(intent_scores.items(), key=lambda x: x[1])[0] if intent_scores else "通用查询"
        
        # 提取实体
        entities = self._extract_entities(query)
        
        # 识别分类
        category = self._extract_category(query)
        
        return {
            "primary_intent": primary_intent,
            "intent_scores": intent_scores,
            "entities": entities,
            "category": category,
            "confidence": max(intent_scores.values()) / len(self.intent_keywords) if intent_scores else 0.5
        }
    
    def _extract_entities(self, query: str) -> Dict[str, List[str]]:
        """提取实体"""
        entities = {
            "category": [],
            "product": [],
            "amount": []
        }
        
        query_lower = query.lower()
        
        for entity_type, keywords in self.entity_types.items():
            for keyword in keywords:
                if keyword in query_lower:
                    entities[entity_type].append(keyword)
        
        return entities
    
    def _extract_category(self, query: str) -> str:
        """提取分类"""
        query_lower = query.lower()
        
        if any(keyword in query_lower for keyword in ["汽车", "车", "燃油", "新能源"]):
            return "汽车"
        elif any(keyword in query_lower for keyword in ["家电", "冰箱", "空调", "电视"]):
            return "家电"
        elif any(keyword in query_lower for keyword in ["数码", "手机", "电脑", "平板"]):
            return "数码"
        
        return "通用"
    
    def is_question(self, query: str) -> bool:
        """判断是否是问题"""
        question_markers = ["?", "？", "什么", "怎么", "如何", "为什么", "多少", "哪个", "哪里"]
        return any(marker in query for marker in question_markers)
    
    def extract_keywords(self, query: str, top_k: int = 5) -> List[str]:
        """提取关键词"""
        # 移除停用词
        stop_words = {"的", "了", "在", "是", "我", "有", "和", "就", "不", "人", "都", "一", "一个", "上", "也", "很", "到", "说", "要", "去", "你", "会", "着", "没有", "看", "好", "自己", "这"}
        
        words = re.findall(r'\w+', query)
        keywords = [word for word in words if word not in stop_words and len(word) > 1]
        
        # 按长度和重要性排序
        keywords.sort(key=lambda x: len(x), reverse=True)
        return keywords[:top_k]

