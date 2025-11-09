# -*- coding: utf-8 -*- Gradio用户界面 (web/gradio_ui.py)

import gradio as gr
from typing import List, Dict, Any
import asyncio
# 改为绝对导入
from core.agent import PolicyAgent
from .components.citation_display import CitationDisplay
from .components.session_manager import SessionManager
from utils.logger import get_logger

logger = get_logger(__name__)

class GradioInterface:
    """Gradio用户界面"""
    
    def __init__(self, agent: PolicyAgent):
        self.agent = agent
        self.citation_display = CitationDisplay()
        self.session_manager = SessionManager(agent)
        
        self._setup_interface()
    
    def _setup_interface(self):
        """设置界面"""
        with gr.Blocks(
            theme=gr.themes.Soft(
                primary_hue="blue",
                neutral_hue="slate"
            ),
            title="政策咨询智能体",
            css=self._get_css()
        ) as self.interface:
            
            # 主布局
            with gr.Row(equal_height=False):
                # 左侧边栏
                with gr.Column(scale=1, min_width=280):
                    self._setup_sidebar()
                
                # 主聊天区域
                with gr.Column(scale=3):
                    self._setup_chat_area()
            
            # 事件绑定
            self._bind_events()
    
    def _setup_sidebar(self):
        """设置侧边栏"""
        gr.Markdown("### 🎯 政策咨询智能体")
        
        # 会话管理
        self.session_dropdown = gr.Dropdown(
            label="对话会话",
            choices=[],
            interactive=True
        )
        
        gr.Button("➕ 新对话", variant="primary")
        
        gr.Markdown("---")
        
        # 引用详情
        gr.Markdown("### 📚 引用详情")
        self.citation_details = gr.HTML(
            value="<div style='text-align: center; color: #666; padding: 20px;'>点击引用标记查看详情</div>"
        )
        
        # 设置
        with gr.Accordion("⚙️ 设置", open=False):
            self.use_web_search = gr.Checkbox(label="🌐 联网搜索", value=True)
            self.use_knowledge_base = gr.Checkbox(label="📚 知识库", value=True)
            self.enable_citation = gr.Checkbox(label="🔗 引用显示", value=True)
    
    def _setup_chat_area(self):
        """设置聊天区域"""
        # 聊天机器人
        self.chatbot = gr.Chatbot(
            label="",
            height=600,
            show_copy_button=True,
            show_share_button=False,
            placeholder="💬 请输入您的政策咨询问题...",
            show_label=False,
            sanitize_html=False
        )
        
        # 输入区域
        with gr.Row():
            self.msg_input = gr.Textbox(
                label="",
                placeholder="输入您的问题...",
                lines=2,
                max_lines=5,
                scale=4,
                container=False
            )
            self.send_btn = gr.Button("发送", variant="primary", scale=1)
        
        # 底部控制
        with gr.Row():
            gr.Button("🗑️ 清空对话", size="sm")
            gr.Button("💾 导出对话", size="sm")
            gr.Button("📊 知识库管理", size="sm")
    
    def _bind_events(self):
        """绑定事件"""
        # 发送消息
        self.send_btn.click(
            fn=self._handle_user_message,
            inputs=[self.msg_input, self.chatbot, self.use_web_search, self.use_knowledge_base],
            outputs=[self.chatbot, self.msg_input]
        )
        
        self.msg_input.submit(
            fn=self._handle_user_message,
            inputs=[self.msg_input, self.chatbot, self.use_web_search, self.use_knowledge_base],
            outputs=[self.chatbot, self.msg_input]
        )
    
    async def _handle_user_message(self, message: str, history: List, use_web: bool, use_kb: bool):
        """处理用户消息"""
        if not message.strip():
            return history, ""
        
        # 添加用户消息到历史
        history.append([message, ""])
        
        try:
            # 处理查询
            result = await self.agent.process_query(
                query=message,
                use_web_search=use_web,
                use_knowledge_base=use_kb
            )
            
            # 流式输出
            answer = result['answer']
            for i in range(0, len(answer), 5):
                history[-1][1] = answer[:i+5]
                yield history, ""
                await asyncio.sleep(0.02)
            
            history[-1][1] = answer
            
        except Exception as e:
            history[-1][1] = f"抱歉，处理您的请求时出现错误：{str(e)}"
            logger.error(f"处理消息错误: {str(e)}")
        
        yield history, ""
    
    def _get_css(self) -> str:
        """获取CSS样式"""
        return """
        .citation {
            color: #1e88e5;
            cursor: pointer;
            font-weight: 600;
            padding: 1px 4px;
            border-radius: 3px;
            background: #e3f2fd;
            margin: 0 2px;
        }
        .citation:hover {
            background: #bbdefb;
            text-decoration: underline;
        }
        .source-details {
            background: #f8f9fa;
            border: 1px solid #e9ecef;
            border-radius: 8px;
            padding: 15px;
            margin: 10px 0;
        }
        """
    
    def launch(self, **kwargs):
        """启动界面"""
        return self.interface.launch(**kwargs)