from tokenizers import Tokenizer
import torch
from torch.utils.data import DataLoader, TensorDataset
import matplotlib.pyplot as plt
import torch.nn as nn
import torch.optim as optim
import os

os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"

# ----------- 数据部分 -----------
# 加载 BPE Tokenizer
tokenizer = Tokenizer.from_file("bpe_tokenizer.json")

# 获取词表大小
vocab_size = tokenizer.get_vocab_size()
print("词表大小:", vocab_size)

def create_training_data(text, tokenizer, seq_length=50):
    """将文本转换为 Token ID，并生成训练样本"""
    token_ids = tokenizer.encode(text).ids
    inputs, targets = [], []

    for i in range(len(token_ids) - seq_length):
        inputs.append(token_ids[i:i+seq_length])
        targets.append(token_ids[i+1:i+seq_length+1])

    return torch.tensor(inputs), torch.tensor(targets)

# # 读取训练数据
# file_paths = ["data1.txt", "data2.txt"]
# text = "\n".join([open(f, "r", encoding="utf-8").read() for f in file_paths])

# # 生成训练样本
# inputs, targets = create_training_data(text, tokenizer)
# print("训练数据大小:", inputs.shape, targets.shape)

# 读取训练数据
# file_paths = ["data1.txt", "data2.txt"]
# text = "\n".join([open(f, "r", encoding="utf-8").read() for f in file_paths])

text = open("./processed_data.txt", 'r', encoding='utf-8').read()[:2000]

# 生成训练样本
inputs, targets = create_training_data(text, tokenizer)
print("训练数据大小:", inputs.shape, targets.shape)

# ----------- 训练数据 DataLoader -----------
dataset = TensorDataset(inputs, targets)
dataloader = DataLoader(dataset, batch_size=16, shuffle=True)

# 自动设备检测
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print("使用设备:", device)

# ----------- 模型定义 -----------
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
        memory_emb = self.embedding(memory) + self.positional_encoding[:, :memory.size(1), :]

        # Transformer 需要 (seq_len, batch_size, d_model)
        embedded = embedded.transpose(0, 1)
        memory_emb = memory_emb.transpose(0, 1)

        output = self.transformer_decoder(embedded, memory_emb)
        output = output.transpose(0, 1)  # (batch_size, seq_len, d_model)
        return self.fc_out(output)

# ----------- 超参数 -----------
d_model = 64
num_heads = 4
num_layers = 3
dim_feedforward = 128
max_len = inputs.shape[1]  # 自动用 seq_length
print("max_len:", max_len)

model = TransformerDecoder(vocab_size, d_model, num_heads, num_layers, dim_feedforward, max_len).to(device)

# ----------- 优化器、调度器、损失函数 -----------
optimizer = torch.optim.Adam(model.parameters(), lr=0.001)
scheduler = torch.optim.lr_scheduler.StepLR(optimizer, step_size=10, gamma=0.95)
loss_fn = nn.CrossEntropyLoss()

# ----------- 训练函数 -----------
def train(model, dataloader, epochs=20):
    epochses = []
    losses = []

    plt.ion()  # 打开交互式
    fig, ax = plt.subplots()

    for epoch in range(epochs):
        epoch_loss = 0
        for batch_inputs, batch_targets in dataloader:
            batch_inputs = batch_inputs.to(device)
            batch_targets = batch_targets.to(device)

            optimizer.zero_grad()
            output = model(batch_inputs, batch_inputs)  # decoder memory = 输入

            # output: (batch_size, seq_len, vocab_size)
            # 需要 flatten 两个 tensor 对齐
            loss = loss_fn(output.view(-1, vocab_size), batch_targets.view(-1))

            loss.backward()
            torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=1.0)
            optimizer.step()

            epoch_loss += loss.item()

        scheduler.step()
        avg_loss = epoch_loss / len(dataloader)
        print(f"Epoch {epoch + 1}/{epochs}, Loss: {avg_loss:.4f}")

        epochses.append(epoch + 1)
        losses.append(avg_loss)

        # 实时绘图
        ax.clear()
        ax.plot(epochses, losses, label='Loss')
        ax.set_xlabel('Epochs')
        ax.set_ylabel('Loss')
        ax.set_title('Training Loss')
        ax.legend()
        plt.pause(0.1)

    plt.ioff()
    plt.show()
    plt.close()

# ----------- 启动训练 -----------
train(model, dataloader, epochs=20)
# 保存模型
torch.save(model.state_dict(), f"model_1.pth")

def generate_text(model, tokenizer, start_text, max_length=50):
    """用 BPE 词表生成文本"""

    # 加载训练好的模型
    model.load_state_dict(torch.load("./model_1.pth", weights_only=True))
    
    # 为什么要设置为评估模式？
    # 因为在评估模式下，模型会关闭 Dropout 和 BatchNorm 等训练时使用的操作，从而使得模型在推理时更加稳定和一致。
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
text = "hello"

word_count = len(text.split())  # 获取单词个数
print("生成文本:", generate_text(model, tokenizer, text, max_length=20))

