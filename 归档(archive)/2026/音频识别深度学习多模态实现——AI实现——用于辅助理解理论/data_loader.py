"""
data_loader.py — RAVDESS 数据集加载、特征提取与数据划分
支持纯音频模式和多模态（音频+文本）模式
"""
import os
import numpy as np
import librosa
import torch
from torch.utils.data import Dataset, DataLoader
from sklearn.model_selection import train_test_split
from collections import defaultdict

import config


class RAVDESSDataset(Dataset):
    """
    RAVDESS 纯音频数据集加载器（单模态）

    文件名格式: 03-01-XX-XX-XX-XX-XX.wav
    第3段(XX)为情绪编码: 01=neutral, 03=happy, 04=sad, 05=angry
    """

    def __init__(self, file_paths, labels):
        self.file_paths = file_paths
        self.labels = labels

    def __len__(self):
        return len(self.file_paths)

    def __getitem__(self, idx):
        file_path = self.file_paths[idx]
        label = self.labels[idx]
        mfcc = self._load_and_extract(file_path)
        if mfcc is None:
            mfcc = np.zeros((config.N_MFCC, config.MAX_TIME_STEPS), dtype=np.float32)
        mfcc = mfcc.T  # (T, D)
        if mfcc.shape[0] < config.MAX_TIME_STEPS:
            pad = config.MAX_TIME_STEPS - mfcc.shape[0]
            mfcc = np.pad(mfcc, ((0, pad), (0, 0)), mode="constant")
        elif mfcc.shape[0] > config.MAX_TIME_STEPS:
            mfcc = mfcc[:config.MAX_TIME_STEPS, :]
        mfcc = torch.tensor(mfcc, dtype=torch.float32)
        label = torch.tensor(label, dtype=torch.long)
        return mfcc, label, file_path

    def _load_and_extract(self, file_path):
        try:
            y, sr = librosa.load(file_path, sr=config.SAMPLE_RATE,
                                  duration=config.DURATION)
        except Exception:
            return None
        target_len = int(config.SAMPLE_RATE * config.DURATION)
        if len(y) < target_len:
            y = np.pad(y, (0, target_len - len(y)))
        else:
            y = y[:target_len]
        mfcc = librosa.feature.mfcc(
            y=y, sr=sr, n_mfcc=config.N_MFCC,
            n_fft=config.N_FFT, hop_length=config.HOP_LENGTH)
        mfcc = (mfcc - mfcc.mean(axis=1, keepdims=True)) / (
            mfcc.std(axis=1, keepdims=True) + 1e-6)
        return mfcc


class MultimodalDataset(Dataset):
    """
    多模态数据集：同时返回 MFCC 特征和文本 TF-IDF 特征
    """

    def __init__(self, file_paths, labels, text_features):
        """
        Args:
            file_paths: list[str]  音频文件路径
            labels: list[int]      数字标签
            text_features: np.ndarray (N, tfidf_dim)  预提取的文本特征
        """
        self.file_paths = file_paths
        self.labels = labels
        self.text_features = text_features

    def __len__(self):
        return len(self.file_paths)

    def __getitem__(self, idx):
        file_path = self.file_paths[idx]
        label = self.labels[idx]
        text_feat = self.text_features[idx]

        mfcc = self._load_and_extract(file_path)
        if mfcc is None:
            mfcc = np.zeros((config.N_MFCC, config.MAX_TIME_STEPS), dtype=np.float32)
        mfcc = mfcc.T
        if mfcc.shape[0] < config.MAX_TIME_STEPS:
            pad = config.MAX_TIME_STEPS - mfcc.shape[0]
            mfcc = np.pad(mfcc, ((0, pad), (0, 0)), mode="constant")
        elif mfcc.shape[0] > config.MAX_TIME_STEPS:
            mfcc = mfcc[:config.MAX_TIME_STEPS, :]

        mfcc = torch.tensor(mfcc, dtype=torch.float32)
        text_feat = torch.tensor(text_feat, dtype=torch.float32)
        label = torch.tensor(label, dtype=torch.long)
        return mfcc, text_feat, label, file_path

    def _load_and_extract(self, file_path):
        try:
            y, sr = librosa.load(file_path, sr=config.SAMPLE_RATE,
                                  duration=config.DURATION)
        except Exception:
            return None
        target_len = int(config.SAMPLE_RATE * config.DURATION)
        if len(y) < target_len:
            y = np.pad(y, (0, target_len - len(y)))
        else:
            y = y[:target_len]
        mfcc = librosa.feature.mfcc(
            y=y, sr=sr, n_mfcc=config.N_MFCC,
            n_fft=config.N_FFT, hop_length=config.HOP_LENGTH)
        mfcc = (mfcc - mfcc.mean(axis=1, keepdims=True)) / (
            mfcc.std(axis=1, keepdims=True) + 1e-6)
        return mfcc


