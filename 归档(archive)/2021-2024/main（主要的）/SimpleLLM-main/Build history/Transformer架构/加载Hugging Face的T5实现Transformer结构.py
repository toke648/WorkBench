# import torch
# import torch.nn as nn
# import torch.nn.functional as F
# from transformers import AutoTokenizer
# from modelscope import snapshot_download

# # Transformer 编码器
# class TransformerEncoder(nn.Module):
#     def __init__(self, vocab_size, d_model, num_heads, num_layers, dim_feedforward, max_len=512):
#         super().__init__()
#         self.embedding = nn.Embedding(vocab_size, d_model)
#         self.pos_embedding = nn.Parameter(torch.randn(max_len, d_model))
#         self.layers = nn.ModuleList([
#             nn.TransformerEncoderLayer(d_model, num_heads, dim_feedforward, dropout=0.1, batch_first=True)
#             for _ in range(num_layers)
#         ])
#         self.norm = nn.LayerNorm(d_model)

#     def forward(self, x, mask=None):
#         seq_len = x.shape[1]
#         x = self.embedding(x) + self.pos_embedding[:seq_len, :]  # 修正形状错误
#         for layer in self.layers:
#             x = layer(x, src_key_padding_mask=mask)
#         return self.norm(x)

# # Transformer 解码器
# class TransformerDecoder(nn.Module):
#     def __init__(self, vocab_size, d_model, num_heads, num_layers, dim_feedforward, max_len=512):
#         super().__init__()
#         self.embedding = nn.Embedding(vocab_size, d_model)
#         self.pos_embedding = nn.Parameter(torch.randn(max_len, d_model))
#         self.layers = nn.ModuleList([
#             nn.TransformerDecoderLayer(d_model, num_heads, dim_feedforward, dropout=0.1, batch_first=True)
#             for _ in range(num_layers)
#         ])
#         self.norm = nn.LayerNorm(d_model)
#         self.fc = nn.Linear(d_model, vocab_size)  # 修正 lm_head

#     def forward(self, x, encoder_output, tgt_mask=None):
#         seq_len = x.shape[1]
#         x = self.embedding(x) + self.pos_embedding[:seq_len, :]
#         for layer in self.layers:
#             x = layer(x, encoder_output, tgt_mask=tgt_mask, memory_key_padding_mask=tgt_mask)  # 修正 memory_key_padding_mask
#         return self.fc(self.norm(x))  # 修正 lm_head

# # 整体 Seq2Seq Transformer
# class Seq2SeqTransformer(nn.Module):
#     def __init__(self, vocab_size, d_model=768, num_heads=12, num_layers=6, dim_feedforward=3072):
#         super().__init__()
#         self.encoder = TransformerEncoder(vocab_size, d_model, num_heads, num_layers, dim_feedforward)
#         self.decoder = TransformerDecoder(vocab_size, d_model, num_heads, num_layers, dim_feedforward)

#     def forward(self, input_ids, decoder_input_ids):
#         encoder_output = self.encoder(input_ids)
#         decoder_output = self.decoder(decoder_input_ids, encoder_output)
#         return decoder_output

# # 加载 tokenizer
# model_id = 'charent/ChatLM-mini-Chinese'
# model_path = snapshot_download(model_id, cache_dir='./model_save')

# device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
# tokenizer = AutoTokenizer.from_pretrained(model_path)

# # 处理 bos_token_id 为空的情况
# if tokenizer.bos_token_id is None:
#     tokenizer.bos_token = "[BOS]"
#     tokenizer.bos_token_id = tokenizer.convert_tokens_to_ids("[BOS]")
# if tokenizer.eos_token_id is None:
#     tokenizer.eos_token = "[EOS]"
#     tokenizer.eos_token_id = tokenizer.convert_tokens_to_ids("[EOS]")

# # 初始化 Transformer
# model = Seq2SeqTransformer(vocab_size=30000).to(device)

# # 生成文本
# def generate(model, tokenizer, text, max_length=50):
#     model.eval()
#     input_ids = tokenizer.encode(text, return_tensors="pt").to(device)
    
#     # 先输入一个 `[BOS]` 作为解码器的起始 token
#     decoder_input_ids = torch.tensor([[tokenizer.bos_token_id]], device=device)

#     for _ in range(max_length):
#         with torch.no_grad():
#             outputs = model(input_ids, decoder_input_ids)
#         next_token_logits = outputs[:, -1, :]
#         next_token = next_token_logits.argmax(dim=-1, keepdim=True)

#         # 如果生成了 `[EOS]`，就停止
#         if next_token.item() == tokenizer.eos_token_id:
#             break

#         decoder_input_ids = torch.cat([decoder_input_ids, next_token], dim=-1)

