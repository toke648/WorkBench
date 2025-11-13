# from abc import ABC, abstractmethod
# from typing import List, Dict, Any
# from pathlib import Path

# class BaseParser(ABC):
#     """解析器基类"""
    
#     @abstractmethod
#     def can_parse(self, file_path: str) -> bool:
#         """判断是否能解析该文件"""
#         pass
    
#     @abstractmethod
#     def parse(self, file_path: str) -> List[Dict[str, Any]]:
#         """解析文件返回对话列表"""
#         pass
    
#     @abstractmethod
#     def get_platform_name(self) -> str:
#         """返回平台名称"""
#         pass


from .base import BaseParser
from .chatgpt import ChatGPTParser
from .deepseek import DeepSeekParser
from .claude import ClaudeParser
from .universal import UniversalParser

__all__ = [
    "BaseParser",
    "ChatGPTParser", 
    "DeepSeekParser",
    "ClaudeParser",
    "UniversalParser"
]