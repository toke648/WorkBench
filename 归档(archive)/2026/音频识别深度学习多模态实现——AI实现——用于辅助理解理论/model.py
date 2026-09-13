"""
model.py — 多模态语音情绪识别模型定义

模型架构：
  - AudioEncoder: BiGRU + Self-Attention → 音频特征向量 (256维)
  - TextEncoder:  MLP + Self-Attention → 文本特征向量 (128维)
  - MultimodalEmotionClassifier: [音频;文本] 融合 → 分类器 → 4 类情绪
  - EmotionClassifier: 纯音频单模态模型（fallback 兼容）
"""
import torch
import torch.nn as nn
import torch.nn.functional as F


class SelfAttention(nn.Module):
    """多头自注意力层，聚合时间步信息"""

    def __init__(self, input_dim, hidden_dim):
        super(SelfAttention, self).__init__()
        self.query = nn.Linear(input_dim, hidden_dim)
        self.key = nn.Linear(input_dim, hidden_dim)
        self.value = nn.Linear(input_dim, hidden_dim)
        self.scale = hidden_dim ** 0.5

    def forward(self, x, mask=None):
        Q = self.query(x)
        K = self.key(x)
        V = self.value(x)
        scores = torch.bmm(Q, K.transpose(1, 2)) / self.scale
        if mask is not None:
            mask_exp = mask.unsqueeze(1).expand(-1, scores.size(1), -1)
            scores = scores.masked_fill(~mask_exp, -1e9)
        attn_weights = F.softmax(scores, dim=-1)
        attended = torch.bmm(attn_weights, V)
        context = attended.mean(dim=1)
        avg_attn = attn_weights.mean(dim=1)
        return context, avg_attn


class AudioEncoder(nn.Module):
    """BiGRU + Self-Attention 音频编码器"""

    def __init__(self, input_size, hidden_size, num_layers,
                 dropout=0.5, bidirectional=True, attention_size=64):
        super(AudioEncoder, self).__init__()
        self.hidden_size = hidden_size
        self.bidirectional = bidirectional
        self.gru = nn.GRU(
            input_size=input_size, hidden_size=hidden_size,
            num_layers=num_layers, batch_first=True,
            dropout=dropout if num_layers > 1 else 0.0,
            bidirectional=bidirectional,
        )
        gru_output_dim = hidden_size * 2 if bidirectional else hidden_size
        self.output_dim = gru_output_dim
        self.attention = SelfAttention(gru_output_dim, attention_size)

    def forward(self, x, lengths=None):
        batch_size, seq_len, _ = x.shape
        mask = None
        if lengths is not None:
            mask = torch.arange(seq_len, device=x.device).unsqueeze(0) < lengths.unsqueeze(1)
            lengths_cpu = lengths.cpu()
            x_packed = nn.utils.rnn.pack_padded_sequence(
                x, lengths_cpu, batch_first=True, enforce_sorted=False)
            gru_out_packed, _ = self.gru(x_packed)
            gru_out, _ = nn.utils.rnn.pad_packed_sequence(
                gru_out_packed, batch_first=True, total_length=seq_len)
        else:
            gru_out, _ = self.gru(x)
        context, attn_weights = self.attention(gru_out, mask)
        return context, attn_weights


class TextEncoder(nn.Module):
    """文本编码器：MLP + 注意力加权 → 文本特征向量"""

    def __init__(self, input_dim, hidden_size=128, output_dim=128,
                 dropout=0.3, attention_size=64):
        super(TextEncoder, self).__init__()
        self.input_dim = input_dim
        self.output_dim = output_dim
        self.proj = nn.Sequential(
            nn.Linear(input_dim, hidden_size),
            nn.ReLU(),
            nn.Dropout(dropout),
            nn.Linear(hidden_size, hidden_size),
        )
        self.attn_fc = nn.Sequential(
            nn.Linear(hidden_size, attention_size),
            nn.Tanh(),
            nn.Linear(attention_size, 1),
        )
        self.output_proj = nn.Linear(hidden_size, output_dim)

    def forward(self, x):
        h = self.proj(x)
        attn_scores = self.attn_fc(h)
        attn_weights = F.softmax(attn_scores, dim=0)
        weighted = h * attn_weights
        text_feat = self.output_proj(weighted)
        return text_feat


