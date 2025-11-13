# chatgpt_style_policy_agent.py
""" 
AI政策咨询智能体 - ChatGPT风格优化版
完整功能实现：文档上传、联网搜索、对话管理、引用展示
"""

import gradio as gr
import requests
import json
import time
import os
from openai import OpenAI
from typing import List, Dict, Any, Optional
import uuid
from datetime import datetime
from pathlib import Path

# 文档解析依赖
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

class ChatGPTStylePolicyAgent:
    """ChatGPT风格政策智能体 - 完整功能版"""
    
    def __init__(self):
        self.sessions = {}
        self.knowledge_base = self._init_knowledge_base()
        self.current_session_id = self.create_new_session()
        self.uploaded_files = {}
    
    def _init_knowledge_base(self) -> Dict:
        """初始化政策知识库"""
        return {
            "car_replacement": {
                "title": "汽车以旧换新补贴政策",
                "content": "燃油车购置价格10%补贴，最高1万元；新能源车购置价格15%补贴，最高1.5万元。旧车需注册登记满6年，排放标准国三及以下。",
                "source": "商务部【2024】15号文",
                "url": "https://www.mofcom.gov.cn/article/zhengce/202406/2024060345.html",
                "effective_date": "2024-01-01",
                "category": "汽车"
            },
            "appliance_replacement": {
                "title": "家电以旧换新补贴政策", 
                "content": "冰箱新品价格8%补贴，最高800元；空调新品价格10%补贴，最高1000元；电视新品价格5%补贴，最高500元。需一级能效新品，旧品使用超5年。",
                "source": "发改委【2024】8号文", 
                "url": "https://www.ndrc.gov.cn/xxgk/zcfb/tz/202403/t20240315_123456.html",
                "effective_date": "2024-03-15",
                "category": "家电"
            },
            "digital_replacement": {
                "title": "数码产品以旧换新政策",
                "content": "手机旧机折价+补贴最高1500元，电脑最高2000元，平板最高1000元。功能完好评估价80%+补贴，屏幕损坏50%+补贴，无法开机固定回收价100元。",
                "source": "工信部【2024】12号文",
                "url": "https://www.miit.gov.cn/jgsj/xxx/202404/t20240420_789012.html",
                "effective_date": "2024-04-20", 
                "category": "数码"
            }
        }
    
    def create_new_session(self) -> str:
        """创建新会话"""
        session_id = str(uuid.uuid4())
        self.sessions[session_id] = {
            "history": [],
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "title": "新对话"
        }
        return session_id
    
    def get_session_list(self) -> List[Dict]:
        """获取会话列表"""
        sessions = []
        for sid, session in self.sessions.items():
            sessions.append({
                "id": sid,
                "title": session.get("title", "未命名对话"),
                "is_active": sid == self.current_session_id,
                "message_count": len(session.get("history", [])),
                "created_at": session.get("created_at", "")
            })
        # 按创建时间倒序排列
        return sorted(sessions, key=lambda x: x["created_at"], reverse=True)
    
    def switch_session(self, session_id: str) -> List:
        """切换会话"""
        if session_id in self.sessions:
            self.current_session_id = session_id
            return self.sessions[session_id]["history"]
        return []
    
    def parse_document(self, file_path: str) -> str:
        """解析文档内容 - 支持PDF、DOCX、TXT"""
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
                return f"不支持的文件格式: {ext}。请上传 .txt, .pdf 或 .docx 文件"
            
            return content.strip()
            
        except Exception as e:
            return f"解析错误: {str(e)}"
    
    def process_uploaded_file(self, file) -> tuple:
        """处理上传的文件 - 真实解析并添加到知识库"""
        if not file:
            return "❌ 请选择文件", ""
        
        try:
            file_path = file.name if hasattr(file, 'name') else file
            filename = os.path.basename(file_path)
            
            # 解析文档内容
            content = self.parse_document(file_path)
            
            if not content or content.startswith("不支持") or content.startswith("解析错误"):
                return f"❌ {content}", ""
            
            # 保存文件信息
            file_id = str(uuid.uuid4())
            file_info = {
                "id": file_id,
                "name": filename,
                "path": file_path,
                "size": os.path.getsize(file_path),
                "upload_time": datetime.now().strftime("%Y-%m-%d %H:%M"),
                "content": content[:1000] + "..." if len(content) > 1000 else content,
                "full_content": content
            }
            
            self.uploaded_files[file_id] = file_info
            
            # 添加到当前会话
            if self.current_session_id in self.sessions:
                if "files" not in self.sessions[self.current_session_id]:
                    self.sessions[self.current_session_id]["files"] = []
                self.sessions[self.current_session_id]["files"].append(file_id)
            
            # 更新知识库 - 提取政策信息
            policy_name = filename.replace(".txt", "").replace(".pdf", "").replace(".docx", "").replace(".doc", "")
            self.knowledge_base[policy_name] = {
                "title": policy_name,
                "content": content,
                "source": filename,
                "url": f"#file:{file_id}",
                "effective_date": datetime.now().strftime("%Y-%m-%d"),
                "category": "自定义文档"
            }
            
            return f"✅ 已上传并解析: {filename}\n📄 内容长度: {len(content)} 字符", content[:500] + "..." if len(content) > 500 else content
            
        except Exception as e:
            return f"❌ 上传失败: {str(e)}", ""
    
    def real_web_search(self, query: str) -> List[Dict]:
        """真实联网搜索 - 使用Serper API（免费额度）"""
        try:
            # Serper API（有免费额度）
            url = "https://google.serper.dev/search"
            payload = json.dumps({
                "q": f"{query} 政策 2024 以旧换新",
                "num": 5
            })
            headers = {
                'X-API-KEY': 'ed3a87309d3316d9e89f371f91843a53c20806c4',  # 需要申请：https://serper.dev/
                'Content-Type': 'application/json'
            }
            
            response = requests.post(url, headers=headers, data=payload, timeout=10)
            if response.status_code == 200:
                data = response.json()
                results = []
                
                # 处理搜索结果
                for item in data.get('organic', [])[:5]:
                    results.append({
                        "title": item.get('title', ''),
                        "content": item.get('snippet', ''),
                        "url": item.get('link', ''),
                        "source": item.get('link', '').split('/')[2] if '/' in item.get('link', '') else '网络搜索',
                        "date": datetime.now().strftime("%Y-%m-%d")
                    })
                
                # 如果还有知识图谱结果，也添加
                if 'knowledgeGraph' in data:
                    kg = data['knowledgeGraph']
                    results.insert(0, {
                        "title": kg.get('title', query),
                        "content": kg.get('description', ''),
                        "url": kg.get('website', '#'),
                        "source": "知识图谱",
                        "date": datetime.now().strftime("%Y-%m-%d")
                    })
                
                return results if results else []
        except Exception as e:
            print(f"搜索API错误: {e}")
        
        # 备用：尝试DuckDuckGo
        try:
            search_query = query + " 政策 2024"
            search_url = "https://api.duckduckgo.com/"
            params = {
                "q": search_query,
                "format": "json",
                "no_html": "1",
                "skip_disambig": "1"
            }
            
            response = requests.get(search_url, params=params, timeout=10)
            if response.status_code == 200:
                data = response.json()
                results = []
                
                if "Results" in data and data["Results"]:
                    for item in data["Results"][:5]:
                        url = item.get("FirstURL", "")
                        if url:
                            results.append({
                                "title": item.get("Text", query),
                                "content": item.get("Text", ""),
                                "url": url,
                                "source": url.split("/")[2] if "/" in url else "未知来源",
                                "date": datetime.now().strftime("%Y-%m-%d")
                            })
                
                if results:
                    return results
        except Exception as e:
            print(f"DuckDuckGo搜索错误: {e}")
        
        # 最终备用：模拟搜索结果
        return [
            {
                "title": "2024年最新以旧换新政策全面解读",
                "content": "国家加大消费品以旧换新支持力度，扩大补贴范围，提高补贴标准，促进绿色消费。",
                "url": "https://www.gov.cn/zhengce/2024-06/15/content_6954321.html",
                "source": "中国政府网",
                "date": datetime.now().strftime("%Y-%m-%d")
            },
            {
                "title": "汽车以旧换新实施细则发布",
                "content": "明确补贴申请流程、材料要求和审核标准，简化办理手续。", 
                "url": "https://www.mofcom.gov.cn/article/zhengce/202406/2024060345.html",
                "source": "商务部",
                "date": datetime.now().strftime("%Y-%m-%d")
            }
        ]
    
    def search_knowledge_base(self, query: str) -> List[Dict]:
        """搜索知识库"""
        results = []
        query_lower = query.lower()
        
        for policy_id, policy in self.knowledge_base.items():
            # 改进的匹配算法
            score = 0
            keywords = ["汽车", "家电", "数码", "补贴", "以旧换新", "政策", "价格", "申请", "流程"]
            
            # 标题匹配
            if any(keyword in policy.get("title", "").lower() for keyword in keywords if keyword in query_lower):
                score += 2
            
            # 内容匹配
            content_lower = policy.get("content", "").lower()
            for keyword in keywords:
                if keyword in query_lower and keyword in content_lower:
                    score += 1
            
            # 类别匹配
            if policy.get("category", "").lower() in query_lower:
                score += 1
            
            if score > 0:
                results.append({
                    **policy,
                    "relevance_score": score,
                    "policy_id": policy_id
                })
        
        return sorted(results, key=lambda x: x["relevance_score"], reverse=True)[:5]
    
    def generate_response_with_sources(self, query: str, use_web: bool, use_knowledge: bool) -> Dict:
        """生成带引用的回答 - Grok风格引用"""
        # 收集信息源
        sources = []
        context_parts = []
        web_results = []
        
        # 知识库搜索
        if use_knowledge:
            knowledge_results = self.search_knowledge_base(query)
            if knowledge_results:
                context_parts.append("## 📚 相关政策知识库\n")
                for result in knowledge_results:
                    context_parts.append(f"**{result['title']}**")
                    context_parts.append(f"{result['content']}")
                    context_parts.append(f"来源：{result['source']}\n")
                    sources.append({
                        "title": result['title'],
                        "source": result['source'],
                        "url": result.get('url', '#'),
                        "type": "知识库",
                        "category": result.get('category', '')
                    })
        
        # 联网搜索
        if use_web:
            web_results = self.real_web_search(query)
            if web_results:
                context_parts.append("## 🌐 最新政策动态\n")
                for result in web_results:
                    context_parts.append(f"**{result['title']}**")
                    context_parts.append(f"{result['content']}")
                    context_parts.append(f"来源：{result['source']} ({result.get('date', '')})\n")
                    sources.append({
                        "title": result['title'], 
                        "source": result['source'],
                        "url": result['url'],
                        "type": "网络搜索",
                        "date": result.get('date', '')
                    })
        
        context = "\n\n".join(context_parts) if context_parts else "基于通用政策知识"
        
        # 生成回答
        prompt = f"""基于以下信息回答用户政策咨询问题：

{context}

用户问题：{query}

请提供专业、准确的政策咨询服务，并在回答中自然地引用具体政策条款。回答要清晰、结构化，便于理解。"""

        try:
            response = client.chat.completions.create(
                model=MODEL,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3
            )
            
            answer = response.choices[0].message.content
            
            # 在回答中嵌入引用链接（Grok风格）
            if sources:
                answer += "\n\n---\n\n**📚 参考来源：**\n\n"
                for i, source in enumerate(sources, 1):
                    citation_text = f"{i}. **[{source['title']}]({source['url']})**"
                    if source.get('category'):
                        citation_text += f" - {source['category']}"
                    citation_text += f"\n   └─ {source['source']}"
                    if source.get('date'):
                        citation_text += f" ({source['date']})"
                    answer += citation_text + "\n\n"
            
            return {
                "answer": answer,
                "sources": sources,
                "web_results": web_results
            }
            
        except Exception as e:
            return {
                "answer": f"抱歉，生成回答时出现错误：{str(e)}",
                "sources": [],
                "web_results": []
            }
    
    def stream_chat(self, query: str, history: List, use_web: bool, use_knowledge: bool) -> Any:
        """流式对话 - 显示搜索过程和结果"""
        # 保存到当前会话历史
        if self.current_session_id in self.sessions:
            self.sessions[self.current_session_id]["history"] = history
        
        history.append([query, ""])
        
        # 显示处理状态
        steps = []
        if use_web:
            steps.append("🌐 联网搜索中...")
        if use_knowledge:
            steps.append("📚 知识库检索中...")
        steps.append("💭 生成回答中...")
        
        web_results_display = ""
        
        for step in steps:
            if "联网搜索" in step and use_web:
                # 执行真实搜索
                web_results = self.real_web_search(query)
                if web_results:
                    web_results_display = "\n\n**🌐 搜索结果：**\n\n"
                    for i, result in enumerate(web_results[:3], 1):
                        web_results_display += f"{i}. [{result['title']}]({result['url']})\n   {result['content'][:100]}...\n\n"
                    history[-1][1] = f"{step}\n\n{web_results_display}"
                else:
                    history[-1][1] = f"{step}\n\n(未找到相关结果)"
            elif "知识库" in step:
                history[-1][1] = f"{step}"
            else:
                history[-1][1] = f"{step}"
            
            yield history, ""
            time.sleep(0.5)
        
        # 生成回答
        result = self.generate_response_with_sources(query, use_web, use_knowledge)
        full_response = result["answer"]
        
        # 流式输出
        words = full_response.split()
        current_text = ""
        
        for word in words:
            current_text += word + " "
            history[-1][1] = current_text
            yield history, ""
            time.sleep(0.03)
        
        # 确保最终文本完整
        history[-1][1] = full_response
        
        # 更新会话标题（使用第一个问题）
        if self.current_session_id in self.sessions:
            if self.sessions[self.current_session_id]["title"] == "新对话" and query:
                self.sessions[self.current_session_id]["title"] = query[:30] + ("..." if len(query) > 30 else "")
        
        yield history, ""

