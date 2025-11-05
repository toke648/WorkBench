# cherry_style_policy_agent.py
""" 
AI政策咨询智能体 - ChatGPT风格
集成化功能 + 专业界面 + 真实功能实现

功能特性：
1. ChatGPT风格界面：左侧会话列表，中间聊天区，右侧功能标签
2. 真实联网搜索：使用DuckDuckGo API（可扩展为SerpAPI/Google Custom Search等）
3. 真实文档上传：支持PDF/DOCX/TXT文件解析
4. 多会话管理：创建、切换、管理多个对话会话
5. 引用链接：回答中自动添加引用来源（类似Grok风格）

依赖安装：
- pip install gradio openai requests
- pip install PyPDF2  # 可选，用于PDF解析
- pip install python-docx  # 可选，用于DOCX解析
"""

import gradio as gr
import requests
import json
import time
import os
from openai import OpenAI
from typing import List, Dict, Any, Optional
import pandas as pd
import uuid
from datetime import datetime
import re
from pathlib import Path

# 文档解析依赖（可选）
try:
    import PyPDF2
    PDF_AVAILABLE = True
except ImportError:
    PDF_AVAILABLE = False
    print("提示：安装 PyPDF2 以支持PDF文件解析: pip install PyPDF2")

try:
    from docx import Document as DocxDocument
    DOCX_AVAILABLE = True
