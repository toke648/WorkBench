import requests
from playsound import playsound
url = 'http://cloud-vms.volcengineapi.com?Action=OpenCreateTts&Version=2022-01-01'  # 请根据实际API文档修改
headers = {
    'Authorization': 'dQxoR6t4LlXrqYhQ8o5-Rbf3fRP4-Uep',  # 替换为你的访问令牌
    'Content-Type': 'application/json'
}
data = {
    'text': '你好，世界！',
    'voice': 'BV001_streaming',  # 替换为所需的声音
    'output_format': 'mp3'  # 输出格式可以是mp3或其他支持的格式
}

response = requests.post(url, headers=headers, json=data)

if response.status_code == 200:
    with open('output.mp3', 'wb') as f:
        f.write(response.content)
    print("音频已保存为output.mp3")
else:
    print("请求失败:", response.text)

# 指定音频文件的路径
audio_file = 'output.mp3'  # 或者使用其他音频文件的路径

# 播放音频
playsound(audio_file)