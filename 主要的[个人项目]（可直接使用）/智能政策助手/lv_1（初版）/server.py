""" utf-8 encoding Generation_LLM.py """
from openai import OpenAI
import pandas as pd
import json
import gradio as gr
import time
import os

system_prompt_file = "templates/ai_setting_VTuber-Neuro sama.txt"
openai_api_key = "63f72c10e53241509645b29dfc5f06c8.x0RKmLAYwR7uJMsr"
openai_base_url = "https://open.bigmodel.cn/api/paas/v4/"
models = "GLM-4-Flash"

class ContentGenerate:
    """内容生成类"""
    def __init__(self):
        """初始化内容生成类"""
        self.content_history = [
            {'role': 'system', 'content': '你是一个智能政策查询助手'}
        ]

    def _client(self) -> OpenAI:
        """初始化OpenAI客户端"""
        return OpenAI(
            api_key=openai_api_key,
            base_url=(openai_base_url or None)
        )

    def _chat(self, content: str, model: str) -> str:
        try:
            self.content_history.append({'role': 'user', 'content': content})
            client = self._client()
            completion = client.chat.completions.create(
                model=model or models,
                messages=self.content_history
            )
            message = completion.choices[0].message.content
            self.content_history.append({'role': 'assistant', 'content': message})
            return message
        except Exception as e:
            print(f'LLM error: {e}')
            return f'抱歉，出现错误：{str(e)}'

    def generate_content(self, content: str) -> str:
        return self._chat(content, models)

    def ollama_content(self, content: str) -> str:
        return self._chat(content, models)

    def deepseek_content(self, content: str) -> str:
        return self._chat(content, models)

    def zhipuai_content(self, content: str) -> str:
        return self._chat(content, models)
    
    def clear_history(self):
        """清空对话历史"""
        self.content_history = [
            {'role': 'system', 'content': '你是一个智能政策查询助手'}
        ]
        return "对话历史已清空"

# 创建全局实例
chat_bot = ContentGenerate()

def chat_with_bot(message, history):
    """处理用户消息并返回回复"""
    if not message.strip():
        return "", history, "请输入有效的问题"
    
    try:
        # 显示思考中状态
        yield "", history + [[message, "正在思考..."]], "正在生成回复..."
        
        # 获取AI回复
        response = chat_bot.zhipuai_content(content=message)
        
        # 更新对话历史
        new_history = history + [[message, response]]
        
        # 返回结果
        yield "", new_history, "回复生成完成"
        
    except Exception as e:
        error_msg = f"发生错误：{str(e)}"
        new_history = history + [[message, error_msg]]
        yield "", new_history, error_msg

def clear_chat():
    """清空聊天界面"""
    chat_bot.clear_history()
    return [], "对话历史已清空"

def get_conversation_count():
    """获取当前对话轮数"""
    user_messages = [msg for msg in chat_bot.content_history if msg['role'] == 'user']
    return f"当前对话轮数：{len(user_messages)}"

def export_conversation():
    """导出对话记录"""
    if len(chat_bot.content_history) <= 1:  # 只有系统提示
        return "暂无对话记录可导出"
    
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    filename = f"policy_conversation_{timestamp}.txt"
    
    with open(filename, 'w', encoding='utf-8') as f:
        f.write("政策查询助手对话记录\n")
        f.write("=" * 50 + "\n\n")
        
        for msg in chat_bot.content_history:
            if msg['role'] == 'user':
                f.write(f"用户：{msg['content']}\n\n")
            elif msg['role'] == 'assistant':
                f.write(f"助手：{msg['content']}\n")
                f.write("-" * 50 + "\n\n")
    
    return f"对话记录已导出到：{filename}"

# 创建Gradio界面
with gr.Blocks(
    title="智能政策查询助手",
    theme=gr.themes.Soft(),
    css="""
    .chat-container { max-height: 500px; overflow-y: auto; }
    .status-panel { background-color: #f0f0f0; padding: 10px; border-radius: 5px; }
    """
) as demo:
    
    gr.Markdown("""
    # 🎯 智能政策查询助手
    欢迎使用智能政策查询助手！我可以帮助您解答各类政策相关问题。
    """)
    
    with gr.Row():
        with gr.Column(scale=2):
            # 聊天界面
            chatbot = gr.Chatbot(
                label="政策咨询对话",
                height=500,
                show_copy_button=True,
                container=True
            )
            
            with gr.Row():
                msg = gr.Textbox(
                    label="请输入您的问题",
                    placeholder="例如：请问最新的税收政策有哪些？",
                    lines=2,
                    scale=4
                )
                submit_btn = gr.Button("发送", variant="primary", scale=1)
            
            with gr.Row():
                clear_btn = gr.Button("清空对话", variant="secondary")
                export_btn = gr.Button("导出记录", variant="secondary")
                count_btn = gr.Button("对话统计", variant="secondary")
        
        with gr.Column(scale=1):
            # 状态面板
            status = gr.Textbox(
                label="系统状态",
                value="就绪",
                interactive=False,
                lines=3
            )
            
            # 对话统计显示
            stats_display = gr.Textbox(
                label="对话统计",
                value="当前对话轮数：0",
                interactive=False,
                lines=2
            )
            
            # 功能说明
            with gr.Accordion("使用说明", open=False):
                gr.Markdown("""
                ### 📖 使用指南
                - **提问方式**：直接输入您想了解的政策问题
                - **多轮对话**：系统会记住之前的对话内容
                - **清空对话**：点击清空按钮开始新的对话
                - **导出记录**：可以将对话记录保存为文本文件
                
                ### 💡 示例问题
                - 企业税收优惠政策有哪些？
                - 最新的社保政策是什么？
                - 如何申请创业补贴？
                - 人才引进政策具体内容？
                """)
    
    # 事件处理
    submit_btn.click(
        fn=chat_with_bot,
        inputs=[msg, chatbot],
        outputs=[msg, chatbot, status]
    )
    
    msg.submit(
        fn=chat_with_bot,
        inputs=[msg, chatbot],
        outputs=[msg, chatbot, status]
    )
    
    clear_btn.click(
        fn=clear_chat,
        inputs=[],
        outputs=[chatbot, status]
    )
    
    export_btn.click(
        fn=export_conversation,
        inputs=[],
        outputs=[status]
    )
    
    count_btn.click(
        fn=get_conversation_count,
        inputs=[],
        outputs=[stats_display]
    )

# 启动界面
if __name__ == "__main__":
    demo.launch(
        server_name="0.0.0.0",  # 允许外部访问
        server_port=7860,       # 端口号
        share=False,            # 是否创建公共链接
        inbrowser=True          # 自动在浏览器打开
    )