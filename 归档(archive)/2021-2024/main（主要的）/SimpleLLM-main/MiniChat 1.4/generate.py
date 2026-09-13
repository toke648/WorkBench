import math
import os
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader, random_split
from tokenizers import Tokenizer
from tqdm import tqdm

# 环境配置
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# 超参数配置
class Config:
    # 数据参数
    data_path = "./processed_data.txt"
    max_length = 128  # 最大序列长度
    batch_size = 32
    train_ratio = 0.9  # 训练集比例
    
    # 模型参数
    d_model = 256
    num_heads = 8
    num_layers = 4
    dim_feedforward = 1024
    dropout = 0.1
    
    # 训练参数
    lr = 5e-5
    weight_decay = 0.01
    epochs = 20
    warmup_steps = 4000
    label_smoothing = 0.1
    grad_clip = 1.0  # 梯度裁剪
    
    # 生成参数
    temperature = 0.7
    top_k = 40

# 加载分词器
tokenizer = Tokenizer.from_file("bpe_tokenizer.json")
vocab_size = tokenizer.get_vocab_size()
bos_id = tokenizer.token_to_id("<bos>")
eos_id = tokenizer.token_to_id("<eos>")
pad_id = tokenizer.token_to_id("<pad>")

# 增强的Transformer模型
class EnhancedTransformer(nn.Module):
    def __init__(self, config):
        super().__init__()
        self.config = config
        
        # 词嵌入层（带缩放）
        self.embedding = nn.Embedding(vocab_size, config.d_model)
        self.emb_scale = math.sqrt(config.d_model)
        
        # 位置编码
        self.positional_encoding = self._init_positional_encoding()
        
        # Transformer编码器
        encoder_layer = nn.TransformerEncoderLayer(
            d_model=config.d_model,
            nhead=config.num_heads,
            dim_feedforward=config.dim_feedforward,
            dropout=config.dropout,
            activation='gelu'
        )
        self.encoder = nn.TransformerEncoder(encoder_layer, config.num_layers)
        
        # Transformer解码器
        decoder_layer = nn.TransformerDecoderLayer(
            d_model=config.d_model,
            nhead=config.num_heads,
            dim_feedforward=config.dim_feedforward,
            dropout=config.dropout,
            activation='gelu'
        )
        self.decoder = nn.TransformerDecoder(decoder_layer, config.num_layers)
        
        # 增强输出层
        self.output_layer = nn.Sequential(
            nn.Linear(config.d_model, config.dim_feedforward),
            nn.GELU(),
            nn.Linear(config.dim_feedforward, vocab_size))
        
        self.dropout = nn.Dropout(config.dropout)
        
        # 初始化参数
        self._init_weights()

    def _init_positional_encoding(self):
        position = torch.arange(Config.max_length).unsqueeze(1)
        div_term = torch.exp(torch.arange(0, self.config.d_model, 2) * 
                   (-math.log(10000.0) / self.config.d_model))
        pe = torch.zeros(1, Config.max_length, self.config.d_model)
        pe[0, :, 0::2] = torch.sin(position * div_term)
        pe[0, :, 1::2] = torch.cos(position * div_term)
        return pe.to(device)
    
    def _init_weights(self):
        for p in self.parameters():
            if p.dim() > 1:
                nn.init.xavier_uniform_(p)

    def forward(self, src, tgt):
        # 嵌入层处理
        src_emb = self.embedding(src) * self.emb_scale + self.positional_encoding[:, :src.size(1)]
        tgt_emb = self.embedding(tgt) * self.emb_scale + self.positional_encoding[:, :tgt.size(1)]
        
        # 调整维度并添加dropout
        src_emb = self.dropout(src_emb.transpose(0, 1))  # (S, B, D)
        tgt_emb = self.dropout(tgt_emb.transpose(0, 1))
        
        # 创建掩码
        src_mask = (src == pad_id)
        tgt_mask = self._generate_square_subsequent_mask(tgt.size(1))
        
        # 编码器前向
        memory = self.encoder(src_emb, src_key_padding_mask=src_mask)
        
        # 解码器前向
        output = self.decoder(
            tgt_emb, memory,
            tgt_mask=tgt_mask,
            memory_key_padding_mask=src_mask
        )
        
        # 输出处理
        output = output.transpose(0, 1)  # (B, S, D)
        return self.output_layer(output)

    def _generate_square_subsequent_mask(self, sz):
        mask = (torch.triu(torch.ones(sz, sz)) == 1).transpose(0, 1)
        mask = mask.float().masked_fill(mask == 0, float('-inf'))
        return mask.to(device)

# 初始化模型
config = Config()
model = EnhancedTransformer(config).to(device)

# 生成函数
def generate_response(model, input_text, max_length=50):
    model.load_state_dict(torch.load("best_model.pth", map_location=device))
    model.eval()
    
    # 编码输入
    input_ids = [bos_id] + tokenizer.encode(input_text).ids[:Config.max_length-2] + [eos_id]
    src = torch.tensor([input_ids], device=device)
    
    # 生成序列
    generated = [bos_id]
    for _ in range(max_length):
        tgt = torch.tensor([generated], device=device)
        
        with torch.no_grad():
            output = model(src, tgt)
            logits = output[0, -1, :] / Config.temperature
            topk = torch.topk(logits, Config.top_k)
            probs = torch.softmax(topk.values, dim=-1)
            next_token = topk.indices[torch.multinomial(probs, 1)].item()
        
        if next_token == eos_id:
            break
        generated.append(next_token)
    
    # 解码并过滤特殊标记
    return tokenizer.decode([t for t in generated if t not in [bos_id, eos_id, pad_id]])

# 交互测试
while True:
    try:
        user_input = input("You: ")
        if user_input.lower() in ["exit", "quit"]:
            break
        response = generate_response(model, user_input)
        print(f"Bot: {response}")
    except KeyboardInterrupt:
        break