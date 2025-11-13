# 政策咨询智能体 - 模块化架构版本

## 📋 项目简介

这是一个基于模块化架构的AI政策咨询智能体，专为"消费品以旧换新"政策咨询场景设计。系统采用分层架构设计，支持灵活的模型配置、知识库管理、文档导入等功能。

## 🏗️ 架构设计

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   用户交互层     │    │   业务逻辑层      │    │   数据服务层     │
│                 │    │                  │    │                 │
│ • Gradio Web界面 │◄──►│ • 意图识别       │◄──►│ • 政策知识库     │
│ • 多轮对话管理   │    │ • 政策检索       │    │ • 用户对话历史   │
│ • 实时响应       │    │ • 回答生成       │    │ • 更新监控       │
│ • 触摸引用显示   │    │ • LLM客户端      │    │ • 文档解析       │
└─────────────────┘    └──────────────────┘    │ • 爬虫功能       │
                                                 └─────────────────┘
```

## 📁 项目结构

```
lv_10/
├── config/                 # 配置模块
│   ├── __init__.py
│   └── settings.py          # 配置管理（模型、数据库、搜索等）
│
├── data_service/            # 数据服务层
│   ├── __init__.py
│   ├── database.py          # 数据库管理（MySQL/内存模式）
│   ├── knowledge_base.py    # 知识库管理
│   ├── document_parser.py   # 文档解析（PDF/DOCX/TXT）
│   └── crawler.py           # 爬虫功能（可选）
│
├── business_logic/          # 业务逻辑层
│   ├── __init__.py
│   ├── llm_client.py        # LLM客户端（支持多种模型）
│   ├── intent_recognition.py # 意图识别
│   ├── policy_retrieval.py  # 政策检索
│   └── response_generator.py # 回答生成
│
├── ui_layer/                # 用户交互层
│   ├── __init__.py
│   ├── conversation_manager.py # 对话管理
│   └── gradio_interface.py  # Gradio界面
│
├── utils/                   # 工具模块
│   ├── __init__.py
│   └── logger.py           # 日志工具
│
├── main.py                  # 主入口文件
├── requirements.txt         # 依赖列表
└── README.md               # 说明文档
```

## ✨ 核心功能

### 1. 灵活的模型配置
- ✅ 支持多种模型提供商（OpenAI、DeepSeek、GLM等）
- ✅ 支持自定义模型和API
- ✅ 深度思考模式
- ✅ 模型管理器（支持多模型切换）

### 2. 知识数据库系统
- ✅ MySQL数据库支持（可选）
- ✅ 内存模式（默认，无需数据库）
- ✅ 文档一键导入（支持PDF、DOCX、TXT）
- ✅ 批量导入功能
- ✅ 爬虫导入（可选）

### 3. 智能化的前端显示
- ✅ ChatGPT风格界面
- ✅ 触摸友好的引用显示
- ✅ 引用点击/触摸查看详情
- ✅ 多轮对话管理
- ✅ 会话历史记录

### 4. 其他功能
- ✅ 联网搜索（Serper API）
- ✅ 意图识别
- ✅ 政策检索
- ✅ 流式回答生成

## 🚀 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置系统

创建 `config/config.json` 文件（可选，系统会自动创建默认配置）：

```json
{
  "model": {
    "default_model": "deepseek-chat",
    "api_key": "your-api-key",
    "base_url": "https://api.deepseek.com",
    "provider": "deepseek",
    "enable_deep_thinking": false
  },
  "database": {
    "enable_mysql": false,
    "host": "localhost",
    "port": 3306,
    "user": "root",
    "password": "",
    "database": "policy_agent"
  },
  "search": {
    "enable_web_search": true,
    "search_engine": "serper",
    "api_key": "your-serper-api-key",
    "max_results": 5
  },
  "ui": {
    "server_port": 7860,
    "enable_touch": true
  }
}
```

或使用环境变量：

```bash
export MODEL_API_KEY="your-api-key"
export MODEL_BASE_URL="https://api.deepseek.com"
export MODEL_NAME="deepseek-chat"
export SEARCH_API_KEY="your-serper-api-key"
```

### 3. 运行系统

```bash
python main.py
```

### 4. 访问界面

打开浏览器访问：`http://localhost:7860`

