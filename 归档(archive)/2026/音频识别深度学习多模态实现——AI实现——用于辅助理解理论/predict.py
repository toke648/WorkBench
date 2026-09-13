"""
predict.py — 多模态语音情绪推理（单条/批量）
支持多模态和纯音频两种模式
"""
import sys
import os
import torch
import numpy as np

import config
from model import EmotionClassifier, MultimodalEmotionClassifier, build_multimodal_model
from data_loader import RAVDESSDataset
from asr_module import ASRProcessor
from text_processor import TextProcessor


def load_audio_model(model_path=config.MODEL_SAVE_PATH):
    """加载纯音频模型"""
    model = EmotionClassifier(
        input_size=config.AUDIO_INPUT_SIZE,
        hidden_size=config.AUDIO_HIDDEN_SIZE,
        num_layers=config.AUDIO_NUM_LAYERS,
        num_classes=config.NUM_CLASSES,
        dropout=0.0,
        bidirectional=config.AUDIO_BIDIRECTIONAL,
        attention_size=config.AUDIO_ATTENTION_SIZE,
    )
    checkpoint = torch.load(model_path, map_location=config.DEVICE)
    model.load_state_dict(checkpoint["model_state_dict"])
    model.to(config.DEVICE)
    model.eval()
    print(f"音频模型已加载: {model_path}")
    return model


def load_multimodal_model(model_path=config.MODEL_SAVE_PATH, tfidf_dim=None):
    """加载多模态模型"""
    if tfidf_dim is None:
        tfidf_dim = config.TFIDF_MAX_FEATURES
    model = build_multimodal_model(tfidf_dim=tfidf_dim)
    checkpoint = torch.load(model_path, map_location=config.DEVICE)
    model.load_state_dict(checkpoint["model_state_dict"])
    model.to(config.DEVICE)
    model.eval()
    print(f"多模态模型已加载: {model_path}")
    return model


@torch.no_grad()
def predict_single_audio(model, audio_path, device=config.DEVICE):
    """纯音频单条推理"""
    temp_dataset = RAVDESSDataset([audio_path], [0])
    mfcc, _, _ = temp_dataset[0]
    mfcc = mfcc.unsqueeze(0).to(device)
    logits, attn_weights = model(mfcc)
    probs = torch.softmax(logits, dim=-1).squeeze().cpu().numpy()
    pred_idx = int(torch.argmax(logits, dim=-1).item())
    pred_emotion_en = config.IDX_TO_EMOTION[pred_idx]
    pred_emotion_cn = config.EMOTION_CN[pred_emotion_en]
    confidence = float(probs[pred_idx])
    return {
        "file": audio_path,
        "prediction": pred_emotion_en,
        "prediction_cn": pred_emotion_cn,
        "confidence": round(confidence, 4),
        "probabilities": {
            config.IDX_TO_EMOTION[i]: round(float(p), 4)
            for i, p in enumerate(probs)
        },
        "attn_weights": attn_weights.squeeze().cpu().numpy(),
    }


@torch.no_grad()
def predict_single_multimodal(model, audio_path, text_feature, device=config.DEVICE):
    """多模态单条推理"""
    temp_dataset = RAVDESSDataset([audio_path], [0])
    mfcc, _, _ = temp_dataset[0]
    mfcc = mfcc.unsqueeze(0).to(device)
    text_feat = torch.tensor(text_feature, dtype=torch.float32).unsqueeze(0).to(device)
    logits, attn_weights = model(mfcc, text_feat)
    probs = torch.softmax(logits, dim=-1).squeeze().cpu().numpy()
    pred_idx = int(torch.argmax(logits, dim=-1).item())
    pred_emotion_en = config.IDX_TO_EMOTION[pred_idx]
    pred_emotion_cn = config.EMOTION_CN[pred_emotion_en]
    confidence = float(probs[pred_idx])
    return {
        "file": audio_path,
        "prediction": pred_emotion_en,
        "prediction_cn": pred_emotion_cn,
        "confidence": round(confidence, 4),
        "probabilities": {
            config.IDX_TO_EMOTION[i]: round(float(p), 4)
            for i, p in enumerate(probs)
        },
        "attn_weights": attn_weights.squeeze().cpu().numpy(),
    }


def predict_batch(model, audio_paths, text_processor=None, asr=None,
                   device=config.DEVICE, multimodal=False):
    """批量预测"""
    results = []
    for path in audio_paths:
        if not os.path.exists(path):
            results.append({"file": path, "error": "文件不存在"})
            continue
        try:
            if multimodal and text_processor is not None:
                text = asr.transcribe(path) if asr else ""
                text_feat = text_processor.transform(text)
                res = predict_single_multimodal(model, path, text_feat, device)
            else:
                res = predict_single_audio(model, path, device)
            results.append(res)
        except Exception as e:
            results.append({"file": path, "error": str(e)})
    return results


def print_prediction(result):
    """格式化打印预测结果"""
    if "error" in result:
        print(f"[错误] {result['file']}: {result['error']}")
        return
    print(f"\n{'='*50}")
    print(f"文件: {result['file']}")
    print(f"预测情绪: {result['prediction_cn']} ({result['prediction']})")
    print(f"置信度: {result['confidence']:.2%}")
    print(f"各类概率:")
    for emo, prob in result["probabilities"].items():
        bar = "█" * int(prob * 40)
        print(f"  {config.EMOTION_CN.get(emo, emo):<6} ({emo:<8}): {prob:.4f}  {bar}")
    print(f"{'='*50}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("用法: python predict.py <音频文件路径> [更多音频...]")
        print("选项: --multimodal  启用多模态推理")
        sys.exit(1)

    multimodal = "--multimodal" in sys.argv
    audio_paths = [a for a in sys.argv[1:] if a != "--multimodal"]

    asr = None
    text_processor = None

    if multimodal:
        try:
            asr = ASRProcessor()
            if asr.is_available():
                text_processor = TextProcessor()
                # 注意：实际使用需要先拟合 vectorizer
                # 这里仅作示例，完整流程请参考 main.py
                print("[警告] 多模态推理需要预先拟合的 TF-IDF vectorizer")
                print("  建议先运行 main.py 完成训练后再使用 --multimodal 推理")
        except Exception as e:
            print(f"[警告] 多模态初始化失败: {e}，回退纯音频")
            multimodal = False

    if multimodal and text_processor is not None:
        model = load_multimodal_model()
    else:
        model = load_audio_model()

    results = predict_batch(model, audio_paths, text_processor, asr,
                             multimodal=multimodal)
    for r in results:
        print_prediction(r)
