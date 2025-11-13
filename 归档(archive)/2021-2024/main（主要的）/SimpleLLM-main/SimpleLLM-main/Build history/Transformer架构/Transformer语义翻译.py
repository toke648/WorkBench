import torch
import torch.nn as nn

# Transformer 编码器
class TransformerEncoder(nn.Module):
    def __init__(self, vocab_size, d_model, num_heads, num_layers, dim_feedforward, max_len=512):
        super().__init__()
        self.embedding = nn.Embedding(vocab_size, d_model)
        self.pos_embedding = nn.Parameter(torch.randn(1, max_len, d_model))
        self.layers = nn.ModuleList([
            nn.TransformerEncoderLayer(d_model, num_heads, dim_feedforward, dropout=0.1, batch_first=True)
            for _ in range(num_layers)
        ])
        self.norm = nn.LayerNorm(d_model)

    def forward(self, x):
        seq_len = x.shape[1]
        x = self.embedding(x) + self.pos_embedding[:, :seq_len, :]
        for layer in self.layers:
            x = layer(x)
        return self.norm(x)

# Transformer 解码器
class TransformerDecoder(nn.Module):
    def __init__(self, vocab_size, d_model, num_heads, num_layers, dim_feedforward, max_len=512):
        super().__init__()
        self.embedding = nn.Embedding(vocab_size, d_model)
        self.pos_embedding = nn.Parameter(torch.randn(1, max_len, d_model))
        self.layers = nn.ModuleList([
            nn.TransformerDecoderLayer(d_model, num_heads, dim_feedforward, dropout=0.1, batch_first=True)
            for _ in range(num_layers)
        ])
        self.norm = nn.LayerNorm(d_model)
        self.fc = nn.Linear(d_model, vocab_size)

    def forward(self, x, memory):
        seq_len = x.shape[1]
        x = self.embedding(x) + self.pos_embedding[:, :seq_len, :]
        for layer in self.layers:
            x = layer(x, memory)
        return self.fc(self.norm(x))

# Seq2Seq Transformer
class Seq2SeqTransformer(nn.Module):
    def __init__(self, vocab_size, d_model=512, num_heads=8, num_layers=6, dim_feedforward=2048):
        super().__init__()
        self.encoder = TransformerEncoder(vocab_size, d_model, num_heads, num_layers, dim_feedforward)
        self.decoder = TransformerDecoder(vocab_size, d_model, num_heads, num_layers, dim_feedforward)

    def forward(self, src, tgt):
        encoder_output = self.encoder(src)
        decoder_output = self.decoder(tgt, encoder_output)
        return decoder_output


import torch.optim as optim

# 加载 tokenizer
tokenizer = Tokenizer.from_file("custom_tokenizer.json")

# 处理数据
train_data = [
    ("你好，世界！", "Hello, world!"),
    ("今天天气怎么样？", "How is the weather today?"),
]

def tokenize_pairs(pairs):
    src_texts, tgt_texts = zip(*pairs)
    src_tensors = [torch.tensor(tokenizer.encode(t).ids) for t in src_texts]
    tgt_tensors = [torch.tensor(tokenizer.encode(t).ids) for t in tgt_texts]
    return src_tensors, tgt_tensors

src_tensors, tgt_tensors = tokenize_pairs(train_data)

# 初始化模型
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model = Seq2SeqTransformer(vocab_size=tokenizer.get_vocab_size()).to(device)

# 训练
optimizer = optim.Adam(model.parameters(), lr=5e-4)
criterion = nn.CrossEntropyLoss()

for epoch in range(100):
    total_loss = 0
    for src, tgt in zip(src_tensors, tgt_tensors):
        src, tgt = src.to(device), tgt.to(device)
        
        optimizer.zero_grad()
        output = model(src.unsqueeze(0), tgt.unsqueeze(0)[:, :-1])
        loss = criterion(output.view(-1, output.shape[-1]), tgt[:, 1:].view(-1))
        loss.backward()
        optimizer.step()
        
        total_loss += loss.item()
    print(f"Epoch {epoch}: Loss = {total_loss:.4f}")


def translate(model, tokenizer, text, max_length=50):
    model.eval()
    src_tensor = torch.tensor(tokenizer.encode(text).ids, device=device).unsqueeze(0)
    
    tgt_tokens = torch.tensor([[tokenizer.token_to_id("[BOS]")]], device=device)
    
    for _ in range(max_length):
        with torch.no_grad():
            output = model(src_tensor, tgt_tokens)
        next_token = output[:, -1, :].argmax(dim=-1, keepdim=True)
        
        if next_token.item() == tokenizer.token_to_id("[EOS]"):
            break
        
        tgt_tokens = torch.cat([tgt_tokens, next_token], dim=-1)

    return tokenizer.decode(tgt_tokens.squeeze().tolist(), skip_special_tokens=True)

# 测试翻译
text = "你好，世界！"
translation = translate(model, tokenizer, text)
print(f"翻译结果: {translation}")
