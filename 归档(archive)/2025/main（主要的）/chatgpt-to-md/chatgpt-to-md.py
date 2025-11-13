"""
食用方法

```
1. 运行: python change.py

2. 输入zip文件路径和输出目录:
zip文件路径: 个人主要项目（可直接使用）/ (输入zip文件的完整路径)
输出目录: 个人主要项目（可直接使用）/ (选填，默认当前目录下 chatgpt_output 文件夹)

3. 运行完成，会在指定目录下生成Markdown文件
```

Ciallo～(∠・ω< )⌒☆
什么做成可视化程序打包成.exe？下次一定，暂时不感兴趣
"""

import json
import zipfile
import os
from datetime import datetime
import re

def extract_and_convert(zip_path, output_dir):
    """从zip文件提取并转换ChatGPT对话为Markdown"""
    
    # 创建输出目录
    os.makedirs(output_dir, exist_ok=True)
    
    try:
        # 解压zip文件
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(output_dir)
        
        # 查找conversations.json
        json_path = os.path.join(output_dir, 'conversations.json')
        if not os.path.exists(json_path):
            # 可能在子目录中
            for root, dirs, files in os.walk(output_dir):
                if 'conversations.json' in files:
                    json_path = os.path.join(root, 'conversations.json')
                    break
        
        if not os.path.exists(json_path):
            print("错误: 在zip文件中找不到 conversations.json")
            return
        
        # 读取并解析JSON数据
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # 转换每个对话
        successful_conversions = 0
        for conversation in data:
            try:
                convert_single_conversation(conversation, output_dir)
                successful_conversions += 1
            except Exception as e:
                print(f"转换对话时出错: {e}")
                continue
        
        print(f"成功转换 {successful_conversions} 个对话")
        
    except Exception as e:
        print(f"处理过程中出错: {e}")

def convert_single_conversation(conversation, output_dir):
    """转换单个对话为Markdown"""
    
    # 获取对话标题
    title = conversation.get('title', '未命名对话')
    create_time = conversation.get('create_time')
    
    # 清理文件名中的非法字符
    safe_title = re.sub(r'[<>:"/\\|?*]', '_', title)
    if create_time:
        try:
            dt = datetime.fromtimestamp(create_time)
            timestamp = dt.strftime("%Y-%m-%d")
            filename = f"{timestamp}_{safe_title}.md"
        except:
            filename = f"{safe_title}.md"
    else:
        filename = f"{safe_title}.md"
    
    filepath = os.path.join(output_dir, filename)
    
    # 构建Markdown内容
    md_content = []
    
    # 添加YAML front matter
    md_content.append("---")
    md_content.append(f"title: {title}")
    if create_time:
        dt = datetime.fromtimestamp(create_time)
        md_content.append(f"date: {dt.strftime('%Y-%m-%d %H:%M:%S')}")
    md_content.append(f"source: ChatGPT Export")
    md_content.append("---\n")
    
    md_content.append(f"# {title}\n")
    
    # 提取并排序消息
    messages = []
    for key, value in conversation.get('mapping', {}).items():
        if value and 'message' in value and value['message']:
            msg = value['message']
            if msg.get('content') and msg.get('author'):
                role = msg['author']['role']
                content_parts = msg['content'].get('parts', [''])
                content = ''.join(content_parts) if content_parts else ''
                
                if content.strip():
                    # 获取时间戳用于排序
                    timestamp = msg.get('create_time') or 0
                    messages.append({
                        'timestamp': timestamp,
                        'role': role,
                        'content': content.strip()
                    })
    
    # 按时间排序
    messages.sort(key=lambda x: x['timestamp'])
    
    # 转换为Markdown
    for msg in messages:
        role = msg['role']
        content = msg['content']
        
        # 角色映射到显示名称
        role_display = {
            'user': '我',
            'assistant': 'ChatGPT', 
            'system': '系统',
            'tool': '工具'
        }.get(role, role)
        
        # 添加消息到Markdown
        md_content.append(f"## {role_display}")
        md_content.append("")
        md_content.append(content)
        md_content.append("")
    
    # 写入文件
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write('\n'.join(md_content))
    
    print(f"已创建: {filename}")

if __name__ == "__main__":
    zip_path = input("请输入zip文件路径: ").strip().strip('"')
    output_dir = input("请输入输出目录: ").strip().strip('"') or "./chatgpt_output"
    
    extract_and_convert(zip_path, output_dir)
    print("转换完成！")