import requests
import os

# 1. 配置推理服务端口
INFER_PORT = 9872
INFER_HOST = f"http://localhost:{INFER_PORT}"
INFER_ENDPOINT = f"{INFER_HOST}/infer"  # 假设你的服务接口是这个路径

# 2. 设置参数
config = {
    "ref_audio": "samples/ref.wav",         # 参考音色
    "input_audio": "samples/input.wav",     # 要转换的语音
    "output_path": "output/converted.wav",  # 输出保存路径
    "model_name": "gpt_sovits_v1",          # 模型名称
    "text_prompt": "role:boy;emotion:happy",  # 可选 prompt
    "pitch_shift": 0,                       # 音高调节
    "speed": 1.0                            # 语速调节
}

# 3. 发送请求
def convert_voice(config):
    if not os.path.exists(config['ref_audio']) or not os.path.exists(config['input_audio']):
        print("❌ 输入文件不存在，请检查路径")
        return
    
    print("🚀 开始语音转换请求...")
    try:
        files = {
            'ref_audio': open(config['ref_audio'], 'rb'),
            'input_audio': open(config['input_audio'], 'rb')
        }
        data = {
            'model_name': config['model_name'],
            'text_prompt': config['text_prompt'],
            'pitch_shift': config['pitch_shift'],
            'speed': config['speed']
        }

        response = requests.post(INFER_ENDPOINT, data=data, files=files)
        response.raise_for_status()

        # 保存结果
        with open(config["output_path"], "wb") as f:
            f.write(response.content)
        print(f"✅ 转换成功，已保存到 {config['output_path']}")

    except Exception as e:
        print(f"❌ 转换失败：{e}")

convert_voice(config)
