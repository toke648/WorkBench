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

# 数据集类
class QADataset(Dataset):
    def __init__(self, file_path, tokenizer, max_length):
        self.pairs = []
        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                if '\t' in line:
                    q, a = line.strip().split('\t')
                    # 动态截断并添加特殊标记
                    q_ids = [bos_id] + tokenizer.encode(q).ids[:max_length-2] + [eos_id]
                    a_ids = [bos_id] + tokenizer.encode(a).ids[:max_length-2] + [eos_id]
                    self.pairs.append((q_ids, a_ids))
    
    def __len__(self):
        return len(self.pairs)
    
    def __getitem__(self, idx):
        q, a = self.pairs[idx]
        return torch.tensor(q), torch.tensor(a)

# 数据整理函数
def collate_fn(batch):
    src_batch, tgt_batch = zip(*batch)
    
    # 动态padding
    src = torch.nn.utils.rnn.pad_sequence(
        src_batch, padding_value=pad_id, batch_first=True)
    tgt = torch.nn.utils.rnn.pad_sequence(
        tgt_batch, padding_value=pad_id, batch_first=True)
    
    return src, tgt

# 初始化数据集
full_dataset = QADataset(Config.data_path, tokenizer, Config.max_length)
train_size = int(Config.train_ratio * len(full_dataset))
val_size = len(full_dataset) - train_size
train_dataset, val_dataset = random_split(full_dataset, [train_size, val_size])

# 数据加载器
train_loader = DataLoader(
    train_dataset, 
    batch_size=Config.batch_size, 
    shuffle=True, 
    collate_fn=collate_fn
)
val_loader = DataLoader(
    val_dataset, 
    batch_size=Config.batch_size, 
    collate_fn=collate_fn
)

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

# 标签平滑损失
class LabelSmoothingLoss(nn.Module):
    def __init__(self, smoothing=0.1):
        super().__init__()
        self.confidence = 1.0 - smoothing
        self.smoothing = smoothing

    def forward(self, pred, target):
        pred = pred.log_softmax(dim=-1)
        n_class = pred.size(-1)
        true_dist = torch.full_like(pred, self.smoothing / (n_class - 1))
        true_dist.scatter_(-1, target.unsqueeze(-1), self.confidence)
        mask = (target == pad_id)
        true_dist[mask] = 0
        return torch.mean(torch.sum(-true_dist * pred, dim=-1))

# 训练准备
optimizer = optim.AdamW(
    model.parameters(), 
    lr=config.lr, 
    weight_decay=config.weight_decay
)

scheduler = optim.lr_scheduler.LambdaLR(
    optimizer,
    lr_lambda=lambda step: min(
        (step + 1) ** -0.5, 
        (step + 1) * config.warmup_steps ** -1.5
    )
)

loss_fn = LabelSmoothingLoss(config.label_smoothing)

# 训练循环
def train_epoch(model, loader, optimizer, scheduler):
    model.train()
    total_loss = 0
    for src, tgt in tqdm(loader, desc="Training"):
        src, tgt = src.to(device), tgt.to(device)
        
        optimizer.zero_grad()
        output = model(src, tgt[:, :-1])
        
        loss = loss_fn(output.reshape(-1, vocab_size), tgt[:, 1:].reshape(-1))
        loss.backward()
        
        torch.nn.utils.clip_grad_norm_(model.parameters(), config.grad_clip)
        optimizer.step()
        scheduler.step()
        
        total_loss += loss.item()
    return total_loss / len(loader)

# 验证循环
def evaluate(model, loader):
    model.eval()
    total_loss = 0
    with torch.no_grad():
        for src, tgt in tqdm(loader, desc="Validating"):
            src, tgt = src.to(device), tgt.to(device)
            output = model(src, tgt[:, :-1])
            loss = loss_fn(output.reshape(-1, vocab_size), tgt[:, 1:].reshape(-1))
            total_loss += loss.item()
    return total_loss / len(loader)

# 主训练流程
best_val_loss = float('inf')
for epoch in range(config.epochs):
    train_loss = train_epoch(model, train_loader, optimizer, scheduler)
    val_loss = evaluate(model, val_loader)
    
    print(f"Epoch {epoch+1}/{config.epochs}")
    print(f"Train Loss: {train_loss:.4f} | Val Loss: {val_loss:.4f}")
    
    # 保存最佳模型
    if val_loss < best_val_loss:
        best_val_loss = val_loss
        torch.save(model.state_dict(), "best_model.pth")
        print("Saved best model!")

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