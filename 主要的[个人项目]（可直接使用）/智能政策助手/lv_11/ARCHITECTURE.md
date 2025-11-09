# 架构设计文档

## 📐 整体架构

本系统采用**分层架构**设计，将系统分为三个主要层次：

```
┌─────────────────────────────────────────────────────────┐
│                   用户交互层 (UI Layer)                  │
│  • Gradio Web界面                                        │
│  • 对话管理                                              │
│  • 触摸友好的引用显示                                    │
└──────────────────────┬──────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────┐
│                 业务逻辑层 (Business Logic)              │
│  • 意图识别                                              │
│  • 政策检索                                              │
│  • 回答生成                                              │
│  • LLM客户端管理                                         │
└──────────────────────┬──────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────┐
│                 数据服务层 (Data Service)                │
│  • 知识库管理                                            │
│  • 数据库操作 (MySQL/内存)                               │
│  • 文档解析                                              │
│  • 爬虫功能                                              │
└─────────────────────────────────────────────────────────┘
```

## 🔧 模块详解

### 1. 配置模块 (`config/`)

**职责**：统一管理所有配置

**核心类**：
- `ConfigManager`: 配置管理器（单例模式）
- `ModelConfig`: 模型配置
- `DatabaseConfig`: 数据库配置
- `SearchConfig`: 搜索配置
- `UISettings`: UI设置

**特性**：
- 支持配置文件（JSON格式）
- 支持环境变量（优先级更高）
- 配置自动保存和加载

### 2. 数据服务层 (`data_service/`)

#### 2.1 数据库模块 (`database.py`)

**职责**：提供数据持久化能力

**特性**：
- 支持MySQL数据库
- 支持内存模式（默认，无需数据库）
- 自动创建表结构
- 连接失败自动降级到内存模式

**核心方法**：
- `insert_policy()`: 插入政策数据
- `search_policies()`: 搜索政策
- `insert_document()`: 插入文档
- `get_all_policies()`: 获取所有政策

#### 2.2 知识库模块 (`knowledge_base.py`)

**职责**：知识库的统一管理接口

**特性**：
- 知识库搜索
- 文档一键导入
- 批量导入
- 自动提取政策信息

**核心方法**：
- `search()`: 搜索知识库
- `add_policy()`: 添加政策
- `import_from_file()`: 从文件导入
- `batch_import()`: 批量导入

#### 2.3 文档解析模块 (`document_parser.py`)

**职责**：解析各种格式的文档

**支持格式**：
- TXT: 纯文本
- PDF: PDF文档（需要PyPDF2）
- DOCX: Word文档（需要python-docx）

**核心方法**：
- `parse()`: 解析单个文档
- `batch_parse()`: 批量解析

#### 2.4 爬虫模块 (`crawler.py`)

**职责**：从网页爬取政策文档

**特性**：
- 支持域名白名单
- 可配置爬取深度
- 自动提取政策链接
- 失败降级处理

**核心方法**：
- `crawl()`: 爬取指定URL
- `crawl_policy_site()`: 爬取政策网站

### 3. 业务逻辑层 (`business_logic/`)

#### 3.1 LLM客户端模块 (`llm_client.py`)

**职责**：提供统一的LLM调用接口

**支持的提供商**：
- OpenAI兼容（DeepSeek、GLM等）
- 自定义模型（可扩展）

**核心类**：
- `BaseLLMClient`: 基类（抽象接口）
- `OpenAICompatibleClient`: OpenAI兼容客户端
- `CustomModelClient`: 自定义模型客户端
- `LLMClient`: 统一客户端接口
- `ModelManager`: 模型管理器（支持多模型）

**特性**：
- 支持流式输出
- 支持深度思考模式
- 支持自定义模型配置

#### 3.2 意图识别模块 (`intent_recognition.py`)

**职责**：识别用户查询意图

**识别的意图类型**：
- 查询补贴标准
- 查询申请流程
- 查询适用条件
- 查询产品范围
- 查询政策文件
- 对比政策
- 时间相关
- 地点相关

**核心方法**：
- `recognize()`: 识别意图
- `extract_keywords()`: 提取关键词
- `is_question()`: 判断是否是问题

#### 3.3 政策检索模块 (`policy_retrieval.py`)

**职责**：整合知识库搜索和联网搜索

**特性**：
- 知识库检索
- 联网搜索（Serper API）
- 结果统一格式
- 相关性评分

**核心方法**：
- `retrieve()`: 检索政策信息
- `_web_search()`: 联网搜索
- `_serper_search()`: Serper API搜索

#### 3.4 回答生成模块 (`response_generator.py`)

**职责**：整合检索结果和LLM生成专业回答

**特性**：
- 流式回答生成
- 自动添加引用标记
- 意图感知的提示词构建
- 上下文整合

