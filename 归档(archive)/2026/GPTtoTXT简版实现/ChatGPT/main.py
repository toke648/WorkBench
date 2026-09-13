import zipfile
import json
import os

def node_Selector(mapping: dict):
    """
    从 ChatGpt 的 mapping 树结构中提取最终采用的对话路径
    处理逻辑：
    1.从根节点（parent=None）开始
    2.遇到多个子节点（重新生成），选create_time最新的
    3.跳过 message 为 None 的节点
    """

    # 构建父子关系
    children_map = {}
    for node_id, node in mapping.items():
        parent_id = node.get('parent')
        if parent_id:
            children_map.setdefault(parent_id, []).append(node_id)
    
    # 找到根节点
    current_id = None
    for node_id, node in mapping.items():
        if node.get('parent') is None:
            current_id = node_id
            break
    
    # 沿树向下走
    selected_messages = []
    while current_id and current_id in mapping:
        node = mapping[current_id]
        msg = node.get('message')
        
        # 关键：只处理有消息的节点
        if (msg is not None) and (isinstance(msg, dict)) and ('content' in msg):
            parts = msg['content'].get('parts', [])
            if parts:
                role = msg.get('author', {}).get('role', 'unknown')
                if role == 'user': # 仅获取用户消息，如果需要获取assistant 和 system 消息，这句删掉即可
                    selected_messages.append({
                        'content': f"{[role]}: {parts[0]}",
                        'create_time': msg.get('create_time') or 0,
                        'update_time': msg.get('update_time') or 0,
                        'role': role
                    })
        
        # 选择下一个节点（处理重新生成）
        children = children_map.get(current_id, [])
        if children:
            # 收集所有子节点的时间
            children_with_time = []
            for child_id in children:
                child_node = mapping.get(child_id)
                if child_node:
                    child_msg = child_node.get('message')
                    child_time = 0
                    if child_msg and isinstance(child_msg, dict):  # isinstance(child_msg, dict) 确保是字典类型
                        child_time = child_msg.get('create_time', 0)
                    children_with_time.append((child_id, child_time))
            
            # 按时间排序，选择最新的
            if children_with_time:
                children_with_time.sort(key=lambda x: x[1])
                current_id = children_with_time[-1][0]
            else:
                current_id = None
        else:
            current_id = None

    return selected_messages
    

ZIP_FILE = './73408963e57d55b4bf934a001213d795a2a045b8adb53eebe70356f6315a9bb4-2026-05-02-08-21-53-85b2be1acace42418f6990a2b2c0d4e8.zip'
OUTPUT_DIR = './gptchat_data'

os.makedirs(OUTPUT_DIR, exist_ok=True)
    
data = []

# Step 1: 读取ZIP文件中的JSON文件
with zipfile.ZipFile(ZIP_FILE, 'r') as zf:
    for filename in zf.namelist():
        if filename.startswith('conversations-') and filename.endswith('.json'):
            # 使用extend()方法合并数据列表，extend()方法会自动将列表中的元素添加到新的列表中，和append()方法不同，
            # append()方法会创建一个新的列表，将元素添加到该列表中，并返回该列表。
            data.extend(json.load(zf.open(filename))) 


def main():
    # Step 2: 遍历每个对话
    for conv in data:
        title = conv.get('title', 'untitled')
        safe_title = title.replace('/', '_').replace('\\', '_')
        
        mapping = conv.get('mapping', {})

        # Step 3: 节点选择
        selected_messages = node_Selector(mapping)
        
        # Step 4: 保存文件
        if selected_messages:
            selected_messages.sort(key=lambda x: x.get('create_time', 0))
            
            outfile = f"{OUTPUT_DIR}/{selected_messages[0]['create_time']}_{safe_title}.txt"
            with open(outfile, 'w', encoding='utf-8') as f:
                f.write(f"标题: {title}\n")
                f.write(f"ID: {conv.get('id', '')}\n")
                f.write(f"创建时间: {conv.get('create_time', '')}\n")
                f.write(f"更新时间: {conv.get('update_time', '')}\n")
                f.write("="*60 + "\n\n")
                
                for msg in selected_messages:
                    f.write(msg['content'] + "\n\n")
            print(f"✓ {title}")

if __name__ == "__main__":
    main()
    print(f"\n✅ 完成！共保存 {len(data)} 个对话到 {OUTPUT_DIR}/")