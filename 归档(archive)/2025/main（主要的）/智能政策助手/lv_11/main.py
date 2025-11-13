#!/usr/bin/env python3
"""
政策咨询智能体 - 主入口文件
模块化架构版本，支持：
- 灵活的模型配置（支持自定义模型和API）
- 深度思考模式
- MySQL知识库（可选）
- 爬虫导入（可选）
- 触摸友好的引用显示
"""
import sys
import os
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from config import ConfigManager, get_config
from data_service.database import DatabaseManager
from data_service.knowledge_base import KnowledgeBase
from business_logic.llm_client import LLMClient, ModelManager
from business_logic.intent_recognition import IntentRecognizer
from business_logic.policy_retrieval import PolicyRetriever
from business_logic.response_generator import ResponseGenerator
from ui_layer.conversation_manager import ConversationManager
from ui_layer.gradio_interface import GradioInterface
from utils.logger import setup_logging


def initialize_system():
    """初始化系统组件"""
    print("=" * 60)
    print("🎯 政策咨询智能体 - 模块化架构版本")
    print("=" * 60)
    
    # 1. 加载配置
    print("\n📋 [1/8] 加载配置...")
    config = get_config()
    print(f"   ✅ 配置加载完成")
    print(f"   - 模型: {config.model_config.default_model}")
    print(f"   - 数据库: {'MySQL' if config.db_config.enable_mysql else '内存模式'}")
    print(f"   - 联网搜索: {'启用' if config.search_config.enable_web_search else '禁用'}")
    
    # 2. 设置日志
    print("\n📝 [2/8] 设置日志系统...")
    setup_logging()
    print("   ✅ 日志系统就绪")
    
    # 3. 初始化数据库
    print("\n💾 [3/8] 初始化数据库...")
    db_manager = DatabaseManager(config.db_config)
    print("   ✅ 数据库初始化完成")
    
    # 4. 初始化知识库
    print("\n📚 [4/8] 初始化知识库...")
    knowledge_base = KnowledgeBase(db_manager)
    print(f"   ✅ 知识库初始化完成")
    
    # 5. 初始化LLM客户端
    print("\n🤖 [5/8] 初始化大模型客户端...")
    llm_client = LLMClient(config.model_config)
    model_manager = ModelManager(config.model_config)
    print(f"   ✅ LLM客户端初始化完成 ({config.model_config.default_model})")
    
    # 6. 初始化业务逻辑组件
    print("\n🔧 [6/8] 初始化业务逻辑组件...")
    intent_recognizer = IntentRecognizer()
    policy_retriever = PolicyRetriever(knowledge_base, config.search_config)
    response_generator = ResponseGenerator(
        llm_client, policy_retriever, intent_recognizer
    )
    print("   ✅ 业务逻辑组件初始化完成")
    
    # 7. 初始化对话管理器
    print("\n💬 [7/8] 初始化对话管理器...")
    conversation_manager = ConversationManager()
    conversation_manager.create_session()
    print("   ✅ 对话管理器初始化完成")
    
    # 8. 创建界面
    print("\n🎨 [8/8] 创建用户界面...")
    interface = GradioInterface(
        response_generator,
        knowledge_base,
        conversation_manager,
        config.ui_settings
    )
    print("   ✅ 用户界面创建完成")
    
    print("\n" + "=" * 60)
    print("🚀 系统初始化完成！")
    print("=" * 60)
    print("\n📝 功能特性:")
    print("   ✅ 灵活的模型配置（支持自定义模型和API）")
    print("   ✅ 深度思考模式")
    print("   ✅ MySQL知识库（可选内存模式）")
    print("   ✅ 文档一键导入")
    print("   ✅ 爬虫功能（可选）")
    print("   ✅ 触摸友好的引用显示")
    print("   ✅ 多轮对话管理")
    print("   ✅ 联网搜索")
    print("\n🌐 访问地址: http://localhost:{}".format(config.ui_settings.server_port))
    print("=" * 60 + "\n")
    
    return interface, config


def main():
    """主函数"""
    try:
        # 初始化系统
        interface, config = initialize_system()
        
        # 启动界面
        interface.launch(
            server_name=config.ui_settings.server_name,
            server_port=config.ui_settings.server_port,
            share=False,
            inbrowser=True
        )
    except KeyboardInterrupt:
        print("\n\n👋 程序已停止")
    except Exception as e:
        print(f"\n❌ 启动失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()