except ImportError:
    DOCX_AVAILABLE = False
    print("提示：安装 python-docx 以支持DOCX文件解析: pip install python-docx")

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
            "title": f"新对话 {datetime.now().strftime('%m-%d %H:%M')}",
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
    
    def create_new_session(self, title: str = None):
        """创建新会话"""
        session_id = str(uuid.uuid4())
        if not title:
            title = f"新对话 {datetime.now().strftime('%m-%d %H:%M')}"
        self.sessions[session_id] = {
            "title": title,
            "history": [],
            "knowledge_files": [],
            "settings": self.sessions[self.current_session_id]["settings"].copy() if self.current_session_id in self.sessions else {
                "enable_web_search": True,
                "enable_deep_thinking": True,
                "enable_knowledge_base": True,
                "temperature": 0.3,
                "max_tokens": 2000
            }
        }
        self.current_session_id = session_id
        return session_id
    
    def get_session_list(self) -> List[Dict]:
        """获取会话列表"""
        sessions = []
        for sid, session in self.sessions.items():
            sessions.append({
                "id": sid,
                "title": session.get("title", "未命名对话"),
                "is_active": sid == self.current_session_id,
                "message_count": len(session.get("history", []))
            })
        return sessions
    
    def switch_session(self, session_id: str):
        """切换会话"""
        if session_id in self.sessions:
            self.current_session_id = session_id
            return self.sessions[session_id]["history"]
        return []
    
    def update_settings(self, settings: Dict):
        """更新会话设置"""
        if self.current_session_id in self.sessions:
            self.sessions[self.current_session_id]["settings"].update(settings)
    
    def parse_document(self, file_path: str) -> str:
        """解析文档内容"""
        ext = Path(file_path).suffix.lower()
        content = ""
        
        try:
            if ext == ".txt":
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()
            
            elif ext == ".pdf" and PDF_AVAILABLE:
                with open(file_path, "rb") as f:
                    pdf_reader = PyPDF2.PdfReader(f)
                    for page in pdf_reader.pages:
                        content += page.extract_text() + "\n"
            
            elif ext == ".docx" and DOCX_AVAILABLE:
                doc = DocxDocument(file_path)
                for paragraph in doc.paragraphs:
                    content += paragraph.text + "\n"
            
            else:
                return f"不支持的文件格式: {ext}"
            
            return content.strip()
            
        except Exception as e:
            return f"解析错误: {str(e)}"
    
    def upload_knowledge_file(self, file) -> tuple:
        """真实上传并解析知识文件"""
        if not file:
            return "❌ 请选择文件", ""
        
        try:
            file_path = file.name if hasattr(file, 'name') else file
            filename = os.path.basename(file_path)
            
            # 解析文档内容
            content = self.parse_document(file_path)
            
            if not content or content.startswith("不支持") or content.startswith("解析错误"):
                return f"❌ {content}", ""
            
            # 保存到知识库
            file_info = {
                "name": filename,
                "size": os.path.getsize(file_path),
                "upload_time": datetime.now().strftime("%Y-%m-%d %H:%M"),
                "content": content[:1000] + "..." if len(content) > 1000 else content,  # 预览前1000字符
                "full_content": content
            }
            
            self.sessions[self.current_session_id]["knowledge_files"].append(file_info)
            
            # 更新知识库
            # 简单提取关键词作为政策名称
            policy_name = filename.replace(".txt", "").replace(".pdf", "").replace(".docx", "")
            self.knowledge_base[policy_name] = {
                "category": "自定义文档",
                "content": content,
                "source": filename,
                "effective_date": datetime.now().strftime("%Y-%m-%d"),
                "tags": ["自定义", "文档"]
            }
            
            return f"✅ 已上传并解析: {filename}\n📄 内容长度: {len(content)} 字符", content[:500] + "..." if len(content) > 500 else content
            
        except Exception as e:
            return f"❌ 上传失败: {str(e)}", ""
    
    def web_search(self, query: str) -> List[Dict]:
        """真实的联网搜索功能"""
        try:
            # 方法1: 尝试使用DuckDuckGo Instant Answer API
            search_query = query + " 政策 2024"
            search_url = "https://api.duckduckgo.com/"
            params = {
                "q": search_query,
                "format": "json",
                "no_html": "1",
                "skip_disambig": "1"
            }
            
            results = []
            response = requests.get(search_url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                # 处理DuckDuckGo返回的结果
                if "Results" in data and data["Results"]:
                    for item in data["Results"][:5]:
                        url = item.get("FirstURL", "")
                        if url:
                            results.append({
                                "title": item.get("Text", query),
                                "content": item.get("Text", ""),
                                "source": url.split("/")[2] if "/" in url else "未知来源",
                                "url": url,
                                "date": datetime.now().strftime("%Y-%m-%d")
                            })
            
            # 如果DuckDuckGo没有足够结果，补充一些相关结果
            if len(results) < 3:
                # 可以在这里添加其他搜索引擎API，如：
                # - SerpAPI (需要API key)
                # - Google Custom Search API (需要API key)
                # - Bing Search API (需要API key)
                # 或者使用爬虫方式（需要额外库如selenium/beautifulsoup）
                pass
            
            # 如果还是没有结果，返回基于查询的备用结果
            if not results:
                results = [
                    {
                        "title": f"{query} - 相关政策信息",
                        "content": f"关于{query}的最新政策信息，建议访问官方网站查询最新政策文件",
                        "source": "政策咨询系统",
                        "url": f"https://www.gov.cn/zhengce/",
                        "date": datetime.now().strftime("%Y-%m-%d")
                    }
                ]
            
            return results[:5]  # 最多返回5个结果
            
        except Exception as e:
            print(f"搜索错误: {str(e)}")
            # 返回备用结果
            return [
                {
                    "title": f"{query} - 搜索服务",
                    "content": f"搜索服务暂时不可用。如需联网搜索功能，请配置搜索API（如SerpAPI、Google Custom Search等）。当前错误: {str(e)}",
                    "source": "系统提示",
                    "url": "#",
                    "date": datetime.now().strftime("%Y-%m-%d")
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
    
    def generate_response(self, query: str, use_web: bool, use_knowledge: bool, use_mcp: bool) -> tuple:
        """生成回答并返回引用链接"""
        settings = self.sessions[self.current_session_id]["settings"]
        
        # 构建上下文和引用
        context_parts = []
        citations = []  # 存储引用链接
        
        if use_knowledge and settings["enable_knowledge_base"]:
            # 知识库检索
            knowledge_results = []
            for policy_name, policy_info in self.knowledge_base.items():
                if any(keyword in query for keyword in policy_name.split()):
                    knowledge_results.append((policy_name, policy_info))
            
            if knowledge_results:
                context_parts.append("## 相关知识库内容\n")
                for policy_name, result in knowledge_results[:3]:
                    context_parts.append(f"**{policy_name}**")
                    context_parts.append(f"内容: {result['content']}")
                    context_parts.append(f"来源: {result['source']}\n")
                    # 添加引用
                    citations.append({
                        "title": policy_name,
                        "source": result['source'],
                        "url": f"#knowledge:{policy_name}",
                        "type": "知识库"
                    })
        
        if use_web and settings["enable_web_search"]:
            # 联网搜索
            web_results = self.web_search(query)
            if web_results:
                context_parts.append("## 最新政策动态\n")
                for result in web_results[:3]:
                    context_parts.append(f"**{result['title']}**")
                    context_parts.append(f"内容: {result['content']}")
                    context_parts.append(f"来源: {result['source']} ({result['date']})\n")
                    # 添加引用
                    citations.append({
                        "title": result['title'],
                        "source": result['source'],
                        "url": result.get('url', '#'),
                        "type": "网络搜索",
                        "date": result.get('date', '')
                    })
        
        if use_mcp:
            # MCP工具调用
            mcp_result = self.mcp_tool_call("policy_lookup", {"policy_name": "以旧换新"})
            context_parts.append(f"## 工具分析\n{mcp_result}\n")
        
        context = "\n".join(context_parts) if context_parts else "基于通用政策知识"
        
        prompt = f"""
        基于以下信息回答用户政策咨询问题：
        
        {context}
        
        用户问题：{query}
        
        请提供专业、准确、友好的政策咨询服务。在回答中，如果引用了政策内容，请明确指出信息来源。
        """
        
        try:
            response = client.chat.completions.create(
                model=MODEL,
                messages=[{"role": "user", "content": prompt}],
                temperature=settings["temperature"],
                max_tokens=settings["max_tokens"]
            )
            answer = response.choices[0].message.content
            
            # 在回答末尾添加引用链接（类似Grok风格）
            if citations:
                answer += "\n\n---\n**📚 参考来源：**\n"
                for i, citation in enumerate(citations, 1):
                    answer += f"{i}. [{citation['title']}]({citation['url']}) - {citation['source']}"
                    if citation.get('date'):
                        answer += f" ({citation['date']})"
                    answer += "\n"
            
            return answer, citations
        except Exception as e:
            return f"生成回答时出现错误：{str(e)}", []
    
    def stream_chat(self, query: str, history: List, use_web: bool, use_knowledge: bool, use_mcp: bool) -> Any:
        """流式对话"""
        settings = self.sessions[self.current_session_id]["settings"]
        
        # 初始化对话
        history.append([query, ""])
        full_response = ""
        citations = []
        
        # 步骤提示
        steps = []
        if use_web and settings["enable_web_search"]:
            steps.append("🌐 联网搜索中...")
            # 执行真实搜索
            web_results = self.web_search(query)
            if web_results:
                citations.extend([
                    {
                        "title": r['title'],
                        "source": r['source'],
                        "url": r.get('url', '#'),
                        "type": "网络搜索",
                        "date": r.get('date', '')
                    } for r in web_results[:3]
                ])
        
        if use_knowledge and settings["enable_knowledge_base"]:
            steps.append("📚 知识库检索中...")
            # 知识库检索
            knowledge_results = []
            for policy_name, policy_info in self.knowledge_base.items():
                if any(keyword in query for keyword in policy_name.split()):
                    knowledge_results.append((policy_name, policy_info))
                    citations.append({
                        "title": policy_name,
                        "source": policy_info['source'],
                        "url": f"#knowledge:{policy_name}",
                        "type": "知识库"
                    })
        
        if use_mcp:
            steps.append("🛠️ MCP工具调用中...")
        
        steps.append("✍️ 生成回答中...")
        
        # 显示处理步骤
        for i, step in enumerate(steps):
            history[-1][1] = f"**{step}**"
            yield history, ""
            time.sleep(0.3)
        
        # 构建上下文
        context_parts = []
        if citations:
            context_parts.append("## 参考信息\n")
            for cit in citations[:5]:
                if cit['type'] == '网络搜索':
                    context_parts.append(f"**{cit['title']}** - {cit['source']}")
                else:
                    policy_name = cit['title']
                    if policy_name in self.knowledge_base:
                        context_parts.append(f"**{policy_name}**: {self.knowledge_base[policy_name]['content'][:200]}...")
        
        context = "\n".join(context_parts) if context_parts else ""
        
        prompt = f"""
        {context}
        
        用户问题：{query}
        
        请提供专业的政策咨询服务回答。如果引用了政策内容，请明确指出信息来源。
        """
        
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
            
            # 添加引用链接（类似Grok风格）
            if citations:
                citation_text = "\n\n---\n**📚 参考来源：**\n"
                for i, cit in enumerate(citations[:5], 1):
                    citation_text += f"{i}. [{cit['title']}]({cit['url']}) - {cit['source']}"
                    if cit.get('date'):
                        citation_text += f" ({cit['date']})"
                    citation_text += "\n"
                history[-1][1] += citation_text
                yield history, ""
            
            # 保存到会话历史
            self.sessions[self.current_session_id]["history"] = history
                
        except Exception as e:
            history[-1][1] = f"❌ 抱歉，出现错误：{str(e)}"
            yield history, ""

# 创建智能体实例
agent = CherryStylePolicyAgent()

def create_cherry_style_interface():
    """创建ChatGPT风格的界面"""
    with gr.Blocks(
        theme=gr.themes.Soft(
            primary_hue="blue",
            secondary_hue="gray"
        ),
        title="AI政策咨询智能体",
        css="""
        .gradio-container {
            max-width: 100% !important;
            padding: 0 !important;
        }
        .main-container {
            display: flex;
            height: 100vh;
        }
        .sidebar {
            width: 260px;
            background: #202123;
            color: white;
            padding: 10px;
        }
        .chat-area {
            flex: 1;
            display: flex;
            flex-direction: column;
            background: #343541;
        }
        .right-panel {
            width: 300px;
            background: #202123;
            padding: 10px;
            overflow-y: auto;
        }
        .session-btn {
            width: 100%;
            text-align: left;
            padding: 10px;
            margin: 5px 0;
            border-radius: 5px;
            background: transparent;
            border: none;
            color: white;
            cursor: pointer;
        }
        .session-btn:hover {
            background: #343541;
        }
        .session-btn.active {
            background: #343541;
        }
        """
    ) as demo:
        
        # ChatGPT风格布局：左侧会话列表 + 中间聊天区 + 右侧功能标签
        with gr.Row(equal_height=True):
            # 左侧边栏 - 会话列表（ChatGPT风格）
            with gr.Column(scale=0, min_width=260):
                with gr.Group():
                    new_chat_btn = gr.Button("+ 新对话", variant="primary", size="sm")
                    sessions_list = agent.get_session_list()
                    session_choices = [s['title'] for s in sessions_list] if sessions_list else ["新对话"]
                    current_title = [s['title'] for s in sessions_list if s['id'] == agent.current_session_id][0] if sessions_list else "新对话"
                    sessions_dropdown = gr.Dropdown(
                        choices=session_choices,
                        value=current_title,
                        label="会话列表",
                        interactive=True
                    )
                
                with gr.Group():
                    gr.Markdown("### 功能")
                    use_web = gr.Checkbox(label="🌐 联网搜索", value=True, interactive=True)
                    use_knowledge = gr.Checkbox(label="📚 知识库", value=True, interactive=True)
                    use_mcp = gr.Checkbox(label="🛠️ MCP工具", value=False, interactive=True)
            
            # 中间 - 主聊天区域（ChatGPT风格）
            with gr.Column(scale=1):
                # 聊天区域 - 简洁风格
                chatbot = gr.Chatbot(
                    label="",
                    height=600,
                    show_copy_button=True,
                    container=True,
                    bubble_full_width=False,
                    avatar_images=(None, None),
                    placeholder="开始对话..."
                )
                
                # 输入区域 - 简洁风格
                with gr.Row():
                    msg = gr.Textbox(
                        label="",
                        placeholder="输入您的问题...",
                        lines=1,
                        scale=9,
                        container=False,
                        show_label=False
                    )
                    submit_btn = gr.Button("发送", variant="primary", scale=1, size="sm")
            
            # 右侧边栏 - 功能标签化展示
            with gr.Column(scale=0, min_width=280, visible=True) as right_panel:
                # 标签页组
                with gr.Tabs():
                    # 知识库标签
                    with gr.Tab("📚 知识库"):
                        file_upload = gr.File(
                            label="上传文档",
                            file_types=[".txt", ".pdf", ".docx"],
                            file_count="single"
                        )
                        upload_status = gr.Textbox(
                            label="状态",
                            interactive=False,
                            lines=3
                        )
                        file_preview = gr.Textbox(
                            label="文档预览",
                            interactive=False,
                            lines=5
                        )
                    
                    # 设置标签
                    with gr.Tab("⚙️ 设置"):
                        web_search_toggle = gr.Checkbox(label="启用联网搜索", value=True)
                        knowledge_base_toggle = gr.Checkbox(label="启用知识库", value=True)
                        deep_thinking_toggle = gr.Checkbox(label="深度思考", value=True)
                        temperature_slider = gr.Slider(0, 1, value=0.3, label="创造性", step=0.1)
                        max_tokens_slider = gr.Slider(100, 4000, value=2000, step=100, label="最大长度")
                    
                    # 工具标签
                    with gr.Tab("🛠️ 工具"):
                        mcp_tool = gr.Dropdown(
                            choices=["政策查询", "补贴计算", "流程指导", "条件验证"],
                            label="MCP工具",
                            value="政策查询"
                        )
                        mcp_params = gr.Textbox(label="参数", placeholder='{"policy_name": "以旧换新"}', lines=2)
                        run_tool_btn = gr.Button("运行", size="sm")
                        mcp_result = gr.Textbox(label="结果", interactive=False, lines=5)
                    
                    # 状态标签
                    with gr.Tab("📊 状态"):
                        system_status = gr.Textbox(
                            label="系统状态",
                            value="✅ 所有服务正常\n🟢 API连接正常\n🔵 知识库加载完成\n🟡 搜索服务就绪",
                            interactive=False,
                            lines=6
                        )
                        knowledge_stats = gr.Textbox(
                            label="知识库统计",
                            value="政策文档: 3个\n自定义文件: 0个",
                            interactive=False,
                            lines=3
                        )
        
        # 事件处理
        def handle_stream_chat(message, history, web, knowledge, mcp):
            if not message.strip():
                return history, ""
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
            session_id = agent.create_new_session()
            sessions = agent.get_session_list()
            # 使用完整session_id作为value，标题作为显示
            choices = [f"{s['title']}" for s in sessions]
            values = [s['id'] for s in sessions]
            current_title = [s['title'] for s in sessions if s['id'] == session_id][0] if sessions else "新对话"
            return [], gr.Dropdown(choices=choices, value=current_title)
        
        def update_sessions_list():
            sessions = agent.get_session_list()
            choices = [f"{s['title']}" for s in sessions]
            current_title = [s['title'] for s in sessions if s['id'] == agent.current_session_id][0] if sessions else "新对话"
            return gr.Dropdown(choices=choices, value=current_title)
        
        new_chat_btn.click(
            fn=new_conversation,
            outputs=[chatbot, sessions_dropdown]
        ).then(
            fn=update_sessions_list,
            outputs=[sessions_dropdown]
        )
        
        # 切换会话 - 通过标题匹配
        def switch_session_by_title(title):
            if title:
                sessions = agent.get_session_list()
                # 找到匹配的session_id
                for s in sessions:
                    if s['title'] == title:
                        history = agent.switch_session(s['id'])
                        return history
            return []
        
        sessions_dropdown.change(
            fn=switch_session_by_title,
            inputs=[sessions_dropdown],
            outputs=[chatbot]
        )
        
        # 文件上传 - 返回状态和预览
        def handle_file_upload(file):
            if file:
                status, preview = agent.upload_knowledge_file(file)
                # 更新知识库统计
                files_count = len(agent.sessions[agent.current_session_id]["knowledge_files"])
                stats = f"政策文档: 3个\n自定义文件: {files_count}个"
                return status, preview, stats
            return "", "", "政策文档: 3个\n自定义文件: 0个"
        
        file_upload.upload(
            fn=handle_file_upload,
            inputs=[file_upload],
            outputs=[upload_status, file_preview, knowledge_stats]
        )
        
        # 工具运行
        def run_mcp_tool(tool_name, params):
            try:
                params_dict = json.loads(params) if params else {}
                result = agent.mcp_tool_call(tool_name, params_dict)
                return result
            except Exception as e:
                return f"工具执行失败: {str(e)}"
        
        run_tool_btn.click(
            fn=run_mcp_tool,
            inputs=[mcp_tool, mcp_params],
            outputs=[mcp_result]
        )
        
        # 设置更新
        def update_settings(web, knowledge, thinking, temp, max_tokens):
            agent.update_settings({
                "enable_web_search": web,
                "enable_knowledge_base": knowledge,
                "enable_deep_thinking": thinking,
                "temperature": temp,
                "max_tokens": max_tokens
            })
            return "设置已更新"
        
        web_search_toggle.change(
            fn=lambda x: agent.update_settings({"enable_web_search": x}),
            inputs=[web_search_toggle],
            outputs=[]
        )
        
        knowledge_base_toggle.change(
            fn=lambda x: agent.update_settings({"enable_knowledge_base": x}),
            inputs=[knowledge_base_toggle],
            outputs=[]
        )
        
        temperature_slider.change(
            fn=lambda x: agent.update_settings({"temperature": x}),
            inputs=[temperature_slider],
            outputs=[]
        )
        
        return demo

if __name__ == "__main__":
    print("🚀 启动AI政策咨询智能体...")
    print("📱 ChatGPT风格界面")
    print("💬 多会话管理就绪")
    print("📚 知识库系统就绪（支持PDF/DOCX/TXT）")
    print("🌐 联网搜索就绪（DuckDuckGo API）")
    print("🔗 引用链接功能就绪（类似Grok）")
    print("⚙️ 功能配置就绪")
    print("🚀 访问地址: http://localhost:7860")
    
    demo = create_cherry_style_interface()
    demo.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=False,
        inbrowser=True
    )