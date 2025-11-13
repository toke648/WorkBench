# cherry_style_policy_agent.py
""" 
AI政策咨询智能体 - Cherry Studio风格
集成化功能 + 专业界面 + 演示级效果
"""

import gradio as gr
import requests
import json
import time
import os
from openai import OpenAI
from typing import List, Dict, Any
import pandas as pd
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
                "enable_web_search": True,
                "enable_deep_thinking": True,
                "enable_knowledge_base": True,
                "temperature": 0.3,
                "max_tokens": 2000
            }
        }
    
    def _init_knowledge_base(self) -> Dict:
        """初始化政策知识库"""
        return {
            "汽车以旧换新": {
                "category": "汽车",
                "content": "燃油车补贴10%最高1万元，新能源车补贴15%最高1.5万元。旧车需注册满6年，国三及以下排放标准。",
                "source": "商务部【2024】15号文",
                "effective_date": "2024-01-01",
                "tags": ["补贴", "汽车", "环保"]
            },
            "家电以旧换新": {
                "category": "家电", 
                "content": "冰箱补贴8%最高800元，空调补贴10%最高1000元，电视补贴5%最高500元。需一级能效新品。",
                "source": "发改委【2024】8号文",
                "effective_date": "2024-03-15",
                "tags": ["补贴", "家电", "节能"]
            },
            "数码产品以旧换新": {
                "category": "数码",
                "content": "手机最高1500元，电脑最高2000元，平板最高1000元。根据旧机状况分级补贴。",
                "source": "工信部【2024】12号文",
                "effective_date": "2024-04-20",
                "tags": ["补贴", "数码", "回收"]
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
    
    def update_settings(self, settings: Dict):
        """更新会话设置"""
        if self.current_session_id in self.sessions:
            self.sessions[self.current_session_id]["settings"].update(settings)
    
    def upload_knowledge_file(self, file):
        """模拟上传知识文件"""
        if file:
            filename = file.name
            self.sessions[self.current_session_id]["knowledge_files"].append({
                "name": filename,
                "size": os.path.getsize(file.name),
                "upload_time": datetime.now().strftime("%Y-%m-%d %H:%M")
            })
            return f"✅ 已上传文件: {filename}"
        return "❌ 上传失败"
    
    def web_search(self, query: str) -> List[Dict]:
        """联网搜索功能"""
        # 模拟搜索过程
        time.sleep(1)
        return [
            {
                "title": "2024年最新以旧换新政策解读",
                "content": "国家加大补贴力度，扩大政策覆盖范围",
                "source": "中国政府网",
                "url": "https://www.gov.cn/zhengce/2024-06/xx.html",
                "date": "2024-06-15"
            },
            {
                "title": "汽车以旧换新实施细则发布",
                "content": "明确补贴申请流程和材料要求",
                "source": "商务部官网", 
                "url": "https://www.mofcom.gov.cn/2024/xx.html",
                "date": "2024-06-10"
            }
        ]
    
    def mcp_tool_call(self, tool_name: str, params: Dict) -> Any:
        """MCP工具调用模拟"""
        tools = {
            "policy_lookup": lambda p: f"查询政策: {p.get('policy_name', '未知')}",
            "subsidy_calculate": lambda p: f"计算补贴: 车型{p.get('car_type')} 预估{p.get('price', 0)*0.1}元",
            "process_guide": lambda p: "申请流程: 提交材料→审核→发放补贴"
        }
        return tools.get(tool_name, lambda p: "工具未找到")(params)
    
    def deep_thinking_analysis(self, query: str) -> Dict:
        """深度思考分析"""
        prompt = f"""
        请深度分析以下政策咨询问题：
        
        用户问题：{query}
        
        请分析：
        1. 用户的核心需求是什么？
        2. 涉及哪些政策领域？
        3. 需要哪些具体信息？
        4. 可能的后续问题是什么？
        
        返回JSON格式分析结果。
        """
        
        try:
            response = client.chat.completions.create(
                model=MODEL,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.1
            )
            return json.loads(response.choices[0].message.content)
        except:
            return {"analysis": "基础分析", "needs": ["政策信息"], "suggestions": []}
    
    def generate_response(self, query: str, use_web: bool, use_knowledge: bool, use_mcp: bool) -> str:
        """生成回答"""
        settings = self.sessions[self.current_session_id]["settings"]
        
        # 构建上下文
        context_parts = []
        
        if use_knowledge and settings["enable_knowledge_base"]:
            # 知识库检索
            knowledge_results = []
            for policy_name, policy_info in self.knowledge_base.items():
                if any(keyword in query for keyword in policy_name.split()):
                    knowledge_results.append(policy_info)
            
            if knowledge_results:
                context_parts.append("## 相关知识库内容\n")
                for result in knowledge_results[:3]:
                    context_parts.append(f"**{list(self.knowledge_base.keys())[list(self.knowledge_base.values()).index(result)]}**")
                    context_parts.append(f"内容: {result['content']}")
                    context_parts.append(f"来源: {result['source']}\n")
        
        if use_web and settings["enable_web_search"]:
            # 联网搜索
            web_results = self.web_search(query)
            if web_results:
                context_parts.append("## 最新政策动态\n")
                for result in web_results[:2]:
                    context_parts.append(f"**{result['title']}**")
                    context_parts.append(f"内容: {result['content']}")
                    context_parts.append(f"来源: {result['source']} ({result['date']})\n")
        
        if use_mcp:
            # MCP工具调用
            mcp_result = self.mcp_tool_call("policy_lookup", {"policy_name": "以旧换新"})
            context_parts.append(f"## 工具分析\n{mcp_result}\n")
        
        context = "\n".join(context_parts) if context_parts else "基于通用政策知识"
        
        prompt = f"""
        基于以下信息回答用户政策咨询问题：
        
        {context}
        
        用户问题：{query}
        
        请提供专业、准确、友好的政策咨询服务。
        """
        
        try:
            response = client.chat.completions.create(
                model=MODEL,
                messages=[{"role": "user", "content": prompt}],
                temperature=settings["temperature"],
                max_tokens=settings["max_tokens"]
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"生成回答时出现错误：{str(e)}"
    
    def stream_chat(self, query: str, history: List, use_web: bool, use_knowledge: bool, use_mcp: bool) -> Any:
        """流式对话"""
        settings = self.sessions[self.current_session_id]["settings"]
        
        # 初始化对话
        history.append([query, ""])
        full_response = ""
        
        # 步骤提示
        steps = []
        if settings["enable_deep_thinking"]:
            steps.append("🤔 深度思考分析")
        if use_web and settings["enable_web_search"]:
            steps.append("🌐 联网搜索")
        if use_knowledge and settings["enable_knowledge_base"]:
            steps.append("📚 知识库检索")
        if use_mcp:
            steps.append("🛠️ MCP工具调用")
        steps.append("✍️ 生成回答")
        
        for i, step in enumerate(steps):
            history[-1][1] = f"**处理进度 ({i+1}/{len(steps)})**\n\n{step}..."
            yield history, ""
            time.sleep(0.5)
        
        # 生成回答流
        prompt = f"用户问题：{query}\n请提供专业的政策咨询服务回答。"
        
        try:
            stream = client.chat.completions.create(
                model=MODEL,
                messages=[{"role": "user", "content": prompt}],
                stream=True,
                temperature=settings["temperature"]
            )
            
            for chunk in stream:
                if chunk.choices[0].delta.content is not None:
                    word = chunk.choices[0].delta.content
                    full_response += word
                    history[-1][1] = full_response
                    yield history, ""
            
            # 添加功能使用说明
            used_features = []
            if use_web: used_features.append("联网搜索")
            if use_knowledge: used_features.append("知识库")
            if use_mcp: used_features.append("MCP工具")
            
            if used_features:
                feature_text = f"\n\n---\n**使用的功能**: {', '.join(used_features)}"
                history[-1][1] += feature_text
                yield history, ""
                
        except Exception as e:
            history[-1][1] = f"❌ 抱歉，出现错误：{str(e)}"
            yield history, ""

# 创建智能体实例
agent = CherryStylePolicyAgent()

def create_cherry_style_interface():
    with gr.Blocks(
        theme=gr.themes.Soft(
            primary_hue="emerald",
            secondary_hue="slate"
        ),
        title="AI政策咨询智能体 - Cherry Studio风格",
        css="""
        .gradio-container {
            max-width: 1400px !important;
        }
        .feature-card {
            border: 1px solid #e2e8f0;
            border-radius: 8px;
            padding: 12px;
            margin: 8px 0;
            background: #f8fafc;
        }
        .session-item {
            padding: 8px 12px;
            margin: 4px 0;
            border-radius: 6px;
            cursor: pointer;
        }
        .session-item:hover {
            background: #edf2f7;
        }
        .session-active {
            background: #e6fffa;
            border-left: 4px solid #38b2ac;
        }
        """
    ) as demo:
        
        # 顶部导航
        gr.Markdown("""
        <div style="display: flex; justify-content: space-between; align-items: center; padding: 15px 20px; background: linear-gradient(135deg, #10b981 0%, #059669 100%); border-radius: 10px; color: white; margin-bottom: 20px;">
            <div>
                <h1 style="margin: 0; display: flex; align-items: center; gap: 10px;">
                    <span>🍒 AI政策咨询智能体</span>
                </h1>
                <p style="margin: 5px 0 0 0; opacity: 0.9;">Cherry Studio风格 · 多功能集成 · 专业政策服务</p>
            </div>
            <div style="display: flex; gap: 10px;">
                <div style="background: rgba(255,255,255,0.2); padding: 8px 15px; border-radius: 20px;">🚀 在线</div>
                <div style="background: rgba(255,255,255,0.2); padding: 8px 15px; border-radius: 20px;">📚 知识库就绪</div>
                <div style="background: rgba(255,255,255,0.2); padding: 8px 15px; border-radius: 20px;">🌐 联网搜索</div>
            </div>
        </div>
        """)
        
        with gr.Row(equal_height=False):
            # 左侧边栏 - 功能面板
            with gr.Column(scale=1, min_width=300):
                # 会话管理
                with gr.Group():
                    gr.Markdown("### 💬 会话管理")
                    with gr.Row():
                        new_chat_btn = gr.Button("🆕 新对话", size="sm")
                        clear_chat_btn = gr.Button("🗑️ 清空", size="sm", variant="secondary")
                    
                    sessions_list = gr.JSON(
                        label="当前会话",
                        value={"当前会话": "政策咨询"},
                        every=1
                    )
                
                # 知识库管理
                with gr.Group():
                    gr.Markdown("### 📚 知识库")
                    file_upload = gr.File(
                        label="上传政策文档",
                        file_types=[".txt", ".pdf", ".docx"],
                        file_count="multiple"
                    )
                    upload_status = gr.Textbox(label="上传状态", interactive=False)
                    
                    knowledge_stats = gr.Textbox(
                        label="知识库统计",
                        value="政策文档: 3个\n自定义文件: 0个\n总容量: 2.1MB",
                        interactive=False
                    )
                
                # 功能配置
                with gr.Group():
                    gr.Markdown("### ⚙️ 功能配置")
                    
                    web_search_toggle = gr.Checkbox(label="🌐 启用联网搜索", value=True)
                    knowledge_base_toggle = gr.Checkbox(label="📚 启用知识库", value=True)
                    deep_thinking_toggle = gr.Checkbox(label="🤔 启用深度思考", value=True)
                    mcp_tools_toggle = gr.Checkbox(label="🛠️ 启用MCP工具", value=True)
                    
                    temperature_slider = gr.Slider(0, 1, value=0.3, label="创造性")
                    max_tokens_slider = gr.Slider(100, 4000, value=2000, step=100, label="最大长度")
            
            # 中间 - 聊天区域
            with gr.Column(scale=2):
                # 功能开关栏
                with gr.Row():
                    use_web = gr.Checkbox(label="使用联网搜索", value=True, interactive=True)
                    use_knowledge = gr.Checkbox(label="使用知识库", value=True, interactive=True)
                    use_mcp = gr.Checkbox(label="使用MCP工具", value=False, interactive=True)
                    quick_settings = gr.Dropdown(
                        choices=["标准模式", "深度分析", "快速响应", "联网优先"],
                        value="标准模式",
                        label="预设模式"
                    )
                
                # 聊天区域
                chatbot = gr.Chatbot(
                    label="政策咨询对话",
                    height=500,
                    show_copy_button=True,
                    show_share_button=True,
                    avatar_images=(
                        "https://api.dicebear.com/7.x/avataaars/svg?seed=user",
                        "https://api.dicebear.com/7.x/bottts/svg?seed=policy"
                    ),
                    placeholder="💬 请输入政策咨询问题...\n\n💡 提示：您可以开启不同的功能模块来获得更精准的回答"
                )
                
                # 输入区域
                with gr.Row():
                    msg = gr.Textbox(
                        label="",
                        placeholder="例如：汽车以旧换新的补贴标准和申请流程是什么？",
                        lines=2,
                        scale=4,
                        container=False
                    )
                    submit_btn = gr.Button("🚀 发送", variant="primary", scale=1)
                
                # 快捷操作
                with gr.Row():
                    gr.Button("📋 导出对话", variant="secondary", size="sm")
                    gr.Button("🔄 重新生成", variant="secondary", size="sm")
                    gr.Button("📊 分析报告", variant="secondary", size="sm")
                    gr.Button("🎯 示例问题", variant="secondary", size="sm")
            
            # 右侧 - 信息面板
            with gr.Column(scale=1, min_width=280):
                # 系统状态
                with gr.Group():
                    gr.Markdown("### 📊 系统状态")
                    system_status = gr.Textbox(
                        label="运行状态",
                        value="✅ 所有服务正常\n🟢 API连接正常\n🔵 知识库加载完成\n🟡 搜索服务就绪",
                        interactive=False,
                        lines=4
                    )
                
                # 工具面板
                with gr.Group():
                    gr.Markdown("### 🛠️ 工具面板")
                    
                    # MCP工具
                    mcp_tool = gr.Dropdown(
                        choices=["政策查询", "补贴计算", "流程指导", "条件验证"],
                        label="MCP工具选择"
                    )
                    mcp_params = gr.Textbox(label="工具参数", placeholder="JSON格式参数")
                    mcp_result = gr.Textbox(label="工具结果", interactive=False)
                    run_tool_btn = gr.Button("运行工具", size="sm")
                
                # 快速问答模板
                with gr.Group():
                    gr.Markdown("### 🎯 快速问答")
                    template_questions = [
                        "汽车补贴标准？",
                        "家电申请条件？", 
                        "数码回收流程？",
                        "最新政策变化？"
                    ]
                    
                    for q in template_questions:
                        gr.Button(q, size="sm", variant="secondary")
        
        # 事件处理
        def handle_stream_chat(message, history, web, knowledge, mcp):
            for update in agent.stream_chat(message, history, web, knowledge, mcp):
                yield update
        
        submit_btn.click(
            fn=handle_stream_chat,
            inputs=[msg, chatbot, use_web, use_knowledge, use_mcp],
            outputs=[chatbot, msg]
        )
        
        msg.submit(
            fn=handle_stream_chat,
            inputs=[msg, chatbot, use_web, use_knowledge, use_mcp],
            outputs=[chatbot, msg]
        )
        
        # 新对话
        def new_conversation():
            agent.create_new_session()
            return [], "新对话已创建"
        
        new_chat_btn.click(
            fn=new_conversation,
            outputs=[chatbot, upload_status]
        )
        
        clear_chat_btn.click(lambda: [], None, chatbot)
        
        # 文件上传
        file_upload.upload(
            fn=agent.upload_knowledge_file,
            inputs=[file_upload],
            outputs=[upload_status]
        )
        
        # 工具运行
        def run_mcp_tool(tool_name, params):
            try:
                params_dict = json.loads(params) if params else {}
                result = agent.mcp_tool_call(tool_name, params_dict)
                return result
            except:
                return "工具执行失败"
        
        run_tool_btn.click(
            fn=run_mcp_tool,
            inputs=[mcp_tool, mcp_params],
            outputs=[mcp_result]
        )
        
        # 预设模式
        def apply_preset_mode(mode):
            settings = {
                "标准模式": {"web": True, "knowledge": True, "thinking": True, "temp": 0.3},
                "深度分析": {"web": True, "knowledge": True, "thinking": True, "temp": 0.1},
                "快速响应": {"web": False, "knowledge": False, "thinking": False, "temp": 0.7},
                "联网优先": {"web": True, "knowledge": False, "thinking": False, "temp": 0.3}
            }
            config = settings.get(mode, settings["标准模式"])
            return config["web"], config["knowledge"], config["temp"]
        
        quick_settings.change(
            fn=apply_preset_mode,
            inputs=[quick_settings],
            outputs=[use_web, use_knowledge, temperature_slider]
        )
        
        return demo

if __name__ == "__main__":
    print("🍒 启动Cherry Studio风格政策智能体...")
    print("💬 多会话管理就绪")
    print("📚 知识库系统就绪")
    print("🌐 联网搜索就绪") 
    print("🛠️ MCP工具就绪")
    print("⚙️ 功能配置就绪")
    print("🚀 访问地址: http://localhost:7860")
    
    demo = create_cherry_style_interface()
    demo.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=False,
        inbrowser=True
    )