## 📖 使用说明

### 文档导入

1. **单文件导入**：在左侧边栏的"知识库管理"中，点击"上传政策文档"
2. **批量导入**：使用"批量上传文档"功能，可一次上传多个文件
3. **支持格式**：TXT、PDF、DOCX

### 模型配置

1. **修改配置文件**：编辑 `config/config.json`
2. **使用环境变量**：设置相应的环境变量
3. **切换模型**：在代码中使用 `ModelManager` 进行模型切换

### 启用MySQL数据库

1. 安装MySQL数据库
2. 在配置文件中设置数据库连接信息
3. 设置 `enable_mysql: true`
4. 系统会自动创建表结构

### 启用爬虫功能

1. 安装 `beautifulsoup4`：`pip install beautifulsoup4`
2. 在配置文件中设置爬虫参数
3. 使用 `PolicyCrawler` 进行网页爬取

## 🔧 模块说明

### 配置模块 (`config/`)
- `settings.py`: 统一管理所有配置
- 支持配置文件和环境变量
- 配置自动保存和加载

### 数据服务层 (`data_service/`)
- `database.py`: 数据库管理，支持MySQL和内存模式
- `knowledge_base.py`: 知识库管理，提供搜索、导入等功能
- `document_parser.py`: 文档解析，支持多种格式
- `crawler.py`: 网页爬虫，支持政策文档爬取

### 业务逻辑层 (`business_logic/`)
- `llm_client.py`: LLM客户端，支持多种模型提供商
- `intent_recognition.py`: 意图识别，分析用户查询意图
- `policy_retrieval.py`: 政策检索，整合知识库和联网搜索
- `response_generator.py`: 回答生成，整合检索结果和LLM生成

### 用户交互层 (`ui_layer/`)
- `conversation_manager.py`: 对话管理，管理多轮对话和会话
- `gradio_interface.py`: Gradio界面，提供现代化的Web界面

## 🎯 扩展开发

### 添加新的模型提供商

1. 在 `business_logic/llm_client.py` 中创建新的客户端类
2. 继承 `BaseLLMClient`
3. 实现 `chat()` 和 `stream_chat()` 方法
4. 在 `LLMClient._create_client()` 中添加新提供商的判断

### 添加新的文档格式支持

1. 在 `data_service/document_parser.py` 中添加新的解析方法
2. 在 `parse()` 方法中添加格式判断

### 自定义UI界面

1. 修改 `ui_layer/gradio_interface.py`
2. 添加新的组件和事件处理
3. 自定义CSS样式

## 📝 注意事项

1. **API密钥**：确保配置正确的模型API密钥和搜索API密钥
2. **数据库**：MySQL是可选的，系统默认使用内存模式
3. **依赖**：某些功能需要额外的依赖（如PDF解析需要PyPDF2）
4. **触摸支持**：CSS已优化触摸设备，但Gradio的触摸支持有限

## 🐛 问题排查

### 模型调用失败
- 检查API密钥是否正确
- 检查网络连接
- 检查模型配置

### 文档解析失败
- 确保安装了相应的依赖（PyPDF2、python-docx）
- 检查文件格式是否支持

### 数据库连接失败
- 检查MySQL服务是否运行
- 检查连接配置是否正确
- 可以使用内存模式（设置 `enable_mysql: false`）

## 📄 许可证

本项目仅供学习和研究使用。

## 🤝 贡献

欢迎提交Issue和Pull Request！

---

**版本**: 模块化架构 v1.0  
**更新日期**: 2024年
