import edge_tts
from playsound import playsound
import asyncio
from pyarrow import duration

# async await 异步并行操作
async def pronunciation(sound):
    sound = str(sound)
    print(sound)

    voice = 'zh-CN-XiaoxiaoNeural'

    tts = edge_tts.Communicate(text=sound, voice=voice, rate=rate, volume=volume)
    await  tts.save(output)


if __name__ == '__main__':
    text = ['你好', ",", '欢迎', '光临']

    # mp3音频输出路径可自定义
    output = 'C:\\Users\\16673\\Desktop\\yuyin4.mp3'
    rate = '-2%'  # 音速调整
    volume = '+50%'  # 音速调整：带+或-号，注意：0%必须写成+0%

    for i in text:
        asyncio.run(pronunciation(i))

        playsound(output)


# import edge_tts
# from playsound import playsound
# import asyncio
#
# # async await 异步并行操作
# async def pronunciation(sound):
#     sound = str(sound)
#     print(sound)
#
#     voice = 'zh-CN-XiaoxiaoNeural'
#     output = 'C:\\Users\\16673\\Desktop\\input.mp3'  # 每次生成音频的路径
#
#     # 生成音频
#     tts = edge_tts.Communicate(text=sound, voice=voice, rate=rate, volume=volume)
#     await tts.save(output)
#
#     # 播放音频
#     playsound(output)
#
# if __name__ == '__main__':
#     text = ['你好', ",", '欢迎', '光临']
#
#     # 音速和音量调整
#     rate = '-2%'  # 音速调整
#     volume = '+50%'  # 音量调整：带+或-号，注意：0%必须写成+0%
#
#     # 创建异步任务并运行
#     for i in text:
#         asyncio.run(pronunciation(i))


# import edge_tts
# from playsound import playsound
# import asyncio
#
# # async await 异步并行操作
# async def pronunciation(text, voice, rate, volume, output):
#     print(f"Generating speech for: {text}")
#
#     # 生成音频
#     tts = edge_tts.Communicate(text=text, voice=voice, rate=rate, volume=volume)
#     await tts.save(output)
#
#     # 播放音频
#     playsound(output)
#
# async def main():
#     # 设置文本和参数
#     text = ['你好', '，', '欢迎', '光临', '这是一段长文章的例子。']
#     voice = 'zh-CN-XiaoxiaoNeural'
#     rate = '-2%'  # 音速调整
#     volume = '+50%'  # 音量调整
#     output = 'C:\\Users\\16673\\Desktop\\input.mp3'  # mp3音频输出路径
#
#     # 为每个文本生成语音
#     for i in text:
#         await pronunciation(i, voice, rate, volume, output)
#
# if __name__ == '__main__':
#     asyncio.run(main())


# import edge_tts
# import asyncio
# import os
# import pygame
#
# # 初始化pygame
# pygame.mixer.init()
#
# # 异步生成语音
# async def generate_speech(text, voice, rate, volume, output):
#     print(f"Generating speech for: {text}")
#
#     # 生成音频
#     tts = edge_tts.Communicate(text=text, voice=voice, rate=rate, volume=volume)
#     await tts.save(output)
#
#     # 播放音频
#     pygame.mixer.music.load(output)
#     pygame.mixer.music.play()
#
#     # 等待音频播放完成
#     while pygame.mixer.music.get_busy():
#         await asyncio.sleep(0.1)  # 每0.1秒检查一次音频是否播放完成
#
# async def main():
#     # 设置文本和参数
#     text = [
#         '你好，',
#         '欢迎光临这是一段长文章的例子。',
#         '这段文章用于演示如何逐步生成和播放语音。',
#         '希望这个示例对你有帮助。'
#     ]
#     voice = 'zh-CN-XiaoxiaoNeural'
#     rate = '-2%'  # 音速调整
#     volume = '+50%'  # 音量调整
#     output = 'C:\\Users\\16673\\Desktop\\input.mp3'  # mp3音频输出路径
#
#     # 为每个文本生成语音
#     for i in text:
#         await generate_speech(i, voice, rate, volume, output)
#
# if __name__ == '__main__':
#     asyncio.run(main())



