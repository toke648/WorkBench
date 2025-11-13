# main_app.py
import gradio as gr
import time
from knowledge_base import PolicyKnowledgeBase
from enhanced_chat import EnhancedPolicyChat

# 初始化组件
knowledge_base = PolicyKnowledgeBase()
chat_bot = EnhancedPolicyChat(knowledge_base)

def chat_interface(message, chat_history):
    """聊天界面处理函数"""
    if not message.strip():
        return chat_history, "", "请输入有效问题"
    
    # 获取回答和引用
    response, references = chat_bot.chat_with_reference(message)
    
    # 更新聊天历史
    chat_history.append([message, response])
    
    return chat_history, "", references

def crawl_and_add_policies(keywords, url):
    """爬取并添加政策到知识库"""
    try:
        policies = []
        
        if url.strip():
            policies = knowledge_base.crawl_policy_data(url=url.strip())
        elif keywords.strip():
            keyword_list = [k.strip() for k in keywords.split(",")]
            policies = knowledge_base.crawl_policy_data(keywords=keyword_list)
        
        if policies:
            result = knowledge_base.add_policies_to_knowledge(policies)
            return result
        else:
            return "未获取到政策数据，请检查输入"
            
    except Exception as e:
        return f"爬取失败: {str(e)}"

def update_knowledge_stats():
    """更新知识库统计"""
    return knowledge_base.get_knowledge_stats()

def clear_conversation():
    """清空对话"""
    chat_bot.clear_history()
    return [], "对话已清空", ""

# 创建Gradio界面
with gr.Blocks(theme=gr.themes.Soft(), title="智能政策查询系统") as demo:
    gr.Markdown("""
    # 🎯 智能政策查询系统
    💡 **基于知识库的精准政策问答** | 🔍 **实时政策爬取** | 📚 **引用溯源**
    """)
    
    with gr.Tab("💬 政策问答"):
        with gr.Row():
            with gr.Column(scale=2):
                chatbot = gr.Chatbot(
                    label="政策智能助手",
                    height=500,
                    show_copy_button=True
                )
                
                with gr.Row():
                    msg = gr.Textbox(
                        label="请输入政策问题",
                        placeholder="例如：企业税收优惠政策有哪些？如何申请创业补贴？",
                        lines=2,
                        scale=4
                    )
                    submit_btn = gr.Button("发送", variant="primary", scale=1)
                
                with gr.Row():
                    clear_btn = gr.Button("🧹 清空对话", variant="secondary")
                    stats_btn = gr.Button("📊 知识库统计", variant="secondary")
            
            with gr.Column(scale=1):
                references = gr.Textbox(
                    label="📚 引用来源",
                    lines=10,
                    interactive=False
                )
                
                stats_display = gr.Textbox(
                    label="知识库状态",
                    value="点击统计按钮查看",
                    interactive=False
                )
    
    with gr.Tab("🕸️ 政策采集"):
        gr.Markdown("### 自动采集政策数据到知识库")
        
        with gr.Row():
            with gr.Column():
                keywords_input = gr.Textbox(
                    label="政策关键词（用逗号分隔）",
                    placeholder="例如：科技创新,税收优惠,人才引进",
                    lines=2
                )
                
            with gr.Column():
                url_input = gr.Textbox(
                    label="政策网页URL",
                    placeholder="例如：https://www.gov.cn/...",
                    lines=2
                )
        
        crawl_btn = gr.Button("🚀 开始采集", variant="primary")
        crawl_result = gr.Textbox(label="采集结果", interactive=False)
        
        gr.Markdown("""
        **使用说明：**
        - 输入关键词：系统会模拟搜索相关主题政策
        - 输入URL：系统会爬取指定网页的政策内容
        - 采集的数据会自动添加到知识库中
        """)
    
    with gr.Tab("📖 使用指南"):
        gr.Markdown("""
        ## 系统使用指南
        
        ### 💬 政策问答
        1. 在输入框直接提问政策相关问题
        2. 系统会从知识库中检索最相关的政策文档
        3. 回答会附带引用来源，确保准确性
        
        ### 🕸️ 政策采集  
        1. **关键词采集**：输入政策主题关键词，批量获取相关政策
        2. **URL采集**：输入具体政策网页URL，精准采集单一政策
        3. 采集的数据会立即加入知识库，可用于后续问答
        
        ### 🔍 核心特性
        - **精准回答**：基于真实政策文档，避免幻觉
        - **引用溯源**：每个回答都可追溯原始政策
        - **持续学习**：通过采集不断丰富知识库
        - **多轮对话**：保持上下文连贯性
        """)
    
    # 事件绑定
    submit_btn.click(
        fn=chat_interface,
        inputs=[msg, chatbot],
        outputs=[chatbot, msg, references]
    )
    
    msg.submit(
        fn=chat_interface,
        inputs=[msg, chatbot],
        outputs=[chatbot, msg, references]
    )
    
    clear_btn.click(
        fn=clear_conversation,
        inputs=[],
        outputs=[chatbot, msg, references]
    )
    
    stats_btn.click(
        fn=update_knowledge_stats,
        inputs=[],
        outputs=[stats_display]
    )
    
    crawl_btn.click(
        fn=crawl_and_add_policies,
        inputs=[keywords_input, url_input],
        outputs=[crawl_result]
    )

if __name__ == "__main__":
    demo.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=False,
        inbrowser=True
    )