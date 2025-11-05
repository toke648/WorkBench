import torch
import torch.nn as nn
import torch.nn.functional as F


class SimpleCNN(nn.Module):
    def __init__(self):
        super(SimpleCNN, self).__init__()

        # 1. 卷积层1：输入通道1，输出通道2，卷积核3x3
        self.conv1 = nn.Conv2d(in_channels=1, out_channels=2, kernel_size=3, padding=1)
        # 2. 卷积层2：输入通道2，输出通道2，卷积核3x3
        self.conv2 = nn.Conv2d(in_channels=2, out_channels=2, kernel_size=3, padding=1)
        # 3. 密集层1：输出512个神经元
        self.fc1 = nn.Linear(2 * 28 * 28, 512)  # 输入尺寸需要计算
        # 4. 密集层2：输出512个神经元
        self.fc2 = nn.Linear(512, 512)
        # 5. 输出层：10个神经元（十分类）
        self.fc3 = nn.Linear(512, 10)

    def forward(self, x):
        # 第一个卷积操作
        x = self.conv1(x)
        x = F.relu(x)
        # 第二个卷积操作
        x = self.conv2(x)
        x = F.relu(x)
        # 展平操作
        x = x.view(x.size(0), -1)  # 或者使用 torch.flatten(x, 1)
        # 第一个全连接层
        x = self.fc1(x)
        x = F.relu(x)
        # 第二个全连接层
        x = self.fc2(x)
        x = F.relu(x)
        # 输出层
        x = self.fc3(x)
        return x


# 创建输入张量：大小为[1, 28, 28]（需要添加batch维度）
input_tensor = torch.randn(1, 1, 28, 28)  # [batch_size=1, channels=1, height=28, width=28]
print("输入张量形状: {input_tensor.shape}")


# 创建模型实例
model = SimpleCNN()

# 前向传播验证
output = model(input_tensor)
print(f"最终输出形状: {output.shape}")
print(f"输出值: {output}")

# 打印各层形状变化（用于验证）
print("\n=== 各层形状变化 ===")
x = input_tensor
print(f"输入: {x.shape}")

x = model.conv1(x)
print(f"卷积1后: {x.shape}")

x = F.relu(x)
x = model.conv2(x)
print(f"卷积2后: {x.shape}")

x = F.relu(x)
x = x.view(x.size(0), -1)
print(f"展平后: {x.shape}")

x = model.fc1(x)
print(f"全连接1后: {x.shape}")

x = F.relu(x)
x = model.fc2(x)
print(f"全连接2后: {x.shape}")

x = F.relu(x)
x = model.fc3(x)
print(f"输出层后: {x.shape}")



model = nn.Sequential(
    nn.Linear(1024, 512),
    nn.ReLU(),
    nn.Dropout(p=0.5),  # 全连接层后添加Dropout
    nn.Linear(512, 10)
)