"""
app.py — 多模态语音情绪识别系统 Web 可视化界面（Gradio）

功能：
  - 上传 .wav 音频文件
  - 显示波形图、MFCC 特征图、梅尔频谱图
  - 调用模型进行情绪预测
  - 显示预测结果、概率分布、注意力权重图

用法:
    python app.py
    然后访问 http://127.0.0.1:7860
"""
import os
import sys
import tempfile
import numpy as np
import torch

import config
from utils import extract_mfcc, extract_mel_spectrogram, plot_attention_weights

# 延迟导入：仅在 Gradio 可用时加载
try:
    import gradio as gr
except ImportError:
    print("请安装 Gradio: pip install gradio")
    sys.exit(1)


# ==================== 全局模型加载 ====================

_model = None
_asr = None
_text_processor = None
_multimodal = False


def init_model():
    """初始化模型（尝试多模态，失败则回退纯音频）"""
    global _model, _asr, _text_processor, _multimodal

    from model import build_multimodal_model, build_audio_model
    from train import load_best_model

    # 尝试多模态
    try:
        from asr_module import ASRProcessor
        from text_processor import TextProcessor
        _asr = ASRProcessor()
        if _asr.is_available():
            _text_processor = TextProcessor()
            _model = build_multimodal_model()
            _multimodal = True
            if os.path.exists(config.MODEL_SAVE_PATH):
                _model = load_best_model(_model)
            return "多模态模型就绪 (音频 + 文本)"
    except Exception:
        pass

    # 回退纯音频
    _multimodal = False
    _model = build_audio_model()
    if os.path.exists(config.MODEL_SAVE_PATH):
        _model = load_best_model(_model)
    return "纯音频模型就绪"


# ==================== 推理函数 ====================

def predict_emotion(audio_file):
    """
    Gradio 回调：处理上传的音频文件

    Returns:
        (prediction_text, waveform_fig, mfcc_fig, mel_fig, attn_fig, prob_plot)
    """
    global _model, _multimodal, _asr, _text_processor

    if _model is None:
        status = init_model()
        print(status)

    if audio_file is None:
        return "请上传音频文件", None, None, None, None, None

    device = config.DEVICE

    # 提取特征
    result = extract_mfcc(audio_file)
    if result is None:
        return "无法加载音频文件", None, None, None, None, None

    y, mfcc_raw = result
    sr = config.SAMPLE_RATE
    mel_spec = extract_mel_spectrogram(audio_file)

    # 准备模型输入
    mfcc = mfcc_raw.T  # (T, D)
    max_t = config.MAX_TIME_STEPS
    if mfcc.shape[0] < max_t:
        mfcc = np.pad(mfcc, ((0, max_t - mfcc.shape[0]), (0, 0)))
    else:
        mfcc = mfcc[:max_t, :]
    audio_tensor = torch.tensor(mfcc, dtype=torch.float32).unsqueeze(0).to(device)

    # 推理
    with torch.no_grad():
        if _multimodal and _asr and _text_processor:
            # 需要 TF-IDF vectorizer 已拟合，这里使用简化版本
            text = _asr.transcribe(audio_file)
            text_feat = _text_processor.transform(text)
            text_tensor = torch.tensor(text_feat, dtype=torch.float32).unsqueeze(0).to(device)
            logits, attn_weights = _model(audio_tensor, text_tensor)
        else:
            logits, attn_weights = _model(audio_tensor)

    probs = torch.softmax(logits, dim=-1).squeeze().cpu().numpy()
    pred_idx = int(torch.argmax(logits, dim=-1).item())
    attn_np = attn_weights.squeeze().cpu().numpy()

    # 预测结果文本
    pred_en = config.IDX_TO_EMOTION[pred_idx]
    pred_cn = config.EMOTION_CN[pred_en]
    conf = probs[pred_idx]

    lines = [
        f"## 预测结果: {pred_cn} ({pred_en})",
        f"**置信度**: {conf:.2%}",
        "",
        "### 各类别概率:",
    ]
    for i in range(config.NUM_CLASSES):
        emo_en = config.IDX_TO_EMOTION[i]
        emo_cn = config.EMOTION_CN[emo_en]
        bar_len = int(probs[i] * 30)
        bar = "█" * bar_len + "░" * (30 - bar_len)
        lines.append(f"- {emo_cn} ({emo_en}): {probs[i]:.4f}  `{bar}`")
    pred_text = "\n".join(lines)

    # 波形图
    import matplotlib.pyplot as plt
    import librosa.display

    fig_wave, ax = plt.subplots(figsize=(8, 2))
    librosa.display.waveshow(y, sr=sr, ax=ax)
    ax.set_title("Waveform")
    plt.tight_layout()

    # MFCC 图
    fig_mfcc, ax = plt.subplots(figsize=(8, 3))
    img = librosa.display.specshow(mfcc_raw, sr=sr, hop_length=config.HOP_LENGTH,
                                    x_axis="time", y_axis="mel", ax=ax)
    plt.colorbar(img, ax=ax, format="%+2.0f dB")
    ax.set_title("MFCC Features")
    plt.tight_layout()

    # 梅尔频谱图
    fig_mel = None
    if mel_spec is not None:
        fig_mel, ax = plt.subplots(figsize=(8, 3))
        img = librosa.display.specshow(mel_spec, sr=sr, hop_length=config.HOP_LENGTH,
                                        x_axis="time", y_axis="mel", ax=ax)
        plt.colorbar(img, ax=ax, format="%+2.0f dB")
        ax.set_title("Mel Spectrogram")
        plt.tight_layout()

    # 注意力权重图
    fig_attn, ax = plt.subplots(figsize=(8, 2))
    ax.imshow(attn_np.reshape(1, -1), aspect="auto", cmap="hot")
    ax.set_xlabel("Time Frame")
    ax.set_title("Self-Attention Weights")
    plt.tight_layout()

    # 概率柱状图
    fig_prob, ax = plt.subplots(figsize=(5, 3))
    emo_labels = [config.EMOTION_CN[config.IDX_TO_EMOTION[i]]
                  for i in range(config.NUM_CLASSES)]
    colors = ["#4CAF50" if i == pred_idx else "#BDBDBD" for i in range(config.NUM_CLASSES)]
    ax.bar(emo_labels, probs, color=colors)
    ax.set_ylim(0, 1)
    ax.set_ylabel("Probability")
    ax.set_title("Emotion Probability Distribution")
    plt.tight_layout()

    return pred_text, fig_wave, fig_mfcc, fig_mel, fig_attn, fig_prob


