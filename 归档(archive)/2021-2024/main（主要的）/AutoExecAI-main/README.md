# AI Command Hub

[![license](https://img.shields.io/github/license/toke648/AutoExecAI)](https://github.com/toke648/AutoExecAI/blob/main/LICENSE)
[![Python](https://img.shields.io/badge/Python-3.8%2B-blue)](https://www.python.org/)

[![Discord](https://img.shields.io/badge/Discord-7289DA?style=for-the-badge&logo=discord&logoColor=white)](https://discord.gg/kwCY2wFPNh)

[**English**](En_README.md) | **简体中文**

**AutoExecAI** 是一个基于 AI 的智能工具，能够分析用户的需求并自动生成终端命令，执行命令后获取结果，并根据需要继续执行下一步命令。它通过自然语言处理（NLP）理解用户需求，并将其转换为可执行的命令。每次执行命令前，都会展示生成的命令供用户确认是否执行。支持多轮对话，直到任务完成。

## 功能特点

- **智能命令生成**：通过自然语言处理，根据用户的需求分析并生成相应的终端命令。
- **自动执行命令**：自动执行命令并返回执行结果，用户无需手动输入。
- **命令确认**：在每次命令执行前，展示生成的命令并要求用户确认是否执行。
- **多轮对话**：支持持续对话，直到任务完成。用户可以随时输入新的需求，系统会根据需求继续生成和执行命令。
- **错误处理和重试**：如果命令执行失败，系统会自动重试，并在几次失败后反馈错误。

## 安装

### 1. 克隆项目

```bash
git clone https://github.com/toke648/AutoExecAI.git
cd AutoExecAI
```

### 2. 安装依赖

```bash
pip install -r requirements.txt
```

### 3. 设置 API 密钥

在使用该项目之前，您需要获取一个有效的 OpenAI API 密钥并将其配置在代码中。请访问 [OpenAI](https://platform.openai.com/account/api-keys) 获取您的 API 密钥。

将密钥添加到 `ai_thinker.py` 文件中的 `client = OpenAI(api_key="YOUR_API_KEY")` 位置，替换为您的密钥。

## 使用方式

### 启动程序

在终端中运行以下命令：

```bash
python main.py
```

或者运行
```bash
python auto_ai.py
```

### 交互式使用

程序将提示您输入需求，您可以描述您需要执行的任务，系统会分析您的请求并展示生成的命令：

```
Describe what you need to do (or type 'exit' to quit): 我想在Windows上创建一个名为test.txt的文件
Thinking... Please wait while I analyze your request.
Suggested command: echo. > test.txt
Do you want to execute this command? (yes/no):
```

- 如果您确认执行命令，系统会在后台执行并返回结果。
- 如果命令执行成功，您可以继续输入下一个需求，系统会根据新的需求生成并执行命令。
- 如果执行失败，系统会自动重试，直到达到最大重试次数。

### 示例

1. 用户输入需求：“创建一个test.txt文件”。
2. 系统生成命令并要求确认：“echo. > test.txt”。
3. 用户确认执行后，系统执行命令并显示结果。
4. 如果执行成功，继续等待下一次对话。

## 开发

### 1. 修改需求分析和命令生成

如果需要自定义需求分析和命令生成逻辑，可以修改 `ai_thinker.py` 文件中的 `thinking_step` 函数，该函数负责将用户输入转化为命令。

### 2. 改进命令执行流程

如果需要增加其他命令执行的方式或增加错误处理机制，可以修改 `main.py` 中的 `execute_command` 函数。

## 贡献

欢迎提出问题或贡献代码！请通过以下方式提交问题或请求功能：

- Fork 本仓库并提交 PR。
- 在 Issues 中报告 bug 或提出新特性请求。

## License

Apache License. See LICENSE for more information.
