"""
utils.py — 工具函数：特征提取、可视化、评估指标
"""
import os
import random
import numpy as np
import librosa
import librosa.display
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import torch
from sklearn.metrics import (
    accuracy_score, precision_recall_fscore_support,
    confusion_matrix, classification_report,
)
import seaborn as sns

import config


def set_seed(seed=config.RANDOM_SEED):
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    torch.cuda.manual_seed_all(seed)
    torch.backends.cudnn.deterministic = True
    torch.backends.cudnn.benchmark = False


# ==================== 音频特征提取 ====================

def extract_mfcc(file_path, sr=config.SAMPLE_RATE, n_mfcc=config.N_MFCC,
                 n_fft=config.N_FFT, hop_length=config.HOP_LENGTH,
                 duration=config.DURATION):
    try:
        y, sr = librosa.load(file_path, sr=sr, duration=duration)
    except Exception as e:
        print(f"[警告] 无法加载 {file_path}: {e}")
        return None
    target_len = int(sr * duration)
    y = np.pad(y, (0, max(0, target_len - len(y))))[:target_len]
    mfcc = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=n_mfcc,
                                n_fft=n_fft, hop_length=hop_length)
    mfcc = (mfcc - mfcc.mean(axis=1, keepdims=True)) / (mfcc.std(axis=1, keepdims=True) + 1e-6)
    return y, mfcc


def extract_mel_spectrogram(file_path, sr=config.SAMPLE_RATE, n_mels=config.N_MELS,
                            n_fft=config.N_FFT, hop_length=config.HOP_LENGTH,
                            duration=config.DURATION):
    try:
        y, sr = librosa.load(file_path, sr=sr, duration=duration)
    except Exception as e:
        print(f"[警告] 无法加载 {file_path}: {e}")
        return None
    target_len = int(sr * duration)
    y = np.pad(y, (0, max(0, target_len - len(y))))[:target_len]
    mel_spec = librosa.feature.melspectrogram(y=y, sr=sr, n_mels=n_mels,
                                               n_fft=n_fft, hop_length=hop_length)
    log_mel = librosa.power_to_db(mel_spec, ref=np.max)
    return log_mel


# ==================== 特征图像可视化（题目要求：可视化音频特征图像） ====================

def plot_waveform(y, sr, save_path, title="Waveform"):
    plt.figure(figsize=(10, 3))
    librosa.display.waveshow(y, sr=sr)
    plt.title(title)
    plt.tight_layout()
    plt.savefig(save_path, dpi=150, bbox_inches="tight")
    plt.close()


def plot_mfcc(mfcc, sr, save_path, title="MFCC"):
    plt.figure(figsize=(10, 4))
    librosa.display.specshow(mfcc, sr=sr, hop_length=config.HOP_LENGTH,
                             x_axis="time", y_axis="mel")
    plt.colorbar(format="%+2.0f dB")
    plt.title(title)
    plt.tight_layout()
    plt.savefig(save_path, dpi=150, bbox_inches="tight")
    plt.close()


def plot_mel_spectrogram(mel_spec, sr, save_path, title="Mel Spectrogram"):
    plt.figure(figsize=(10, 4))
    librosa.display.specshow(mel_spec, sr=sr, hop_length=config.HOP_LENGTH,
                             x_axis="time", y_axis="mel")
    plt.colorbar(format="%+2.0f dB")
    plt.title(title)
    plt.tight_layout()
    plt.savefig(save_path, dpi=150, bbox_inches="tight")
    plt.close()


def plot_attention_weights(attn_weights, save_path, title="Attention Weights"):
    """
    绘制注意力权重热力图（题目要求：可视化注意力权重图）
    """
    plt.figure(figsize=(10, 2))
    plt.imshow(attn_weights.reshape(1, -1), aspect="auto", cmap="hot")
    plt.colorbar(label="Attention Weight")
    plt.xlabel("Time Frame")
    plt.title(title)
    plt.tight_layout()
    plt.savefig(save_path, dpi=150, bbox_inches="tight")
    plt.close()


