# policy_assistant.py
""" utf-8 encoding 智能政策查询助手 """
import os
import json
import requests
import gradio as gr
import time
from bs4 import BeautifulSoup
from openai import OpenAI
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores import Chroma
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.schema import Document

# 配置信息
system_prompt_file = "templates/ai_setting_VTuber-Neuro sama.txt"
openai_api_key = "63f72c10e53241509645b29dfc5f06c8.x0RKmLAYwR7uJMsr"
openai_base_url = "https://open.bigmodel.cn/api/paas/v4/"
models = "GLM-4-Flash"

class PolicyKnowledgeBase:
    """政策知识库管理类"""
    def __init__(self, persist_directory="./chroma_db"):
        self.persist_directory = persist_directory
        # 使用中文优化的嵌入模型
        self.embeddings = HuggingFaceEmbeddings(
            model_name="BAAI/bge-small-zh-v1.5",
            model_kwargs={'device': 'cpu'}
        )
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=500,
            chunk_overlap=50,
            length_function=len,
        )
        self.vector_store = None
        self._init_vector_store()
    
    def _init_vector_store(self):
        """初始化向量数据库"""
        if os.path.exists(self.persist_directory):
            try:
                self.vector_store = Chroma(
                    persist_directory=self.persist_directory,
                    embedding_function=self.embeddings
                )
                print("✅ 已加载现有知识库")
            except Exception as e:
                print(f"加载知识库失败，创建新的: {e}")
                self._create_new_vector_store()
        else:
            self._create_new_vector_store()
    
    def _create_new_vector_store(self):
        """创建新的向量数据库"""
        self.vector_store = Chroma.from_documents(
            documents=[],
            embedding=self.embeddings,
            persist_directory=self.persist_directory
        )
        print("✅ 创建新的知识库")
    
    def crawl_policy_data(self, url=None, keywords=None):
        """爬取政策数据"""
        policies = []
        
        try:
            if url and url.strip():
                # 从指定URL爬取
                print(f"正在爬取URL: {url}")
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                }
                response = requests.get(url.strip(), timeout=10, headers=headers)
                response.encoding = 'utf-8'
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # 提取政策信息
                title = soup.find('title').text if soup.find('title') else "无标题"
                
                # 提取正文内容
                content_elements = soup.find_all(['p', 'div'])
                content_texts = []
                for elem in content_elements[:30]:  # 限制元素数量
                    text = elem.get_text().strip()
                    if len(text) > 10:  # 只取有内容的文本
                        content_texts.append(text)
                
                content = ' '.join(content_texts)[:2000]  # 限制总长度
                
                policy = {
                    "title": title,
                    "content": content,
                    "source": url.strip(),
                    "publish_date": time.strftime("%Y-%m-%d"),
                    "department": "相关政府部门"
                }
                policies.append(policy)
                print(f"✅ 成功爬取政策: {title}")
            
            elif keywords and keywords.strip():
                # 模拟根据关键词生成政策数据
                keyword_list = [k.strip() for k in keywords.split(",") if k.strip()]
                for keyword in keyword_list[:5]:  # 限制关键词数量
                    policy = {
                        "title": f"关于{keyword}的相关政策规定",
                        "content": f"这是关于{keyword}的详细政策内容。该政策旨在促进相关领域的发展，提供具体的实施细则和保障措施。政策内容包括申请条件、支持标准、办理流程等具体事项。",
                        "source": f"https://www.example.gov.cn/policy/{keyword}",
                        "publish_date": "2024-01-01",
                        "department": f"{keyword}管理部门"
                    }
                    policies.append(policy)
                    print(f"✅ 生成模拟政策: {policy['title']}")
                    
        except Exception as e:
            print(f"❌ 爬取数据失败: {e}")
            return []
            
        return policies
    
    def add_policies_to_knowledge(self, policies):
        """将政策数据添加到知识库"""
        if not policies:
            return "没有可添加的政策数据"
            
        documents = []
        
        for policy in policies:
            # 创建文档对象
            content = f"政策标题：{policy['title']}\n发布部门：{policy['department']}\n发布日期：{policy['publish_date']}\n政策内容：{policy['content']}\n来源链接：{policy['source']}"
            
            doc = Document(
                page_content=content,
                metadata={
                    "title": policy['title'],
                    "department": policy['department'],
                    "publish_date": policy['publish_date'],
                    "source": policy['source'],
                    "type": "policy"
                }
            )
            documents.append(doc)
        
        # 分割文本
        split_docs = self.text_splitter.split_documents(documents)
        
        # 添加到向量数据库
        if split_docs:
            self.vector_store.add_documents(split_docs)
            self.vector_store.persist()
            return f"✅ 成功添加 {len(split_docs)} 个文档片段到知识库"
        return "❌ 没有添加新的文档"
    
    def search_similar_policies(self, query, k=3):
        """在知识库中搜索相似政策"""
        if self.vector_store is None:
            print("❌ 向量数据库未初始化")
            return []
            
        try:
            results = self.vector_store.similarity_search_with_relevance_scores(query, k=k)
            print(f"✅ 搜索到 {len(results)} 个相关文档")
            return results
        except Exception as e:
            print(f"❌ 搜索失败: {e}")
            return []
    
    def get_knowledge_stats(self):
        """获取知识库统计信息"""
        if self.vector_store:
            try:
                collection = self.vector_store._collection
                if collection:
                    count = collection.count()
                    return f"📊 知识库统计:\n文档数量: {count} 个片段\n存储位置: {self.persist_directory}"
            except Exception as e:
                return f"❌ 获取统计信息失败: {e}"
        return "❌ 知识库未初始化"

