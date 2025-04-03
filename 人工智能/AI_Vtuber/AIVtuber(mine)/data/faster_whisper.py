# from faster_whisper import WhisperModel
#
# model_size = "large-v3"
#
# # Run on GPU with FP16
# model = WhisperModel(model_size, device="cuda", compute_type="float16")
#
# # or run on GPU with INT8
# # model = WhisperModel(model_size, device="cuda", compute_type="int8_float16")
# # or run on CPU with INT8
# # model = WhisperModel(model_size, device="cpu", compute_type="int8")
#
# segments, info = model.transcribe("input.mp3", beam_size=5)
#
# print("Detected language '%s' with probability %f" % (info.language, info.language_probability))
#
# for segment in segments:
#     print("[%.2fs -> %.2fs] %s" % (segment.start, segment.end, segment.text))


from faster_whisper import WhisperModel
import os
import tool
import threading

threads = []
i = 0


def parse_autdio(mdoel, audio_url, savePath, language='zh'):
    model = WhisperModel('large-v3', device="cuda", compute_type="int8", download_root=os.getcwd() + './models')
    segments, info = model.transcribe(audio_url, beam_size=5, language=language)
    file_name = os.path.basename(audio_url)
    noextname, ext = os.path.splitext(file_name)
    textname = noextname + '.txt'
    saveName = os.path.join(savePath, textname)
    with open(saveName, 'w', encoding="utf-8") as f:
        for segment in segments:
            print("[%.2fs -> %.2fs] %s" % (segment.start, segment.end, segment.text))
            f.write(segment.text + '\n')

        f.close()


def parse_dir(dir_path, savePath):
    for file in os.listdir(dir_path):
        full_path = os.path.join(dir_path, file)
        if (os.path.isdir(full_path)):
            parse_dir(full_path, savePath)
        else:
            for i in range(3):
                t = threading.Thread(target=parse_file, args=(full_path, savePath))
                threads.append(t)
            #    return
            parse_file(full_path, savePath)


def parse_file(file_path, savePath):
    print('当前转换文件：', file_path)
    # audio_file = open(file_path)
    # 如果是mp4
    file_name = os.path.basename(file_path)
    noextname, ext = os.path.splitext(file_name)
    ext = ext.lower()
    # 如果是视频，先分离
    if (not os.path.exists(savePath)):
        os.makedirs(savePath)
    wav_file = os.path.join(savePath, f'{noextname}.wav')
    text_file = os.path.join(savePath, f'{noextname}.txt')
    if (os.path.exists(wav_file) and os.path.exists(text_file)):
        print('————————文件已经转换过——————————————————————————————')
        return
    if ext in ['.mp4', '.mov', '.avi', '.mkv', '.mpeg', '.mp3', '.flac']:
        video_file = file_path

        params = [
            "-i",
            video_file,
        ]
        print(wav_file, 'fff_____________')
        if ext not in ['.mp3', '.flac']:
            params.append('-vn')
        params.append(wav_file)
        rs = tool.runffmpeg(params)
        parse_autdio('base', wav_file, savePath)


path = 'G:/学习视频/手把手教你零基础写作，业余时间月入过万'
savePath = 'G:/学习视频/手把手教你零基础写作，业余时间月入过万/视频字幕'

parse_dir(path, savePath)

for t in threads:
    t.start()

for t in threads:
    t.join()


