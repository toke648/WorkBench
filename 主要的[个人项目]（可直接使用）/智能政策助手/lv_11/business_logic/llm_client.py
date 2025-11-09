"""
大模型客户端模块
支持多种模型提供商和自定义模型配置
"""
from typing import List, Dict, Any, Optional, Iterator
from abc import ABC, abstractmethod
from openai import OpenAI
from config.settings import ModelConfig


class BaseLLMClient(ABC):
    """大模型客户端基类"""
    
    @abstractmethod
    def chat(self, messages: List[Dict[str, str]], **kwargs) -> str:
        """发送聊天请求"""
        pass
    
    @abstractmethod
    def stream_chat(self, messages: List[Dict[str, str]], **kwargs) -> Iterator[str]:
        """流式聊天请求"""
        pass


class OpenAICompatibleClient(BaseLLMClient):
    """OpenAI兼容的客户端（支持DeepSeek、GLM等）"""
    
    def __init__(self, config: ModelConfig):
        """
        初始化客户端
        
        Args:
            config: 模型配置
        """
        self.config = config
        self.client = OpenAI(
            api_key=config.api_key,
            base_url=config.base_url
        )
        self.model_name = config.custom_model_name or config.default_model
    
    def chat(self, messages: List[Dict[str, str]], **kwargs) -> str:
        """发送聊天请求"""
        params = {
            "model": self.model_name,
            "messages": messages,
            "temperature": kwargs.get("temperature", self.config.temperature),
            "max_tokens": kwargs.get("max_tokens", self.config.max_tokens)
        }
        
        # 深度思考模式
        if self.config.enable_deep_thinking:
            params["extra_body"] = {
                "reasoning": True  # 某些模型支持推理模式
            }
        
        response = self.client.chat.completions.create(**params)
        return response.choices[0].message.content
    
    def stream_chat(self, messages: List[Dict[str, str]], **kwargs) -> Iterator[str]:
        """流式聊天请求"""
        params = {
            "model": self.model_name,
            "messages": messages,
            "temperature": kwargs.get("temperature", self.config.temperature),
            "max_tokens": kwargs.get("max_tokens", self.config.max_tokens),
            "stream": True
        }
        
        if self.config.enable_deep_thinking:
            params["extra_body"] = {
                "reasoning": True
            }
        
        stream = self.client.chat.completions.create(**params)
        
        for chunk in stream:
            if chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content


class CustomModelClient(BaseLLMClient):
    """自定义模型客户端（可扩展支持其他模型）"""
    
    def __init__(self, config: ModelConfig, custom_api_func=None):
        """
        初始化自定义客户端
        
        Args:
            config: 模型配置
            custom_api_func: 自定义API调用函数
        """
        self.config = config
        self.custom_api_func = custom_api_func
    
    def chat(self, messages: List[Dict[str, str]], **kwargs) -> str:
        """发送聊天请求"""
        if self.custom_api_func:
            return self.custom_api_func(messages, **kwargs)
        raise NotImplementedError("需要提供自定义API函数")
    
    def stream_chat(self, messages: List[Dict[str, str]], **kwargs) -> Iterator[str]:
        """流式聊天请求"""
        if self.custom_api_func:
            result = self.chat(messages, **kwargs)
            # 简单的字符级流式输出
            for char in result:
                yield char
        raise NotImplementedError("需要提供自定义API函数")


class LLMClient:
    """统一的大模型客户端接口"""
    
    def __init__(self, config: ModelConfig):
        """
        初始化客户端
        
        Args:
            config: 模型配置
        """
        self.config = config
        self._client = self._create_client()
    
    def _create_client(self) -> BaseLLMClient:
        """根据配置创建客户端"""
        if self.config.provider == "openai" or self.config.provider == "deepseek":
            return OpenAICompatibleClient(self.config)
        elif self.config.provider == "custom":
            return CustomModelClient(self.config)
        else:
            # 默认使用OpenAI兼容客户端
            return OpenAICompatibleClient(self.config)
    
    def chat(self, messages: List[Dict[str, str]], **kwargs) -> str:
        """发送聊天请求"""
        return self._client.chat(messages, **kwargs)
    
    def stream_chat(self, messages: List[Dict[str, str]], **kwargs) -> Iterator[str]:
        """流式聊天请求"""
        return self._client.stream_chat(messages, **kwargs)
    
    def update_config(self, config: ModelConfig):
        """更新配置"""
        self.config = config
        self._client = self._create_client()


class ModelManager:
    """模型管理器 - 支持多模型切换"""
    
    def __init__(self, default_config: ModelConfig):
        """
        初始化模型管理器
        
        Args:
            default_config: 默认模型配置
        """
        self.default_config = default_config
        self.clients: Dict[str, LLMClient] = {}
        self.current_model = default_config.default_model
        
        # 创建默认客户端
        self.clients["default"] = LLMClient(default_config)
    
    def add_model(self, name: str, config: ModelConfig):
        """添加新模型"""
        self.clients[name] = LLMClient(config)
    
    def switch_model(self, name: str) -> bool:
        """切换模型"""
        if name in self.clients:
            self.current_model = name
            return True
        return False
    
    def get_client(self, model_name: Optional[str] = None) -> LLMClient:
        """获取客户端"""
        if model_name and model_name in self.clients:
            return self.clients[model_name]
        return self.clients.get(self.current_model, self.clients["default"])
    
    def list_models(self) -> List[str]:
        """列出所有可用模型"""
        return list(self.clients.keys())

