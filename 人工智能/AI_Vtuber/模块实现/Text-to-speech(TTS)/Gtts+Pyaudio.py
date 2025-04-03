from gtts import gTTS
import pyaudio
import io

# 文本内容
text = "你好，世界！"

# 文本转语音
tts = gTTS(text=text, lang='zh-cn')

# 初始化音频播放器
p = pyaudio.PyAudio()

stream = p.open(format=p.get_format_from_width(tts.audio.sample_width),
                channels=tts.audio.channels,
                rate=tts.audio.frame_rate,
                output=True)

# 将音频写入流
buffer = io.BytesIO(tts.audio.get_wav_data())

# 播放音频
for data in iter(lambda: buffer.read(1024), b''):
    stream.write(data)

# 释放资源
stream.stop_stream()
stream.close()
p.terminate()