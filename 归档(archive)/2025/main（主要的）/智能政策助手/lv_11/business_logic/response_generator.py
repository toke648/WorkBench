"""
回答生成模块
整合检索结果和LLM生成专业回答
"""
from typing import List, Dict, Any, Optional
import re
from .llm_client import LLMClient
from .intent_recognition import IntentRecognizer
from .policy_retrieval import PolicyRetriever


class ResponseGenerator:
    """回答生成器"""
    
    def __init__(self, llm_client: LLMClient, retriever: PolicyRetriever, 
                 intent_recognizer: IntentRecognizer):
        """
        初始化回答生成器
        
        Args:
            llm_client: LLM客户端
            retriever: 政策检索器
            intent_recognizer: 意图识别器
        """
        self.llm_client = llm_client
        self.retriever = retriever
        self.intent_recognizer = intent_recognizer
    
    def generate(self, query: str, use_web: bool = True, use_knowledge: bool = True,
                 history: Optional[List] = None) -> Dict[str, Any]:
        """
        生成回答
        
        Args:
            query: 用户查询
            use_web: 是否使用联网搜索
            use_knowledge: 是否使用知识库
            history: 对话历史
            
        Returns:
            包含回答和来源的字典
        """
        # 识别意图
        intent_result = self.intent_recognizer.recognize(query)
        
        # 检索相关信息
        retrieval_result = self.retriever.retrieve(
            query,
            use_web=use_web,
            use_knowledge=use_knowledge,
            category=intent_result.get("category")
        )
        
        # 构建上下文
        context = self._build_context(retrieval_result)
        
        # 构建提示词
        prompt = self._build_prompt(query, context, intent_result)
        
        # 构建消息列表
        messages = self._build_messages(prompt, history)
        
        # 生成回答
        answer = self.llm_client.chat(messages)
        
        # 格式化回答，添加引用标记
        formatted_answer = self._format_with_citations(answer, retrieval_result["sources"])
        
        return {
            "answer": formatted_answer,
            "raw_answer": answer,
            "sources": retrieval_result["sources"],
            "intent": intent_result,
            "knowledge_results": retrieval_result["knowledge_results"],
            "web_results": retrieval_result["web_results"]
        }
    
    def stream_generate(self, query: str, use_web: bool = True, use_knowledge: bool = True,
                        history: Optional[List] = None) -> Dict[str, Any]:
        """
        流式生成回答
        
        Returns:
            生成器，每次yield部分回答和状态
        """
        # 识别意图
        intent_result = self.intent_recognizer.recognize(query)
        
        # 检索相关信息
        yield {"type": "status", "message": "🔍 正在检索相关信息..."}
        
        retrieval_result = self.retriever.retrieve(
            query,
            use_web=use_web,
            use_knowledge=use_knowledge,
            category=intent_result.get("category")
        )
        
        yield {
            "type": "status",
            "message": f"✅ 找到 {len(retrieval_result['sources'])} 个相关来源"
        }
        
        # 构建上下文和提示词
        context = self._build_context(retrieval_result)
        prompt = self._build_prompt(query, context, intent_result)
        messages = self._build_messages(prompt, history)
        
        yield {"type": "status", "message": "💭 正在生成回答..."}
        
        # 流式生成
        full_answer = ""
        for chunk in self.llm_client.stream_chat(messages):
            full_answer += chunk
            yield {
                "type": "chunk",
                "content": chunk,
                "full_answer": full_answer
            }
        
        # 格式化最终回答
        formatted_answer = self._format_with_citations(full_answer, retrieval_result["sources"])
        
        yield {
            "type": "complete",
            "answer": formatted_answer,
            "raw_answer": full_answer,
            "sources": retrieval_result["sources"],
            "intent": intent_result
        }
    
    def _build_context(self, retrieval_result: Dict[str, Any]) -> str:
        """构建上下文"""
        context_parts = []
        
        for source in retrieval_result["sources"]:
            source_id = source["id"]
            title = source.get("title", "")
            content = source.get("content", "")
            context_parts.append(f"[{source_id}] {title}: {content}")
        
        return "\n".join(context_parts) if context_parts else "基于通用政策知识"
    
    def _build_prompt(self, query: str, context: str, intent_result: Dict[str, Any]) -> str:
        """构建提示词"""
        intent = intent_result.get("primary_intent", "通用查询")
        
        prompt = f"""你是一个专业的政策咨询助手。请基于以下信息回答用户关于"以旧换新"政策的咨询问题。

**上下文信息：**
{context}

**用户问题：** {query}
**识别意图：** {intent}

**重要要求：**
1. 请提供专业、准确的政策咨询服务，回答要清晰、结构化，便于理解。
2. 在回答中自然地引用具体来源，使用[0][1][2]这样的引用标记。
3. 如果信息不足，请诚实说明，不要编造信息。
4. 回答要针对用户的具体问题，提供实用的信息。

**引用格式示例：**
根据最新政策，汽车以旧换新补贴标准为购置价格的10%[0]，新能源车补贴标准为15%[1]。申请流程需要提供旧车登记证书、新车购车合同等材料[2]。
"""
        return prompt
    
    def _build_messages(self, prompt: str, history: Optional[List] = None) -> List[Dict[str, str]]:
        """构建消息列表"""
        messages = []
        
        # 系统提示
        messages.append({
            "role": "system",
            "content": "你是一个专业的政策咨询助手，擅长回答关于消费品以旧换新政策的问题。"
        })
        
        # 历史对话（最近几轮）
        if history:
            for i, (user_msg, assistant_msg) in enumerate(history[-3:]):  # 只保留最近3轮
                messages.append({"role": "user", "content": user_msg})
                if assistant_msg:
                    # 移除HTML标签
                    clean_msg = re.sub(r'<[^>]+>', '', assistant_msg)
                    messages.append({"role": "assistant", "content": clean_msg})
        
        # 当前问题
        messages.append({"role": "user", "content": prompt})
        
        return messages
    
    def _format_with_citations(self, answer: str, sources: List[Dict[str, Any]]) -> str:
        """格式化回答，添加引用标记的HTML样式"""
        formatted_answer = answer
        
        # 为每个引用标记添加样式
        for source in sources:
            citation_pattern = f'\\[{source["id"]}\\]'
            replacement = f'<span class="citation" data-id="{source["id"]}" data-source=\'{source.get("title", "")}\'>[{source["id"]}]</span>'
            formatted_answer = re.sub(citation_pattern, replacement, formatted_answer)
        
        return formatted_answer

