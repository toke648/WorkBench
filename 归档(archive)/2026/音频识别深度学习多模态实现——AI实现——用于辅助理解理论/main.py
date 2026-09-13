"""
main.py — 多模态语音情绪识别系统主入口
支持多模态（音频+文本）训练/评估和纯音频 fallback
"""
import os
import sys
import argparse
import numpy as np
import torch

import config
from config import DEVICE
from utils import (
    set_seed, compute_metrics, format_metrics_table,
    plot_training_curves, plot_confusion_matrix,
)
from data_loader import (
    scan_dataset, create_dataloaders, create_multimodal_dataloaders,
)
from model import (
    build_multimodal_model, build_audio_model, count_parameters,
)
from train import (
    train_model, train_multimodal_model, load_best_model,
    evaluate, evaluate_multimodal,
)
from asr_module import ASRProcessor
from text_processor import TextProcessor


def parse_args():
    parser = argparse.ArgumentParser(description="多模态语音情绪识别系统")
    parser.add_argument("--train", action="store_true", help="仅训练")
    parser.add_argument("--eval", action="store_true", help="仅评估")
    parser.add_argument("--epochs", type=int, default=config.NUM_EPOCHS)
    parser.add_argument("--audio-only", action="store_true",
                        help="仅使用音频模态（跳过 ASR）")
    return parser.parse_args()


def main():
    args = parse_args()
    set_seed(config.RANDOM_SEED)

    print("=" * 60)
    print("  多模态语音情绪识别系统")
    print("  题目：基于多模态融合的语音情绪识别系统")
    print("  模态：语音 + 文本（Whisper ASR → NLTK → TF-IDF）")
    print("  情绪类别: 中性 / 高兴 / 悲伤 / 愤怒")
    print(f"  设备: {DEVICE}")
    print("=" * 60)

    # ====== Step 1: 扫描数据集 ======
    print("\n[Step 1] 扫描数据集...")
    file_paths, labels, counts = scan_dataset()
    print(f"  总样本数: {len(file_paths)}")
    for lbl_idx, cnt in sorted(counts.items()):
        emo_en = config.IDX_TO_EMOTION[lbl_idx]
        print(f"    {config.EMOTION_CN[emo_en]} ({emo_en}): {cnt} 条")

    # ====== 检测 ASR 可用性 ======
    multimodal_mode = config.USE_MULTIMODAL and not args.audio_only
    asr_available = False

    if multimodal_mode:
        asr = ASRProcessor()
        asr_available = asr.is_available()
        if not asr_available:
            print("\n[警告] Whisper ASR 不可用，回退到纯音频模式")
            print("  如需多模态，请执行: pip install openai-whisper")
            multimodal_mode = False

    # ====== Step 2: 文本模态处理（多模态模式） ======
    text_features = None
    tfidf_dim = config.TFIDF_MAX_FEATURES

    if multimodal_mode and asr_available:
        print("\n[Step 2a] Whisper ASR 语音转文本...")
        transcripts = asr.transcribe_batch(file_paths, use_cache=True, verbose=True)

        print("\n[Step 2b] NLTK 文本预处理 + TF-IDF 向量化...")
        text_processor = TextProcessor(max_features=config.TFIDF_MAX_FEATURES)
        texts = [transcripts.get(p, "") for p in file_paths]
        text_processor.fit_vectorizer(texts)
        text_features = text_processor.transform_batch(texts)
        tfidf_dim = text_features.shape[1]
        print(f"  文本特征维度: {text_features.shape}")

    # ====== Step 3: 数据划分 ======
    if multimodal_mode and text_features is not None:
        print("\n[Step 3] 多模态数据划分...")
        train_loader, val_loader, test_loader, splits = create_multimodal_dataloaders(
            file_paths, labels, text_features)
    else:
        print("\n[Step 3] 纯音频数据划分...")
        train_loader, val_loader, test_loader, splits = create_dataloaders(
            file_paths, labels)

    # ====== Step 4: 创建模型 ======
    print("\n[Step 4] 创建模型...")
    if multimodal_mode and text_features is not None:
        model = build_multimodal_model(tfidf_dim=tfidf_dim)
        print(f"  模型: BiGRU + Text MLP + Self-Attention + 多模态融合")
        train_fn = train_multimodal_model
        eval_fn = evaluate_multimodal
    else:
        model = build_audio_model()
        print(f"  模型: BiGRU + Self-Attention（纯音频模式）")
        train_fn = train_model
        eval_fn = evaluate

    print(f"  可训练参数: {count_parameters(model):,}")

    # ====== Step 5: 训练 ======
    if not args.eval:
        print("\n[Step 5] 开始训练...")
        config.NUM_EPOCHS = args.epochs
        model, history = train_fn(model, train_loader, val_loader)
        plot_training_curves(history, "training_curves.png")
        print("训练曲线已保存: training_curves.png")

    # ====== Step 6: 加载最佳模型并评估 ======
    print("\n[Step 6] 加载最佳模型并评估...")
    model = load_best_model(model, DEVICE)

    criterion = torch.nn.CrossEntropyLoss()
    if multimodal_mode and text_features is not None:
        test_loss, test_acc, all_labels, all_preds = eval_fn(
            model, test_loader, criterion, DEVICE)
    else:
        test_loss, test_acc, all_labels, all_preds = evaluate(
            model, test_loader, criterion, DEVICE)

    print(f"\n  测试集 Loss: {test_loss:.4f}")
    print(f"  测试集 Accuracy: {test_acc:.4f}")

    # ====== Step 7: 详细评估 ======
    print("\n[Step 7] 详细评估指标...")
    class_names = [config.EMOTION_CN[config.IDX_TO_EMOTION[i]]
                   for i in range(config.NUM_CLASSES)]
    metrics = compute_metrics(all_labels, all_preds, class_names)
    print(format_metrics_table(metrics))

    report_path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "classification_report.txt")
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(metrics["report"])
    print(f"\n分类报告已保存: {report_path}")

    # ====== Step 8: 混淆矩阵 ======
    print("\n[Step 8] 绘制混淆矩阵...")
    plot_confusion_matrix(all_labels, all_preds, class_names, "confusion_matrix.png")
    print("混淆矩阵已保存: confusion_matrix.png")

    # ====== 总结 ======
    print("\n" + "=" * 60)
    print("  系统运行完成！")
    print(f"  运行模式: {'多模态融合' if multimodal_mode else '纯音频'}")
    print(f"  模型文件: {config.MODEL_SAVE_PATH}")
    print(f"  训练曲线: training_curves.png")
    print(f"  混淆矩阵: confusion_matrix.png")
    print(f"  分类报告: classification_report.txt")
    print("=" * 60)


if __name__ == "__main__":
    main()
