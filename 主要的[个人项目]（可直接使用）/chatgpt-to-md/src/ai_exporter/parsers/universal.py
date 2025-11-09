import json
import os
from typing import List, Dict, Any

from .base import BaseParser


class UniversalParser(BaseParser):
    """通用解析器：尽可能兼容各类 JSON/JSONL 导出结构

    目标：
    - 支持直接传入数组型 JSON，其中每项可能包含 `mapping`、`messages`、`conversation` 等字段
    - 兼容消息位于 `message.fragments` 的结构；将 `REQUEST` 视为 user、`RESPONSE` 视为 assistant
    - 回退为 JSONL（每行一个 JSON）的场景
    """

    def get_platform_name(self) -> str:
        return "Unknown"

    def can_parse(self, file_path: str) -> bool:
        # 仅处理 .json/.jsonl 文件
        lower = file_path.lower()
        if not (lower.endswith(".json") or lower.endswith(".jsonl")):
            return False

        # 快速探测内容结构
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            # JSONL：以换行分隔；尝试第一行
            if '\n' in content and lower.endswith('.jsonl'):
                first = content.split('\n', 1)[0].strip()
                json.loads(first)  # 能解析即认为可处理
                return True

            # JSON：整体加载
            data = json.loads(content)
            if isinstance(data, list):
                if not data:
                    return False
                sample = data[0]
                if isinstance(sample, dict):
                    # 只要出现这些常见字段之一就交由通用解析器
                    keys = set(sample.keys())
                    if keys & {"mapping", "messages", "conversation", "id", "title"}:
                        return True
            elif isinstance(data, dict):
                # 单会话对象
                if any(k in data for k in ("mapping", "messages", "conversation")):
                    return True
        except Exception:
            return False

        return False

    def parse(self, file_path: str) -> List[Dict[str, Any]]:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # JSONL：逐行解析为多会话或多消息
            if file_path.lower().endswith('.jsonl'):
                return self._parse_jsonl(content)

            # 标准 JSON
            data = json.loads(content)
            if isinstance(data, list):
                conversations: List[Dict[str, Any]] = []
                for conv in data:
                    parsed = self._parse_one(conv)
                    if parsed and parsed.get('messages'):
                        conversations.append(parsed)
                return conversations
            elif isinstance(data, dict):
                parsed = self._parse_one(data)
                return [parsed] if parsed and parsed.get('messages') else []
        except Exception as e:
            print(f"通用解析器错误: {e}")
            return []

    # ---- Helpers ----
    def _parse_jsonl(self, content: str) -> List[Dict[str, Any]]:
        conversations: List[Dict[str, Any]] = []
        for line in content.splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                obj = json.loads(line)
            except Exception:
                continue
            parsed = self._parse_one(obj)
            if parsed and parsed.get('messages'):
                conversations.append(parsed)
        return conversations

    def _parse_one(self, conv_data: Dict[str, Any]) -> Dict[str, Any]:
        # 优先标题与时间
        title = conv_data.get('title') or conv_data.get('id') or '对话'

        # 优先解析常见字段
        if 'messages' in conv_data and isinstance(conv_data['messages'], list):
            messages = self._normalize_messages_list(conv_data['messages'])
        elif 'conversation' in conv_data and isinstance(conv_data['conversation'], list):
            messages = self._normalize_messages_list(conv_data['conversation'])
        elif 'mapping' in conv_data and isinstance(conv_data['mapping'], dict):
            messages = self._extract_from_mapping(conv_data['mapping'])
        else:
            messages = []

        return {
            'id': conv_data.get('id', ''),
            'title': title,
            'messages': messages
        }

    def _normalize_messages_list(self, raw_messages: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        normalized: List[Dict[str, Any]] = []
        for msg in raw_messages:
            role = msg.get('role') or msg.get('author') or ''
            if isinstance(role, dict):
                role = role.get('role') or role.get('name') or ''
            content = msg.get('content') or ''
            # 有的结构是数组片段
            if isinstance(content, list):
                content = '\n'.join([str(part) for part in content])
            # 有的结构使用 fragments
            fragments = msg.get('fragments')
            if isinstance(fragments, list) and fragments:
                for frag in fragments:
                    frag_type = (frag.get('type') or '').upper()
                    frag_content = frag.get('content') or ''
                    mapped_role = 'user' if frag_type == 'REQUEST' else ('assistant' if frag_type == 'RESPONSE' else 'system')
                    if str(frag_content).strip():
                        normalized.append({
                            'role': mapped_role,
                            'content': str(frag_content).strip(),
                            'timestamp': msg.get('inserted_at') or msg.get('timestamp')
                        })
                continue

            # 常规 role/content
            if str(content).strip():
                normalized.append({
                    'role': str(role) if role else 'user',
                    'content': str(content).strip(),
                    'timestamp': msg.get('timestamp') or msg.get('inserted_at')
                })

        return normalized

    def _extract_from_mapping(self, mapping: Dict[str, Any]) -> List[Dict[str, Any]]:
        messages: List[Dict[str, Any]] = []
        # 映射中通常每项含 message，message 里可能是 content/parts 或 fragments
        for _, node in mapping.items():
            msg = node.get('message') if isinstance(node, dict) else None
            if not msg:
                continue

            # 优先 fragments（你的示例结构）
            fragments = msg.get('fragments')
            if isinstance(fragments, list) and fragments:
                ts = msg.get('inserted_at') or msg.get('timestamp')
                for frag in fragments:
                    frag_type = (frag.get('type') or '').upper()
                    content = frag.get('content') or ''
                    if not str(content).strip():
                        continue
                    role = 'user' if frag_type == 'REQUEST' else ('assistant' if frag_type == 'RESPONSE' else 'system')
                    messages.append({
                        'role': role,
                        'content': str(content).strip(),
                        'timestamp': ts
                    })
                continue

            # ChatGPT 经典 parts 结构
            content_obj = msg.get('content')
            author = msg.get('author') or {}
            if isinstance(content_obj, dict) and content_obj.get('parts'):
                parts = content_obj.get('parts') or []
                content = ''.join([str(p) for p in parts])
                if content.strip():
                    messages.append({
                        'role': author.get('role') or 'user',
                        'content': content.strip(),
                        'timestamp': msg.get('create_time') or msg.get('timestamp')
                    })

        # 映射无序，无法可靠按树排序；按时间字段尽力排序
        messages.sort(key=lambda m: m.get('timestamp') or 0)
        return messages


