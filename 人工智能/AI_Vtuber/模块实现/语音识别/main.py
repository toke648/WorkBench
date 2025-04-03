from audio_record import record
from audio_play import play
from baidu_ai import audio_to_text, text_to_audio


def record():
    file = r'C:\Users\16673\Desktop\yuyin4.mp3'  # 语音录制，识别文件
    # synth_file = "synth.mp3"  # 语音合成文件

    record(file)  # 录制音频

    res_str = audio_to_text(file)  # 语音识别
    print(res_str)  # 打印识别结果
    #
    # ret = text_to_audio(synth_file, res_str)  # 语音合成
    #
    # if ret != -1:
    #     play(synth_file)  # 播放合成结果

