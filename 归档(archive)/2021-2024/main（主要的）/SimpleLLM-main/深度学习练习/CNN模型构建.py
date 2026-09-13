import torch
from torch import nn
from torch.utils.data import DataLoader, Dataset
from torchvision import transforms
from PIL import Image
import os
import matplotlib.pyplot as plt
import numpy as np

"""
    回滚一遍全流程
"""

os.environ["KMP_DUPLICATE_LIB_OK"] = "True"

# 图像预处理
transform = transforms.Compose([
    transforms.Resize((28, 28)),  # 将图片统一调整为28x28大小
    transforms.ToTensor(),  # 转为Tensor
    transforms.Normalize((0.5,), (0.5,))  # 归一化处理
])

class CNNModel(nn.Module):
    def __init__(self):
        super(CNNModel, self).__init__()
        self.conv1 = nn.Conv2d(1, 32, kernel_size=3, padding=1)
        self.pool = nn.MaxPool2d(2, 2)  # 定义2 x 2 池化
        self.conv2 = nn.Conv2d(32, 64, kernel_size=3, padding=1)
        self.fc1 = nn.Linear(64 * 7 * 7, 128)
        self.fc2 = nn.Linear(128, 10)

    def forward(self, x):
        # 第一层卷积
        x = torch.relu(self.conv1(x))
        # 第一层池化
        x = self.pool(x)
        # 第二层卷积
        x = torch.relu(self.conv2(x))
        # 第二层池化
        x = self.pool(x)
        # 展平
        x = torch.flatten(x, 1)
        x = torch.relu(self.fc1(x))
        x = self.fc2(x)
        return x


# 创建模型实例
model = CNNModel()
print(model)
model.load_state_dict(torch.load('cnn_digit_model.pth'))  # 打开模型文件路径
model.eval()

print(torch.load('cnn_digit_model.pth'))  # 训练集结构

# 测试单张图片
def predict(image_path):
    img = Image.open(image_path).convert('L')
    img = transform(img).unsqueeze(0)  # 加一个batch维度
    with torch.no_grad():
        output = model(img)
        probabilities = torch.softmax(output, dim=1).numpy()[0]  # 使用softmax函数转换为概率
        predicted_class = torch.argmax(output, dim=1).item()  # 返回最大值的索引（预测类别）
    return predicted_class, probabilities




