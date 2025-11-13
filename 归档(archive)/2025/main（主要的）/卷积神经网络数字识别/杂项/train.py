import matplotlib.pyplot as plt
from torchvision import transforms
from PIL import Image
from torch import nn
import numpy as np
import torch
import os

class CNNModel(nn.Module):
    def __init__(self) -> None:
        """
            卷积层 conv
            in_channels 输入张量
            out_channels 输出通道
            kernel_size 卷积核
            padding 填充

            池化层 pool
            kernel_size 卷积核/池化大小
            stride 步幅

            全连接层 linear
            in_features 输入值
            out_features 输出值
        """
        super().__init__()
        # 卷积 -> 激活 -> 池化
        self.conv1 = nn.Conv2d(1, 32, 3 , padding=2)
        self.pool = nn.MaxPool2d(2, 2)
        self.conv2 = nn.Conv2d(32, 64,3, padding=1)
        # 全连接
        self.fc1 = nn.Linear(64 * 7 * 7, 128)
        self.fc2 = nn.Linear(128, 10)

    def forward(self, x):
        # 卷积 -> 激活 -> 池化
        # -> 多次操作
        # -> 全连接层

        # 卷积 -> relu激活 -> 池化
        x = torch.relu(self.conv1(x))
        x = self.pool(x)
        # 二次卷积 -> relu激活 -> 池化
        x = torch.relu(self.conv2(x))
        x = self.pool(x)

        # 展平 64卷积 -> 一维张量
        #  -> 128 一维张量 -> relu激活 ->
        x = torch.flatten(x, 1)
        x = torch.relu(self.fc1(x))
        x = self.fc2
        return x

# 创建训练数据集和Dataloader

# 创建模型实例

# 使用交叉熵损失函数和Adam优化器

# 训练数据集

# 保存训练好的模型

# 测试单张图片

os.environ["KMP_DUPLICATE_LIB_OK"] = "True"

# 图像预处理
transform = transforms.Compose([
    transforms.Resize((28, 28)),  # 将图片统一调整为28x28大小
    transforms.ToTensor(),  # 转为Tensor
    transforms.Normalize((0.5,), (0.5,))  # 归一化处理
])

model = CNNModel()

# 测试单张图片
model.eval()
def predict(image_path):
    img = Image.open(image_path).convert('L')
    img = transform(img).unsqueeze(0)  # 加一个batch维度
    with torch.no_grad():
        output = model(img)
        predicted_class = torch.argmax(output, dim=1).item()  # 返回最大值的索引（预测类别）
    return predicted_class

test_image = "1.jpg"  # 修改为测试图片路径
predicted_digit = predict(test_image)
print(f'Predicted digit: {predicted_digit}')



pth = torch.load('cnn_digit_model.pth')
print(pth)

model = CNNModel()
model.load_state_dict(torch.load('cnn_digit_model.pth'))  # 修改为你的模型文件路径
print(model)
print(model.eval())
