# GPTtoTXT 简版实现 · 说明文档

> 将 ChatGPT / DeepSeek 的聊天记录导出包（ZIP）批量转换为 `.txt` 纯文本文件。

---

## 目录结构

```
GPTtoTXT简版实现/
├── ChatGPT/
│   ├── main.py      # 完整版：树形路径选择 + 完整元数据头
│   └── mini.py      # 简版：扁平遍历，适合快速导出
├── DEEPSEEK/
│   ├── main.py      # 完整版：树形路径选择 + 去重 + 完整元数据头
│   └── mini.py      # 简版：扁平遍历，适合快速导出
└── 说明文档.md
```

---

## 背景：为什么需要这个工具

ChatGPT 和 DeepSeek 都支持导出聊天记录，但导出格式是 **ZIP 压缩包内的 JSON 文件**，结构复杂，人眼难以阅读。

这两个工具的作用是把 JSON 解析成可直接阅读的 `.txt` 文件，每个对话存为一个文件。

---

## ChatGPT 版

### JSON 数据结构

ChatGPT 导出的 JSON 文件（`conversations-001.json` 等）是一个**对话数组**，每个对话结构如下：

```json
{
    "id": "abc-123",
    "title": "哲学讨论",
    "create_time": 1724082985.0,
    "update_time": 1724083100.0,
    "mapping": {
        "节点ID1": {
            "parent": null,
            "children": ["节点ID2"],
            "message": null
        },
        "节点ID2": {
            "parent": "节点ID1",
            "children": ["节点ID3", "节点ID4"],
            "message": {
                "author": { "role": "user" },
                "create_time": 1724082990.0,
                "content": {
                    "content_type": "text",
                    "parts": ["你好，请问..."]
                }
            }
        }
    }
}
```

**关键点**：消息存在 `mapping` 树中，每个节点有 `parent` / `children` 关系；用户重新生成回复时会产生**分叉子节点**。

---

### main.py（完整版）

**核心函数：`node_Selector(mapping)`**

沿树从根节点走到叶节点，提取**最终采用的对话路径**：

```
根节点（parent=None）
    ↓
遇到分叉 → 选 create_time 最新的子节点（即最后一次重新生成的版本）
    ↓
跳过 message=None 的占位节点
    ↓
返回按时间排序的消息列表
```

**当前行为**：仅提取 `role == 'user'` 的消息（注释掉的代码可改为同时提取助手回复）。

**输出文件名格式**：`{第一条消息的create_time}_{对话标题}.txt`

**输出文件内容**：
```
标题: 哲学讨论
ID: abc-123
创建时间: 1724082985.0
更新时间: 1724083100.0
============================================================

[user]: 你好，请问...

[user]: 继续问...
```

---

### mini.py（简版）

不做树形路径选择，**直接遍历所有节点**提取消息（无法过滤分叉中被废弃的版本）。

适用场景：快速验证数据、内容完整性比路径正确性更重要时。

**输出文件名格式**：`{对话标题}.txt`（无时间前缀）

---

## DeepSeek 版

### JSON 数据结构

DeepSeek 导出的 JSON 结构与 ChatGPT **不同**，消息内容存在 `fragments` 数组中，而非 `parts`：

```json
{
    "id": "xyz-456",
    "title": "代码调试",
    "inserted_at": "2026-05-05T10:00:00Z",
    "updated_at": "2026-05-05T10:30:00Z",
    "mapping": {
        "节点ID1": {
            "parent": null,
            "message": {
                "inserted_at": "2026-05-05T10:00:00Z",
                "model": "deepseek-chat",
                "fragments": [
                    {
                        "type": "REQUEST",
                        "content": "帮我写一个排序算法"
                    }
                ]
            }
        }
    }
}
```

**关键差异对比**：

| 字段 | ChatGPT | DeepSeek |
|------|---------|----------|
| 消息文本位置 | `message.content.parts[0]` | `message.fragments[].content` |
| 角色区分 | `message.author.role` (`user`/`assistant`) | `fragments[].type` (`REQUEST`=用户 / 其他=助手) |
| 时间字段 | `create_time`（Unix 时间戳浮点数） | `inserted_at`（ISO 8601 字符串） |
| 对话时间 | `create_time` / `update_time` | `inserted_at` / `updated_at` |

---

### main.py（完整版）

**核心函数：`node_Selector(mapping)`**

由于 DeepSeek 的树结构中可能存在重新生成导致的**重复 parent_id 消息**，采用去重策略：

```
遍历所有节点，提取 type=REQUEST 的 fragment
    ↓
以 parent_id 为 key 去重：同一 parent_id 只保留 inserted_at 最新的消息
    ↓
按 inserted_at 排序返回
```

**输出文件名格式**：`{inserted_at前10位，即日期}_{对话标题前20字}.txt`

**输出文件内容**：
```
标题: 代码调试
ID: xyz-456
创建时间: 2026-05-05T10:00:00Z
更新时间: 2026-05-05T10:30:00Z
模型: deepseek-chat
============================================================

[user]: 帮我写一个排序算法

[user]: 改成快速排序
```

---

### mini.py（简版）

扁平遍历所有 fragments，`REQUEST` 类型标记为「用户」，其余标记为「助手」，**不做去重**。

---

## 使用方法

### 1. 准备导出文件

- **ChatGPT**：`设置 → 数据控制 → 导出数据`，下载 ZIP 文件
- **DeepSeek**：`设置 → 导出数据`，下载 ZIP 文件

### 2. 修改配置

打开对应的 `main.py` 或 `mini.py`，修改顶部的路径变量：

```python
# ChatGPT
ZIP_FILE = './你的chatgpt导出文件.zip'
OUTPUT_DIR = './gptchat_data'   # 输出目录，不存在会自动创建

# DeepSeek
ZIP_FILE = './你的deepseek导出文件.zip'
OUTPUT_DIR = './deepseek_chats'
```

### 3. 运行

```bash
python main.py
# 或
python mini.py
```

### 4. 查看输出

运行完成后，`OUTPUT_DIR` 目录下会生成每个对话对应的 `.txt` 文件。

---

## main.py vs mini.py 选哪个？

| 场景 | 推荐 |
|------|------|
| 想要干净的「最终版」对话，过滤掉废弃的重新生成版本 | `main.py` |
| 快速验证导出文件是否正常，不在乎分叉 | `mini.py` |
| 学习数据结构、逐行理解解析逻辑 | `main.py`（有详细注释） |

---

## 扩展提示

- **提取助手回复**：在 `node_Selector` 中删除 `if role == 'user'` 的过滤条件即可同时保留双方对话。
- **文件名包含时间**：`main.py` 默认用时间戳做文件名前缀，方便按时间排序。
- **特殊字符**：`main.py` 使用正则表达式清理文件名非法字符；`mini.py` 仅替换 `/` 和 `\`，如果标题含有 `?*:` 等字符可能报错，按需增强。

---

*最后更新：2026-05-05*
