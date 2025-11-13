import torch
import torch.nn as nn
import torch.optim as optim
import torch.nn.functional as F
import numpy as np

"""
定义 Tokenizer
我们使用简单的字符级 Tokenizer（方便测试），但实际应用中会用 BPE、WordPiece 或 SentencePiece。
"""

class SimpleTokenizer:
    def __init__(self, text):
        # 统计字符出现频率，构建词表
        self.chars = sorted(set(text)) # 构建字符集
        self.vocab_size = len(self.chars) # 构建字符集大小
        self.char_to_idx = {ch: i for i, ch in enumerate(self.chars)}
        self.idx_to_char = {i: ch for i, ch in enumerate(self.chars)}
    
    def encode(self, text):
        return [self.char_to_idx[ch] for ch in text] # 编码
    
    def decode(self, indices):
        return ''.join([self.idx_to_char[idx] for idx in indices]) # 解码
    
text = "hello world! this is a simple LLM."
tokenizer = SimpleTokenizer(text)
encoded = tokenizer.encode("hello")
print("编码:", encoded)
print("解码:", tokenizer.decode(encoded))

class TransformerDecoder(nn.Module):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
    
    def forward(self, *args, **kwargs):
        pass

vocab_size = tokenizer.chars
print(vocab_size)