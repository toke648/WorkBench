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
def generate_prompt(task, environment, feedback=""):
    return f"""
    你是一个智能终端助手，可以执行终端命令，并在需要时创建文件。
    你的开发者将你的返回的指令通过程序的方式填入终端了，你得以执行终端命令，在开发者状态你可以在message与开发者正常沟通。
    你执行的命令需要等到下一轮你才能接受到终端返回信息，因此禁止胡言乱语，禁止生成不切实际的信息，确保你的信息是准确的。
    你可以用好的请稍等，正在执行命令等信息来告诉用户你正在执行命令。
    得到终端返回信息后，你需要分析终端返回的信息，判断是否执行成功，如果失败了，你需要分析错误原因，调整策略，再次尝试。
    你的目标是 **完成用户的任务**，即使遇到错误，也要尝试修正后重新运行。

    第一次执行命令时，你需要自动执行命令检测和获取当前系统环境和相关配置项 如systeminfo、当前路径、用户名、当前路径下的内容、网络环境等命令，获取当前系统环境信息，进行初始化。
    并且在之后的每一次移动路径都要从新读取当前路径，自动获取当前路径和路径下的内容。

    请严格按以下 JSON 格式返回：
    {{
    "message": "任务描述，如果没有任务需求，可以正常沟通",
    "code": "如果需要创建文件，则包含代码内容，否则为空",
    "terminal": ["依次执行的终端命令"]
    }}
    - 要求：
    1. 先自动检测当前系统环境，并根据环境生成最合适的命令。
    2. 如果检测到 Windows，请使用 `cmd.exe` 或 `powershell`；如果是 Linux/Mac，请使用 Bash 命令。
    3. 如果 **上一次命令失败**，请分析错误原因，调整策略，再次尝试。

    - 当前系统环境状态:
    {json.dumps(environment, indent=2, ensure_ascii=False)}

    - 上一次终端返回信息(如果有):
    {feedback}

    任务:
    {task}

    - 某用户使用后的反馈：你马，不要瞎搞，不要突然写一堆指令，介绍功能写在message里就够了，我页面突然弹出来一堆东西。
    """

# **调用 AI 生成指令**
def generate_command(task, conversation_history, environment, feedback="", retries=3):
    conversation_history.append({'role': 'user', 'content': generate_prompt(task, environment, feedback)})
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
    command_str = " && ".join(commands)
    # for command in commands:
    print(f"[EXEC] {command_str}")
    try:
        result = subprocess.run(command_str, shell=True, capture_output=True, text=True, timeout=10)
        cmmand_output = result.stdout.strip()
        print(f"[INFO] 终端返回信息: {cmmand_output}")
        return cmmand_output
    except subprocess.TimeoutExpired:
        print("[ERROR] 命令超时")
        return "命令超时"
# **检查命令是否安全，避免危险命令**
def is_safe_command(command):
    blacklisted = ["rm -rf", "dd if=", ":(){ :|: & };:"]
    return not any(blk in command for blk in blacklisted)
# **主程序**
def main():
    conversation_history = []

    # **启动时检测环境**
    environment = detect_environment()
    print("[INFO] 当前运行环境:")
    print(json.dumps(environment, indent=2, ensure_ascii=False))  # **打印环境信息**

    # 初始化feedback为空
    feedback = ""

    while True:
        task = input("请输入任务 (或 'exit' 退出): ").strip()

        if task.lower() == 'exit':
            print("退出程序。")
            break

        max_attempts = 3  # 允许最多 3 次自动修正

        # 使用上次反馈作为参数传入，并将反馈清空，只保留最新的反馈
        response = generate_command(task, conversation_history, environment, feedback)
        if not response:
            print("[ERROR] AI 生成失败")
        
        try:
            parsed = parse_response(response)  # 解析 JSON
            if not parsed or "terminal" not in parsed:
                print("[ERROR] 解析失败")
        except Exception as e:
            print(f"[ERROR] 解析失败: {e}")

        # **执行终端命令**
        if parsed["terminal"]:
            feedback = execute_commands(parsed["terminal"])

        # 如果任务成功，则跳出
        if "ERROR" not in feedback:
            print("[INFO] 任务成功")
        else:
            print(f"[RETRY] AI 发现错误: {feedback}，正在修正...")

    print("[INFO] 最终任务完成")

if __name__ == "__main__":
    main()
