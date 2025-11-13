import json
import zipfile
import os
from typing import List, Dict, Any
from .base import BaseParser

class ChatGPTParser(BaseParser):
    """ChatGPT 导出格式解析器"""
    
    def can_parse(self, file_path: str) -> bool:
        if file_path.endswith('.zip'):
            try:
                with zipfile.ZipFile(file_path, 'r') as zip_ref:
                    return any('conversations.json' in name for name in zip_ref.namelist())
            except:
                return False
        # 支持直接传入 ChatGPT 导出的 conversations.json 文件
        if file_path.endswith('.json') and os.path.basename(file_path) == 'conversations.json':
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                # ChatGPT 导出为列表，每项通常包含 conversation_id/mapping 等
                if isinstance(data, list) and any(isinstance(item, dict) and ('mapping' in item or 'conversation_id' in item) for item in data):
                    return True
            except:
                return False
        return False
    
    def parse(self, file_path: str) -> List[Dict[str, Any]]:
        import tempfile
        import shutil
        
        conversations = []
        
        # 分支1：直接读取 conversations.json
        if file_path.endswith('.json') and os.path.basename(file_path) == 'conversations.json':
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                for conv_data in data:
                    conversation = self._parse_single_conversation(conv_data)
                    if conversation and conversation.get('messages'):
                        conversations.append(conversation)
                return conversations
            except Exception as e:
                print(f"解析 ChatGPT conversations.json 时出错: {e}")
                return []
        
        # 分支2：zip 包内查找 conversations.json
        import_path_temp_dir = tempfile.mkdtemp()
        try:
            with zipfile.ZipFile(file_path, 'r') as zip_ref:
                zip_ref.extractall(import_path_temp_dir)
            json_path = self._find_conversations_json(import_path_temp_dir)
            if not json_path:
                return conversations
            with open(json_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            for conv_data in data:
                conversation = self._parse_single_conversation(conv_data)
                if conversation and conversation.get('messages'):
                    conversations.append(conversation)
        finally:
            shutil.rmtree(import_path_temp_dir)
        
        return conversations
    
    def _find_conversations_json(self, directory: str) -> str:
        """递归查找 conversations.json"""
        for root, dirs, files in os.walk(directory):
            if 'conversations.json' in files:
                return os.path.join(root, 'conversations.json')
        return ""
    
    def _parse_single_conversation(self, conv_data: Dict[str, Any]) -> Dict[str, Any]:
        """解析单个对话"""
        try:
            messages = []
            for key, value in conv_data.get('mapping', {}).items():
                if value and 'message' in value and value['message']:
                    msg_data = value['message']
                    # 新结构：fragments（含 REQUEST/RESPONSE）
                    fragments = msg_data.get('fragments')
                    if isinstance(fragments, list) and fragments:
                        ts = msg_data.get('inserted_at') or msg_data.get('timestamp') or msg_data.get('create_time')
                        for frag in fragments:
                            frag_type = (frag.get('type') or '').upper()
                            frag_content = frag.get('content') or ''
                            if not str(frag_content).strip():
                                continue
                            role = 'user' if frag_type == 'REQUEST' else ('assistant' if frag_type == 'RESPONSE' else 'system')
                            messages.append({
                                'role': role,
                                'content': str(frag_content).strip(),
                                'timestamp': ts
                            })
                    # 经典结构：content.parts + author.role
                    elif msg_data.get('content') and msg_data.get('author'):
                        content_parts = msg_data['content'].get('parts', [''])
                        content = ''.join(content_parts) if content_parts else ''
                        if content.strip():
                            messages.append({
                                'role': msg_data['author']['role'],
                                'content': content.strip(),
                                'timestamp': msg_data.get('create_time')
                            })
            
            # 按时间排序
            messages.sort(key=lambda x: x.get('timestamp', 0))
            
            return {
                'id': conv_data.get('conversation_id', ''),
                'title': conv_data.get('title', 'ChatGPT 对话'),
                'messages': messages,
                'create_time': conv_data.get('create_time'),
                'update_time': conv_data.get('update_time')
            }
        except Exception as e:
            print(f"解析 ChatGPT 对话时出错: {e}")
            return None
    
    def get_platform_name(self) -> str:
        return "ChatGPT"