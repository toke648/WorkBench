# knowledge_base.py
import os
import json
import requests
from bs4 import BeautifulSoup
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores import Chroma
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.schema import Document
import hashlib

class PolicyKnowledgeBase:
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
            self.vector_store = Chroma(
                persist_directory=self.persist_directory,
                embedding_function=self.embeddings
            )
        else:
            # 创建空的向量数据库
            self.vector_store = Chroma.from_documents(
                documents=[],
                embedding=self.embeddings,
                persist_directory=self.persist_directory
            )
    
    def crawl_policy_data(self, url=None, keywords=None):
        """爬取政策数据（示例：爬取中国政府网）"""
        policies = []
        
        try:
            if url:
                # 从指定URL爬取
                response = requests.get(url, timeout=10)
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # 提取政策信息（根据实际网站结构调整）
                title = soup.find('title').text if soup.find('title') else "无标题"
                content_elements = soup.find_all(['p', 'div'])
                content = ' '.join([elem.get_text().strip() for elem in content_elements[:20]])
                
                policy = {
                    "title": title,
                    "content": content[:1000],  # 限制长度
                    "source": url,
                    "publish_date": "2024-01-01",  # 实际中应从页面提取
                    "department": "相关政府部门"
                }
                policies.append(policy)
            
            elif keywords:
                # 模拟根据关键词搜索政策（实际应调用政务API或爬虫）
                for keyword in keywords:
                    policy = {
                        "title": f"关于{keyword}的相关政策",
                        "content": f"这是关于{keyword}的详细政策内容...",
                        "source": "https://www.gov.cn/example",
                        "publish_date": "2024-01-01",
                        "department": "相关部门"
                    }
                    policies.append(policy)
                    
        except Exception as e:
            print(f"爬取数据失败: {e}")
            
        return policies
    
    def add_policies_to_knowledge(self, policies):
        """将政策数据添加到知识库"""
        documents = []
        
        for policy in policies:
            # 创建文档对象
            content = f"标题：{policy['title']}\n部门：{policy['department']}\n日期：{policy['publish_date']}\n内容：{policy['content']}\n来源：{policy['source']}"
            
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
            return f"成功添加 {len(split_docs)} 个文档片段到知识库"
        return "没有添加新的文档"
    
    def search_similar_policies(self, query, k=3):
        """在知识库中搜索相似政策"""
        if self.vector_store is None:
            return []
            
        results = self.vector_store.similarity_search_with_relevance_scores(query, k=k)
        return results
    
    def get_knowledge_stats(self):
        """获取知识库统计信息"""
        if self.vector_store:
            collection = self.vector_store._collection
            if collection:
                return f"知识库中文档数量: {collection.count()}"
        return "知识库未初始化"