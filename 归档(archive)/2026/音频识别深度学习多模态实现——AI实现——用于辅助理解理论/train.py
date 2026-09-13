"""
train.py — 模型训练、验证、Early Stopping 与最佳模型保存
支持纯音频训练和多模态训练
"""
import os
import time
import torch
import torch.nn as nn
import torch.optim as optim
from torch.optim.lr_scheduler import ReduceLROnPlateau

import config
from model import EmotionClassifier, MultimodalEmotionClassifier


class EarlyStopping:
    """早停机制"""

    def __init__(self, patience=config.PATIENCE, mode="max", delta=0.0):
        self.patience = patience
        self.mode = mode
        self.delta = delta
        self.counter = 0
        self.best_score = None
        self.early_stop = False
        self.best_epoch = -1

    def __call__(self, epoch, score):
        if self.best_score is None:
            self.best_score = score
            self.best_epoch = epoch
            return False
        improved = (score > self.best_score + self.delta if self.mode == "max"
                    else score < self.best_score - self.delta)
        if improved:
            self.best_score = score
            self.counter = 0
            self.best_epoch = epoch
        else:
            self.counter += 1
            if self.counter >= self.patience:
                self.early_stop = True
                return True
        return False


# ==================== 纯音频训练 ====================

def train_epoch(model, dataloader, criterion, optimizer, device):
    model.train()
    running_loss = 0.0
    correct = 0
    total = 0
    for mfcc, labels, _ in dataloader:
        mfcc = mfcc.to(device)
        labels = labels.to(device)
        optimizer.zero_grad()
        logits, _ = model(mfcc)
        loss = criterion(logits, labels)
        loss.backward()
        optimizer.step()
        running_loss += loss.item() * mfcc.size(0)
        _, predicted = torch.max(logits, 1)
        total += labels.size(0)
        correct += (predicted == labels).sum().item()
    return running_loss / total, correct / total


@torch.no_grad()
def evaluate(model, dataloader, criterion, device):
    model.eval()
    running_loss = 0.0
    correct = 0
    total = 0
    all_labels = []
    all_preds = []
    for mfcc, labels, _ in dataloader:
        mfcc = mfcc.to(device)
        labels = labels.to(device)
        logits, _ = model(mfcc)
        loss = criterion(logits, labels)
        running_loss += loss.item() * mfcc.size(0)
        _, predicted = torch.max(logits, 1)
        total += labels.size(0)
        correct += (predicted == labels).sum().item()
        all_labels.extend(labels.cpu().tolist())
        all_preds.extend(predicted.cpu().tolist())
    return running_loss / total, correct / total, all_labels, all_preds


def train_model(model, train_loader, val_loader, device=config.DEVICE):
    """纯音频完整训练流程"""
    model = model.to(device)
    criterion = nn.CrossEntropyLoss()
    optimizer = optim.Adam(model.parameters(), lr=config.LEARNING_RATE,
                           weight_decay=config.WEIGHT_DECAY)
    scheduler = ReduceLROnPlateau(optimizer, mode="max", factor=0.5,
                                  patience=5, verbose=True)
    early_stopping = EarlyStopping(patience=config.PATIENCE, mode="max")
    history = {"train_loss": [], "val_loss": [], "train_acc": [], "val_acc": []}
    best_val_acc = 0.0
    best_epoch = -1

    print(f"\n{'='*60}")
    print(f"开始训练 | 设备: {device} | Epochs: {config.NUM_EPOCHS}")
    print(f"学习率: {config.LEARNING_RATE} | Batch Size: {config.BATCH_SIZE}")
    print(f"{'='*60}\n")

    for epoch in range(1, config.NUM_EPOCHS + 1):
        t_start = time.time()
        train_loss, train_acc = train_epoch(model, train_loader, criterion,
                                             optimizer, device)
        val_loss, val_acc, _, _ = evaluate(model, val_loader, criterion, device)
        scheduler.step(val_acc)
        history["train_loss"].append(train_loss)
        history["val_loss"].append(val_loss)
        history["train_acc"].append(train_acc)
        history["val_acc"].append(val_acc)
        elapsed = time.time() - t_start
        print(f"Epoch {epoch:3d}/{config.NUM_EPOCHS} | "
              f"Train Loss: {train_loss:.4f} | Train Acc: {train_acc:.4f} | "
              f"Val Loss: {val_loss:.4f} | Val Acc: {val_acc:.4f} | "
              f"Time: {elapsed:.1f}s")
        if val_acc > best_val_acc:
            best_val_acc = val_acc
            best_epoch = epoch
            torch.save({
                "epoch": epoch, "model_state_dict": model.state_dict(),
                "optimizer_state_dict": optimizer.state_dict(),
                "val_acc": val_acc, "val_loss": val_loss,
            }, config.MODEL_SAVE_PATH)
            print(f"  >> 保存最佳模型 (Val Acc: {val_acc:.4f})")
        if early_stopping(epoch, val_acc):
            print(f"\n早停触发于 Epoch {epoch}，最佳 Epoch {best_epoch}")
            break

    print(f"\n{'='*60}")
    print(f"训练完成 | 最佳 Epoch: {best_epoch} | 最佳 Val Acc: {best_val_acc:.4f}")
    print(f"模型已保存至: {config.MODEL_SAVE_PATH}")
    print(f"{'='*60}\n")
    return model, history


