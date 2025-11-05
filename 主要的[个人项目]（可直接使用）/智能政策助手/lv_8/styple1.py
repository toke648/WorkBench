# cherry_style_policy_agent.py
""" 
Cherry Studio风格 - AI政策咨询智能体
修复版 + 高度集成化
"""

import gradio as gr
import requests
import json
import time
import os
import pandas as pd
from openai import OpenAI
from typing import List, Dict, Any
import uuid
from datetime import datetime

# 配置
OPENAI_API_KEY = "63f72c10e53241509645b29dfc5f06c8.x0RKmLAYwR7uJMsr"
OPENAI_BASE_URL = "https://open.bigmodel.cn/api/paas/v4/"
MODEL = "GLM-4-Flash"

client = OpenAI(api_key=OPENAI_API_KEY, base_url=OPENAI_BASE_URL)

class CherryStylePolicyAgent:
    """Cherry Studio风格政策智能体"""
    
    def __init__(self):
        self.sessions = {}  # 多会话管理
        self.knowledge_base = self._init_knowledge_base()
        self.current_session_id = str(uuid.uuid4())
        self.sessions[self.current_session_id] = {
            "history": [],
            "knowledge_files": [],
            "settings": {
                "web_search": True,
                "deep_thinking": True,
                "stream_output": True,
                "temperature": 0.3
            }
        }
    
    def _init_knowledge_base(self) -> Dict:
        """初始化政策知识库"""
        return {
            "汽车以旧换新": {
                "type": "政策文件",
                "content": "燃油车补贴10%最高1万元，新能源车补贴15%最高1.5万元。申请条件：旧车注册满6年，国三及以下排放标准。",
                "source": "商务部【2024】15号文",
                "update_time": "2024-06-01"
            },
            "家电补贴": {
                "type": "实施细则", 
                "content": "冰箱补贴8%最高800元，空调补贴10%最高1000元，电视补贴5%最高500元。需提供旧机回收证明。",
                "source": "发改委【2024】8号文",
                "update_time": "2024-05-15"
            },
            "数码产品": {
                "type": "补充规定",
                "content": "手机最高补贴1500元，电脑最高2000元，平板最高1000元。支持在线评估和邮寄回收。",
                "source": "工信部【2024】12号文",
                "update_time": "2024-04-20"
            }
        }
    
    def create_new_session(self):
        """创建新会话"""
        session_id = str(uuid.uuid4())
        self.sessions[session_id] = {
            "history": [],
            "knowledge_files": [],
            "settings": self.sessions[self.current_session_id]["settings"].copy()
        }
        self.current_session_id = session_id
        return session_id
    
    def upload_document(self, file):
        """上传文档到知识库"""
        if file:
            filename = os.path.basename(file.name)
            # 模拟文档处理
            self.sessions[self.current_session_id]["knowledge_files"].append({
                "name": filename,
                "type": "policy_doc",
                "upload_time": datetime.now().strftime("%Y-%m-%d %H:%M"),
                "size": "256KB"
            })
            return f"✅ 已上传: {filename}"
        return "❌ 上传失败"
    
    def web_search(self, query: str) -> List[Dict]:
        """联网搜索"""
        # 模拟搜索最新政策
        time.sleep(1)  # 模拟搜索延迟
        return [
            {
                "title": "2024年最新以旧换新政策解读",
                "content": "国家进一步扩大消费品以旧换新补贴范围，新增智能家居产品类别",
                "source": "中国政府网",
                "url": "https://www.gov.cn/zhengce/2024-06/content.html",
                "date": "2024-06-15"
            }
        ]
    
    def deep_analysis(self, query: str) -> Dict:
        """深度分析"""
        prompt = f"""
        分析以下政策咨询问题的核心需求：
        用户问题：{query}
        
        请返回JSON格式：
        {{
            "domain": "政策领域",
            "needs": ["具体需求1", "具体需求2"],
            "focus": "回答重点方向",
            "urgency": "紧急程度"
        }}
        """
        try:
            response = client.chat.completions.create(
                model=MODEL,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.1
            )
            return json.loads(response.choices[0].message.content)
        except:
            return {"domain": "通用政策", "needs": ["政策咨询"], "focus": "详细解答", "urgency": "普通"}
    
    def search_knowledge_base(self, query: str, analysis: Dict) -> List[Dict]:
        """搜索知识库"""
        results = []
        for policy_name, policy_info in self.knowledge_base.items():
            relevance = 0
            
            # 基于领域匹配
            if analysis.get("domain", "") in policy_name:
                relevance += 0.4
            
            # 基于关键词匹配
            keywords = query.split()
            for keyword in keywords:
                if keyword in policy_name or keyword in policy_info["content"]:
                    relevance += 0.3
                    break
            
            if relevance > 0:
                results.append({
                    "policy": policy_name,
                    "info": policy_info,
                    "relevance": min(relevance, 0.9),
                    "match_type": "智能匹配"
                })
        
        return sorted(results, key=lambda x: x["relevance"], reverse=True)[:3]
    
    def stream_chat(self, query: str, history: List, web_search: bool, deep_thinking: bool):
        """流式对话核心"""
        current_session = self.sessions[self.current_session_id]
        settings = current_session["settings"]
        
        # 初始化回答
        full_response = ""
        history.append([query, ""])
        
        # 执行功能步骤
        steps = []
        
        if deep_thinking:
            steps.append("🤔 深度分析用户需求中...")
            history[-1][1] = steps[-1]
            yield history, ""
            analysis = self.deep_analysis(query)
            time.sleep(1)
        else:
            analysis = {}
        
        if web_search:
            steps.append("🌐 联网搜索最新政策...")
            history[-1][1] = steps[-1]
            yield history, ""
            web_results = self.web_search(query)
            time.sleep(1)
        else:
            web_results = []
        
        steps.append("📚 检索知识库政策...")
        history[-1][1] = steps[-1]
        yield history, ""
        knowledge_results = self.search_knowledge_base(query, analysis)
        time.sleep(0.5)
        
        steps.append("✍️ 生成专业回答...")
        history[-1][1] = steps[-1]
        yield history, ""
        
        # 构建上下文
        context = f"""
        用户问题：{query}
        
        需求分析：{json.dumps(analysis, ensure_ascii=False)}
        
        相关政策：
        {json.dumps(knowledge_results, ensure_ascii=False)}
        
        最新动态：
        {json.dumps(web_results, ensure_ascii=False)}
        """
        
        # 流式生成回答
        try:
            stream = client.chat.completions.create(
                model=MODEL,
                messages=[{"role": "user", "content": f"请基于以下信息回答政策咨询问题：{context}"}],
                stream=True,
                temperature=settings["temperature"]
            )
            
            for chunk in stream:
                if chunk.choices[0].delta.content is not None:
                    word = chunk.choices[0].delta.content
                    full_response += word
                    history[-1][1] = full_response
                    yield history, ""
            
            # 添加引用信息
            references = "\n\n---\n**📋 参考信息**\n"
            
            if knowledge_results:
                references += "**相关政策：**\n"
                for result in knowledge_results:
                    ref = result["info"]
                    references += f"• {result['policy']} - {ref['source']}\n"
            
            if web_results:
                references += f"**最新动态：** {web_results[0]['title']}\n"
            
            if analysis.get('domain'):
                references += f"**分析领域：** {analysis['domain']}\n"
                
            history[-1][1] += references
            yield history, ""
                
        except Exception as e:
            history[-1][1] = f"❌ 抱歉，生成回答时出现错误：{str(e)}"
            yield history, ""