def visualize_audio_features(audio_path, output_dir="."):
    """
    可视化一条音频的波形图、MFCC 和梅尔频谱图
    题目要求：可视化音频特征图像
    """
    y_sr = extract_mfcc(audio_path)
    if y_sr is None:
        print(f"无法处理 {audio_path}")
        return
    y, mfcc = y_sr
    sr = config.SAMPLE_RATE
    mel_spec = extract_mel_spectrogram(audio_path)
    base = os.path.splitext(os.path.basename(audio_path))[0]

    plot_waveform(y, sr, os.path.join(output_dir, f"{base}_waveform.png"))
    plot_mfcc(mfcc, sr, os.path.join(output_dir, f"{base}_mfcc.png"))
    if mel_spec is not None:
        plot_mel_spectrogram(mel_spec, sr,
                             os.path.join(output_dir, f"{base}_melspectrogram.png"))
    print(f"特征图已保存至: {output_dir}/")


# ==================== 混淆矩阵 ====================

def plot_confusion_matrix(y_true, y_pred, class_names, save_path):
    cm = confusion_matrix(y_true, y_pred)
    plt.figure(figsize=(8, 6))
    sns.heatmap(cm, annot=True, fmt="d", cmap="Blues",
                xticklabels=class_names, yticklabels=class_names)
    plt.xlabel("Predicted")
    plt.ylabel("True")
    plt.title("Confusion Matrix")
    plt.tight_layout()
    plt.savefig(save_path, dpi=150, bbox_inches="tight")
    plt.close()


# ==================== 训练曲线 ====================

def plot_training_curves(history, save_path):
    epochs = range(1, len(history["train_loss"]) + 1)
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 4))
    ax1.plot(epochs, history["train_loss"], "b-", label="Train Loss")
    ax1.plot(epochs, history["val_loss"], "r-", label="Val Loss")
    ax1.set_xlabel("Epoch"); ax1.set_ylabel("Loss")
    ax1.set_title("Training & Validation Loss")
    ax1.legend(); ax1.grid(True, alpha=0.3)
    ax2.plot(epochs, history["train_acc"], "b-", label="Train Accuracy")
    ax2.plot(epochs, history["val_acc"], "r-", label="Val Accuracy")
    ax2.set_xlabel("Epoch"); ax2.set_ylabel("Accuracy")
    ax2.set_title("Training & Validation Accuracy")
    ax2.legend(); ax2.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(save_path, dpi=150, bbox_inches="tight")
    plt.close()


# ==================== 评估指标 ====================

def compute_metrics(y_true, y_pred, class_names=None):
    accuracy = accuracy_score(y_true, y_pred)
    precision, recall, f1, support = precision_recall_fscore_support(
        y_true, y_pred, average=None, zero_division=0)
    macro_precision, macro_recall, macro_f1, _ = precision_recall_fscore_support(
        y_true, y_pred, average="macro", zero_division=0)
    weighted_f1 = _weighted_f1(y_true, y_pred)
    if class_names is None:
        class_names = [f"class_{i}" for i in range(len(precision))]
    per_class = {}
    for i, name in enumerate(class_names):
        per_class[name] = {
            "precision": round(precision[i], 4),
            "recall": round(recall[i], 4),
            "f1": round(f1[i], 4),
            "support": int(support[i]),
        }
    report = classification_report(y_true, y_pred, target_names=class_names,
                                     zero_division=0)
    return {
        "accuracy": round(accuracy, 4),
        "macro_precision": round(macro_precision, 4),
        "macro_recall": round(macro_recall, 4),
        "macro_f1": round(macro_f1, 4),
        "weighted_f1": round(weighted_f1, 4),
        "per_class": per_class,
        "report": report,
    }


def _weighted_f1(y_true, y_pred):
    _, _, f1, support = precision_recall_fscore_support(
        y_true, y_pred, average=None, zero_division=0)
    return np.average(f1, weights=support)


def format_metrics_table(metrics):
    lines = []
    lines.append(f"{'='*60}")
    lines.append(f"Overall Accuracy : {metrics['accuracy']:.2%}")
    lines.append(f"Macro Precision  : {metrics['macro_precision']:.4f}")
    lines.append(f"Macro Recall     : {metrics['macro_recall']:.4f}")
    lines.append(f"Macro F1         : {metrics['macro_f1']:.4f}")
    lines.append(f"Weighted F1      : {metrics['weighted_f1']:.4f}")
    lines.append(f"{'='*60}")
    lines.append(f"{'Emotion':<12} {'Precision':>10} {'Recall':>10} {'F1':>10} {'Support':>8}")
    lines.append(f"{'-'*52}")
    for name, m in metrics["per_class"].items():
        lines.append(f"{name:<12} {m['precision']:>10.4f} {m['recall']:>10.4f} "
                     f"{m['f1']:>10.4f} {m['support']:>8d}")
    lines.append(f"{'='*60}")
    return "\n".join(lines)
