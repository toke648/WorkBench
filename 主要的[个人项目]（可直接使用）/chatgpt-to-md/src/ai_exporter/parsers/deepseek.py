import json
from . import BaseParser
from typing import List, Dict, Any

file_path = "deepseek_export.jsonl"

class DeepSeekParser(BaseParser):
    """DeepSeek 解析器 - 支持Web版和API导出格式"""
    
    def can_parse(self, file_path: str) -> bool:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read().strip()
                
                # 尝试解析为JSON
                data = json.loads(content)
                
                # DeepSeek Web版导出格式检测
                if isinstance(data, list):
                    for item in data:
                        if isinstance(item, dict) and 'conversation_id' in item:
                            return True
                
                # DeepSeek API格式检测
                if isinstance(data, dict) and 'messages' in data:
                    return True
                    
                # DeepSeek JSONL格式检测
                if '\n' in content:
                    first_line = content.split('\n')[0].strip()
                    line_data = json.loads(first_line)
                    if 'role' in line_data and 'content' in line_data:
                        return True
                        
        except:
            pass
        return False
    
    def parse(self, file_path: str) -> List[Dict[str, Any]]:
        conversations = []
        
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read().strip()
        
        try:
            data = json.loads(content)
            
            # 格式1: DeepSeek Web版导出 (数组格式)
            if isinstance(data, list):
                for conv in data:
                    if self._parse_web_format(conv, conversations):
                        continue
            
            # 格式2: DeepSeek API格式
            elif isinstance(data, dict):
                if 'messages' in data:
                    conversations.append({
                        'title': 'DeepSeek 对话',
                        'messages': self._parse_api_messages(data['messages']),
                        'platform': 'deepseek'
                    })
                
        except json.JSONDecodeError:
            # 格式3: JSONL格式
            conversations.extend(self._parse_jsonl_format(content))
        
        return conversations
    
    def _parse_web_format(self, conv_data: dict, conversations: list) -> bool:
        """解析DeepSeek Web版导出格式"""
        if 'conversation_id' in conv_data and 'messages' in conv_data:
            messages = []
            for msg in conv_data['messages']:
                if 'role' in msg and 'content' in msg:
                    messages.append({
                        'role': msg['role'],
                        'content': msg['content'],
                        'timestamp': msg.get('create_time')
                    })
            
            if messages:
                conversations.append({
                    'title': conv_data.get('title', 'DeepSeek 对话'),
                    'messages': messages,
                    'platform': 'deepseek'
                })
                return True
        return False
    
    def _parse_api_messages(self, messages: list) -> List[Dict[str, Any]]:
        """解析API格式消息"""
        result = []
        for msg in messages:
            if isinstance(msg, dict):
                result.append({
                    'role': msg.get('role', ''),
                    'content': msg.get('content', ''),
                    'timestamp': msg.get('timestamp')
                })
        return result
    
    def _parse_jsonl_format(self, content: str) -> List[Dict[str, Any]]:
        """解析JSONL格式"""
        conversations = []
        messages = []
        
        for line in content.split('\n'):
            line = line.strip()
            if not line:
                continue
            
            try:
                data = json.loads(line)
                if 'role' in data and 'content' in data:
                    messages.append({
                        'role': data['role'],
                        'content': data['content'],
                        'timestamp': data.get('timestamp')
                    })
            except:
                continue
        
        if messages:
            conversations.append({
                'title': 'DeepSeek 对话',
                'messages': messages,
                'platform': 'deepseek'
            })
        
        return conversations
    
    def get_platform_name(self) -> str:
        return "DeepSeek"