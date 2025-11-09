import json
from . import BaseParser
from typing import List, Dict, Any

class ClaudeParser(BaseParser):
    """Claude 格式解析器"""
    
    def can_parse(self, file_path: str) -> bool:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return 'conversation' in data or 'messages' in data
        except:
            return False
    
    def parse(self, file_path: str) -> List[Dict[str, Any]]:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        conversations = []
        
        # Claude 多种可能的格式
        if 'conversation' in data:
            messages = []
            for msg in data['conversation']:
                # 转换 Claude 的角色名称
                role_map = {'human': 'user', 'assistant': 'assistant'}
                messages.append({
                    'role': role_map.get(msg.get('role'), msg.get('role')),
                    'content': msg.get('content', ''),
                    'timestamp': msg.get('timestamp')
                })
            
            conversations.append({
                'title': 'Claude 对话',
                'messages': messages,
                'platform': 'claude'
            })
        
        elif 'messages' in data:
            # 另一种可能的 Claude 格式
            messages = []
            for msg in data['messages']:
                messages.append({
                    'role': msg.get('role', ''),
                    'content': msg.get('content', ''),
                    'timestamp': msg.get('timestamp')
                })
            
            conversations.append({
                'title': 'Claude 对话',
                'messages': messages,
                'platform': 'claude'
            })
        
        return conversations
    
    def get_platform_name(self) -> str:
        return "Claude"