import asyncio
import edge_tts
import time
from pydub import AudioSegment
import hashlib

pwd = "/var/www/html/sound"

rate = '+0%'
volume = '+0%'
pitch = '+0Hz'


def calculate_8_digit_md5(input_string):
    md5 = hashlib.md5()
    md5.update(input_string.encode('utf-8'))
    md5_hash = md5.hexdigest()[:8]
    return md5_hash


def get_current_time():
    current_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
    return current_time


async def convert(text, file_name, count, voice_name) -> None:
    global result
    start_time = time.time()
    communicate = edge_tts.Communicate(text=text, voice=voice_name, rate=rate, volume=volume, pitch=pitch)
    await communicate.save(pwd + f"/cache/{file_name}{count}.mp3")
    print(f"{file_name}用时：{int(time.time() - start_time)}秒")


def split_and_terminate(input_string, chunk_size=3000):
    res = []
    start = 0
    while start < len(input_string):
        # 截取指定大小的片段
        chunk = input_string[start:start + chunk_size]
        if start + chunk_size < len(input_string):
            last_comma = chunk.rfind('，')
            last_period = chunk.rfind('。')
            last_punctuation = max(last_comma, last_period)
            if last_punctuation != -1:
                chunk = chunk[:last_punctuation + 1]
        res.append(chunk)
        start += len(chunk)
    return res


async def main():
    print("md5:" + md5)
    result = split_and_terminate(text)
    tasks = []
    for index, chunk in enumerate(result):
        tasks.append(convert(chunk, md5, str(index + 1), "zh-CN-XiaoxiaoNeural"))
    await asyncio.gather(*tasks)


def save_string_to_file(data, file_path):
    try:
        with open(file_path, 'w', encoding='utf-8') as file:
            file.write(data)
        print(f"字符串已成功保存到文件: {file_path}")
    except Exception as e:
        print(f"保存文件时发生错误: {e}")


if __name__ == "__main__":
    global text, md5
    with open(pwd + "/texts/测试.txt", "r", encoding='utf-8') as text_file:
        text = text_file.read()
        md5 = calculate_8_digit_md5(text + str(time.time()))
    asyncio.run(main())
    print('音频下载完成')
    result = AudioSegment.from_file(pwd + "/cache/" + md5 + "1.mp3")
    print('第1段合成完成')
    count = len(split_and_terminate(text))
    for i in range(2, count + 1):
        result += AudioSegment.from_file(pwd + "/cache/" + md5 + str(i) + ".mp3")
        print('第' + str(i) + '段合成完成')
    result.export(pwd + "/download/" + md5 + ".mp3", format="mp3")
    print(md5 + ".mp3生成成功")