# ==================== 多模态训练 ====================

def train_multimodal_epoch(model, dataloader, criterion, optimizer, device):
    model.train()
    running_loss = 0.0
    correct = 0
    total = 0
    for mfcc, text_feat, labels, _ in dataloader:
        mfcc = mfcc.to(device)
        text_feat = text_feat.to(device)
        labels = labels.to(device)
        optimizer.zero_grad()
        logits, _ = model(mfcc, text_feat)
        loss = criterion(logits, labels)
        loss.backward()
        optimizer.step()
        running_loss += loss.item() * mfcc.size(0)
        _, predicted = torch.max(logits, 1)
        total += labels.size(0)
        correct += (predicted == labels).sum().item()
    return running_loss / total, correct / total


@torch.no_grad()
def evaluate_multimodal(model, dataloader, criterion, device):
    model.eval()
    running_loss = 0.0
    correct = 0
    total = 0
    all_labels = []
    all_preds = []
    for mfcc, text_feat, labels, _ in dataloader:
        mfcc = mfcc.to(device)
        text_feat = text_feat.to(device)
        labels = labels.to(device)
        logits, _ = model(mfcc, text_feat)
        loss = criterion(logits, labels)
        running_loss += loss.item() * mfcc.size(0)
        _, predicted = torch.max(logits, 1)
        total += labels.size(0)
        correct += (predicted == labels).sum().item()
        all_labels.extend(labels.cpu().tolist())
        all_preds.extend(predicted.cpu().tolist())
    return running_loss / total, correct / total, all_labels, all_preds


def train_multimodal_model(model, train_loader, val_loader, device=config.DEVICE):
    """多模态完整训练流程"""
    model = model.to(device)
    criterion = nn.CrossEntropyLoss()
    optimizer = optim.Adam(model.parameters(), lr=config.LEARNING_RATE,
                           weight_decay=config.WEIGHT_DECAY)
    scheduler = ReduceLROnPlateau(optimizer, mode="max", factor=0.5,
                                  patience=5, verbose=True)
    early_stopping = EarlyStopping(patience=config.PATIENCE, mode="max")
    history = {"train_loss": [], "val_loss": [], "train_acc": [], "val_acc": []}
    best_val_acc = 0.0
    best_epoch = -1

    print(f"\n{'='*60}")
    print(f"多模态训练开始 | 设备: {device} | Epochs: {config.NUM_EPOCHS}")
    print(f"{'='*60}\n")

    for epoch in range(1, config.NUM_EPOCHS + 1):
        t_start = time.time()
        train_loss, train_acc = train_multimodal_epoch(
            model, train_loader, criterion, optimizer, device)
        val_loss, val_acc, _, _ = evaluate_multimodal(
            model, val_loader, criterion, device)
        scheduler.step(val_acc)
        history["train_loss"].append(train_loss)
        history["val_loss"].append(val_loss)
        history["train_acc"].append(train_acc)
        history["val_acc"].append(val_acc)
        elapsed = time.time() - t_start
        print(f"Epoch {epoch:3d}/{config.NUM_EPOCHS} | "
              f"Train Loss: {train_loss:.4f} | Train Acc: {train_acc:.4f} | "
              f"Val Loss: {val_loss:.4f} | Val Acc: {val_acc:.4f} | "
              f"Time: {elapsed:.1f}s")
        if val_acc > best_val_acc:
            best_val_acc = val_acc
            best_epoch = epoch
            torch.save({
                "epoch": epoch, "model_state_dict": model.state_dict(),
                "optimizer_state_dict": optimizer.state_dict(),
                "val_acc": val_acc, "val_loss": val_loss,
                "model_type": "multimodal",
            }, config.MODEL_SAVE_PATH)
            print(f"  >> 保存最佳模型 (Val Acc: {val_acc:.4f})")
        if early_stopping(epoch, val_acc):
            print(f"\n早停触发于 Epoch {epoch}，最佳 Epoch {best_epoch}")
            break

    print(f"\n{'='*60}")
    print(f"多模态训练完成 | 最佳 Val Acc: {best_val_acc:.4f}")
    print(f"{'='*60}\n")
    return model, history


def load_best_model(model, device=config.DEVICE):
    """加载保存的最佳模型权重"""
    if not os.path.exists(config.MODEL_SAVE_PATH):
        raise FileNotFoundError(f"模型文件不存在: {config.MODEL_SAVE_PATH}")
    checkpoint = torch.load(config.MODEL_SAVE_PATH, map_location=device)
    model.load_state_dict(checkpoint["model_state_dict"])
    model = model.to(device)
    model_type = checkpoint.get("model_type", "audio")
    print(f"加载最佳模型 (Epoch {checkpoint['epoch']}, "
          f"Val Acc: {checkpoint['val_acc']:.4f}, Type: {model_type})")
    return model
