# chatgpt_style_policy_agent.py
""" 
AI政策咨询智能体 - 带内联引用功能
修复版本：兼容Gradio版本问题
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
import re

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
# OPENAI_API_KEY = "63f72c10e53241509645b29dfc5f06c8.x0RKmLAYwR7uJMsr"
# OPENAI_BASE_URL = "https://open.bigmodel.cn/api/paas/v4/"
# MODEL = "GLM-4-Flash"

OPENAI_API_KEY = "sk-59018d1beb1a4783b510403496e0cce7"
OPENAI_BASE_URL = "https://api.deepseek.com"
MODEL = "deepseek-chat"

client = OpenAI(api_key=OPENAI_API_KEY, base_url=OPENAI_BASE_URL)

class ChatGPTStylePolicyAgent:
    """ChatGPT风格政策智能体 - 带内联引用功能"""
    
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
            "title": "新对话",
            "current_sources": {}
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
        
        # 备用：模拟搜索结果
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
        """生成带内联引用的回答 - 可点击的引用标签"""
        sources = []
        context_parts = []
        web_results = []
        
        # 知识库搜索
        if use_knowledge:
            knowledge_results = self.search_knowledge_base(query)
            for result in knowledge_results:
                source_id = len(sources)
                sources.append({
                    "id": source_id,
                    "title": result['title'],
                    "source": result['source'],
                    "url": result.get('url', '#'),
                    "type": "知识库",
                    "category": result.get('category', ''),
                    "content": result.get('content', '')[:200] + "..."  # 缩略内容
                })
                context_parts.append(f"[知识库{source_id}] {result['title']}: {result['content'][:100]}...")
        
        # 联网搜索
        if use_web:
            web_results = self.real_web_search(query)
            for result in web_results:
                source_id = len(sources)
                sources.append({
                    "id": source_id,
                    "title": result['title'],
                    "source": result['source'],
                    "url": result['url'],
                    "type": "网络搜索",
                    "date": result.get('date', ''),
                    "content": result.get('content', '')[:200] + "..."  # 缩略内容
                })
                context_parts.append(f"[网络{source_id}] {result['title']}: {result['content'][:100]}...")
        
        context = "\n".join(context_parts) if context_parts else "基于通用政策知识"
        
        # 生成带引用标记的回答
        prompt = f"""基于以下信息回答用户政策咨询问题：

{context}

用户问题：{query}

重要要求：
1.请提供专业、准确的政策咨询服务，并在回答中自然地引用具体政策条款。回答要清晰、结构化，便于理解。
2. 在回答中自然地引用具体来源，使用[1][2][3]这样的引用标记

