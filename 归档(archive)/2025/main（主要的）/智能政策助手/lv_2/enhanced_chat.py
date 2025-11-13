# enhanced_chat.py
from openai import OpenAI
import re

class EnhancedPolicyChat:
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
        self.openai_api_key = "63f72c10e53241509645b29dfc5f06c8.x0RKmLAYwR7uJMsr"
        self.openai_base_url = "https://open.bigmodel.cn/api/paas/v4/"
        self.model = "GLM-4-Flash"
    
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
            
            return response, "\n".join(references) if references else "本次回答未引用具体政策文档。"
            
        except Exception as e:
            error_msg = f"系统错误：{str(e)}"
            return error_msg, ""
    
    def clear_history(self):
        """清空对话历史"""
        self.content_history = [
            {'role': 'system', 'content': '你是一个智能政策查询助手'}
        ]