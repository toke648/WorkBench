from tokenizers import Tokenizer

# 加载 BPE Tokenizer
tokenizer = Tokenizer.from_file("bpe_tokenizer.json")

# 获取词表大小
vocab_size = tokenizer.get_vocab_size()
print("词表大小:", vocab_size)

import torch

def create_training_data(text, tokenizer, seq_length=50):
    """将文本转换为 Token ID，并生成训练样本"""
    token_ids = tokenizer.encode(text).ids
    inputs, targets = [], []

    for i in range(len(token_ids) - seq_length):
        inputs.append(token_ids[i:i+seq_length])
        targets.append(token_ids[i+1:i+seq_length+1])

    return torch.tensor(inputs), torch.tensor(targets)

# 读取训练数据
file_paths = ["data1.txt", "data2.txt"]
text = "\n".join([open(f, "r", encoding="utf-8").read() for f in file_paths])

# 生成训练样本
inputs, targets = create_training_data(text, tokenizer)
print("训练数据大小:", inputs.shape, targets.shape)

from torch.utils.data import DataLoader, TensorDataset
import torch.nn as nn
import torch.optim as optim

# 创建 PyTorch 数据加载器
dataset = TensorDataset(inputs, targets)
dataloader = DataLoader(dataset, batch_size=16, shuffle=True)

# 定义 Transformer Decoder
class TransformerDecoder(nn.Module):
    def __init__(self, vocab_size, d_model, num_heads, num_layers, dim_feedforward, max_len):
        super().__init__()
        self.embedding = nn.Embedding(vocab_size, d_model)
        self.positional_encoding = nn.Parameter(torch.randn(1, max_len, d_model))
        
        decoder_layer = nn.TransformerDecoderLayer(d_model, num_heads, dim_feedforward)
        self.transformer_decoder = nn.TransformerDecoder(decoder_layer, num_layers)
        self.fc_out = nn.Linear(d_model, vocab_size)

    def forward(self, input_seq, memory):
        seq_len = input_seq.size(1)
        embedded = self.embedding(input_seq) + self.positional_encoding[:, :seq_len, :]
        memory = self.embedding(memory) + self.positional_encoding[:, :memory.size(1), :]
        output = self.transformer_decoder(embedded, memory)
        return self.fc_out(output)

# 超参数
d_model = 64  
num_heads = 4  
num_layers = 3  
dim_feedforward = 128  
max_len = 100  

model = TransformerDecoder(vocab_size, d_model, num_heads, num_layers, dim_feedforward, max_len)

# 训练参数
optimizer = torch.optim.Adam(model.parameters(), lr=0.001)
scheduler = torch.optim.lr_scheduler.StepLR(optimizer, step_size=10, gamma=0.95)

def train(model, dataloader, epochs=20):
    for epoch in range(epochs):
        for batch_inputs, batch_targets in dataloader:
            optimizer.zero_grad()
            output = model(batch_inputs, batch_inputs)
            loss = nn.CrossEntropyLoss()(output.view(-1, vocab_size), batch_targets.view(-1))
            loss.backward()
            torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=1.0)  # 避免梯度爆炸
            optimizer.step()
        scheduler.step()
        print(f"Epoch {epoch}, Loss: {loss.item()}")

# 训练模型
train(model, dataloader, epochs=20)

def generate_text(model, tokenizer, start_text, max_length=50):
    """用 BPE 词表生成文本"""
    model.eval()
    input_tokens = tokenizer.encode("<bos> " + start_text).ids
    input_tensor = torch.tensor([input_tokens])

    with torch.no_grad():
        for _ in range(max_length):
            output = model(input_tensor, input_tensor)
            next_token = output.argmax(dim=-1)[:, -1].item()
            input_tokens.append(next_token)
            input_tensor = torch.tensor([input_tokens])

            # 如果遇到 <eos> 结束标记，则停止
            if tokenizer.decode([next_token]) == "<eos>":
                break

    return tokenizer.decode(input_tokens)

# 测试生成
print("生成文本:", generate_text(model, tokenizer, "hello"))
