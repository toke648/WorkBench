import zipfile
import json
import os

# 配置
ZIP_FILE = './73408963e57d55b4bf934a001213d795a2a045b8adb53eebe70356f6315a9bb4-2026-05-02-08-21-53-85b2be1acace42418f6990a2b2c0d4e8.zip'  # 改成你的zip文件路径
OUTPUT_DIR = './chatgpt_user_chats'

os.makedirs(OUTPUT_DIR, exist_ok=True)

# 提取并保存
# STEP 1: 获取所有对话文件
with zipfile.ZipFile(ZIP_FILE, 'r') as zf:
    for filename in zf.namelist():
        if filename.startswith('conversations-') and filename.endswith('.json'):
            data = json.load(zf.open(filename))
            
            # STEP 2: 数据处理
            for conv in data:
                # 清洗标题，避免标题中的特殊字符，导致文件名无效
                title = conv.get('title', 'untitled')
                safe_title = title.replace('/', '_').replace('\\', '_')

                # 获取存储消息的mapping结构
                mapping = conv.get('mapping', {})

                children_map = {}

                # 找出每个节点的所有子节点
                for node_id, node in mapping.items():
                    parent_id = node.get('parent', '')
                    if parent_id:
                        # 添加子节点, setdefault()方法用于在字典中设置键值对
                        # 如果键已经存在，则返回该键对应的值，如果键不存在，则创建该键并返回None
                        # children_map.setdefault(parent_id, []).append(node_id)  
                        children_map.setdefault(parent_id, []).append(node_id)  

                # 选择正确的路径（深度优先或广度优先选择最后一个回答）
                selected_messages = []
                current_id = None # 当前节点的ID，默认为None

                # 找到根节点（parent为None的节点）
                for node_id, node in mapping.items():
                    if node.get('parent') is None:
                        current_id = node_id
                        break

                # 沿着树向下走，每次如果有多个子节点，选择最后一个（最新的回答）
                while current_id and current_id in mapping:
                    node = mapping[current_id]
                    msg = node.get('message')

                    if msg and 'content' in msg:
                        part = msg['content'].get('parts', [])
                        if part:
                            role = msg.get('author', {}).get('role', 'unknown')
                            if role == 'user':
                                selected_messages.append({
                                    'content': f"{role}: {part[0]}",
                                    'create_time': msg.get('create_time') or 0,
                                    'update_time': msg.get('update_time') or 0,
                                    'parent' : node.get('parent', ''),
                                    'node_id' : current_id
                                })

                    # 找到下一个节点：如果有子节点，选择最新的（排序取最后一个）
                    children = children_map.get(current_id, [])
                    if children: # 如果有子节点
                        # create_time排序，选择最新的
                        children_with_time = []
                        for child_id in children: # 遍历所有子节点
                            child_node = mapping.get(child_id)
                            child_msg = child_node.get('message')  if child_node else None
                            child_time = child_msg.get('create_time', 0) if child_msg else 0

                        # 对子节点进行排序，选择最新的
                        children_with_time.sort(key=lambda x: x[1])
                        # 获取子节点，也就是最新创建的ID（即最后一个元素）
                        current_id = children_with_time[-1][0] if children_with_time else None
                    else: # 如果没有子节点
                        current_id = None

                if selected_messages:
                    # 按时间排序
                    selected_messages.sort(key=lambda x: x.get('create_time', 0))

                    # STEP 3: 保存文件
                    # 生成文件名
                    outfile = f"{OUTPUT_DIR}/{selected_messages[0]['create_time']}_{safe_title}.txt"

                    with open(outfile, 'w', encoding='utf-8') as f:
                        f.write(f"标题: {title}\n")
                        f.write(f"ID: {conv.get('id', '')}\n")
                        f.write(f"创建时间: {selected_messages[0]['create_time']}\n")
                        f.write(f"更新时间: {selected_messages[0]['update_time']}\n")
                        f.write("="*60 + "\n\n")

                        # 遍历所有消息，保存消息内容
                        for msg in selected_messages:
                            f.write(msg['content'] + "\n\n")
                    print(f"✓ {title}")


                # path = []
                # path.append({
                #     'current_id': current_id,
                #     'len': len(children_map),
                # })

                # print(f"根节点ID: {current_id}")
                # print(f"子节点数量: {len(children_map)}")

                # break




                # 选择正确的路径（深度优先）

                # # 提取消息
                # messages = []
                # for node_id, node in mapping.items():
                #     msg = node.get('message')
                #     if msg and 'content' in msg:
                #         parts = msg['content'].get('parts', [])
                #         if parts:
                #             role = msg.get('author', {}).get('role', 'unknown') # 获取消息的角色（默认为'unknown'，可选'system'、'assistant'、'user'）
                #             if role == 'user': # 如果是'user'角色，则只保存第一部分（即消息内容）
                #                 messages.append({
                #                      'content': f"{role}: {parts[0]}",
                #                      'create_time': msg.get('create_time') or 0,
                #                      'update_time': msg.get('update_time') or 0,
                #                     })
                                

                # messages.sort(key=lambda x: x.get('create_time', 0)) # 按时间排序
                

                # if messages:
                #     with open(f"{OUTPUT_DIR}/{messages[0]['create_time']}_{safe_title}.txt", 'w', encoding='utf-8') as f:
                #         f.write(f"标题: {title}\n")
                #         f.write(f"ID: {conv.get('id', '')}\n")
                #         f.write(f"创建时间: {conv.get('create_time', '')}\n\n")
                #         f.write("\n\n".join([msg['content'] for msg in messages]))
                #     print(f"✓ {title}")