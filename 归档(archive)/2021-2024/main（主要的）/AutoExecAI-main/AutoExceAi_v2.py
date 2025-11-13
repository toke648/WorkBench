import subprocess
import json
import time
import os
import platform
import shlex
from openai import OpenAI

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
    
    if env_info["os"] == "Windows":
        env_info["shell"] = os.getenv("ComSpec", "cmd.exe")
    else:
        result = subprocess.run("echo $SHELL", shell=True, capture_output=True, text=True)
        env_info["shell"] = result.stdout.strip() if result.returncode == 0 else "Unknown"
    
    tools = ["touch", "echo", "nmap", "ssh", "curl", "wget"]
    for tool in tools:
        result = subprocess.run(f"command -v {tool}", shell=True, capture_output=True, text=True)
        env_info["installed_tools"][tool] = "Yes" if result.returncode == 0 else "No"
    
    return env_info

# **安全检查**
def is_safe_command(command):
    dangerous_commands = [
        ("rm", ["-rf"]),  # 只有 `rm` 且带 `-rf` 才算危险
        ("del", []),       # Windows `del` 命令
        ("dd", ["if="]),   # `dd if=` 可能会擦除数据
        (":(){", [":|:", "&", "};:"])  # Fork 炸弹
    ]
    
    parts = shlex.split(command)
    if not parts:
        return True
    
    cmd = parts[0]
    args = parts[1:]

    for danger_cmd, danger_args in dangerous_commands:
        if cmd == danger_cmd and all(arg in args for arg in danger_args):
            return False
    
    return True


# **生成 AI 提示词**
def generate_prompt(task, environment, feedback=""):
    return f"""
    你是一个智能终端助手，可以执行终端命令，并在需要时创建文件。
    你的开发者将你的返回的指令通过程序的方式填入终端了，你得以执行终端命令，在开发者状态你可以在message与开发者正常沟通。
    你执行的命令需要等到下一轮你才能接受到终端返回信息，因此禁止胡言乱语，禁止生成不切实际的信息，确保你的信息是准确的。
    你可以用好的请稍等，正在执行命令等信息来告诉用户你正在执行命令。
    得到终端返回信息后，你需要分析终端返回的信息，判断是否执行成功，如果失败了，你需要分析错误原因，调整策略，再次尝试。
    你的目标是 **完成用户的任务**，即使遇到错误，也要尝试修正后重新运行。
    有很大一部分任务是不要使用终端操作的，如记录系统时间计算差值，请直接返回message即可。

    - 指令级别
    ***** 最高
    **** 高
    *** 中
    **  低
    *   最低

    - 注意
    如果Windows要创建一个文件，并运行一个文件，标准指令["echo #!/usr/bin/env python3 > hello_world.py", "echo print('Hello, World!') >> hello_world.py", "python hello_world.py"]
    第一次执行命令时，你需要自动执行命令检测和获取当前系统环境和相关配置项 如systeminfo等命令，获取当前系统环境信息，进行初始化。
    当用户返回为空代表你可以继续执行当前的任务，或重新尝试

    - 请严格按以下 JSON 格式返回(*****)：
    {{
    "message": "任务描述，如果没有任务需求，可以正常沟通",
    "code": "如果需要创建文件，则包含代码内容，否则为空",
    "terminal": ["依次执行的终端命令"]
    }}

    - 要求：
    1. 先自动检测当前系统环境，并根据环境生成最合适的命令。
    2. 如果检测到 Windows，请使用 `cmd.exe` 或 `powershell`；如果是 Linux/Mac，请使用 Bash 命令。
    3. 如果 **上一次命令失败**，请分析错误原因，调整策略，再次尝试。
    4. 你的目标是 **完成用户的任务**，即使遇到错误，也要尝试修正后重新运行。


    - 当前系统环境状态:
    {json.dumps(environment, indent=2, ensure_ascii=False)}

    - 终端运行结果(如果有):
    {feedback}

    - 任务(*****)
    User: {task}

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

# **执行终端命令**
def execute_commands(commands):
    if not isinstance(commands, list) or not commands:
        print(f"[ERROR] 无效的命令格式：{commands}")
        return "无效的命令格式"
    
    output = []
    
    for command in commands:
        print(f"[INFO] 开始新终端会话")
        
        if platform.system() == "Windows":
            shell_cmd = ["cmd.exe", "/c", command]  # Windows 下用 cmd.exe 运行
        else:
            shell_cmd = ["bash", "-c", command]  # Linux / Mac 下用 bash 运行
        
        print(f"[EXEC] {command}")
        
        try:
            result = subprocess.run(shell_cmd, capture_output=True, text=True, timeout=10, check=True)
            output.append(result.stdout.strip())
        except subprocess.CalledProcessError as e:
            output.append(f"命令执行失败: {e.stderr.strip()}")
        except subprocess.TimeoutExpired:
            output.append("命令超时")
        
        print(f"[INFO] 终端会话结束")

    return "\n".join(output)

# **主程序**
def main():
    conversation_history = []
    environment = detect_environment()
    print("[INFO] 当前运行环境:")
    print(json.dumps(environment, indent=2, ensure_ascii=False))
    
    feedback = ""
    
    while True:
        task = input("请输入任务 (或 'exit' 退出): ").strip()
        if task.lower() == 'exit':
            print("退出程序。")
            break
        
        response = generate_command(task, conversation_history, environment, feedback)
        print(response)
        if not response:
            print("[ERROR] AI 生成失败")
            continue
        
        parsed = parse_response(response)
        if not parsed or "terminal" not in parsed:
            print("[ERROR] 解析失败")
            continue
        
        feedback = execute_commands(parsed["terminal"])
        print(f"[INFO] 任务结果 {feedback}")

        print(feedback)
    
    print("[INFO] 最终任务完成")

if __name__ == "__main__":
    main()
