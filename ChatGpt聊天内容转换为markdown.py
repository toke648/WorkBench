"""
食用方法
在ChatGpt界面Ctrl+A全选，复制下来后直接黏贴到text中。
运行本程序，将格式化后的文本保存为output.txt。

复制输出文件到剪贴板，即可食用
Ciallo～(∠・ω< )⌒☆

什么做成可视化程序打包成.exe？下次一定，暂时不感兴趣
"""

import os

def format_and_save(text, filename="output.txt", windows_notepad=False):
    sep = "\r\n" if windows_notepad else "\n"
    lines = text.splitlines()
    blocks = []
    i = 0
    speakers = ("你說：", "ChatGPT 說：")

    while i < len(lines):
        line = lines[i].strip()
        if not line:
            i += 1
            continue

        if line in speakers:
            label = line
            i += 1
            # 收集当前标签下的所有内容行，直到下一个标签或 EOF
            content = []
            while i < len(lines) and lines[i].strip() not in speakers:
                content.append(lines[i])
                i += 1

            block = [
                
                "",              # 空行
                "###" + label,   # 带 ###
                ""               # 空行
            ]
            # 保留内容原有换行（去掉首尾空行）
            for c in content:
                if c.strip() != "":
                    block.append(c)
            block.extend(["", "---"])  # 结尾空行 + 分隔线
            blocks.append(sep.join(block))
        else:
            # 普通说明段落，直到下一个标签或空行
            paragraph = []
            while i < len(lines) and lines[i].strip() not in speakers:
                if lines[i].strip() == "":
                    i += 1
                    break
                paragraph.append(lines[i])
                i += 1
            block = ["---", "", *paragraph, "", "---"]
            blocks.append(sep.join(block))

    # 每个块之间用一个空行分隔，文件末尾加一个换行
    output = (sep*2).join(blocks) + sep
    with open(filename, "w", encoding="utf-8", newline="") as f:
        f.write(output)

    print("Saved:", os.path.abspath(filename))


text = """
跳至內容
聊天歷程紀錄


No file chosenNo file chosen
ChatGPT 可能會出錯。請查核重要資訊。

"""

# 使用示例
format_and_save(text, filename="output.txt", windows_notepad=False) # 保存为Markdown格式 // windows_notepad=True: 保存为Notepad格式
