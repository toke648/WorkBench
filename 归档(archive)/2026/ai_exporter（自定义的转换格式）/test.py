import zipfile
import json

with zipfile.ZipFile('./deepseek_data-2026-01-15.zip', 'r') as zip_ref:
    with zip_ref.open('conversations.json') as file:
        content = file.read()
        text_content = content.decode('utf-8')
        conversations = json.loads(text_content)
        print(len(conversations))

        # 遍历对话
        for i, conversation in enumerate(conversations[:1]):  # 只看第一个作为示例
            conv_id = conversation['id']
            conv_title = conversation['title']
            conv_time = conversation['inserted_at']
            conv_updated_time = conversation['updated_at']
            conv_mapping = conversation['mapping']
            
            print(f"=== 对话 {i+1} ===")
            print(f"ID: {conv_id}")
            print(f"标题: {conv_title}")
            print(f"创建时间: {conv_time}")
            print(f"更新时间: {conv_updated_time}")
            
            # 遍历 mapping 中的消息
            for key, value in conversation['mapping'].items():
                if value.get('message'):  # 确保 message 存在
                    message = value['message']                                  # 消息
                    massage_id = message.get('id', 'N/A')                       # 消息ID
                    message_model = message.get('model', 'N/A')                 # 模型
                    message_inserted_time = message.get('inserted_at', 'N/A')   # 插入时间
                                        
                    # 解析 fragments
                    fragments = message.get('fragments', [])                    # fragments

                    for fragment in fragments:
                        frag_type = fragment.get('type', 'N/A') # 用户输入
                        content = fragment.get('content', '') # 模型回复
                        print("frag_type: \n", frag_type)
                        print("content: \n", content)
                    
                    print("---")

