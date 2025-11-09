import os
from typing import Dict, Any
from dataclasses import dataclass
import yaml

@dataclass
class DatabaseConfig:
    """数据库配置"""
    host: str = "localhost"
    port: int = 3306
    user: str = "root"
    password: str = "password"
    database: str = "policy_agent"
    charset: str = "utf8mb4"

@dataclass
class ModelConfig:
    """模型配置"""
    default_model: str = "deepseek-chat"
    api_key: str = ""
    base_url: str = ""
    temperature: float = 0.3
    max_tokens: int = 2000
    enable_stream: bool = True

@dataclass
class SearchConfig:
    """搜索配置"""
    enable_web_search: bool = True
    search_engine: str = "serper"  # serper, duckduckgo, google
    max_results: int = 5
    timeout: int = 10

@dataclass
class UISettings:
    """界面配置"""
    theme: str = "soft"
    enable_citation: bool = True
    enable_voice: bool = False
    enable_file_upload: bool = True

class ConfigManager:
    """配置管理器"""
    
    def __init__(self, config_path: str = "config.yaml"):
        self.config_path = config_path
        self.db_config = DatabaseConfig()
        self.model_config = ModelConfig()
        self.search_config = SearchConfig()
        self.ui_settings = UISettings()
        
        self.load_config()
    
    def load_config(self):
        """加载配置文件"""
        if os.path.exists(self.config_path):
            with open(self.config_path, 'r', encoding='utf-8') as f:
                config_data = yaml.safe_load(f)
                self._update_from_dict(config_data)
    
    def _update_from_dict(self, config_dict: Dict[str, Any]):
        """从字典更新配置"""
        if 'database' in config_dict:
            for key, value in config_dict['database'].items():
                if hasattr(self.db_config, key):
                    setattr(self.db_config, key, value)
        
        if 'model' in config_dict:
            for key, value in config_dict['model'].items():
                if hasattr(self.model_config, key):
                    setattr(self.model_config, key, value)
    
    def save_config(self):
        """保存配置到文件"""
        config_data = {
            'database': self.db_config.__dict__,
            'model': self.model_config.__dict__,
            'search': self.search_config.__dict__,
            'ui': self.ui_settings.__dict__
        }
        
        with open(self.config_path, 'w', encoding='utf-8') as f:
            yaml.dump(config_data, f, default_flow_style=False, allow_unicode=True)