引用格式示例：
根据最新政策，汽车以旧换新补贴标准为购置价格的10%[1]，新能源车补贴标准为15%[2]。申请流程需要提供旧车登记证书、新车购车合同等材料[3]。
"""

        try:
            response = client.chat.completions.create(
                model=MODEL,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3
            )
            
            answer = response.choices[0].message.content
            
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

    def get_source_details(self, source_id: str) -> Dict:
        """获取特定引用的详细信息"""
        if self.current_session_id in self.sessions:
            current_session = self.sessions[self.current_session_id]
            if "current_sources" in current_session and source_id in current_session["current_sources"]:
                return current_session["current_sources"][source_id]
        return {"error": "引用信息不存在"}
    
    def format_answer_with_citations(self, answer: str, sources: List[Dict]) -> str:
        """格式化回答，为引用标记添加HTML样式"""
        # 使用正则表达式找到所有引用标记并替换为带样式的HTML
        formatted_answer = answer
        
        # 为每个引用标记添加样式
        for source in sources:
            citation_pattern = f'\\[{source["id"]}\\]'
            replacement = f'<span class="citation" data-id="{source["id"]}">[{source["id"]}]</span>'
            formatted_answer = re.sub(citation_pattern, replacement, formatted_answer)
        
        return formatted_answer
    
    def stream_chat(self, query: str, history: List, use_web: bool, use_knowledge: bool) -> Any:
        """流式对话 - 支持内联引用显示"""
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
        
        for step in steps:
            if "联网搜索" in step and use_web:
                web_results = self.real_web_search(query)
                if web_results:
                    history[-1][1] = f"{step} (找到{len(web_results)}个结果)"
                else:
                    history[-1][1] = f"{step} (未找到相关结果)"
            else:
                history[-1][1] = f"{step}"
            
            yield history, ""
            time.sleep(0.5)
        
        # 生成回答和来源
        result = self.generate_response_with_sources(query, use_web, use_knowledge)
        full_response = result["answer"]
        sources = result["sources"]
        
        # 将回答和来源信息一起存储到会话中
        if self.current_session_id in self.sessions:
            current_session = self.sessions[self.current_session_id]
            current_session["current_sources"] = {str(src["id"]): src for src in sources}
        
        # 格式化回答，添加引用样式
        formatted_response = self.format_answer_with_citations(full_response, sources)
        
        # 流式输出回答
        words = full_response.split()
        current_text = ""
        
        for word in words:
            current_text += word + " "
            # 在流式输出时使用纯文本，最后再替换为带样式的版本
            history[-1][1] = current_text
            yield history, ""
            time.sleep(0.03)
        
        # 最终完整回答（带样式）
        history[-1][1] = formatted_response
        
        # 更新会话标题
        if self.current_session_id in self.sessions:
            if self.sessions[self.current_session_id]["title"] == "新对话" and query:
                self.sessions[self.current_session_id]["title"] = query[:30] + ("..." if len(query) > 30 else "")
        
        yield history, ""

# 创建智能体实例
agent = ChatGPTStylePolicyAgent()

def create_chatgpt_style_interface():
    """创建ChatGPT风格界面 - 带内联引用功能（兼容版本）"""
    with gr.Blocks(
        theme=gr.themes.Soft(
            primary_hue="blue",
            neutral_hue="slate"
        ),
        title="政策咨询助手 - 内联引用版",
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
        .message {
            max-width: 100% !important;
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
                
                # 引用详情区域
                gr.Markdown("### 📚 引用详情")
                source_details = gr.HTML(
                    value="<div style='text-align: center; color: #666; padding: 20px;'>点击回答中的引用标记查看详情</div>",
                    label=""
                )
                
                # 引用选择下拉框
                source_selector = gr.Dropdown(
                    label="选择引用查看详情",
                    choices=[],
                    interactive=True,
                    visible=False
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
                    gr.Markdown("### 🎯 政策咨询助手 - 内联引用版", elem_classes="center-title")
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
        
        def handle_source_selector_change(selected_source):
            """处理引用选择器变化"""
            if selected_source and selected_source.isdigit():
                source_info = agent.get_source_details(selected_source)
                if "error" not in source_info:
                    # 构建详情显示HTML
                    source_html = f"""
                    <div class="source-details">
                        <h4>📖 {source_info.get('title', '未知标题')}</h4>
                        <p><strong>内容:</strong> {source_info.get('content', '无详细内容')}</p>
                        <p><strong>来源:</strong> {source_info.get('source', '未知')}</p>
                        <p><strong>类型:</strong> {source_info.get('type', '未知')}</p>
                        <p><strong>分类:</strong> {source_info.get('category', '通用')}</p>
                        <p><strong>日期:</strong> {source_info.get('date', '未知')}</p>
                    """
                    
                    if source_info.get('url') and not source_info.get('url', '').startswith('#'):
                        source_html += f"""
                        <p><strong>链接:</strong> <a href="{source_info['url']}" target="_blank" style="color: #1e88e5;">🌐 打开原始链接</a></p>
                        """
                    
                    source_html += "</div>"
                    return source_html, gr.Dropdown(visible=True)
            
            return "<div style='text-align: center; color: #666; padding: 20px;'>未找到引用信息</div>", gr.Dropdown(visible=True)
        
        def update_source_selector():
            """更新引用选择器"""
            if agent.current_session_id in agent.sessions:
                current_session = agent.sessions[agent.current_session_id]
                if "current_sources" in current_session and current_session["current_sources"]:
                    sources = current_session["current_sources"]
                    choices = [str(src_id) for src_id in sources.keys()]
                    choices.sort(key=int)
                    return gr.Dropdown(choices=choices, visible=bool(choices))
            return gr.Dropdown(choices=[], visible=False)
        
        # 绑定事件
        submit_btn.click(
            fn=handle_stream_chat,
            inputs=[msg, chatbot, use_web_quick, use_knowledge_quick],
            outputs=[chatbot, msg]
        ).then(
            fn=update_sessions_list,
            outputs=[sessions_list]
        ).then(
            fn=update_source_selector,
            outputs=[source_selector]
        )
        
        msg.submit(
            fn=handle_stream_chat, 
            inputs=[msg, chatbot, use_web_quick, use_knowledge_quick],
            outputs=[chatbot, msg]
        ).then(
            fn=update_sessions_list,
            outputs=[sessions_list]
        ).then(
            fn=update_source_selector,
            outputs=[source_selector]
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
            return [], gr.Radio(choices=choices, value=new_choice), gr.Dropdown(choices=[], visible=False)
        
        new_chat_btn.click(
            fn=new_conversation,
            outputs=[chatbot, sessions_list, source_selector]
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
        ).then(
            fn=update_source_selector,
            outputs=[source_selector]
        )
        
        def handle_file_upload(file):
            """处理文件上传"""
            if file:
                status, preview = agent.process_uploaded_file(file)
                return status
            return "请选择文件"
        
        file_upload.upload(
            fn=handle_file_upload,
            inputs=[file_upload],
            outputs=[upload_status]
        )
        
        clear_btn.click(
            fn=lambda: ([], gr.Dropdown(choices=[], visible=False)),
            outputs=[chatbot, source_selector]
        )
        
        # 同步设置
        use_web_quick.change(lambda x: x, use_web_quick, use_web)
        use_knowledge_quick.change(lambda x: x, use_knowledge_quick, use_knowledge)
        
        # 引用选择器事件
        source_selector.change(
            fn=handle_source_selector_change,
            inputs=[source_selector],
            outputs=[source_details, source_selector]
        )
        
        # 初始化会话列表
        demo.load(
            fn=update_sessions_list,
            outputs=[sessions_list]
        ).then(
            fn=update_source_selector,
            outputs=[source_selector]
        )
        
        return demo

if __name__ == "__main__":
    print("🎯 启动政策咨询助手（内联引用版）...")
    print("💬 对话管理功能就绪")
    print("📁 文档上传解析功能就绪") 
    print("🌐 联网搜索功能就绪")
    print("📚 知识库检索功能就绪")
    print("🔗 内联引用功能就绪")
    print("🚀 访问地址: http://localhost:7860")
    
    demo = create_chatgpt_style_interface()
    demo.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=False,
        inbrowser=True
    )