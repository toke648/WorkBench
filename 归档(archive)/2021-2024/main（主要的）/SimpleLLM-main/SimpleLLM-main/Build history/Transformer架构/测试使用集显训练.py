import torch
import torch.nn as nn

# 定义 MyModel 类
class MyModel(nn.Module):
    def __init__(self):
        super(MyModel, self).__init__()
        self.linear = nn.Linear(10, 1)  # 假设输入特征维度为10，输出维度为1

    def forward(self, x):
        return self.linear(x)

# 强制使用 CPU
device = torch.device("xpu" if torch.xpu.is_available() else "cpu")

# 创建模型实例并移动到 CPU
model = MyModel().to(device)

# 假设你有一些输入数据
inputs = torch.randn(1, 10).to(device)  # 创建一个随机输入张量，形状为 (1, 10)

# 训练时将模型和数据移到 CPU
outputs = model(inputs)

print(outputs)