class MultimodalEmotionClassifier(nn.Module):
    """多模态融合情绪分类模型"""

    def __init__(self, audio_encoder, text_encoder,
                 num_classes=4, fusion_hidden=128, dropout=0.5):
        super(MultimodalEmotionClassifier, self).__init__()
        self.audio_encoder = audio_encoder
        self.text_encoder = text_encoder
        fusion_input_dim = audio_encoder.output_dim + text_encoder.output_dim
        self.fusion = nn.Sequential(
            nn.LayerNorm(fusion_input_dim),
            nn.Linear(fusion_input_dim, fusion_hidden),
            nn.ReLU(),
            nn.Dropout(dropout),
            nn.Linear(fusion_hidden, fusion_hidden // 2),
            nn.ReLU(),
            nn.Dropout(dropout),
            nn.Linear(fusion_hidden // 2, num_classes),
        )

    def forward(self, audio_x, text_x, audio_lengths=None):
        audio_feat, audio_attn = self.audio_encoder(audio_x, audio_lengths)
        text_feat = self.text_encoder(text_x)
        fused = torch.cat([audio_feat, text_feat], dim=1)
        logits = self.fusion(fused)
        return logits, audio_attn


class EmotionClassifier(nn.Module):
    """纯音频 BiGRU + Self-Attention 分类器（单模态 fallback）"""

    def __init__(self, input_size, hidden_size, num_layers, num_classes,
                 dropout=0.5, bidirectional=True, attention_size=64):
        super(EmotionClassifier, self).__init__()
        self.encoder = AudioEncoder(
            input_size=input_size, hidden_size=hidden_size,
            num_layers=num_layers, dropout=dropout,
            bidirectional=bidirectional, attention_size=attention_size)
        gru_output_dim = self.encoder.output_dim
        self.classifier = nn.Sequential(
            nn.LayerNorm(gru_output_dim),
            nn.Linear(gru_output_dim, 64),
            nn.ReLU(),
            nn.Dropout(dropout),
            nn.Linear(64, num_classes),
        )

    def forward(self, x, lengths=None):
        context, attn_weights = self.encoder(x, lengths)
        logits = self.classifier(context)
        return logits, attn_weights


def count_parameters(model):
    return sum(p.numel() for p in model.parameters() if p.requires_grad)


def build_multimodal_model(tfidf_dim=None):
    import config as cfg
    if tfidf_dim is None:
        tfidf_dim = cfg.TFIDF_MAX_FEATURES
    audio_encoder = AudioEncoder(
        input_size=cfg.AUDIO_INPUT_SIZE,
        hidden_size=cfg.AUDIO_HIDDEN_SIZE,
        num_layers=cfg.AUDIO_NUM_LAYERS,
        dropout=cfg.AUDIO_DROPOUT,
        bidirectional=cfg.AUDIO_BIDIRECTIONAL,
        attention_size=cfg.AUDIO_ATTENTION_SIZE,
    )
    text_encoder = TextEncoder(
        input_dim=tfidf_dim,
        hidden_size=cfg.TEXT_HIDDEN_SIZE,
        output_dim=cfg.TEXT_FEATURE_DIM,
        dropout=cfg.TEXT_DROPOUT,
    )
    return MultimodalEmotionClassifier(
        audio_encoder=audio_encoder,
        text_encoder=text_encoder,
        num_classes=cfg.NUM_CLASSES,
        fusion_hidden=cfg.FUSION_HIDDEN_SIZE,
        dropout=cfg.FUSION_DROPOUT,
    )


def build_audio_model():
    import config as cfg
    return EmotionClassifier(
        input_size=cfg.AUDIO_INPUT_SIZE,
        hidden_size=cfg.AUDIO_HIDDEN_SIZE,
        num_layers=cfg.AUDIO_NUM_LAYERS,
        num_classes=cfg.NUM_CLASSES,
        dropout=cfg.AUDIO_DROPOUT,
        bidirectional=cfg.AUDIO_BIDIRECTIONAL,
        attention_size=cfg.AUDIO_ATTENTION_SIZE,
    )