**核心方法**：
- `generate()`: 生成回答
- `stream_generate()`: 流式生成回答
- `_build_prompt()`: 构建提示词
- `_format_with_citations()`: 格式化引用

### 4. 用户交互层 (`ui_layer/`)

#### 4.1 对话管理模块 (`conversation_manager.py`)

**职责**：管理多轮对话和会话

**特性**：
- 多会话管理
- 会话历史记录
- 来源信息管理
- 自动标题生成

**核心方法**：
- `create_session()`: 创建新会话
- `switch_session()`: 切换会话
- `add_message()`: 添加消息
- `get_history()`: 获取历史
- `get_sources()`: 获取来源

#### 4.2 Gradio界面模块 (`gradio_interface.py`)

**职责**：提供Web用户界面

**特性**：
- ChatGPT风格界面
- 触摸友好的引用显示
- 文档上传和管理
- 批量导入
- 实时流式输出

**核心组件**：
- 侧边栏：会话列表、引用详情、设置
- 主聊天区：对话界面、输入框
- 知识库管理：文档上传、批量导入

## 🔄 数据流

### 用户查询处理流程

```
用户输入
  │
  ▼
意图识别 (IntentRecognizer)
  │
  ▼
政策检索 (PolicyRetriever)
  ├─→ 知识库搜索 (KnowledgeBase)
  └─→ 联网搜索 (Web Search)
  │
  ▼
上下文构建 (ResponseGenerator)
  │
  ▼
LLM生成回答 (LLMClient)
  │
  ▼
格式化回答（添加引用）
  │
  ▼
显示给用户
```

### 文档导入流程

```
用户上传文件
  │
  ▼
文档解析 (DocumentParser)
  ├─→ PDF解析
  ├─→ DOCX解析
  └─→ TXT解析
  │
  ▼
提取政策信息 (KnowledgeBase)
  │
  ▼
保存到数据库 (DatabaseManager)
  │
  ▼
更新知识库索引
```

## 🎯 扩展点

### 1. 添加新的模型提供商

在 `business_logic/llm_client.py` 中：

```python
class NewProviderClient(BaseLLMClient):
    def __init__(self, config: ModelConfig):
        # 初始化新提供商的客户端
        pass
    
    def chat(self, messages, **kwargs):
        # 实现聊天接口
        pass
    
    def stream_chat(self, messages, **kwargs):
        # 实现流式聊天接口
        pass
```

### 2. 添加新的文档格式

在 `data_service/document_parser.py` 中：

```python
def _parse_new_format(self, file_path: Path) -> str:
    # 实现新格式的解析逻辑
    pass
```

### 3. 自定义UI组件

在 `ui_layer/gradio_interface.py` 中：

```python
# 在 create_interface() 方法中添加新组件
new_component = gr.Component(...)

# 添加事件处理
new_component.change(fn=handle_event, ...)
```

## 📊 配置管理

### 配置文件结构

```json
{
  "model": {
    "default_model": "deepseek-chat",
    "api_key": "...",
    "base_url": "...",
    "provider": "deepseek",
    "enable_deep_thinking": false
  },
  "database": {
    "enable_mysql": false,
    "host": "localhost",
    "port": 3306,
    ...
  },
  "search": {
    "enable_web_search": true,
    "search_engine": "serper",
    ...
  },
  "ui": {
    "server_port": 7860,
    "enable_touch": true,
    ...
  }
}
```

### 环境变量支持

```bash
MODEL_API_KEY=your-api-key
MODEL_BASE_URL=https://api.deepseek.com
MODEL_NAME=deepseek-chat
SEARCH_API_KEY=your-serper-key
DB_HOST=localhost
DB_PASSWORD=your-password
```

## 🚀 性能优化建议

1. **数据库优化**：
   - 使用MySQL时，添加适当的索引
   - 定期清理旧数据

2. **缓存机制**：
   - 可添加缓存层缓存常见查询结果
   - 缓存模型响应（可选）

3. **并发处理**：
   - 使用异步IO提升性能
   - 考虑使用消息队列处理大量请求

4. **搜索优化**：
   - 使用向量数据库（如Chroma）进行语义搜索
   - 优化搜索算法

## 🔒 安全考虑

1. **API密钥**：
   - 不要将密钥提交到版本控制
   - 使用环境变量或密钥管理服务

2. **输入验证**：
   - 验证用户输入
   - 防止SQL注入（使用参数化查询）

3. **文件上传**：
   - 验证文件类型和大小
   - 扫描恶意文件

4. **访问控制**：
   - 考虑添加身份验证
   - 限制API调用频率

## 📝 开发指南

### 添加新功能

1. **确定功能所属层级**
2. **创建或修改相应模块**
3. **更新配置文件（如需要）**
4. **添加测试**
5. **更新文档**

### 代码规范

- 使用类型提示
- 添加文档字符串
- 遵循PEP 8规范
- 适当的错误处理

---

**版本**: v1.0  
**最后更新**: 2024年

