import subprocess
import json
import time
from openai import OpenAI

# 调用 AI 生成指令
def large_language_model(content, conversation_history, retries=3):
    conversation_history.append({'role': 'user', 'content': content})
    client = OpenAI(
        api_key="63f72c10e53241509645b29dfc5f06c8.x0RKmLAYwR7uJMsr",
        base_url="https://open.bigmodel.cn/api/paas/v4/",
    )
    for attempt in range(retries):
        try:
            completion = client.chat.completions.create(
                model="GLM-4-Flash",
                messages=conversation_history
            )
            data = json.loads(completion.model_dump_json())
            result = data['choices'][0]['message']['content']
            conversation_history.append({'role': 'assistant', 'content': result})
            return result
        except Exception as e:
            print(f"Attempt {attempt + 1} failed: {e}")
            if attempt < retries - 1:
                time.sleep(2)
            else:
                raise

# 提取格式化命令
def extract_command(response):
    start = response.find("### ")
    end = response.rfind(" ###")
    if start != -1 and end != -1 and start < end:
        return response[start + 4:end].strip()
    return None

# 执行命令并获取结果
def execute_command(command):
    print(f"Suggested command: {command}")
    confirm = input("Do you want to execute this command? (yes/no): ").strip().lower()
    if confirm != 'yes':
        print("Execution canceled by user.")
        return None, "User canceled execution."

    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print("Command executed successfully:")
            print(result.stdout)
            return result.stdout, None
        else:
            print(f"Error executing command: {result.stderr}")
            return None, result.stderr
    except Exception as e:
        print(f"Execution failed: {e}")
        return None, str(e)

# 主循环
def main():
    conversation_history = []
    while True:
        user_input = input("Describe what you need to do (or type 'exit' to quit): ").strip()
        
        # 如果用户输入 'exit'，则退出程序
        if user_input.lower() == 'exit':
            print("Exiting the program.")
            break

        response = large_language_model(
            f"Provide only a valid Windows command enclosed in '### code position ###' format. "
            f"Do NOT add explanations. Ensure the command works on Windows. "
            f"Task: {user_input}",
            conversation_history
        )
        command = extract_command(response)
        
        if not command or command == "code":
            print("Failed to extract a valid command from AI response. Retrying...")
            continue

        output, error = execute_command(command)

        # 若执行失败，将错误信息传回 AI，请求修正
        if error:
            user_input = f"The command failed with error: {error}. Please suggest a corrected command."
        else:
            print("Task completed successfully.")

if __name__ == "__main__":
    main()
