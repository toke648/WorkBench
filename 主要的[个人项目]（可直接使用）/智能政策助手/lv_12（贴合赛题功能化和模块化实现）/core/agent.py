# -*- coding: utf-8 -*- 核心智能体 (core/agent.py)

from typing import List, Dict, Any, Optional
import uuid
from datetime import datetime
# 改为绝对导入
from models.model_manager import ModelManager
from data.knowledge_base import KnowledgeBase
from data.web_searcher import WebSearcher
from .intent_recognizer import IntentRecognizer
from .response_generator import ResponseGenerator
from utils.cache import CacheManager
from utils.logger import get_logger

logger = get_logger(__name__)

class PolicyAgent:
    """政策咨询智能体 - 核心类"""
    
    def __init__(self, config):
        self.config = config
        self.model_manager = ModelManager(config)
        self.knowledge_base = KnowledgeBase()
        self.web_searcher = WebSearcher(config)
        self.intent_recognizer = IntentRecognizer()
        self.response_generator = ResponseGenerator()
        self.cache_manager = CacheManager()
        
        self.sessions: Dict[str, Any] = {}
        self.current_session_id = self.create_session()
    
    def create_session(self) -> str:
        """创建新会话"""
        session_id = str(uuid.uuid4())
        self.sessions[session_id] = {
            "id": session_id,
            "history": [],
            "created_at": datetime.now(),
            "title": "新对话",
            "context": {}
        }
        return session_id
    
    async def process_query(
        self, 
        query: str, 
        session_id: str = None,
        use_web_search: bool = True,
        use_knowledge_base: bool = True
    ) -> Dict[str, Any]:
        """处理用户查询"""
        session_id = session_id or self.current_session_id
        session = self.sessions.get(session_id)
        
        if not session:
            session_id = self.create_session()
            session = self.sessions[session_id]
        
        # 1. 意图识别
        intent = self.intent_recognizer.recognize(query, session['history'])
        
        # 2. 知识检索
        knowledge_results = []
        if use_knowledge_base:
            knowledge_results = self.knowledge_base.search_policies(query, limit=5)
        
        # 3. 联网搜索
        web_results = []
        if use_web_search and intent.get('need_web_search', True):
            web_results = await self.web_searcher.search(query)
        
        # 4. 生成回答
        response_data = await self.response_generator.generate(
            query=query,
            intent=intent,
            knowledge_results=knowledge_results,
            web_results=web_results,
            conversation_history=session['history'],
            model_manager=self.model_manager
        )
        
        # 5. 更新会话
        session['history'].append({
            "role": "user",
            "content": query,
            "timestamp": datetime.now()
        })
        session['history'].append({
            "role": "assistant",
            "content": response_data['answer'],
            "sources": response_data.get('sources', []),
            "timestamp": datetime.now()
        })
        
        # 6. 更新会话标题
        if len(session['history']) == 2:  # 第一次对话
            session['title'] = query[:20] + ("..." if len(query) > 20 else "")
        
        return {
            "answer": response_data['answer'],
            "sources": response_data.get('sources', []),
            "session_id": session_id,
            "intent": intent
        }
    
    def get_session_history(self, session_id: str) -> List[Dict]:
        """获取会话历史"""
        session = self.sessions.get(session_id)
        return session['history'] if session else []
    
    def clear_session(self, session_id: str):
        """清空会话"""
        if session_id in self.sessions:
            self.sessions[session_id]['history'] = []