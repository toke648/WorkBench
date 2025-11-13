import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim


# 自定义卷积层
class CustomConv(nn.Module):
    def __init__(self, in_channels, out_channels, kernel_size):
        super(CustomConv, self).__init__()
        # 卷积核权重和偏置
        self.weight = nn.Parameter(torch.randn(out_channels, in_channels, kernel_size, kernel_size))
        self.bias = nn.Parameter(torch.randn(out_channels))

    def forward(self, x):
        # 使用 F.conv2d 方法进行卷积
        return F.conv2d(x, self.weight, self.bias, stride=1, padding=0)

    # 定义输入通道、输出通道和卷积核大小


in_channels = 1  # 输入通道数
out_channels = 1  # 输出通道数
kernel_size = 3  # 卷积核大小

# 创建自定义卷积层的实例
model = CustomConv(in_channels, out_channels, kernel_size)

# 随机生成输入数据（批量大小1，大小为5x5）
input_tensor = torch.randn(1, in_channels, 5, 5)

# 初始化卷积核为一个简单的3x3 Sobel滤波器 (边缘检测)
initial_weights = torch.tensor([[[[0, 1, 0],
                                  [1, -4, 1],
                                  [0, 1, 0]]]], dtype=torch.float32)  # 注意 dtype
model.weight.data = initial_weights

# 随机生成目标数据 (target)
target_tensor = torch.randn(1, out_channels, 3, 3)  # 输出大小 = 输入大小 - kernel_size + 1，因此3x3

# 选择损失函数和优化器
criterion = nn.MSELoss()
optimizer = optim.SGD(model.parameters(), lr=0.01)

# 模拟训练过程
num_epochs = 200
for epoch in range(num_epochs):
    optimizer.zero_grad()

    # 前向传播
    output = model(input_tensor)

    # 计算损失
    loss = criterion(output, target_tensor)

    # 反向传播及优化
    loss.backward()
    optimizer.step()

    # 输出训练信息
    print(f'Epoch {epoch + 1}/{num_epochs}, Loss: {loss.item():.4f}')

# 测试模型
with torch.no_grad():
    test_output = model(input_tensor)
    print("Test output:\n", test_output)