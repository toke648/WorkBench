import keyboard
import pyaudio, wave
from tqdm import tqdm


def record(filename):
    p = pyaudio.PyAudio()  # 实例化pyaudio对象

    SECONDS = 5  # 时长(秒)
    FORMAT = pyaudio.paInt16  # 音频格式，即采样位深
    CHANNELS = 1  # 通道数
    RATE = 16000  # 采样率
    CHUNK = 1024  # 采样帧
    OUTPUT_FILE = filename  # 输出的录音文件

    # 打开音频流准备开始录制
    stream = p.open(rate=RATE,
                    format=FORMAT,
                    channels=CHANNELS,
                    input=True,  # 代表此时是输入音频流
                    frames_per_buffer=CHUNK)  # 缓冲区大小为一帧

    frames = []
    frame_num = int(RATE * SECONDS / CHUNK)  # 采样帧个数

    print("按下空格键开始录制音频!")
    while True:
        if keyboard.is_pressed(' '):
            break

    print("录制中...")
    for i in tqdm(range(frame_num)):  # tqdm显示进度条
        data = stream.read(CHUNK)
        frames.append(data)

    stream.stop_stream()  # 停止采集
    stream.close()  # 关闭音频流
    p.terminate()  # 关闭pyaudio

    wf = wave.open(OUTPUT_FILE, 'wb')  # 打开文件

    # 设置参数
    wf.setframerate(RATE)
    wf.setnchannels(CHANNELS)
    wf.setsampwidth(p.get_sample_size(FORMAT))  # 采样位深(字节)

    # frames为二进制列表文件,数据个数为采样帧数,这里把数据连续写入
    wf.writeframes(b''.join(frames))
    wf.close()
