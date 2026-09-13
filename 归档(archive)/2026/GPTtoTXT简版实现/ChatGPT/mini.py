import zipfile
import json
import os

# 配置
ZIP_FILE = './73408963e57d55b4bf934a001213d795a2a045b8adb53eebe70356f6315a9bb4-2026-05-02-08-21-53-85b2be1acace42418f6990a2b2c0d4e8.zip'  # 改成你的zip文件路径
OUTPUT_DIR = './chatgpt_chats'

os.makedirs(OUTPUT_DIR, exist_ok=True)

# 提取并保存
with zipfile.ZipFile(ZIP_FILE, 'r') as zf:
    for filename in zf.namelist():
        if filename.startswith('conversations-') and filename.endswith('.json'):
            data = json.load(zf.open(filename))
            
            for conv in data:
                title = conv.get('title', 'untitled')
                safe_title = title.replace('/', '_').replace('\\', '_')
                
                # 提取消息
                messages = []
                for node_id, node in conv.get('mapping', {}).items():
                    msg = node.get('message')
                    if msg and 'content' in msg:
                        parts = msg['content'].get('parts', [])
                        if parts:
                            role = msg.get('author', {}).get('role', 'unknown')
                            messages.append(f"{role}: {parts[0]}")
                
                if messages:
                    with open(f"{OUTPUT_DIR}/{safe_title}.txt", 'w', encoding='utf-8') as f:
                        f.write(f"标题: {title}\n")
                        f.write(f"ID: {conv.get('id', '')}\n\n")
                        f.write("\n\n".join(messages))
                    print(f"✓ {title}")