# import edge_tts
# import asyncio
# import os
# import pygame
# import tempfile
#
# # 初始化pygame
# pygame.mixer.init()
#
# # 异步生成语音
# async def generate_speech(text, voice, rate, volume):
#     print(f"Generating speech for: {text}")
#
#     # 在临时文件夹中创建音频文件
#     output = tempfile.NamedTemporaryFile(delete=False, suffix='.mp3').name
#
#     # 生成音频
#     tts = edge_tts.Communicate(text=text, voice=voice, rate=rate, volume=volume)
#     await tts.save(output)
#
#     # 播放音频
#     pygame.mixer.music.load(output)
#     pygame.mixer.music.play()
#
#     # 等待音频播放完成
#     while pygame.mixer.music.get_busy():
#         await asyncio.sleep(0.1)  # 每0.1秒检查一次音频是否播放完成
#
# async def main():
#     # 设置文本和参数
#     text = [
#         '你好，',
#         '欢迎光临这是一段长文章的例子。',
#         '这段文章用于演示如何逐步生成和播放语音。',
#         '希望这个示例对你有帮助。'
#     ]
#     voice = 'zh-CN-XiaoxiaoNeural'
#     rate = '-2%'  # 音速调整
#     volume = '+50%'  # 音量调整
#
#     # 为每个文本生成语音
#     for i in text:
#         await generate_speech(i, voice, rate, volume)
#
# if __name__ == '__main__':
#     asyncio.run(main())


# import edge_tts
# import asyncio
# import os
# import pygame
# from pydub import AudioSegment
# from pydub.playback import play
#
# # 初始化pygame
# pygame.mixer.init()
#
# # 异步生成语音
# async def generate_speech(text, voice, rate, volume):
#     print(f"Generating speech for: {text}")
#
#     # 生成音频
#     tts = edge_tts.Communicate(text=text, voice=voice, rate=rate, volume=volume)
#     output = 'C:\\Users\\16673\\Desktop\\yuyin.mp3'
#     await tts.save(output)
#
#     return output
#
# async def main():
#     # 设置文本和参数
#     full_text = (
#         '你好，欢迎光临这是一段长文章的例子。'
#         '这段文章用于演示如何逐步生成和播放语音。'
#         '希望这个示例对你有帮助。'
#     )
#     voice = 'zh-CN-XiaoxiaoNeural'
#     rate = '-2%'  # 音速调整
#     volume = '+50%'  # 音量调整
#
#     # 生成音频
#     audio_path = await generate_speech(full_text, voice, rate, volume)
#
#     # 使用pydub播放音频
#     audio = AudioSegment.from_file(audio_path)
#     play(audio)
#
# if __name__ == '__main__':
#     asyncio.run(main())


# import edge_tts
# import asyncio
# import pygame
#
# # 初始化pygame
# pygame.mixer.init()
#
#
# # 异步生成语音
# async def generate_speech(text, voice, rate, volume):
#     print(f"Generating speech for: {text}")
#
#     # 生成音频
#     tts = edge_tts.Communicate(text=text, voice=voice, rate=rate, volume=volume)
#     output = 'C:\\Users\\16673\\Desktop\\yuyin.mp3'  # 确保路径可写
#     await tts.save(output)
#
#     # 播放音频
#     pygame.mixer.music.load(output)
#     pygame.mixer.music.play()
#
#     # 等待音频播放完成
#     while pygame.mixer.music.get_busy():
#         await asyncio.sleep(0.1)  # 每0.1秒检查一次音频是否播放完成
#
#
# # 模拟异步文本生成
# async def text_generation():
#     texts = [
#         '你好，',
#         '欢迎光临这是一段长文章的例子。',
#         '这段文章用于演示如何逐步生成和播放语音。',
#         '希望这个示例对你有帮助。'
#     ]
#
#     for text in texts:
#         await generate_speech(text, 'zh-CN-XiaoxiaoNeural', '-2%', '+50%')
#         await asyncio.sleep(0.5)  # 可以根据需要调整延迟
#
#
# async def main():
#     await text_generation()
#
#
# if __name__ == '__main__':
#     asyncio.run(main())