# ==================== Gradio 界面构建 ====================

def create_ui():
    with gr.Blocks(title="多模态语音情绪识别系统") as demo:
        gr.Markdown(
            """
            # 基于多模态融合的语音情绪识别系统
            **课程设计项目** | 情绪类别：中性 / 高兴 / 悲伤 / 愤怒

            上传 .wav 音频文件，系统将自动提取 MFCC、梅尔频谱等音频特征，
            通过 BiGRU + Self-Attention 深度学习模型进行情绪识别，
            并可视化音频特征图与注意力权重分布。
            """
        )

        with gr.Row():
            with gr.Column(scale=1):
                audio_input = gr.Audio(
                    label="上传音频文件 (.wav)",
                    type="filepath",
                )
                submit_btn = gr.Button("开始识别", variant="primary")
                output_text = gr.Markdown(label="预测结果")

            with gr.Column(scale=2):
                with gr.Tabs():
                    with gr.TabItem("波形图"):
                        plot_wave = gr.Plot(label="Waveform")
                    with gr.TabItem("MFCC 特征图"):
                        plot_mfcc = gr.Plot(label="MFCC")
                    with gr.TabItem("梅尔频谱图"):
                        plot_mel = gr.Plot(label="Mel Spectrogram")
                    with gr.TabItem("注意力权重"):
                        plot_attn = gr.Plot(label="Attention Weights")
                    with gr.TabItem("概率分布"):
                        plot_prob = gr.Plot(label="Probability Distribution")

        submit_btn.click(
            fn=predict_emotion,
            inputs=[audio_input],
            outputs=[output_text, plot_wave, plot_mfcc, plot_mel, plot_attn, plot_prob],
        )

        gr.Markdown(
            """
            ---
            **技术栈**: Librosa + PyTorch + BiGRU + Self-Attention + Whisper ASR + NLTK + TF-IDF + Gradio

            山东电子职业技术学院 · 人工智能技术应用专业 · J2400X班
            """
        )

    return demo


if __name__ == "__main__":
    print("初始化模型...")
    status = init_model()
    print(f"  状态: {status}")
    demo = create_ui()
    demo.launch(server_name="127.0.0.1", server_port=7860, share=False)
