from abc import ABC, abstractmethod
from typing import List, Dict, Any
import os

class BaseParser(ABC):
    """解析器基类"""
    
    @abstractmethod
    def can_parse(self, file_path: str) -> bool:
        """判断是否能解析该文件"""
        pass
    
    @abstractmethod
    def parse(self, file_path: str) -> List[Dict[str, Any]]:
        """解析文件返回对话列表"""
        pass
    
    @abstractmethod
    def get_platform_name(self) -> str:
        """返回平台名称"""
        pass
    
    def _read_file(self, file_path: str) -> str:
        """读取文件内容"""
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()