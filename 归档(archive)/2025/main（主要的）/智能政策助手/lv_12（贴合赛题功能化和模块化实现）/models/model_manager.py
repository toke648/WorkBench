from typing import Dict, Any, List, Optional
from openai import OpenAI
# 改为绝对导入
from models.deepseek_client import DeepSeekClient
from models.custom_model import CustomModel
from config.settings import ConfigManager

class ModelManager:
    """统一模型管理器"""
    
    def __init__(self, config: ConfigManager):
        self.config = config
        self.clients: Dict[str, Any] = {}
        self._init_clients()
    
    def _init_clients(self):
        """初始化模型客户端"""
        model_config = self.config.model_config
        
        # DeepSeek客户端
        if model_config.default_model.startswith("deepseek"):
            self.clients["deepseek"] = DeepSeekClient(
                api_key=model_config.api_key,
                base_url=model_config.base_url
            )
        
        # OpenAI兼容客户端
        self.clients["openai"] = OpenAI(
            api_key=model_config.api_key or "sk-dummy",
            base_url=model_config.base_url
        )
        
        # 自定义模型客户端
        self.clients["custom"] = CustomModel()
    
    def get_client(self, model_type: str = None):
        """获取模型客户端"""
        if model_type and model_type in self.clients:
            return self.clients[model_type]
        return self.clients.get("deepseek") or self.clients.get("openai")
    
    async def generate_response(
        self, 
        messages: List[Dict[str, str]],
        model: str = None,
        **kwargs
    ) -> Dict[str, Any]:
        """生成回答"""
        client = self.get_client()
        model_config = self.config.model_config
        
        try:
            if hasattr(client, 'chat') and hasattr(client.chat, 'completions'):
                # OpenAI风格API
                response = client.chat.completions.create(
                    model=model or model_config.default_model,
                    messages=messages,
                    temperature=kwargs.get('temperature', model_config.temperature),
                    max_tokens=kwargs.get('max_tokens', model_config.max_tokens),
                    stream=kwargs.get('stream', model_config.enable_stream)
                )
                
                if model_config.enable_stream:
                    return self._handle_stream_response(response)
                else:
                    return {
                        "content": response.choices[0].message.content,
                        "usage": getattr(response, 'usage', {}),
                        "model": response.model
                    }
            else:
                # 自定义API
                return await client.generate_response(messages, **kwargs)
                
        except Exception as e:
            return {
                "content": f"模型调用错误: {str(e)}",
                "error": True
            }
    
    def _handle_stream_response(self, response):
        """处理流式响应"""
        for chunk in response:
            if hasattr(chunk.choices[0].delta, 'content'):
                content = chunk.choices[0].delta.content
                if content:
                    yield content