import torch
import torch.nn as nn

class SelfAttention(nn.Module):
    def __init__(self, embed_size, heads):
        super().__init__()
        self.heads = heads
        self.head_dim = embed_size // heads
        
        # 键、值和查询的线性变换，q、、k、v 的维度为 embed_size // heads
        self.values = nn.Linear(embed_size, embed_size)
        self.keys = nn.Linear(embed_size, embed_size)
        self.queries = nn.Linear(embed_size, embed_size)
        self.fc_out = nn.Linear(embed_size, embed_size)

    def forward(self, x):
        B, T, C = x.shape  # Batch, Token, Channel
        queries = self.queries(x)
        keys = self.keys(x)
        values = self.values(x)

        # Scaled Dot-Product Attention
        energy = torch.matmul(queries, keys.transpose(-2, -1)) / (C ** 0.5)
        attention = torch.softmax(energy, dim=-1)
        out = torch.matmul(attention, values)
        return self.fc_out(out)

# 运行测试
x = torch.randn(1, 10, 512)  # batch=1, 句子长度=10, embedding_dim=512
sa = SelfAttention(512, 8)
print(sa(x).shape)  # 输出: torch.Size([1, 10, 512])
