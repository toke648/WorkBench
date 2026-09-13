"""
asr_module.py — 语音转文本模块（Whisper ASR）
将 RAVDESS 音频转录为英文文本，支持缓存避免重复推理
"""
import os
import json
import warnings
import numpy as np

import config

# 抑制 Whisper 的 FP16 警告
warnings.filterwarnings("ignore", category=UserWarning)


class ASRProcessor:
    """
    基于 OpenAI Whisper 的语音转文本处理器

    工作流：
    1. 检查缓存（asr_cache/ 目录下 .txt 文件）
    2. 缓存未命中时使用 Whisper 推理并写入缓存
    3. 返回转录文本
    """

    def __init__(self, model_size=config.WHISPER_MODEL_SIZE,
                 cache_dir=config.ASR_CACHE_DIR):
        self.model_size = model_size
        self.cache_dir = cache_dir
        self.model = None
        self._available = None  # None=未检测, True/False
        os.makedirs(self.cache_dir, exist_ok=True)

    def _load_model(self):
        """延迟加载 Whisper 模型"""
        if self.model is not None:
            return True
        if self._available is False:
            return False
        try:
            import whisper
            self.model = whisper.load_model(self.model_size)
            self._available = True
            print(f"[ASR] Whisper '{self.model_size}' 模型加载成功")
            return True
        except ImportError:
            print("[ASR] openai-whisper 未安装，请执行: pip install openai-whisper")
            self._available = False
        except Exception as e:
            print(f"[ASR] Whisper 模型加载失败: {e}")
            self._available = False
        return False

    def is_available(self):
        """检查 ASR 是否可用"""
        if self._available is None:
            self._load_model()
        return self._available is True

    def _cache_path(self, audio_path):
        """获取缓存文件路径"""
        base = os.path.splitext(os.path.basename(audio_path))[0]
        return os.path.join(self.cache_dir, base + ".txt")

    def transcribe(self, audio_path, use_cache=True):
        """
        将音频转为文本

        Args:
            audio_path: .wav 文件路径
            use_cache: 是否使用缓存

        Returns:
            str: 转录文本，失败返回 ""
        """
        cache_path = self._cache_path(audio_path)

        # 读取缓存
        if use_cache and os.path.exists(cache_path):
            try:
                with open(cache_path, "r", encoding="utf-8") as f:
                    text = f.read().strip()
                if text:
                    return text
            except Exception:
                pass

        # Whisper 推理
        if not self._load_model():
            return ""

        try:
            result = self.model.transcribe(
                audio_path,
                language="en",
                fp16=False,
                verbose=False,
            )
            text = result["text"].strip()
            # 写入缓存
            if text:
                with open(cache_path, "w", encoding="utf-8") as f:
                    f.write(text)
            return text
        except Exception as e:
            print(f"[ASR] 转录失败 {os.path.basename(audio_path)}: {e}")
            return ""

    def transcribe_batch(self, audio_paths, use_cache=True, verbose=True):
        """
        批量转录，显示进度

        Returns:
            dict: {audio_path: transcribed_text}
        """
        results = {}
        total = len(audio_paths)
        for i, path in enumerate(audio_paths):
            text = self.transcribe(path, use_cache=use_cache)
            results[path] = text
            if verbose and (i + 1) % 50 == 0:
                print(f"  [ASR] 进度: {i+1}/{total}")
        if verbose:
            print(f"  [ASR] 转录完成: {total} 条音频")
        return results
