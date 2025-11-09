"""
配置管理模块
支持从配置文件和环境变量加载配置
"""
import os
from typing import Dict, Any, Optional
from dataclasses import dataclass, asdict
import json
from pathlib import Path


@dataclass
class DatabaseConfig:
    """数据库配置"""
    host: str = "localhost"
    port: int = 3306
    user: str = "root"
    password: str = ""
    database: str = "policy_agent"
    charset: str = "utf8mb4"
    enable_mysql: bool = False  # 是否启用MySQL，False则使用内存字典


@dataclass
class ModelConfig:
    """大模型配置"""
    default_model: str = "deepseek-chat"
    api_key: str = ""
    base_url: str = "https://api.deepseek.com"
    provider: str = "openai"  # openai, deepseek, glm, custom
    temperature: float = 0.3
    max_tokens: int = 2000
    enable_stream: bool = True
    enable_deep_thinking: bool = False  # 深度思考模式
    custom_model_name: Optional[str] = None  # 自定义模型名称


@dataclass
class SearchConfig:
    """搜索配置"""
    enable_web_search: bool = True
    search_engine: str = "serper"  # serper, duckduckgo, google, bing
    api_key: str = ""  # 搜索API密钥
    max_results: int = 5
    timeout: int = 10


@dataclass
class CrawlerConfig:
    """爬虫配置"""
    enable_crawler: bool = False
    allowed_domains: list = None
    max_depth: int = 2
    delay: float = 1.0
    user_agent: str = "Mozilla/5.0"


@dataclass
class UISettings:
    """界面配置"""
    theme: str = "soft"
    enable_citation: bool = True
    enable_touch: bool = True  # 触摸支持
    enable_voice: bool = False
    enable_file_upload: bool = True
    server_name: str = "0.0.0.0"
    server_port: int = 7860


class ConfigManager:
    """配置管理器 - 统一管理所有配置"""
    
    def __init__(self, config_path: Optional[str] = None):
        """
        初始化配置管理器
        
        Args:
            config_path: 配置文件路径，如果为None则使用默认路径
        """
        if config_path is None:
            config_dir = Path(__file__).parent.parent
            config_path = config_dir / "config.json"
        
        self.config_path = Path(config_path)
        self.db_config = DatabaseConfig()
        self.model_config = ModelConfig()
        self.search_config = SearchConfig()
        self.crawler_config = CrawlerConfig()
        self.ui_settings = UISettings()
        
        # 从环境变量加载配置（优先级最高）
        self._load_from_env()
        
        # 从配置文件加载
        self.load_config()
    
    def _load_from_env(self):
        """从环境变量加载配置"""
        # 模型配置
        if os.getenv("MODEL_API_KEY"):
            self.model_config.api_key = os.getenv("MODEL_API_KEY")
        if os.getenv("MODEL_BASE_URL"):
            self.model_config.base_url = os.getenv("MODEL_BASE_URL")
        if os.getenv("MODEL_NAME"):
            self.model_config.default_model = os.getenv("MODEL_NAME")
        
        # 数据库配置
        if os.getenv("DB_HOST"):
            self.db_config.host = os.getenv("DB_HOST")
        if os.getenv("DB_PASSWORD"):
            self.db_config.password = os.getenv("DB_PASSWORD")
        
        # 搜索配置
        if os.getenv("SEARCH_API_KEY"):
            self.search_config.api_key = os.getenv("SEARCH_API_KEY")
    
    def load_config(self):
        """从配置文件加载配置"""
        if self.config_path.exists():
            try:
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    config_data = json.load(f)
                    self._update_from_dict(config_data)
            except Exception as e:
                print(f"⚠️ 加载配置文件失败: {e}，使用默认配置")
        else:
            # 如果配置文件不存在，创建默认配置
            self.save_config()
    
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
        
        if 'search' in config_dict:
            for key, value in config_dict['search'].items():
                if hasattr(self.search_config, key):
                    setattr(self.search_config, key, value)
        
        if 'crawler' in config_dict:
            for key, value in config_dict['crawler'].items():
                if hasattr(self.crawler_config, key):
                    setattr(self.crawler_config, key, value)
        
        if 'ui' in config_dict:
            for key, value in config_dict['ui'].items():
                if hasattr(self.ui_settings, key):
                    setattr(self.ui_settings, key, value)
    
    def save_config(self):
        """保存配置到文件"""
        config_data = {
            'database': asdict(self.db_config),
            'model': asdict(self.model_config),
            'search': asdict(self.search_config),
            'crawler': asdict(self.crawler_config),
            'ui': asdict(self.ui_settings)
        }
        
        try:
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(config_data, f, indent=2, ensure_ascii=False)
            print(f"✅ 配置已保存到: {self.config_path}")
        except Exception as e:
            print(f"⚠️ 保存配置失败: {e}")
    
    def get_model_config(self) -> ModelConfig:
        """获取模型配置"""
        return self.model_config
    
    def get_db_config(self) -> DatabaseConfig:
        """获取数据库配置"""
        return self.db_config
    
    def get_search_config(self) -> SearchConfig:
        """获取搜索配置"""
        return self.search_config
    
    def get_crawler_config(self) -> CrawlerConfig:
        """获取爬虫配置"""
        return self.crawler_config
    
    def get_ui_settings(self) -> UISettings:
        """获取UI设置"""
        return self.ui_settings


# 全局配置实例
_global_config: Optional[ConfigManager] = None


def get_config(config_path: Optional[str] = None) -> ConfigManager:
    """获取全局配置实例（单例模式）"""
    global _global_config
    if _global_config is None:
        _global_config = ConfigManager(config_path)
    return _global_config

