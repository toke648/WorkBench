from playsound import playsound
import edge_tts
import asyncio
import idna

TEXT = ""
# 文本输入路径可自定义
with open('wenzi.txt', 'rb') as f:
    data = f.read()
    TEXT = data.decode('utf-8')
print(TEXT)
# 以下是可选的声音：选择一个即可
# voice = 'zh-CN-XiaoxiaoNeural'
# voice = 'zh-CN-XiaoyiNeural'
voice = 'en-US-AvaNeural'
# voice = 'zh-CN-YunjianNeural'
# voice = 'zh-CN-YunxiNeural'
# voice = 'zh-CN-YunxiaNeural'
# voice = 'zh-CN-YunyangNeural'

# mp3音频输出路径可自定义
output = 'C:\\Users\\16673\\Desktop\\yuyin4.mp3'
rate = '-15%'  # 音速调整：带+或-号，注意：0%必须写为+0%
volume = '+50%' # 音调调整：带+或-号，注意：0%必须写为+0%

async def my_function():
    tts = edge_tts.Communicate(text=TEXT, voice=voice, rate=rate, volume=volume)
    await tts.save(output)


if __name__ == '__main__':
    asyncio.run(my_function())

    audio_file_path = 'C:\\Users\\16673\\Desktop\\yuyin4.mp3'

    playsound(audio_file_path)

