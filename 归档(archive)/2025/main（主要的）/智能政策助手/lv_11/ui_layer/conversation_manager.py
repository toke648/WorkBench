"""
对话管理模块
管理多轮对话、会话历史等
"""
from typing import List, Dict, Any, Optional
import uuid
from datetime import datetime


class ConversationManager:
    """对话管理器"""
    
    def __init__(self):
        """初始化对话管理器"""
        self.sessions: Dict[str, Dict[str, Any]] = {}
        self.current_session_id: Optional[str] = None
    
    def create_session(self) -> str:
        """创建新会话"""
        session_id = str(uuid.uuid4())
        self.sessions[session_id] = {
            "id": session_id,
            "history": [],
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "title": "新对话",
            "current_sources": {},
            "files": []
        }
        
        if not self.current_session_id:
            self.current_session_id = session_id
        
        return session_id
    
    def get_session(self, session_id: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """获取会话"""
        sid = session_id or self.current_session_id
        return self.sessions.get(sid)
    
    def switch_session(self, session_id: str) -> bool:
        """切换会话"""
        if session_id in self.sessions:
            self.current_session_id = session_id
            return True
        return False
    
    def add_message(self, user_message: str, assistant_message: str, 
                   sources: Optional[List[Dict[str, Any]]] = None,
                   session_id: Optional[str] = None):
        """添加消息到会话"""
        session = self.get_session(session_id)
        if not session:
            session_id = self.create_session()
            session = self.get_session(session_id)
        
        session["history"].append([user_message, assistant_message])
        
        # 保存来源信息
        if sources:
            session["current_sources"] = {str(src["id"]): src for src in sources}
        
        # 更新标题（使用第一条用户消息）
        if session["title"] == "新对话" and user_message:
            session["title"] = user_message[:30] + ("..." if len(user_message) > 30 else "")
        
        session["updated_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    def get_history(self, session_id: Optional[str] = None) -> List:
        """获取对话历史"""
        session = self.get_session(session_id)
        if session:
            return session["history"]
        return []
    
    def get_sources(self, session_id: Optional[str] = None) -> Dict[str, Dict[str, Any]]:
        """获取当前来源"""
        session = self.get_session(session_id)
        if session:
            return session.get("current_sources", {})
        return {}
    
    def get_source(self, source_id: str, session_id: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """获取特定来源"""
        sources = self.get_sources(session_id)
        return sources.get(str(source_id))
    
    def list_sessions(self) -> List[Dict[str, Any]]:
        """列出所有会话"""
        sessions = []
        for sid, session in self.sessions.items():
            sessions.append({
                "id": sid,
                "title": session.get("title", "未命名对话"),
                "is_active": sid == self.current_session_id,
                "message_count": len(session.get("history", [])),
                "created_at": session.get("created_at", ""),
                "updated_at": session.get("updated_at", "")
            })
        
        # 按更新时间倒序排列
        return sorted(sessions, key=lambda x: x["updated_at"], reverse=True)
    
    def clear_session(self, session_id: Optional[str] = None):
        """清空会话"""
        session = self.get_session(session_id)
        if session:
            session["history"] = []
            session["current_sources"] = {}
            session["updated_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    def delete_session(self, session_id: str) -> bool:
        """删除会话"""
        if session_id in self.sessions:
            del self.sessions[session_id]
            if self.current_session_id == session_id:
                # 切换到其他会话或创建新会话
                remaining = list(self.sessions.keys())
                self.current_session_id = remaining[0] if remaining else self.create_session()
            return True
        return False

