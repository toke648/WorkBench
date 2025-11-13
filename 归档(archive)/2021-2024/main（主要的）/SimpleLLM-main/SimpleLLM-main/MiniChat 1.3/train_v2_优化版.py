from tokenizers import Tokenizer
import torch
from torch.utils.data import DataLoader, TensorDataset
import torch.nn as nn
import torch.optim as optim
import os

os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"

# ----------- 加载 tokenizer -----------
tokenizer = Tokenizer.from_file("bpe_tokenizer.json")
vocab_size = tokenizer.get_vocab_size()
print("词表大小:", vocab_size)

# ----------- 数据集处理（问 → 答）-----------
def create_qa_data(file_path, tokenizer, seq_length=50):
    inputs, targets = [], []
    with open(file_path, 'r', encoding='utf-8') as f:
        for line in f:
            if '\t' in line:
                q, a = line.strip().split('\t')
                q_ids = tokenizer.encode("<bos> " + q + " <eos>").ids
                a_ids = tokenizer.encode("<bos> " + a + " <eos>").ids

                # padding 到固定长度
                q_ids = q_ids[:seq_length] + [0]*(seq_length - len(q_ids)) if len(q_ids) < seq_length else q_ids[:seq_length]
                a_ids = a_ids[:seq_length] + [0]*(seq_length - len(a_ids)) if len(a_ids) < seq_length else a_ids[:seq_length]

                inputs.append(q_ids)
                targets.append(a_ids)

    return torch.tensor(inputs), torch.tensor(targets)

inputs, targets = create_qa_data("./processed_data.txt", tokenizer, seq_length=50)
print("训练数据大小:", inputs.shape, targets.shape)

# dataset = TensorDataset(inputs, targets)
# dataloader = DataLoader(dataset, batch_size=16, shuffle=True)

# 只取 5000 条训练看看
subset_inputs = inputs[:5000]
subset_targets = targets[:5000]
dataset = TensorDataset(subset_inputs, subset_targets)
dataloader = DataLoader(dataset, batch_size=16, shuffle=True)

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print("使用设备:", device)

# ----------- 模型（Encoder-Decoder）-----------
class TransformerChatbot(nn.Module):
    def __init__(self, vocab_size, d_model, num_heads, num_layers, dim_feedforward, max_len):
        super().__init__()
        self.embedding = nn.Embedding(vocab_size, d_model) # 词向量嵌入
        self.positional_encoding = nn.Parameter(torch.randn(1, max_len, d_model)) # 位置编码

        encoder_layer = nn.TransformerEncoderLayer(d_model, num_heads, dim_feedforward) # TransformerEncoderLayer层: 编码器层
        decoder_layer = nn.TransformerDecoderLayer(d_model, num_heads, dim_feedforward) # TransformerDecoderLayer层: 解码器层

        self.encoder = nn.TransformerEncoder(encoder_layer, num_layers) # TransformerEncoder: 编码器
        self.decoder = nn.TransformerDecoder(decoder_layer, num_layers) # TransformerDecoder: 解码器
        self.fc_out = nn.Linear(d_model, vocab_size)

    def forward(self, src, tgt):
        # src: 输入序列, tgt: 目标序列
        src_emb = self.embedding(src) + self.positional_encoding[:, :src.size(1), :]
        tgt_emb = self.embedding(tgt) + self.positional_encoding[:, :tgt.size(1), :]

        # 转置为 (seq_len, batch_size, d_model) 以适应 nn.TransformerEncoder 和 nn.TransformerDecoder 的输入格式
        src_emb = src_emb.transpose(0,1)
        tgt_emb = tgt_emb.transpose(0,1)
        
        # 编码器和解码器的前向传播
        memory = self.encoder(src_emb)
        output = self.decoder(tgt_emb, memory)
        output = output.transpose(0,1)
        return self.fc_out(output)

d_model = 64
num_heads = 4
num_layers = 2
dim_feedforward = 128
max_len = inputs.shape[1]

model = TransformerChatbot(vocab_size, d_model, num_heads, num_layers, dim_feedforward, max_len).to(device)

optimizer = optim.Adam(model.parameters(), lr=0.001)
loss_fn = nn.CrossEntropyLoss(ignore_index=0)  # 忽略 pad

# ----------- 训练函数 -----------
def train(model, dataloader, epochs=10):
    for epoch in range(epochs):
        model.train()
        epoch_loss = 0
        for src, tgt in dataloader:
            src, tgt = src.to(device), tgt.to(device)
            optimizer.zero_grad()

            output = model(src, tgt[:, :-1])
            loss = loss_fn(output.reshape(-1, vocab_size), tgt[:,1:].reshape(-1))
            loss.backward()
            optimizer.step()

            epoch_loss += loss.item()

        print(f"Epoch {epoch+1}/{epochs}, Loss: {epoch_loss/len(dataloader):.4f}")

    torch.save(model.state_dict(), "chatbot_model.pth")

train(model, dataloader, epochs=20)

# ----------- 生成函数 -----------
def generate_reply(model, tokenizer, input_text, max_length=50):
    model.load_state_dict(torch.load("chatbot_model.pth", map_location=device))
    model.eval()

    input_ids = tokenizer.encode("<bos> " + input_text + " <eos>").ids
    input_ids = input_ids[:max_length] + [0]*(max_length - len(input_ids)) if len(input_ids) < max_length else input_ids[:max_length]
    input_tensor = torch.tensor([input_ids]).to(device)

    generated_ids = [tokenizer.token_to_id("<bos>")]
    for _ in range(max_length):
        tgt_tensor = torch.tensor([generated_ids]).to(device)

        with torch.no_grad():
            output = model(input_tensor, tgt_tensor)
            next_token = output[0, -1].argmax().item()

        if next_token == tokenizer.token_to_id("<eos>") or next_token == 0:
            break
        generated_ids.append(next_token)

    return tokenizer.decode(generated_ids)

# ----------- 测试聊天 -----------
while True:
    user_input = input("👤 你：")
    reply = generate_reply(model, tokenizer, user_input)
    print("🤖 AI：", reply)
