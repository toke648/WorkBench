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


text = open("个人主要项目（可直接使用）/text.txt", encoding="utf-8").read()

print("Text length:", len(text))

# 使用示例
format_and_save(text, filename="个人主要项目（可直接使用）/output.txt", windows_notepad=False) # 保存为Markdown格式 // windows_notepad=True: 保存为Notepad格式




# def format_chatgpt_to_markdown(text) -> str:
#     """
#     将 ChatGPT 的对话格式转换为 Markdown 格式。

#     参数：
#     text (str)：ChatGPT 的对话文本。

#     返回：
#     str：转换后的 Markdown 格式文本。
#     """
#     lines = text.splitlines()
#     speakers = ("你說：", "ChatGPT 說：")

#     print(lines)

    

#     return '0' # 占位符，实际实现请参考上面的代码块

# text = open("个人主要项目（可直接使用）/text.txt", encoding="utf-8").read()
# filename="output.txt"

# formatted_text = format_chatgpt_to_markdown(text)
# # with open(filename, "w", encoding="utf-8", newline="") as f:
# #     f.write(formatted_text)
# # print("Saved:", filename)