#     return tokenizer.decode(decoder_input_ids.squeeze(), skip_special_tokens=True)

# # 测试
# text = "你是谁？"
# response = generate(model, tokenizer, text)
# print(response)


import torch
import torch.nn as nn
import torch.nn.functional as F
from transformers import AutoTokenizer
from modelscope import snapshot_download

# Transformer 编码器
class TransformerEncoder(nn.Module):
    def __init__(self, vocab_size, d_model, num_heads, num_layers, dim_feedforward, max_len=512):
        super().__init__()
        self.embedding = nn.Embedding(vocab_size, d_model)
        self.pos_embedding = nn.Parameter(torch.randn(max_len, d_model))
        self.layers = nn.ModuleList([
            nn.TransformerEncoderLayer(d_model, num_heads, dim_feedforward, dropout=0.1, batch_first=True)
            for _ in range(num_layers)
        ])
        self.norm = nn.LayerNorm(d_model)

    def forward(self, x, mask=None):
        seq_len = x.shape[1]
        x = self.embedding(x) + self.pos_embedding[:seq_len, :]  # 修正形状错误
        for layer in self.layers:
            x = layer(x, src_key_padding_mask=mask)
        return self.norm(x)

# Transformer 解码器
class TransformerDecoder(nn.Module):
    def __init__(self, vocab_size, d_model, num_heads, num_layers, dim_feedforward, max_len=512):
        super().__init__()
        self.embedding = nn.Embedding(vocab_size, d_model)
        self.pos_embedding = nn.Parameter(torch.randn(max_len, d_model))
        self.layers = nn.ModuleList([
            nn.TransformerDecoderLayer(d_model, num_heads, dim_feedforward, dropout=0.1, batch_first=True)
            for _ in range(num_layers)
        ])
        self.norm = nn.LayerNorm(d_model)
        self.fc = nn.Linear(d_model, vocab_size)  # 修正 lm_head

    def forward(self, x, encoder_output, tgt_mask=None):
        seq_len = x.shape[1]
        x = self.embedding(x) + self.pos_embedding[:seq_len, :]
        for layer in self.layers:
            x = layer(x, encoder_output, tgt_mask=tgt_mask, memory_mask=tgt_mask)  # 修正 memory_mask
        return self.fc(self.norm(x))  # 修正 lm_head

# 整体 Seq2Seq Transformer
class Seq2SeqTransformer(nn.Module):
    def __init__(self, vocab_size, d_model=768, num_heads=12, num_layers=6, dim_feedforward=3072):
        super().__init__()
        self.encoder = TransformerEncoder(vocab_size, d_model, num_heads, num_layers, dim_feedforward)
        self.decoder = TransformerDecoder(vocab_size, d_model, num_heads, num_layers, dim_feedforward)

    def forward(self, input_ids, decoder_input_ids):
        encoder_output = self.encoder(input_ids)
        decoder_output = self.decoder(decoder_input_ids, encoder_output)
        return decoder_output

# 加载 tokenizer
model_id = 'charent/ChatLM-mini-Chinese'
model_path = snapshot_download(model_id, cache_dir='./model_save')

device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
tokenizer = AutoTokenizer.from_pretrained(model_path)

# 处理 bos_token_id 为空的情况
if tokenizer.bos_token_id is None:
    tokenizer.bos_token = "[BOS]"
    tokenizer.bos_token_id = tokenizer.convert_tokens_to_ids("[BOS]")
if tokenizer.eos_token_id is None:
    tokenizer.eos_token = "[EOS]"
    tokenizer.eos_token_id = tokenizer.convert_tokens_to_ids("[EOS]")

# 初始化 Transformer
model = Seq2SeqTransformer(vocab_size=30000).to(device)

# 生成文本
def generate(model, tokenizer, text, max_length=50):
    model.eval()
    input_ids = tokenizer.encode(text, return_tensors="pt").to(device)
    
    # 先输入一个 [BOS] 作为解码器的起始 token
    decoder_input_ids = torch.tensor([[tokenizer.bos_token_id]], device=device)

    for _ in range(max_length):
        with torch.no_grad():
            outputs = model(input_ids, decoder_input_ids)
        next_token_logits = outputs[:, -1, :]
        next_token = next_token_logits.argmax(dim=-1, keepdim=True)

        # 如果生成了 [EOS]，就停止
        if next_token.item() == tokenizer.eos_token_id:
            break

        decoder_input_ids = torch.cat([decoder_input_ids, next_token], dim=-1)

    return tokenizer.decode(decoder_input_ids.squeeze(), skip_special_tokens=True)

# 测试
text = "你是谁？"
response = generate(model, tokenizer, text)
print("Generated response:", response)

