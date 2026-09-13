import zipfile
import json
import os
import re
import time

os.makedirs('./deepseek_data', exist_ok=True)
path = './deepseek_data'
def clean_filename(filename):
    """清理文件名中的非法字符"""
    # 首先移除或替换不可见字符和特殊字符
    # 处理换行符、制表符等
    cleaned = str(filename).replace('\n', '_').replace('\r', '_').replace('\t', '_')
    
    # 替换Windows不支持的文件名字符
    illegal_chars = r'[<>:"/\\|?*\[\]]'  # 添加了方括号
    cleaned = re.sub(illegal_chars, '_', cleaned)
    
    # 移除控制字符（ASCII 0-31）
    cleaned = ''.join(char for char in cleaned if ord(char) >= 32)
    
    # 确保文件名长度不超过255字符
    if len(cleaned) > 250:
        cleaned = cleaned[:250]
    
    # 确保文件名不为空
    if not cleaned.strip():
        cleaned = "unnamed_conversation"
    
    return cleaned.strip()

def extract_formatted_chat_history():
    with zipfile.ZipFile('./deepseek_data-2026-01-15.zip', 'r') as zip_ref:
        with zip_ref.open('conversations.json') as file:
            content = file.read()                       # 读取文件内容
            text_content = content.decode('utf-8')      # 解码文件内容
            conversations = json.loads(text_content)    # 解析JSON内容

    all_chats = []
    
    for i, conversation in enumerate(conversations[::-1]):
        chat_session = {
            'conversation_id': conversation['id'],      # 添加对话ID
            'title': conversation['title'],             # 添加对话标题
            'inserted_at': conversation['inserted_at'], # 添加插入时间
            "updated_at": conversation['updated_at'],   # 添加更新时间
            'messages': []                              # 添加消息列表
        }

        # print(conversation['mapping'].keys())
        # # 查看结构
        # print(conversation['mapping']['root'])
        
        # 收集此对话的所有消息
        for key, value in conversation['mapping'].items():
            conv_map_id = value.get('id')
            conv_map_parent = value.get('parent')
            conv_map_root = value.get('root')
            conv_map_children = value.get('children', [])
            
            print(f"查看结构；conv_map_id: {conv_map_id}, conv_map_parent: {conv_map_parent}, conv_map_root: {conv_map_root}, conv_map_children: {conv_map_children}")

            if value.get('message'):
                message = value['message']
                
                for fragment in message.get('fragments', []):           # 遍历消息中的片段
                    content = fragment.get('content')                   # 获取内容
                    if content is not None:                             # 只添加非 None 的内容
                        msg_entry = {
                            'type': fragment.get('type'),               # REQUEST or RESPONSE
                            'content': content,                         # 添加内容
                            'timestamp': message.get('inserted_at'),    # 添加插入时间
                            'model': message.get('model')               # 添加模型
                        }
                    chat_session['messages'].append(msg_entry)          # 将消息添加到上一个字典的messages列表中
                    # print(f"{conversation['id']}. [{msg_entry['type']}] {msg_entry['content'][:100]}...")
                    time.sleep(1)
        all_chats.append(chat_session)
    
    return all_chats

# 使用示例
chats = extract_formatted_chat_history()

# print(f"共 {len(chats)} 个对话")

# for idx, chat in enumerate(chats):
#     conv_title = chat["title"]
#     conv_inserted_at = chat["inserted_at"][:10]
#     print(f"对话 {idx+1}: {conv_title}")
#     print(f"消息总数: {len(chat['messages'])}")

#     # 清理文件名
#     clean_title = clean_filename(conv_title)
#     filename = f"{path}/{conv_inserted_at} {clean_title}.txt"

#     for i, msg in enumerate(chat['messages']):  # print(f"\n{i+1}. [{msg['type']}] {msg['content'][:100]}...")

#         if msg['type'] == "REQUEST":
#             with open(filename, "a", encoding="utf-8") as f:
#                 f.write(msg['content'] + "\n")
#     print(f"已保存到文件{filename}")

#         # # 只在第一次创建文件时写入头部信息
#         # if i == 0:
#         #     with open(f"{conv_inserted_at} {conv_title}.md", "w", encoding="utf-8") as f:
#         #         f.write(f"## {conv_title}\n")
#         #         f.write(f"`insert_time: {first_conversation['inserted_at']}`\n")
#         #         f.write(f"`update_time: {first_conversation['updated_at']}`\n")

#         # with open(f"{conv_inserted_at} {conv_title}.md", "a", encoding="utf-8") as f:
#         #     f.write(f"### " + msg['type'].replace("REQUEST", "User") + "\n")
#         #     if msg['type'] == "REQUEST":
#         #         f.write(f">{msg['content'].replace("REQUEST", "User")}\n")
#         #     elif msg['type'] == "RESPONSE":
#         #         f.write(f"```txt\n{msg['content'].replace("RESPONSE", "AI")}\n```\n")
            
#         #     f.write("\n")