class EnhancedPolicyChat:
    """增强的政策对话类"""
    def __init__(self, knowledge_base):
        self.knowledge_base = knowledge_base
        self.content_history = [
            {'role': 'system', 'content': '''你是一个智能政策查询助手。请严格按照以下要求回答：
1. 基于提供的政策文档内容回答用户问题
2. 回答要准确、专业、清晰
3. 引用具体的政策条款时要注明来源
4. 如果政策文档中没有相关信息，请如实告知'''}
        ]
        
        # API配置
        self.openai_api_key = openai_api_key
        self.openai_base_url = openai_base_url
        self.model = models
    
    def _client(self):
        return OpenAI(
            api_key=self.openai_api_key,
            base_url=self.openai_base_url
        )
    
    def _build_context_prompt(self, query, search_results):
        """构建包含知识库上下文的提示词"""
        context_parts = []
        
        if search_results:
            context_parts.append("## 相关政策文档：")
            for i, (doc, score) in enumerate(search_results):
                context_parts.append(f"\n--- 文档 {i+1} (相关度: {score:.2f}) ---")
                context_parts.append(f"标题: {doc.metadata.get('title', '未知')}")
                context_parts.append(f"部门: {doc.metadata.get('department', '未知')}")
                context_parts.append(f"内容: {doc.page_content[:500]}...")
        
        context = "\n".join(context_parts) if context_parts else "没有找到相关政策文档。"
        
        prompt = f"""请基于以下政策文档回答用户问题。

{context}

用户问题：{query}

请根据上述文档内容回答，如果文档中有相关信息请引用具体内容并注明来源。如果文档中没有相关信息，请如实告知。"""
        
        return prompt
    
    def chat_with_reference(self, query):
        """带引用的对话"""
        try:
            print(f"用户问题: {query}")
            
            # 1. 在知识库中搜索相关内容
            search_results = self.knowledge_base.search_similar_policies(query, k=3)
            
            # 2. 构建增强的提示词
            enhanced_prompt = self._build_context_prompt(query, search_results)
            
            # 3. 调用大模型
            self.content_history.append({'role': 'user', 'content': enhanced_prompt})
            
            client = self._client()
            completion = client.chat.completions.create(
                model=self.model,
                messages=self.content_history,
                temperature=0.1  # 降低随机性，提高准确性
            )
            
            response = completion.choices[0].message.content
            
            # 4. 构建引用信息
            references = []
            if search_results:
                references.append("## 📚 参考政策文档：")
                for i, (doc, score) in enumerate(search_results):
                    ref_info = {
                        "title": doc.metadata.get('title', '未知标题'),
                        "department": doc.metadata.get('department', '未知部门'),
                        "source": doc.metadata.get('source', '未知来源'),
                        "relevance": f"{score:.2f}",
                        "excerpt": doc.page_content[:200] + "..."
                    }
                    references.append(f"{i+1}. **{ref_info['title']}** (相关度: {ref_info['relevance']})")
                    references.append(f"   部门: {ref_info['department']}")
                    references.append(f"   来源: {ref_info['source']}")
            
            # 更新对话历史（只保留原始问题）
            self.content_history[-1] = {'role': 'user', 'content': query}
            self.content_history.append({'role': 'assistant', 'content': response})
            
            final_references = "\n".join(references) if references else "📝 本次回答未引用具体政策文档。"
            print(f"回答完成，引用 {len(search_results)} 个文档")
            
            return response, final_references
            
        except Exception as e:
            error_msg = f"系统错误：{str(e)}"
            print(f"❌ 对话错误: {e}")
            return error_msg, "❌ 无法获取引用信息"
    
    def clear_history(self):
        """清空对话历史"""
        self.content_history = [
            {'role': 'system', 'content': '你是一个智能政策查询助手'}
        ]
        print("✅ 对话历史已清空")

