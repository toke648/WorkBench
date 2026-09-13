import zipfile
import json
import os
import re

os.makedirs('./chatgpt_data', exist_ok=True)
path = './chatgpt_data'

def clean_filename(filename):
    """清理文件名中的非法字符"""
    # 首先移除或替换不可见字符和特殊字符
    cleaned = str(filename).replace('\n', '_').replace('\r', '_').replace('\t', '_')
    
    # 替换Windows不支持的文件名字符
    illegal_chars = r'[<>:"/\\|?*\[\]]'
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

def get_longest_path_from_root(mapping_dict):
    """
    从mapping字典中获取从根节点开始的最长路径
    """
    # 找到根节点
    root_id = None
    for key, value in mapping_dict.items():
        print(key, value.get('parent'))
        if value.get('parent') is None:
            root_id = key
            break
    
    if root_id is None:
        return []
    
    def dfs_path(node_id, visited):
        """深度优先搜索，返回从当前节点开始的最长路径"""
        if node_id in visited or node_id not in mapping_dict:
            return []
        
        visited.add(node_id)
        current_node = mapping_dict[node_id]
        
        # 获取当前节点的消息（如果有）
        current_messages = []
        if current_node.get('message'):
            for fragment in current_node['message'].get('fragments', []):
                content = fragment.get('content')
                if content is not None:
                    current_messages.append({
                        'type': fragment.get('type'),
                        'content': content,
                        'timestamp': current_node['message'].get('inserted_at'),
                        'model': current_node['message'].get('model'),
                        'node_id': node_id  # 添加节点ID用于调试
                    })
        
        # 获取所有子节点的最长路径
        children = current_node.get('children', [])
        longest_child_path = []
        
        for child_id in children:
            child_path = dfs_path(child_id, visited.copy())  # 使用副本避免影响其他分支
            if len(child_path) > len(longest_child_path):
                longest_child_path = child_path
        
        # 返回当前节点消息 + 最长子路径
        return current_messages + longest_child_path
    
    # 从根节点开始查找最长路径
    return dfs_path(root_id, set())

conversation_list = ['conversations-001.json', 'conversations-002.json', 'conversations-003.json', 'conversations-004.json', 'conversations-005.json', 'conversations-006.json', 'conversations-007.json', 'conversations-008.json', 'conversations-009.json', 'conversations-010.json', 'conversations-011.json', 'conversations-012.json']

def extract_formatted_chat_history():
    with zipfile.ZipFile('./73408963e57d55b4bf934a001213d795a2a045b8adb53eebe70356f6315a9bb4-2026-05-02-08-21-53-85b2be1acace42418f6990a2b2c0d4e8.zip', 'r') as zip_ref:
        for conversation in conversation_list:
            with zip_ref.open(conversation) as file:
                content = file.read()
                text_content = content.decode('utf-8')
                conversations = json.loads(text_content)

    all_chats = []
    
    for i, conversation in enumerate(conversations):
            
        print(conversation.get('title', '无标题'))
        print(conversation.get('id', '无ID'))

        chat_session = {
            'conversation_id': conversation['id'],
            'title': conversation['title'],
            'inserted_at': conversation.get('inserted_at', ''),  # 如果有就显示，否则为空
            "update_time": conversation.get('update_time', ''),
            'messages': []
        }
        
        # 获取从根节点开始的最长路径（最深的对话路径）
        # 正确传入整个mapping字典，而不是单个message内容
        # longest_path = get_longest_path_from_root(conversation['mapping'])
        # chat_session['messages'] = longest_path
        longest_path = get_longest_path_from_root(conversation['mapping'])
        chat_session['messages'] = longest_path
        
        all_chats.append(chat_session)
    
    return all_chats

# 使用示例
chats = extract_formatted_chat_history()

print(f"共 {len(chats)} 个对话")

for idx, chat in enumerate(chats):
    conv_title = chat["title"]
    conversation_id = chat["conversation_id"]
    conv_inserted_at = chat["inserted_at"][:10]
    print(f"对话 {idx+1}: {repr(conv_title)} {conversation_id}")
    print(f"消息总数: {len(chat['messages'])}")

    # 清理文件名
    clean_title = clean_filename(conv_title)
    filename = f"{path}/{conv_inserted_at} {clean_title}.txt"

    for msg_idx, msg in enumerate(chat['messages']):
        if msg_idx == 0:
            with open(filename, "w", encoding="utf-8") as f:
                f.write(f"### {conv_title}" + "\n")
                f.write(f"{conversation_id}" + "\n")
                f.write(f"`{msg['timestamp'][:10]}` {msg['model']}" + "\n")
        if msg['type'] == "REQUEST":
            with open(filename, "a", encoding="utf-8") as f:
                f.write("---")
                f.write(msg['content'] + "\n")

    
    print(f"已保存到文件 {filename}")
    print("-" * 50)