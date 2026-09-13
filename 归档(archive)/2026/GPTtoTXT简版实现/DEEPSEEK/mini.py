import zipfile, json, os, re

ZIP_FILE = './deepseek_data-2026-05-05.zip'
OUTPUT_DIR = './deepseek_chats'

os.makedirs(OUTPUT_DIR, exist_ok=True)

with zipfile.ZipFile(ZIP_FILE, 'r') as zf:
    for filename in zf.namelist():
        if filename.endswith('.json'):
            data = json.load(zf.open(filename))
            conversations = data if isinstance(data, list) else [data]
            
            for conv in conversations:
                title = conv.get('title', 'untitled')
                safe_title = re.sub(r'[<>:"/\\|?*\[\]\{\}\n\r\t]', '_', title)[:200] # 限制长度
                
                messages = []
                for node_id, node in conv.get('mapping', {}).items():
                    msg = node.get('message', {})
                    if msg is None: continue # 跳过无消息的节点
                    for frag in msg.get('fragments', []):
                        content = frag.get('content', '')
                        if content:
                            frag_type = frag.get('type', '')
                            role = '用户' if frag_type == 'REQUEST' else '助手'
                            messages.append(f"[{role}]: {content}")
                
                if messages:
                    with open(f"{OUTPUT_DIR}/{safe_title}.txt", 'w', encoding='utf-8') as f:
                        f.write(f"标题: {title}\n")
                        f.write(f"ID: {conv.get('id', '')}\n\n")
                        f.write("\n\n".join(messages))
                    print(f"✓ {title}")