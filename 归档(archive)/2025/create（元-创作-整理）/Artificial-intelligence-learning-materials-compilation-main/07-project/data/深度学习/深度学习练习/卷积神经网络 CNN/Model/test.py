import torch
from torch import nn
from torch.utils.data import DataLoader, Dataset
from torchvision import transforms
from PIL import Image
import os
import matplotlib.pyplot as plt
import numpy as np

os.environ["KMP_DUPLICATE_LIB_OK"] = "True"

# 图像预处理
transform = transforms.Compose([
    transforms.Resize((28, 28)),  # 将图片统一调整为28x28大小
    transforms.ToTensor(),  # 转为Tensor
    transforms.Normalize((0.5,), (0.5,))  # 归一化处理
])

# 定义CNN模型
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
        super(CNNModel, self).__init__()
        self.conv1 = nn.Conv2d(1, 32, kernel_size=3, padding=1)
        self.pool = nn.MaxPool2d(2, 2)
        self.conv2 = nn.Conv2d(32, 64, kernel_size=3, padding=1)
        self.fc1 = nn.Linear(64 * 7 * 7, 128)
        self.fc2 = nn.Linear(128, 10)

    def forward(self, x):
        """
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
        """
        # 第一层卷积
        x = torch.relu(self.conv1(x))
        self.visualize_feature_map(x, "Conv1 Output")
        # 第一层池化
        x = self.pool(x)
        self.visualize_feature_map(x, "Pool1 Output")
        # 第二层卷积
        x = torch.relu(self.conv2(x))
        self.visualize_feature_map(x, "Conv2 Output")
        # 第二层池化
        x = self.pool(x)
        self.visualize_feature_map(x, "Pool2 Output")
        # 展平
        x = torch.flatten(x, 1)
        x = torch.relu(self.fc1(x))
        x = self.fc2(x)
        return x

    def visualize_feature_map(self, feature_map, title):
        # 将特征图从 Tensor 转换为 NumPy 数组
        feature_map = feature_map.detach().cpu().numpy()
        num_channels = feature_map.shape[1]  # 通道数

        # 可视化每个通道（只展示前8个通道）
        for i in range(min(num_channels, 8)):  # 最多显示8个通道
            plt.subplot(2, 4, i + 1)
            plt.imshow(feature_map[0, i, :, :], cmap="gray")
            plt.axis("off")
            plt.title(f"Channel {i + 1}")

        plt.suptitle(title)
        plt.show()


# 创建模型实例
model = CNNModel()
model.load_state_dict(torch.load('cnn_digit_model.pth'))  # 打开模型文件路径
print(model)
model.eval()

# 测试单张图片
def predict(image_path):
    img = Image.open(image_path).convert('L')
    img = transform(img).unsqueeze(0)  # 加一个batch维度
    with torch.no_grad():
        output = model(img)
        probabilities = torch.softmax(output, dim=1).numpy()[0]  # 使用softmax函数转换为概率
        predicted_class = torch.argmax(output, dim=1).item()  # 返回最大值的索引（预测类别）
    return predicted_class, probabilities

test_image = "1.jpg"
predicted_digit, probabilities = predict(test_image)
print(f'Predicted digit: {predicted_digit}')
print(f'Class probabilities: {probabilities}')

image = Image.open(test_image).convert('L')

image_array = np.array(image)  # 转换为 NumPy 数组

plt.gray()
plt.imshow(image_array)
plt.title(f'Result {predicted_digit}')
# plt.axis('') # 坐标轴开关

plt.show()


# z = [[f'{x} * {y} = {x * y}' for y in range(1, x+1)]for x in range(1, 10)]
# # z = [f'{x} * {y} = {x * y}' for x in range(1, 10) for y in range(1, x+1)]
#
# print(z)
#
# for i in z:
#     print(i)
#     # print('\t'.join(i))
#
#
# print('123\t456')