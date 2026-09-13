"""
config.py — 多模态语音情绪识别系统全局配置参数
"""
import os

# ==================== 数据集配置 ====================
DATASET_ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "dataset")

# 情绪映射：RAVDESS 文件名第3段 → 情绪标签
EMOTION_MAP = {
    "01": "neutral",
    "03": "happy",
    "04": "sad",
    "05": "angry",
}

EMOTION_TO_IDX = {
    "neutral": 0,
    "happy": 1,
    "sad": 2,
    "angry": 3,
}

IDX_TO_EMOTION = {v: k for k, v in EMOTION_TO_IDX.items()}

EMOTION_CN = {
    "neutral": "中性",
    "happy": "高兴",
    "sad": "悲伤",
    "angry": "愤怒",
}

NUM_CLASSES = len(EMOTION_MAP)  # 4

# ==================== 音频特征参数 ====================
SAMPLE_RATE = 22050
N_MFCC = 40
N_MELS = 128
HOP_LENGTH = 512
N_FFT = 2048
DURATION = 3.0
MAX_TIME_STEPS = int(SAMPLE_RATE * DURATION / HOP_LENGTH) + 1  # ≈130

# ==================== 音频模型参数 ====================
AUDIO_INPUT_SIZE = N_MFCC
AUDIO_HIDDEN_SIZE = 128
AUDIO_NUM_LAYERS = 2
AUDIO_DROPOUT = 0.5
AUDIO_BIDIRECTIONAL = True
AUDIO_ATTENTION_SIZE = 64
AUDIO_FEATURE_DIM = AUDIO_HIDDEN_SIZE * 2 if AUDIO_BIDIRECTIONAL else AUDIO_HIDDEN_SIZE  # 256

# ==================== 文本模型参数（ASR + NLP） ====================
WHISPER_MODEL_SIZE = "tiny"       # tiny(~39M) / base(~74M) / small(~244M)
TFIDF_MAX_FEATURES = 500          # TF-IDF 最大特征数
TEXT_HIDDEN_SIZE = 128            # 文本编码器隐藏维度
TEXT_FEATURE_DIM = 128            # 文本特征输出维度
TEXT_DROPOUT = 0.3

# ASR 预处理缓存目录（避免重复推理）
ASR_CACHE_DIR = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "asr_cache"
)

# ==================== 多模态融合参数 ====================
FUSION_HIDDEN_SIZE = 128
FUSION_DROPOUT = 0.5
# 是否启用多模态（若 Whisper 不可用则自动回退到纯音频模式）
USE_MULTIMODAL = True

# ==================== 训练参数 ====================
BATCH_SIZE = 32
LEARNING_RATE = 0.001
WEIGHT_DECAY = 1e-4
NUM_EPOCHS = 50
PATIENCE = 10

# ==================== 数据划分 ====================
TRAIN_RATIO = 0.7
VAL_RATIO = 0.15
TEST_RATIO = 0.15
RANDOM_SEED = 42

# ==================== 输出路径 ====================
MODEL_SAVE_PATH = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "best_model.pth"
)
LOG_DIR = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "logs"
)

import torch
DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")