# 创建智能体实例
agent = CherryStylePolicyAgent()

# 创建Cherry Studio风格界面
def create_cherry_style_interface():
    with gr.Blocks(
        theme=gr.themes.Soft(
            primary_hue="blue",
            secondary_hue="slate"
        ),
        title="政策咨询智能体 - Cherry Studio风格",
        css="""
        .gradio-container {
            max-width: 1400px;
            margin: 0 auto;
        }
        .sidebar {
            background: #f8f9fa;
            padding: 20px;
            border-radius: 10px;
        }
        .feature-card {
            border: 1px solid #e1e5e9;
            border-radius: 8px;
            padding: 15px;
            margin: 10px 0;
            background: white;
        }
        .chat-container {
            background: white;
            border-radius: 10px;
            padding: 20px;
            height: 600px;
        }
        """
    ) as demo:
        
        # 顶部导航
        with gr.Row():
            with gr.Column(scale=8):
                gr.Markdown("""
                <div style="display: flex; align-items: center; gap: 15px;">
                    <h1 style="margin: 0; color: #2563eb;">🎯 政策咨询智能体</h1>
                    <span style="background: #dcfce7; color: #166534; padding: 4px 12px; border-radius: 20px; font-size: 12px;">Cherry Studio风格</span>
                </div>
                <p style="margin: 5px 0 0 0; color: #6b7280;">智能政策咨询 · 多源信息整合 · 专业解答</p>
                """)
            with gr.Column(scale=2):
                user_status = gr.Textbox(
                    label="",
                    value="👤 用户 | 🆓 免费版 | ✅ 在线",
                    interactive=False,
                    show_label=False
                )
        
        with gr.Row(equal_height=False):
            # 左侧边栏 - 功能面板
            with gr.Column(scale=1, min_width=280):
                with gr.Group(elem_classes="sidebar"):
                    # 会话管理
                    gr.Markdown("### 💬 会话管理")
                    with gr.Row():
                        new_chat_btn = gr.Button("🆕 新对话", size="sm")
                        clear_chat_btn = gr.Button("🗑️ 清空", size="sm", variant="secondary")
                    
                    # 知识库管理
                    gr.Markdown("### 📚 知识库")
                    file_output = gr.File(
                        label="上传政策文档",
                        file_types=[".txt", ".pdf", ".docx"],
                        file_count="multiple"
                    )
                    upload_btn = gr.Button("📤 上传文档", size="sm")
                    upload_status = gr.Textbox(
                        label="上传状态",
                        interactive=False,
                        lines=2
                    )
                    
                    # 知识库文件列表
                    gr.Markdown("**已上传文件：**")
                    knowledge_files = gr.DataFrame(
                        headers=["文件名", "类型", "上传时间", "大小"],
                        value=[],
                        interactive=False,
                        row_count=3
                    )
                    
                    # 功能配置
                    gr.Markdown("### ⚙️ 功能配置")
                    web_search_toggle = gr.Checkbox(label="🌐 联网搜索", value=True)
                    deep_thinking_toggle = gr.Checkbox(label="🤔 深度思考", value=True)
                    stream_toggle = gr.Checkbox(label="⚡ 流式输出", value=True)
                    
                    temperature_slider = gr.Slider(
                        minimum=0.1, maximum=1.0, value=0.3, step=0.1,
                        label="🎛️ 创造性",
                        info="较低值更准确，较高值更创新"
                    )
                    
                    # 模型选择
                    model_dropdown = gr.Dropdown(
                        choices=["GLM-4-Flash", "GLM-4", "GLM-3-Turbo"],
                        value="GLM-4-Flash",
                        label="🧠 模型选择"
                    )
            
            # 右侧主区域 - 聊天界面
            with gr.Column(scale=3):
                # 聊天容器
                with gr.Group(elem_classes="chat-container"):
                    chatbot = gr.Chatbot(
                        label="政策咨询对话",
                        height=450,
                        show_copy_button=True,
                        show_share_button=False,
                        avatar_images=(
                            "https://i.imgur.com/7I6q1Qy.png",  # 用户
                            "https://i.imgur.com/4Z0Q1qy.png"   # AI
                        )
                    )
                
                # 输入区域
                with gr.Row():
                    msg = gr.Textbox(
                        placeholder="请输入政策问题...（支持：汽车补贴、家电政策、数码产品等）",
                        lines=2,
                        scale=5,
                        container=False
                    )
                    send_btn = gr.Button("🚀 发送", variant="primary", scale=1)
                
                # 快捷操作
                with gr.Row():
                    gr.Markdown("**💡 快捷问题：**")
                
                with gr.Row():
                    quick_btns = []
                    quick_questions = [
                        "汽车补贴标准", "家电申请流程", "最新政策", "对比分析"
                    ]
                    for q in quick_questions:
                        btn = gr.Button(q, size="sm", variant="secondary", min_width=80)
                        quick_btns.append(btn)
                
                # 状态栏
                with gr.Row():
                    status = gr.Textbox(
                        label="",
                        value="✅ 系统就绪 | 📚 知识库: 3个政策 | 🌐 联网: 可用 | 🤔 深度思考: 开启",
                        interactive=False,
                        show_label=False
                    )
        
        # 事件处理
        def handle_chat(message, history, web_search, deep_thinking):
            for update in agent.stream_chat(message, history, web_search, deep_thinking):
                yield update
        
        # 发送消息
        send_btn.click(
            fn=handle_chat,
            inputs=[msg, chatbot, web_search_toggle, deep_thinking_toggle],
            outputs=[chatbot, msg]
        )
        
        msg.submit(
            fn=handle_chat,
            inputs=[msg, chatbot, web_search_toggle, deep_thinking_toggle],
            outputs=[chatbot, msg]
        )
        
        # 新对话
        def new_conversation():
            agent.create_new_session()
            return [], "🆕 新对话已创建，可以开始咨询"
        
        new_chat_btn.click(
            fn=new_conversation,
            outputs=[chatbot, status]
        )
        
        # 清空对话
        clear_chat_btn.click(
            fn=lambda: ([], "🗑️ 当前对话已清空"),
            outputs=[chatbot, status]
        )
        
        # 上传文档
        def handle_upload(files):
            if files:
                results = []
                file_list = []
                for file in files:
                    result = agent.upload_document(file)
                    results.append(result)
                
                # 更新文件列表显示
                current_files = agent.sessions[agent.current_session_id]["knowledge_files"]
                file_list = [
                    [f["name"], f["type"], f["upload_time"], f["size"]]
                    for f in current_files
                ]
                return "\n".join(results), file_list
            return "请选择文件", []
        
        upload_btn.click(
            fn=handle_upload,
            inputs=[file_output],
            outputs=[upload_status, knowledge_files]
        )
        
        # 快捷问题
        for i, btn in enumerate(quick_btns):
            btn.click(
                fn=lambda x=quick_questions[i]: x,
                outputs=[msg]
            )
        
        # 设置更新
        def update_settings(web, deep, stream, temp):
            agent.sessions[agent.current_session_id]["settings"].update({
                "web_search": web,
                "deep_thinking": deep, 
                "stream_output": stream,
                "temperature": temp
            })
            status_text = "✅ 系统就绪"
            if web: status_text += " | 🌐 联网搜索:开启"
            if deep: status_text += " | 🤔 深度思考:开启"
            status_text += f" | 🎛️ 创造性:{temp}"
            return status_text
        
        # 绑定设置变更事件
        for component in [web_search_toggle, deep_thinking_toggle, temperature_slider]:
            component.change(
                fn=update_settings,
                inputs=[web_search_toggle, deep_thinking_toggle, stream_toggle, temperature_slider],
                outputs=[status]
            )

    return demo

if __name__ == "__main__":
    print("🎯 启动Cherry Studio风格政策智能体...")
    print("💬 多会话管理就绪")
    print("📚 知识库系统就绪")
    print("🌐 联网搜索就绪") 
    print("🤔 深度思考就绪")
    print("⚡ 流式输出就绪")
    print("🚀 访问地址: http://localhost:7860")
    
    demo = create_cherry_style_interface()
    demo.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=False,
        inbrowser=True
    )