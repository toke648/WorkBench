# AI Conversation Exporter

导出多个 AI 平台（ChatGPT、DeepSeek、Claude、以及通用 JSON/JSONL）的对话为整洁的 Markdown 文件。

## 特性

- ✅ 自动识别多种导出格式（包含 ChatGPT `conversations.json` 直读）
- ✅ 支持 Zip（ChatGPT 官方导出）、JSON、JSONL
- ✅ YAML frontmatter 元信息（标题、平台、导出时间、消息数）
- ✅ 规范的角色映射（user/assistant/system/tool）
- ✅ 命令行工具 `ai-export`，简单易用

## 安装

本项目尚未发布到 PyPI。请在源码目录内安装：

```bash
pip install ai-conversation-exporter
```

安装后将获得命令：

```bash
ai-export --help
```

## 使用示例

```bash
# 1) ChatGPT 官方导出 zip（包含 conversations.json）
ai-export chatgpt_export.zip

# 2) 直接解析 ChatGPT 的 conversations.json（无需 zip）
ai-export conversations.json

# 3) DeepSeek 导出（数组 JSON / API JSON / JSONL）
ai-export deepseek_export.json
ai-export deepseek_export.jsonl

# 4) Claude 导出 JSON
ai-export claude_chat.json

# 指定输出目录
ai-export conversations.json -o ./ai_output
```

## 支持的输入格式

- ChatGPT
  - `.zip`（官方导出包，自动在包内查找 `conversations.json`）
  - `conversations.json`（直接解析）
  - 消息结构同时兼容：
    - 经典结构：`message.content.parts[] + message.author.role`
    - 变体结构：`message.fragments[]`（`REQUEST` → user，`RESPONSE` → assistant）

- DeepSeek
  - 数组 JSON（含 `conversation_id` / `messages`）
  - API JSON（顶层 `messages`）
  - JSONL（每行一条 `{"role","content"}`）

- Claude
  - JSON（顶层 `conversation` 或 `messages`）

- 通用 JSON/JSONL（Unknown）
  - 自动兜底识别常见字段（`mapping`/`messages`/`conversation`），最大化导出成功率

## 输出格式

- 每个会话导出为单独的 Markdown 文件，命名：`YYYYMMDD_HHMMSS_标题.md`
- 文件内容包含：
  - YAML frontmatter（`title`、`platform`、`export_date`、`message_count`）
  - 标题与概要信息
  - 顺序排列的消息区块（按可用的时间戳排序）

## 常见问题

- 看到“无法识别格式，使用通用解析器”或“检测到 Unknown 格式”？
  - 表示当前输入未匹配 ChatGPT/DeepSeek/Claude 的特定解析器，将由通用解析器尝试解析。
  - 若导出为空，请提供文件前后数条数据样例（可打码隐私），以便完善兼容。

- Windows 中文/空格路径
  - 已使用 UTF-8 打开文件与写入；如使用 PowerShell/终端，请确保当前路径与权限正确。

## 许可协议

MIT