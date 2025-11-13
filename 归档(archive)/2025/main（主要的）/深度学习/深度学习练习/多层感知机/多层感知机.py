import torch
import torch.nn as nn
import torch.optim as optim

# 1. 构建数据集 (XOR 逻辑门)
X = torch.tensor([[0, 0], [0, 1], [1, 0], [1, 1]], dtype=torch.float32)
y = torch.tensor([[0], [1], [1], [0]], dtype=torch.float32)  # 期望输出

# 2. 定义 MLP 网络
class MLP(nn.Module):
    def __init__(self):
        super(MLP, self).__init__()
        self.hidden = nn.Linear(2, 4)  # 输入层 (2) -> 隐藏层 (4)
        self.output = nn.Linear(4, 1)  # 隐藏层 (4) -> 输出层 (1)
        self.activation = nn.ReLU()  # 使用 ReLU 作为隐藏层激活函数
        self.sigmoid = nn.Sigmoid()  # 输出层使用 Sigmoid

    def forward(self, x):
        x = self.activation(self.hidden(x))
        x = self.sigmoid(self.output(x))  # 二分类问题，使用 Sigmoid
        return x

# 3. 初始化模型、损失函数、优化器
model = MLP()
criterion = nn.BCELoss()  # 二分类交叉熵损失
optimizer = optim.SGD(model.parameters(), lr=0.1)  # SGD优化器，学习率 0.1

# 4. 训练模型
epochs = 10000
for epoch in range(epochs):
    optimizer.zero_grad()
    y_pred = model(X)  # 预测
    loss = criterion(y_pred, y)  # 计算损失
    loss.backward()  # 反向传播
    optimizer.step()  # 更新参数
    
    # 每 1000 轮打印一次损失
    if epoch % 1000 == 0:
        print(f"Epoch {epoch}, Loss: {loss.item()}")

# 5. 测试模型
with torch.no_grad():
    predictions = model(X)
    print("\nPredictions:")
    print(predictions.round())  # 取 0 或 1