def scan_dataset(root=config.DATASET_ROOT, emotion_map=config.EMOTION_MAP):
    """扫描 RAVDESS 数据集，返回文件路径和标签"""
    file_paths = []
    labels = []
    if not os.path.isdir(root):
        raise FileNotFoundError(f"数据集目录不存在: {root}")
    for actor_dir in sorted(os.listdir(root)):
        actor_path = os.path.join(root, actor_dir)
        if not os.path.isdir(actor_path):
            continue
        for fname in os.listdir(actor_path):
            if not fname.endswith(".wav"):
                continue
            parts = fname.split("-")
            if len(parts) < 3:
                continue
            emotion_code = parts[2]
            if emotion_code not in emotion_map:
                continue
            file_paths.append(os.path.join(actor_path, fname))
            labels.append(config.EMOTION_TO_IDX[emotion_map[emotion_code]])
    label_counts = defaultdict(int)
    for lbl in labels:
        label_counts[lbl] += 1
    return file_paths, labels, dict(label_counts)


def create_dataloaders(file_paths, labels, batch_size=config.BATCH_SIZE):
    """
    纯音频模式：划分并创建 DataLoader
    """
    train_val_files, test_files, train_val_labels, test_labels = train_test_split(
        file_paths, labels, test_size=config.TEST_RATIO,
        random_state=config.RANDOM_SEED, stratify=labels)
    val_ratio = config.VAL_RATIO / (config.TRAIN_RATIO + config.VAL_RATIO)
    train_files, val_files, train_labels, val_labels = train_test_split(
        train_val_files, train_val_labels, test_size=val_ratio,
        random_state=config.RANDOM_SEED, stratify=train_val_labels)

    train_dataset = RAVDESSDataset(train_files, train_labels)
    val_dataset = RAVDESSDataset(val_files, val_labels)
    test_dataset = RAVDESSDataset(test_files, test_labels)

    train_loader = DataLoader(train_dataset, batch_size=batch_size,
                              shuffle=True, num_workers=0, pin_memory=True)
    val_loader = DataLoader(val_dataset, batch_size=batch_size,
                            shuffle=False, num_workers=0, pin_memory=True)
    test_loader = DataLoader(test_dataset, batch_size=batch_size,
                             shuffle=False, num_workers=0, pin_memory=True)

    print(f"数据划分完成:")
    print(f"  训练集: {len(train_dataset)} 条")
    print(f"  验证集: {len(val_dataset)} 条")
    print(f"  测试集: {len(test_dataset)} 条")

    return train_loader, val_loader, test_loader, (train_files, val_files, test_files)


def create_multimodal_dataloaders(file_paths, labels, text_features,
                                   batch_size=config.BATCH_SIZE):
    """
    多模态模式：划分并创建 DataLoader
    Args:
        text_features: np.ndarray (N, tfidf_dim)
    """
    file_paths = np.array(file_paths)
    labels = np.array(labels)

    train_val_idx, test_idx = train_test_split(
        np.arange(len(file_paths)), test_size=config.TEST_RATIO,
        random_state=config.RANDOM_SEED, stratify=labels)
    val_ratio = config.VAL_RATIO / (config.TRAIN_RATIO + config.VAL_RATIO)
    train_idx, val_idx = train_test_split(
        train_val_idx, test_size=val_ratio,
        random_state=config.RANDOM_SEED, stratify=labels[train_val_idx])

    train_files = file_paths[train_idx].tolist()
    val_files = file_paths[val_idx].tolist()
    test_files = file_paths[test_idx].tolist()

    train_labels = labels[train_idx].tolist()
    val_labels = labels[val_idx].tolist()
    test_labels = labels[test_idx].tolist()

    train_tfidf = text_features[train_idx]
    val_tfidf = text_features[val_idx]
    test_tfidf = text_features[test_idx]

    train_dataset = MultimodalDataset(train_files, train_labels, train_tfidf)
    val_dataset = MultimodalDataset(val_files, val_labels, val_tfidf)
    test_dataset = MultimodalDataset(test_files, test_labels, test_tfidf)

    train_loader = DataLoader(train_dataset, batch_size=batch_size,
                              shuffle=True, num_workers=0, pin_memory=True)
    val_loader = DataLoader(val_dataset, batch_size=batch_size,
                            shuffle=False, num_workers=0, pin_memory=True)
    test_loader = DataLoader(test_dataset, batch_size=batch_size,
                             shuffle=False, num_workers=0, pin_memory=True)

    print(f"多模态数据划分完成:")
    print(f"  训练集: {len(train_dataset)} 条")
    print(f"  验证集: {len(val_dataset)} 条")
    print(f"  测试集: {len(test_dataset)} 条")

    return train_loader, val_loader, test_loader, (train_files, val_files, test_files)


def compute_actual_lengths(mfcc_batch, hop_length=config.HOP_LENGTH,
                            sr=config.SAMPLE_RATE, duration=config.DURATION):
    return torch.full((mfcc_batch.size(0),), config.MAX_TIME_STEPS, dtype=torch.long)
