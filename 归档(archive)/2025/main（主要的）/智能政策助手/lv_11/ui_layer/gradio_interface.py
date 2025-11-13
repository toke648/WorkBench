"""
Gradio用户界面模块
支持触摸显示引用、现代化UI交互
"""
import gradio as gr
import time
from typing import List, Dict, Any, Optional
from business_logic.response_generator import ResponseGenerator
from data_service.knowledge_base import KnowledgeBase
from ui_layer.conversation_manager import ConversationManager
from config.settings import UISettings


class GradioInterface:
    """Gradio界面管理器"""
    
    def __init__(self, response_generator: ResponseGenerator, 
                 knowledge_base: KnowledgeBase,
                 conversation_manager: ConversationManager,
                 ui_settings: UISettings):
        """
        初始化界面
        
        Args:
            response_generator: 回答生成器
            knowledge_base: 知识库
            conversation_manager: 对话管理器
            ui_settings: UI设置
        """
        self.response_generator = response_generator
        self.knowledge_base = knowledge_base
        self.conversation_manager = conversation_manager
        self.ui_settings = ui_settings
        
        # 确保有当前会话
        if not self.conversation_manager.current_session_id:
            self.conversation_manager.create_session()
    
    def create_interface(self):
        """创建Gradio界面"""
        with gr.Blocks(
            theme=gr.themes.Soft(
                primary_hue="blue",
                neutral_hue="slate"
            ),
            title="政策咨询助手 - 模块化增强版",
            css=self._get_css()
        ) as demo:
            
            # 主布局
            with gr.Row(equal_height=False):
                # 左侧边栏
                with gr.Column(scale=1, min_width=280, elem_classes="sidebar") as sidebar:
                    # 新对话按钮
                    new_chat_btn = gr.Button("➕ 新对话", variant="primary", size="sm", scale=1)
                    
                    gr.Markdown("---")
                    gr.Markdown("### 💬 对话历史")
                    
                    # 会话列表
                    sessions_list = gr.Radio(
                        label="",
                        choices=[],
                        value=None,
                        show_label=False,
                        interactive=True,
                        container=False
                    )
                    
                    gr.Markdown("---")
                    
                    # 引用详情区域（支持触摸显示）
                    gr.Markdown("### 📚 引用详情")
                    source_details = gr.HTML(
                        value="<div style='text-align: center; color: #666; padding: 20px;'>点击或触摸回答中的引用标记查看详情</div>",
                        label=""
                    )
                    
                    # 引用选择器
                    source_selector = gr.Dropdown(
                        label="选择引用",
                        choices=[],
                        interactive=True,
                        visible=False
                    )
                    
                    gr.Markdown("---")
                    
                    # 功能设置
                    with gr.Accordion("⚙️ 设置", open=False):
                        use_web = gr.Checkbox(label="🌐 联网搜索", value=True)
                        use_knowledge = gr.Checkbox(label="📚 知识库", value=True)
                        enable_deep_thinking = gr.Checkbox(label="🧠 深度思考模式", value=False)
                    
                    gr.Markdown("---")
                    
                    # 知识库管理
                    with gr.Accordion("📁 知识库管理", open=False):
                        gr.Markdown("### 文档导入")
                        file_upload = gr.File(
                            label="上传政策文档",
                            file_types=[".txt", ".pdf", ".docx", ".doc"],
                            file_count="single",
                            show_label=False
                        )
                        upload_status = gr.Textbox(
                            label="",
                            interactive=False,
                            show_label=False,
                            lines=3,
                            max_lines=5
                        )
                        
                        gr.Markdown("---")
                        gr.Markdown("### 批量导入")
                        batch_upload = gr.File(
                            label="批量上传文档",
                            file_count="multiple",
                            show_label=False
                        )
                        batch_status = gr.Textbox(
                            label="",
                            interactive=False,
                            show_label=False,
                            lines=2
                        )
                
                # 中间主聊天区域
                with gr.Column(scale=3) as main_chat:
                    # 顶部栏
                    with gr.Row():
                        gr.Markdown("### 🎯 政策咨询助手", elem_classes="center-title")
                        model_status = gr.HTML(
                            value="<div style='background: #10a37f; color: white; padding: 4px 8px; border-radius: 4px; font-size: 12px;'>DeepSeek-Chat</div>"
                        )
                    
                    # 聊天区域
                    chatbot = gr.Chatbot(
                        label="",
                        height=650,
                        show_copy_button=True,
                        show_share_button=False,
                        bubble_full_width=False,
                        layout="bubble",
                        placeholder="💬 输入您的政策咨询问题...\n\n例如：汽车以旧换新的补贴标准是多少？",
                        show_label=False,
                        sanitize_html=False  # 允许HTML样式
                    )
                    
                    # 输入区域
                    with gr.Row():
                        msg = gr.Textbox(
                            label="",
                            placeholder="输入消息...",
                            lines=2,
                            max_lines=5,
                            scale=4,
                            container=False
                        )
                        submit_btn = gr.Button("发送", variant="primary", scale=1)
                    
                    # 底部快速设置
                    with gr.Row():
                        use_web_quick = gr.Checkbox(label="🌐 联网搜索", value=True, interactive=True)
                        use_knowledge_quick = gr.Checkbox(label="📚 知识库", value=True, interactive=True)
                        clear_btn = gr.Button("🗑️ 清空", size="sm", variant="secondary")
            
            # 事件处理函数
            def update_sessions_list():
                """更新会话列表"""
                sessions = self.conversation_manager.list_sessions()
                choices = [f"{s['title']} ({s['message_count']}条)" for s in sessions]
                current_choice = None
                for s in sessions:
                    if s['id'] == self.conversation_manager.current_session_id:
                        current_choice = f"{s['title']} ({s['message_count']}条)"
                        break
                if not current_choice and choices:
                    current_choice = choices[0]
                return gr.Radio(choices=choices, value=current_choice)
            
            def handle_chat(message, history, web, knowledge, deep_thinking):
                """处理对话"""
                if not message.strip():
                    return history, "", ""
                
                # 添加用户消息到历史
                history.append([message, ""])
                
                # 流式生成回答
                full_answer = ""
                sources = []
                formatted_answer = ""
                
                for update in self.response_generator.stream_generate(
                    message, use_web=web, use_knowledge=knowledge, history=history[:-1]
                ):
                    if update["type"] == "chunk":
                        full_answer = update["full_answer"]
                        history[-1][1] = full_answer
                        yield history, "", ""
                    elif update["type"] == "complete":
                        formatted_answer = update.get("answer", full_answer)
                        sources = update.get("sources", [])
                        # 更新最终回答
                        history[-1][1] = formatted_answer
                        break
                
                # 如果没有格式化回答，使用原始回答
                if not formatted_answer and full_answer:
                    history[-1][1] = full_answer
                
                # 保存到会话
                self.conversation_manager.add_message(message, history[-1][1], sources)
                
                yield history, "", ""
            
            def handle_source_click(source_id):
                """处理引用点击"""
                if source_id:
                    source = self.conversation_manager.get_source(str(source_id))
                    if source:
                        return self._format_source_details(source)
                return "<div style='text-align: center; color: #666; padding: 20px;'>未找到引用信息</div>"
            
            def update_source_selector():
                """更新引用选择器"""
                sources = self.conversation_manager.get_sources()
                if sources:
                    choices = [str(src_id) for src_id in sources.keys()]
                    choices.sort(key=int)
                    return gr.Dropdown(choices=choices, visible=bool(choices))
                return gr.Dropdown(choices=[], visible=False)
            
            def new_conversation():
                """创建新对话"""
                session_id = self.conversation_manager.create_session()
                return [], gr.Radio(), gr.Dropdown(choices=[], visible=False)
            
            def switch_conversation(choice):
                """切换对话"""
                if choice:
                    sessions = self.conversation_manager.list_sessions()
                    for s in sessions:
                        if f"{s['title']} ({s['message_count']}条)" == choice:
                            self.conversation_manager.switch_session(s['id'])
                            history = self.conversation_manager.get_history()
                            return history
                return []
            
            def handle_file_upload(file):
                """处理文件上传"""
                if file:
                    result = self.knowledge_base.import_from_file(file.name)
                    if result["success"]:
                        return f"✅ {result['message']}"
                    else:
                        return f"❌ {result.get('error', '上传失败')}"
                return "请选择文件"
            
            def handle_batch_upload(files):
                """处理批量上传"""
                if not files:
                    return "请选择文件"
                
                results = self.knowledge_base.batch_import([f.name for f in files])
                success_count = sum(1 for r in results.values() if r.get("success"))
                return f"✅ 成功导入 {success_count}/{len(files)} 个文件"
            
            # 绑定事件
            submit_btn.click(
                fn=handle_chat,
                inputs=[msg, chatbot, use_web_quick, use_knowledge_quick, enable_deep_thinking],
                outputs=[chatbot, msg, source_details]
            ).then(
                fn=update_sessions_list,
                outputs=[sessions_list]
            ).then(
                fn=update_source_selector,
                outputs=[source_selector]
            )
            
            msg.submit(
                fn=handle_chat,
                inputs=[msg, chatbot, use_web_quick, use_knowledge_quick, enable_deep_thinking],
                outputs=[chatbot, msg, source_details]
            ).then(
                fn=update_sessions_list,
                outputs=[sessions_list]
            ).then(
                fn=update_source_selector,
                outputs=[source_selector]
            )
            
            new_chat_btn.click(
                fn=new_conversation,
                outputs=[chatbot, sessions_list, source_selector]
            )
            
            sessions_list.change(
                fn=switch_conversation,
                inputs=[sessions_list],
                outputs=[chatbot]
            ).then(
                fn=update_source_selector,
                outputs=[source_selector]
            )
            
            source_selector.change(
                fn=handle_source_click,
                inputs=[source_selector],
                outputs=[source_details]
            )
            
            file_upload.upload(
                fn=handle_file_upload,
                inputs=[file_upload],
                outputs=[upload_status]
            )
            
            batch_upload.upload(
                fn=handle_batch_upload,
                inputs=[batch_upload],
                outputs=[batch_status]
            )
            
            clear_btn.click(
                fn=lambda: ([], gr.Dropdown(choices=[], visible=False)),
                outputs=[chatbot, source_selector]
            )
            
            # 同步设置
            use_web_quick.change(lambda x: x, use_web_quick, use_web)
            use_knowledge_quick.change(lambda x: x, use_knowledge_quick, use_knowledge)
            
            # 初始化
            demo.load(
                fn=update_sessions_list,
                outputs=[sessions_list]
            ).then(
                fn=update_source_selector,
                outputs=[source_selector]
            )
        
        return demo
    
    def _get_css(self) -> str:
        """获取CSS样式（支持触摸）"""
        return """
        .gradio-container {
            max-width: 1600px !important;
            margin: 0 auto !important;
        }
        .sidebar {
            background: #f7f7f8 !important;
            border-right: 1px solid #e5e5e6 !important;
            padding: 15px !important;
        }
        .citation {
            color: #1e88e5;
            cursor: pointer;
            font-weight: 600;
            padding: 2px 6px;
            border-radius: 4px;
            background: #e3f2fd;
            margin: 0 2px;
            display: inline-block;
            transition: all 0.2s;
            user-select: none;
            -webkit-tap-highlight-color: transparent;
        }
        .citation:hover {
            background: #bbdefb;
            transform: scale(1.1);
        }
        .citation:active {
            background: #90caf9;
            transform: scale(0.95);
        }
        /* 触摸设备优化 */
        @media (hover: none) and (pointer: coarse) {
            .citation {
                padding: 4px 8px;
                min-width: 24px;
                text-align: center;
            }
            .citation:active {
                background: #90caf9;
            }
        }
        .source-details {
            background: #f8f9fa;
            border: 1px solid #e9ecef;
            border-radius: 8px;
            padding: 15px;
            margin: 10px 0;
            max-height: 400px;
            overflow-y: auto;
        }
        .source-details h4 {
            margin-top: 0;
            color: #1e88e5;
        }
        .source-details p {
            margin: 8px 0;
            line-height: 1.6;
        }
        .source-details a {
            color: #1e88e5;
            text-decoration: none;
        }
        .source-details a:hover {
            text-decoration: underline;
        }
        """
    
    def _format_source_details(self, source: Dict[str, Any]) -> str:
        """格式化来源详情"""
        html = f"""
        <div class="source-details">
            <h4>📖 {source.get('title', '未知标题')}</h4>
            <p><strong>内容:</strong> {source.get('content', '无详细内容')}</p>
            <p><strong>来源:</strong> {source.get('source', '未知')}</p>
            <p><strong>类型:</strong> {source.get('type', '未知')}</p>
        """
        
        if source.get('category'):
            html += f"<p><strong>分类:</strong> {source.get('category')}</p>"
        
        if source.get('date'):
            html += f"<p><strong>日期:</strong> {source.get('date')}</p>"
        
        if source.get('url') and not source.get('url', '').startswith('#'):
            html += f"""
            <p><strong>链接:</strong> <a href="{source['url']}" target="_blank">🌐 打开原始链接</a></p>
            """
        
        html += "</div>"
        return html
    
    def launch(self, **kwargs):
        """启动界面"""
        demo = self.create_interface()
        demo.launch(**kwargs)

