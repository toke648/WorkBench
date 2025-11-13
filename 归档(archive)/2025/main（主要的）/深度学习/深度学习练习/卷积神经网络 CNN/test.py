import torch
from torch import nn

# 定义神经网络，并继承nn.Module
class Network(nn.Module):
    # 神经网络中的神经元数量是固定的，所以init不用传入参数
    def __init__(self):
        super().__init__() # 调用了父类的初始话函数
        # layer1 输入层与隐藏层的线性层
        self.layer1 = nn.Linear(28 * 28, 256)
        # layer2 隐藏层与输出层之间的线性层
        self.layer2 = nn.Linear(256, 10)

    # 神经网络向前传播，函数传入输入数据
    def forward(self, x):
        # 使用view函数将n * 28 *28 =的x张量，转换为n*784的张量
        # 定义x，并将其传入全连接层
        x = x.view(-1, 28 * 28)
        x = self.layer1()  # 将数值传入输入层
        x = torch.relu(x)  # relu激活
        return self.layer2(x)


def print_forward(model, x):
    print(f'x: {x.shape}') # 样本个数
    x = x.view(-1, 28 *28) # 经过view函数，变成了一个5*784的张量
    print(x.shape)
    x = model.layer1(x) # 经过第一个线性层，得到5*784的张量
    print(f'{x.shape}')
    x = torch.relu_(x) # 经过relu函数，没有变化
    print(f'{x.shape}')
    x = model.layer2(x) # 经过第二个线性层，得到了一个5*10的结果
    print(f'{x.shape}')


if __name__ == '__main__':
    model = Network()
    print(model)
    print('')

    x = torch.zeros([5, 28, 28])
    print_forward(model, x)



# import torch
# from torch import nn
# from torchvision import transforms
# from PIL import Image
#
# # 定义简化的CNN网络
# class SimpleCNN(nn.Module):
#     def __init__(self):
#         super(SimpleCNN, self).__init__()
#         # 卷积层1：输入1通道（灰度图），输出32个特征图，卷积核大小3x3，步幅1
#         self.conv1 = nn.Conv2d(1, 32, kernel_size=3, stride=1, padding=1)
#         # 池化层1：2x2池化，减少尺寸
#         self.pool = nn.MaxPool2d(2, 2)
#         # 卷积层2：输入32个特征图，输出64个特征图
#         self.conv2 = nn.Conv2d(32, 64, kernel_size=3, stride=1, padding=1)
#         # 全连接层：经过卷积和池化后，输入一个固定大小的张量，输出10个分类
#         self.fc1 = nn.Linear(64 * 7 * 7, 10)  # 假设输入图片是28x28大小，经过池化后是7x7大小
#
#     def forward(self, x):
#         # 卷积层1 + ReLU激活 + 池化层1
#         x = self.pool(torch.relu(self.conv1(x)))
#         # 卷积层2 + ReLU激活 + 池化层2
#         x = self.pool(torch.relu(self.conv2(x)))
#         # 展平张量为一维
#         x = x.view(-1, 64 * 7 * 7)
#         # 全连接层
#         x = self.fc1(x)
#         return x
#
# # 预处理图像
# image_path = 'train_images/1.jpg'
# image = Image.open(image_path).convert('L')
#
# # 定义转换
# transform = transforms.Compose(
#     [transforms.Resize((28, 28)),  # 将图像调整为28x28大小
#      transforms.ToTensor(),  # 转换为张量并归一化到[0, 1]
# ])
#
# # 应用转换
# image_tensor = transform(image).unsqueeze(0)  # 增加batch维度，形状变为[1, 1, 28, 28]
# print(image_tensor.shape)
#
# # 创建CNN模型并进行推理
# model = SimpleCNN()
# output = model(image_tensor)
#
# # 输出预测结果
# print(output)


# import torch
# from torch import nn
# import matplotlib.pyplot as plt
# from torchvision import transforms
# from PIL import Image
# import os
#
# os.environ["KMP_DUPLICATE_LIB_OK"] = "True"
#
# # 定义简化的CNN网络
# class SimpleCNN(nn.Module):
#     def __init__(self):
#         super(SimpleCNN, self).__init__()
#         # 卷积层1：输入1通道（灰度图），输出32个特征图，卷积核大小3x3，步幅1
#         self.conv1 = nn.Conv2d(1, 32, kernel_size=3, stride=1, padding=1)
#         # 池化层1：2x2池化，减少尺寸
#         self.pool = nn.MaxPool2d(2, 2)
#         # 卷积层2：输入32个特征图，输出64个特征图
#         self.conv2 = nn.Conv2d(32, 64, kernel_size=3, stride=1, padding=1)
#         # 全连接层：经过卷积和池化后，输入一个固定大小的张量，输出10个分类
#         self.fc1 = nn.Linear(64 * 7 * 7, 10)  # 假设输入图片是28x28大小，经过池化后是7x7大小
#
#     def forward(self, x):
#         # 卷积层1 + ReLU激活 + 池化层1
#         x1 = torch.relu(self.conv1(x))
#         x1_pool = self.pool(x1)  # 池化后
#
#         # 卷积层2 + ReLU激活 + 池化层2
#         x2 = torch.relu(self.conv2(x1_pool))
#         x2_pool = self.pool(x2)  # 池化后
#
#         # 展平张量为一维
#         x_flat = x2_pool.view(-1, 64 * 7 * 7)
#
#         # 全连接层
#         x_fc = self.fc1(x_flat)
#         return x_fc, x1, x1_pool, x2, x2_pool
#
#
# # 预处理图像
# image_path = 'train_images/1.jpg'
# image = Image.open(image_path).convert('L')
#
# # 定义转换
# transform = transforms.Compose(
#     [transforms.Resize((28, 28)),  # 将图像调整为28x28大小
#      transforms.ToTensor(),  # 转换为张量并归一化到[0, 1]
#      ])
#
# # 应用转换
# image_tensor = transform(image).unsqueeze(0)  # 增加batch维度，形状变为[1, 1, 28, 28]
# print(image_tensor.shape)
#
# # 创建CNN模型并进行推理
# model = SimpleCNN()
# output, x1, x1_pool, x2, x2_pool = model(image_tensor)
#
# # 输出预测结果
# print(output)
#
#
# # 画出每一层的结果
# def plot_feature_map(feature_map, layer_name):
#     # feature_map的形状是[batch_size, channels, height, width]
#     batch_size, channels, height, width = feature_map.shape
#     fig, axes = plt.subplots(1, channels, figsize=(15, 15))
#     fig.suptitle(f'{layer_name} feature maps', fontsize=16)
#     for i in range(channels):
#         ax = axes[i]
#         ax.imshow(feature_map[0, i].detach().cpu(), cmap='gray')
#         ax.axis('off')
#     plt.show()
#
#
# # 绘制每一层的特征图
# plot_feature_map(x1, 'Conv1 Feature Maps')
# plot_feature_map(x1_pool, 'Conv1 Pooling')
# plot_feature_map(x2, 'Conv2 Feature Maps')
# plot_feature_map(x2_pool, 'Conv2 Pooling')

