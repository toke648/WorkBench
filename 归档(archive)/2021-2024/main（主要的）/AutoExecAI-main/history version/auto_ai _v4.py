import subprocess
import json
import time
import os
import platform
from openai import OpenAI

# 读取 API 密钥
API_KEY = os.getenv("OPENAI_API_KEY", "63f72c10e53241509645b29dfc5f06c8.x0RKmLAYwR7uJMsr")
BASE_URL = "https://open.bigmodel.cn/api/paas/v4/"

# **检测当前运行环境**
def detect_environment():
    env_info = {
        "os": platform.system(),
        "os_version": platform.release(),
        "python_version": platform.python_version(),
        "shell": os.getenv("SHELL", "Unknown"),
        "installed_tools": {}
    }

    # **动态检测 shell**
    if env_info["os"] == "Windows":
        env_info["shell"] = os.getenv("ComSpec", "cmd.exe")
    else:
        result = subprocess.run("echo $SHELL", shell=True, capture_output=True, text=True)
        env_info["shell"] = result.stdout.strip() if result.returncode == 0 else "Unknown"

    # **检测常用工具**
    tools = ["touch", "echo", "nmap", "ssh", "curl", "wget"]
    for tool in tools:
        result = subprocess.run(f"command -v {tool}", shell=True, capture_output=True, text=True)
        env_info["installed_tools"][tool] = "Yes" if result.returncode == 0 else "No"

    return env_info

# **生成 AI 提示词**
def generate_prompt(task, environment, error_feedback=""):
    return f"""
你是一个智能终端助手，可以执行终端命令，并在需要时创建文件。
你的目标是 **确保命令能够成功执行**，即使遇到错误，也要尝试修正后重新运行。
请严格按以下 JSON 格式返回：
{{
  "message": "任务描述",
  "code": "如果需要创建文件，则包含代码内容，否则为空",
  "terminal": ["依次执行的终端命令"]
}}
要求：
1. 先自动检测当前系统环境，并根据环境生成最合适的命令。
2. 如果检测到 Windows，请使用 `cmd.exe` 或 `powershell`；如果是 Linux/Mac，请使用 Bash 命令。
3. 如果 **上一次命令失败**，请分析错误原因，调整策略，再次尝试。

### 当前系统环境:
{json.dumps(environment, indent=2, ensure_ascii=False)}

### 上一次错误信息（如果有）:
{error_feedback}

任务:
{task}
"""

# **调用 AI 生成指令**
def generate_command(task, conversation_history, environment, error_feedback="", retries=3):
    conversation_history.append({'role': 'user', 'content': generate_prompt(task, environment, error_feedback)})
    client = OpenAI(api_key=API_KEY, base_url=BASE_URL)

    for attempt in range(retries):
        try:
            completion = client.chat.completions.create(
                model="GLM-4-Flash",
                messages=conversation_history
            )
            response = completion.choices[0].message.content
            print(f"[INFO] AI 响应: {response}")
            conversation_history.append({'role': 'assistant', 'content': response})
            return response
        except Exception as e:
            print(f"[ERROR] AI 调用失败 (尝试 {attempt + 1}): {e}")
            time.sleep(2)
    
    return None

# **解析 AI 生成的 JSON**
def parse_response(response):
    try:
        return json.loads(response)
    except json.JSONDecodeError:
        print("[ERROR] AI 响应格式错误")
        return None

# **执行终端命令，并提供反馈**
def execute_commands(commands):
    for cmd in commands:
        print(f"[EXEC] {cmd}")
        try:
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=10)
            if result.returncode != 0:
                error_msg = result.stderr.strip()
                print(f"[ERROR] 失败: {error_msg}")
                return error_msg, False
            print(f"[INFO] 成功: {result.stdout.strip()}")
        except subprocess.TimeoutExpired:
            print("[ERROR] 命令超时")
            return "命令超时", False
    return "[INFO] 成功", True

# **强化学习机制**
def feedback_based_retry(task, conversation_history, environment, error_feedback=""):
    max_attempts = 3  # 允许最多 3 次自动修正
    attempt = 0
    while attempt < max_attempts:
        # 根据任务生成命令
        response = generate_command(task, conversation_history, environment, error_feedback)
        if not response:
            print("[ERROR] AI 生成失败")
            break

        parsed = parse_response(response)
        if not parsed or "terminal" not in parsed:
            print("[ERROR] 解析失败")
            break

        print(json.dumps(parsed, indent=2, ensure_ascii=False))

        # 执行终端命令并获取反馈
        print(parsed["terminal"])
        if parsed["terminal"]:
            error_feedback, success = execute_commands(parsed["terminal"])

        if success:
            print("[INFO] 任务成功")
            return True  # 任务成功
        else:
            print(f"[RETRY] AI 发现错误: {error_feedback}，正在修正...")
            attempt += 1

    print("[ERROR] 任务失败")
    return False  # 任务失败

# **主程序**
def main():
    conversation_history = []

    # **启动时检测环境**
    environment = detect_environment()
    print("[INFO] 当前运行环境:")
    print(json.dumps(environment, indent=2, ensure_ascii=False))

    while True:
        task = input("请输入任务 (或 'exit' 退出): ").strip()

        if task.lower() == 'exit':
            print("退出程序。")
            break

        # **通过强化学习反馈机制重试任务**
        if not feedback_based_retry(task, conversation_history, environment):
            print("[ERROR] 任务失败，已达到最大重试次数")

if __name__ == "__main__":
    main()
