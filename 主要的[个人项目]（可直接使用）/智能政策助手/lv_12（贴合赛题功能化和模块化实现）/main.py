#!/usr/bin/env python3
"""
政策咨询智能体 - 主入口文件
支持深度思考模型、MySQL知识库、智能引用显示
"""

import asyncio
import sys
import os

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config.settings import ConfigManager
from core.agent import PolicyAgent
from web.gradio_ui import GradioInterface
from utils.logger import setup_logging

async def main():
    """主函数"""
    # 初始化配置
    print("🎯 初始化政策咨询智能体...")
    config = ConfigManager()
    
    # 设置日志
    setup_logging()
    
    # 创建智能体
    print("🤖 创建政策智能体...")
    agent = PolicyAgent(config)
    
    # 创建界面
    print("🎨 创建用户界面...")
    interface = GradioInterface(agent)
    
    # 启动服务
    print("🚀 启动服务...")
    print("📝 功能特性:")
    print("   • 深度思考大模型支持")
    print("   • MySQL知识库管理") 
    print("   • 智能引用显示")
    print("   • 联网搜索")
    print("   • 多轮对话")
    print("   • 文件上传解析")
    print(f"🌐 访问地址: http://localhost:7860")
    
    # 启动界面
    interface.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=False,
        inbrowser=True
    )

if __name__ == "__main__":
    asyncio.run(main())