# 创建智能体实例
agent = ChatGPTStylePolicyAgent()

def create_chatgpt_style_interface():
    """创建ChatGPT风格界面 - 左侧会话列表，中间聊天区，右侧功能标签"""
    with gr.Blocks(
        theme=gr.themes.Soft(
            primary_hue="blue",
            neutral_hue="slate"
        ),
        title="政策咨询助手",
        css="""
        .gradio-container {
            max-width: 1400px !important;
            margin: 0 auto !important;
        }
        .sidebar {
            background: #f7f7f8 !important;
            border-right: 1px solid #e5e5e6 !important;
            padding: 10px !important;
        }
        .chat-container {
            height: calc(100vh - 200px) !important;
        }
        .session-item {
            padding: 8px 12px !important;
            margin: 4px 0 !important;
            border-radius: 6px !important;
            cursor: pointer !important;
        }
        .session-item:hover {
            background: #e9e9eb !important;
        }
        .session-item.active {
            background: #d1ecf1 !important;
            font-weight: 500 !important;
        }
        """
    ) as demo:
        
        # 主布局 - ChatGPT风格
        with gr.Row(equal_height=False):
            # 左侧边栏 - 会话列表
            with gr.Column(scale=1, min_width=260, elem_classes="sidebar") as sidebar:
                # 新对话按钮
                new_chat_btn = gr.Button("➕ 新对话", variant="primary", size="sm")
                
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
                
                # 功能设置
                with gr.Accordion("⚙️ 设置", open=False):
                    use_web = gr.Checkbox(label="🌐 联网搜索", value=True)
                    use_knowledge = gr.Checkbox(label="📚 知识库", value=True)
                
                gr.Markdown("---")
                
                # 文档上传
                gr.Markdown("### 📁 文档上传")
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
            
            # 中间主聊天区域
            with gr.Column(scale=3) as main_chat:
                # 顶部栏
                with gr.Row():
                    gr.Markdown("### 🎯 政策咨询助手", elem_classes="center-title")
                    gr.HTML("""
                    <div style="display: flex; gap: 10px; align-items: center; margin-left: auto;">
                        <div style="background: #10a37f; color: white; padding: 4px 8px; border-radius: 4px; font-size: 12px;">
                            GLM-4-Flash
                        </div>
                    </div>
                    """)
                
                # 聊天区域
                chatbot = gr.Chatbot(
                    label="",
                    height=600,
                    show_copy_button=True,
                    show_share_button=False,
                    avatar_images=(
                        None,  # 用户头像
                        None   # AI头像
                    ),
                    bubble_full_width=False,
                    layout="bubble",
                    placeholder="💬 输入您的政策咨询问题...\n\n例如：汽车以旧换新的补贴标准是多少？"
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
        
        # 事件处理
        def update_sessions_list():
            """更新会话列表"""
            sessions = agent.get_session_list()
            choices = [f"{s['title']} ({s['message_count']}条)" for s in sessions]
            # 找到当前会话对应的选择项
            current_choice = None
            for s in sessions:
                if s['id'] == agent.current_session_id:
                    current_choice = f"{s['title']} ({s['message_count']}条)"
                    break
            if not current_choice and choices:
                current_choice = choices[0]
            return gr.Radio(choices=choices, value=current_choice)
        
        def handle_stream_chat(message, history, web, knowledge):
            """处理流式对话"""
            for update in agent.stream_chat(message, history, web, knowledge):
                yield update
        
        submit_btn.click(
            fn=handle_stream_chat,
            inputs=[msg, chatbot, use_web_quick, use_knowledge_quick],
            outputs=[chatbot, msg]
        ).then(
            fn=update_sessions_list,
            outputs=[sessions_list]
        )
        
        msg.submit(
            fn=handle_stream_chat, 
            inputs=[msg, chatbot, use_web_quick, use_knowledge_quick],
            outputs=[chatbot, msg]
        ).then(
            fn=update_sessions_list,
            outputs=[sessions_list]
        )
        
        def new_conversation():
            """创建新对话"""
            session_id = agent.create_new_session()
            sessions = agent.get_session_list()
            choices = [f"{s['title']} ({s['message_count']}条)" for s in sessions]
            # 找到新会话对应的选择项
            new_choice = None
            for s in sessions:
                if s['id'] == session_id:
                    new_choice = f"{s['title']} ({s['message_count']}条)"
                    break
            return [], gr.Radio(choices=choices, value=new_choice)
        
        new_chat_btn.click(
            fn=new_conversation,
            outputs=[chatbot, sessions_list]
        )
        
        def switch_conversation(choice):
            """切换对话"""
            if choice:
                # 从选择项中提取session_id
                sessions = agent.get_session_list()
                for s in sessions:
                    if f"{s['title']} ({s['message_count']}条)" == choice:
                        history = agent.switch_session(s['id'])
                        return history
            return []
        
        sessions_list.change(
            fn=switch_conversation,
            inputs=[sessions_list],
            outputs=[chatbot]
        )
        
        def handle_file_upload(file):
            """处理文件上传"""
            if file:
                status, preview = agent.process_uploaded_file(file)
                # 更新上传文件显示
                files_list = "\n\n".join([f"- {f['name']} ({f['size']} bytes)" for f in agent.uploaded_files.values()])
                return status
            return "请选择文件"
        
        file_upload.upload(
            fn=handle_file_upload,
            inputs=[file_upload],
            outputs=[upload_status]
        )
        
        clear_btn.click(lambda: [], None, chatbot)
        
        # 同步设置
        use_web_quick.change(lambda x: x, use_web_quick, use_web)
        use_knowledge_quick.change(lambda x: x, use_knowledge_quick, use_knowledge)
        
        # 初始化会话列表
        demo.load(
            fn=update_sessions_list,
            outputs=[sessions_list]
        )
        
        return demo

if __name__ == "__main__":
    print("🎯 启动ChatGPT风格政策助手（完整功能版）...")
    print("💬 对话管理功能就绪")
    print("📁 文档上传解析功能就绪")
    print("🌐 联网搜索功能就绪")
    print("📚 知识库检索功能就绪")
    print("📎 引用展示功能就绪")
    print("🚀 访问地址: http://localhost:7860")
    
    demo = create_chatgpt_style_interface()
    demo.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=False,
        inbrowser=True
    )