# 创建全局实例
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
        
        if url and url.strip():
            policies = knowledge_base.crawl_policy_data(url=url)
        elif keywords and keywords.strip():
            policies = knowledge_base.crawl_policy_data(keywords=keywords)
        else:
            return "❌ 请输入关键词或URL"
        
        if policies:
            result = knowledge_base.add_policies_to_knowledge(policies)
            return result
        else:
            return "❌ 未获取到政策数据，请检查输入"
            
    except Exception as e:
        return f"❌ 爬取失败: {str(e)}"

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
    💡 **基于知识库的精准政策问答** | 🔍 **实时政策采集** | 📚 **引用溯源**
    """)
    
    with gr.Tab("💬 政策问答"):
        with gr.Row():
            with gr.Column(scale=2):
                chatbot = gr.Chatbot(
                    label="政策智能助手",
                    height=500,
                    show_copy_button=True,
                    bubble_full_width=False
                )
                
                with gr.Row():
                    msg = gr.Textbox(
                        label="请输入政策问题",
                        placeholder="例如：企业税收优惠政策有哪些？如何申请创业补贴？人才引进政策是什么？",
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
                    lines=8,
                    interactive=False,
                    show_copy_button=True
                )
                
                stats_display = gr.Textbox(
                    label="知识库状态",
                    value="点击统计按钮查看",
                    interactive=False,
                    lines=3
                )
    
    with gr.Tab("🕸️ 政策采集"):
        gr.Markdown("### 自动采集政策数据到知识库")
        
        with gr.Row():
            with gr.Column():
                keywords_input = gr.Textbox(
                    label="政策关键词（用逗号分隔）",
                    placeholder="例如：科技创新,税收优惠,人才引进,创业补贴",
                    lines=2
                )
                gr.Markdown("💡 **示例关键词**: 科技创新, 税收优惠, 人才引进, 创业补贴, 产业政策")
                
            with gr.Column():
                url_input = gr.Textbox(
                    label="政策网页URL",
                    placeholder="例如：https://www.gov.cn/zhengce/...",
                    lines=2
                )
                gr.Markdown("💡 **支持网站**: 政府官网、政策发布平台等")
        
        with gr.Row():
            crawl_btn = gr.Button("🚀 开始采集", variant="primary", size="lg")
            clear_kb_btn = gr.Button("🗑️ 清空知识库", variant="stop")
        
        crawl_result = gr.Textbox(
            label="采集结果", 
            interactive=False,
            lines=3
        )
        
        gr.Markdown("""
        **使用说明：**
        - **关键词采集**: 输入政策主题关键词，系统会生成模拟政策数据
        - **URL采集**: 输入具体政策网页URL，系统会爬取网页内容
        - **清空知识库**: 删除所有已存储的政策数据，重新开始
        """)
    
    with gr.Tab("📖 使用指南"):
        gr.Markdown("""
        ## 🎯 系统使用指南
        
        ### 💬 政策问答
        1. **直接提问**: 在输入框输入政策相关问题
        2. **智能检索**: 系统从知识库中检索最相关的政策文档
        3. **引用展示**: 回答附带政策来源，确保准确性
        
        ### 🕸️ 政策采集  
        1. **关键词采集**: 输入政策主题关键词，批量获取相关政策
        2. **URL采集**: 输入具体政策网页URL，精准采集单一政策
        3. **立即生效**: 采集的数据会立即加入知识库，可用于后续问答
        
        ### 🔍 核心特性
        - **精准回答**: 基于真实政策文档，避免幻觉
        - **引用溯源**: 每个回答都可追溯原始政策
        - **持续学习**: 通过采集不断丰富知识库
        - **多轮对话**: 保持上下文连贯性
        
        ### 🚀 快速开始
        1. 先在"政策采集"标签页添加一些政策数据
        2. 切换到"政策问答"开始智能咨询
        3. 查看"引用来源"了解答案依据
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
    
    # 清空知识库功能（需要重启程序才能生效）
    def clear_knowledge_base():
        import shutil
        if os.path.exists("./chroma_db"):
            shutil.rmtree("./chroma_db")
        return "✅ 知识库已清空，请重启程序"
    
    clear_kb_btn.click(
        fn=clear_knowledge_base,
        inputs=[],
        outputs=[crawl_result]
    )

if __name__ == "__main__":
    print("🚀 启动智能政策查询系统...")
    print("💡 访问地址: http://localhost:7860")
    print("⏳ 首次启动可能需要下载模型文件，请耐心等待...")
    
    demo.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=False,
        inbrowser=True
    )