# import edge_tts
# import asyncio
# import pygame
# import tempfile
#
# # 初始化pygame
# pygame.mixer.init()
#
#
# # 异步生成语音
# async def generate_speech(text, voice, rate, volume):
#     print(f"Generating speech for: {text}")
#
#     # 创建临时音频文件
#     with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as temp_file:
#         output = temp_file.name
#
#     # 生成音频
#     tts = edge_tts.Communicate(text=text, voice=voice, rate=rate, volume=volume)
#     await tts.save(output)
#
#     # 播放音频
#     pygame.mixer.music.load(output)
#     pygame.mixer.music.play()
#
#     # 等待音频播放完成
#     while pygame.mixer.music.get_busy():
#         await asyncio.sleep(0.1)  # 每0.1秒检查一次音频是否播放完成
#
#
# async def text_generation():
#     texts = [
#         '你好，',
#         '欢迎光临这是一段长文章的例子。',
#         '这段文章用于演示如何逐步生成和播放语音。',
#         '希望这个示例对你有帮助。'
#     ]
#
#     for text in texts:
#         await generate_speech(text, 'zh-CN-XiaoxiaoNeural', '-2%', '+50%')
#         await asyncio.sleep(0.8)  # 设置0.8秒的时间间隔
#
#
# async def main():
#     await text_generation()
#
#
# if __name__ == '__main__':
#     asyncio.run(main())


# import edge_tts
# import asyncio
# import sounddevice as sd
# import numpy as np
# import tempfile
#
#
# # 异步生成语音
# async def generate_speech(text, voice, rate, volume):
#     print(f"Generating speech for: {text}")
#
#     # 创建临时音频文件
#     with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as temp_file:
#         output = temp_file.name
#
#     # 生成音频
#     tts = edge_tts.Communicate(text=text, voice=voice, rate=rate, volume=volume)
#     await tts.save(output)
#
#     # 读取音频文件
#     data, samplerate = sf.read(output)
#
#     # 播放音频
#     sd.play(data, samplerate)
#     sd.wait()  # 等待音频播放完成
#
#
# async def text_generation():
#     texts = [
#         '你好，',
#         '欢迎光临这是一段长文章的例子。',
#         '这段文章用于演示如何逐步生成和播放语音。',
#         '希望这个示例对你有帮助。'
#     ]
#
#     for text in texts:
#         await generate_speech(text, 'zh-CN-XiaoxiaoNeural', '-2%', '+50%')
#         await asyncio.sleep(0.5)  # 减少时间间隔到0.5秒
#
#
# async def main():
#     await text_generation()
#
#
# if __name__ == '__main__':
#     asyncio.run(main())


# import edge_tts
# import asyncio
# import pygame
# import tempfile
#
# # 初始化pygame
# pygame.mixer.init()
#
# # 异步生成语音
# async def generate_speech(text, voice, rate, volume):
#     print(f"Generating speech for: {text}")
#
#     # 创建临时音频文件
#     with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as temp_file:
#         output = temp_file.name
#
#     # 生成音频
#     tts = edge_tts.Communicate(text=text, voice=voice, rate=rate, volume=volume)
#     await tts.save(output)
#
#     # 播放音频
#     pygame.mixer.music.load(output)
#     pygame.mixer.music.play()
#
#     # 等待音频播放完成
#     while pygame.mixer.music.get_busy():
#         await asyncio.sleep(0.1)  # 每0.1秒检查一次音频是否播放完成
#
# async def text_generation():
#     texts = [
#         '你好，',
#         '欢迎光临这是一段长文章的例子。',
#         '这段文章用于演示如何逐步生成和播放语音。',
#         '希望这个示例对你有帮助。'
#     ]
#
#     tasks = []  # 存储生成任务
#     for text in texts:
#         task = generate_speech(text, 'zh-CN-XiaoxiaoNeural', '-2%', '+50%')
#         tasks.append(task)
#         await asyncio.sleep(0.1)  # 生成下一段语音前等待0.1秒
#
#     await asyncio.gather(*tasks)  # 等待所有任务完成
#
# async def main():
#     await text_generation()
#
# if __name__ == '__main__':
#     asyncio.run(main())