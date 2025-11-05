from pathlib import Path

import torch  # 导入PyTorch库，用于深度学习模型的构建和训练
import torchvision
from torchvision import datasets, transforms  # 从torchvision库中导入datasets和transforms模块
from torch.utils.data import DataLoader  # 从torch.utils.data中导入DataLoader，用于数据加载
import torch.nn as nn  # 导入PyTorch的神经网络模块
import torch.nn.functional as F  # 导入PyTorch的神经网络功能函数模块
import torch.optim as optim  # 导入PyTorch的优化器模块
# 注意：下面两行导入了两个不同的SummaryWriter，应该只保留一个，根据使用的库来选择
# from torch.utils.tensorboard import SummaryWriter  # PyTorch官方的TensorBoard支持
from tensorboardX import SummaryWriter  # 第三方库tensorboardX的TensorBoard支持
import numpy as np  # 导入NumPy库，用于数值计算
from datetime import datetime  # 导入datetime模块，用于获取当前时间
import torch  # 导入PyTorch库（此处代码中遗漏了此导入）
import torch.nn as nn  # 导入PyTorch的神经网络模块（此处代码中遗漏了此导入）
import tensorboard as tb



# ==========================================================================================================
# 数据源类，用于封装MNIST数据集的训练和测试数据加载逻辑
class DataSource():
    def __init__(self, batch_size=64):  # 初始化方法，设置默认的批次大小为64
        # transforms.Compose定义数据预处理流程
        transform = transforms.Compose([
            # 输入：PIL图像或numpy数组（像素值0-255）
            # 输出：PyTorch张量，值域转换为[0.0, 1.0]
            # 维度变化：从(H, W)变为(C, H, W)，即添加通道维度
            transforms.ToTensor(),

            # 计算公式：normalized = (input - mean) / std
            # 具体计算：(x - 0.5) / 0.5 = 2x - 1
            # 效果：将值域从[0,1]转换到[-1, 1]，有助于模型训练稳定性
            transforms.Normalize((0.5,), (0.5,))
        ])

        # 下载并加载训练数据集
        # root='./data'：数据集存储目录（当前目录下的data文件夹）
        # train=True/False：区分训练集（60,000样本）和测试集（10,000样本）
        # download=True：自动下载功能（如果本地不存在）
        # transform=transform：应用定义好的预处理流程
        train_dataset = datasets.MNIST(root='./data', train=True, download=True, transform=transform)

        # 下载并加载测试数据集
        # train=False表示加载测试集
        test_dataset = datasets.MNIST(root='./data', train=False, download=True, transform=transform)

        # 创建数据加载器，用于在训练时批量加载数据
        # DataLoader核心功能:
        # 批量处理：将数据集分成小批次，节省内存
        # 数据打乱：避免模型学习到数据顺序偏差
        # 并行加载：支持多进程数据预加载
        # batch_size指定每个批次加载的数据量
        # shuffle=True表示在每个epoch开始时，打乱数据顺序
        self.train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True)

        # 创建数据加载器，用于在测试时批量加载数据
        self.test_loader = DataLoader(test_dataset, batch_size=batch_size, shuffle=False)
        # shuffle=False表示在测试时不需要打乱数据顺序

# --------------------------查看训练数据和测试数据---------------------------------------------
# def analyze_dataset():
#     data_source = DataSource()
#
#     # 基本统计
#     train_size = len(data_source.train_loader.dataset)
#     test_size = len(data_source.test_loader.dataset)
#
#     print("=== MNIST数据集统计信息 ===")
#     print(f"训练集样本总数: {train_size}")
#     print(f"测试集样本总数: {test_size}")
#     print(f"数据集总样本数: {train_size + test_size}")
#
#     # 批次信息
#     batch_size = data_source.train_loader.batch_size
#     print(f"批次大小: {batch_size}")
#     print(f"训练集批次数量: {len(data_source.train_loader)}")
#     print(f"测试集批次数量: {len(data_source.test_loader)}")
#
#     # 查看一个样本的详细信息
#     for images, labels in data_source.train_loader:
#         print(f"\n=== 样本格式信息 ===")
#         print(f"图像张量形状: {images.shape}")  # [batch_size, 通道数, 高度, 宽度]
#         print(f"标签张量形状: {labels.shape}")  # [batch_size]
#         print(f"图像数据类型: {images.dtype}")
#         print(f"标签数据类型: {labels.dtype}")
#         print(f"像素值范围: [{images.min():.3f}, {images.max():.3f}]")
#         print(f"第一个样本的标签: {labels[0].item()}")
#         break
#
# analyze_dataset()

# ==========================================================================================================
# CNN模型类
# nn.Module继承：所有PyTorch神经网络模型的基类，提供参数管理、训练/评估模式切换等核心功能
class CNN(nn.Module):
    def __init__(self):
        # 调用父类构造函数，确保正确的初始化
        super(CNN, self).__init__()  # 调用父类nn.Module的初始化方法

        # 定义第一个卷积层
        # in_channels=1：输入通道数（MNIST是灰度图，所以为1）
        # out_channels=32：输出通道数（使用32个不同的卷积核提取特征）
        # kernel_size=3：3×3卷积核
        # stride=1：步长为1，每次移动1像素
        # padding=1：边缘填充1圈0，保持输出尺寸不变
        # 输入尺寸变化：[64, 1, 28, 28]→ [64, 32, 28, 28]
        self.conv1 = nn.Conv2d(1, 32, kernel_size=3, stride=1, padding=1)

        # 定义最大池化层，池化窗口大小为2x2，步长为2
        # 作用：下采样，减少特征图尺寸，增强特征鲁棒性
        # 效果：尺寸减半（28×28 → 14×14）
        self.pool = nn.MaxPool2d(2, 2)

        # 以下卷积层被注释，可以根据需要取消注释以加深网络
        # 定义第二个卷积层，输入通道数为32，输出通道数为64，卷积核大小为3x3，步长为1，边缘填充为1
        # self.conv2 = nn.Conv2d(32, 64, kernel_size=3, stride=1, padding=1)
        # 定义第三个卷积层，输入通道数为64，输出通道数为64，卷积核大小为3x3，步长为1，边缘填充为1
        # self.conv3 = nn.Conv2d(64, 64, kernel_size=3, stride=1, padding=1)
        # 定义第一个全连接层，输入特征数量为32*14*14（根据卷积和池化后的输出大小计算），输出特征数量为64

        # fc1：将卷积特征映射到64维隐藏表示
        self.fc1 = nn.Linear(32 * 14 * 14, 64)  # 注意：这里的输入特征数需要根据实际卷积输出调整
        # 定义第二个全连接层（输出层），输入特征数量为64，输出特征数量为10（对应10个类别）
        # fc2：输出层，对应10个数字类别（0-9）
        self.fc2 = nn.Linear(64, 10)

    def forward(self, x):
        # x通过第一个卷积层，然后应用ReLU激活函数，再通过最大池化层
        x = self.pool(F.relu(self.conv1(x)))
        # 如果取消注释了conv2和conv3，这里也需要相应地应用卷积、ReLU激活和池化
        # x = self.pool(F.relu(self.conv2(x)))
        # x = self.pool(F.relu(self.conv3(x)))
        # 将x展平为一维向量，以便输入到全连接层
        x = torch.flatten(x, 1)  # 展平除了第一（批次）维度之外的所有维度
        # x通过第一个全连接层，然后应用ReLU激活函数
        x = F.relu(self.fc1(x))
        # x通过第二个全连接层（输出层）
        x = self.fc2(x)
        # 返回x的log-softmax，用于多分类任务，dim=1指定在类别维度上进行softmax计算
        return F.log_softmax(x, dim=1)



# 假设CNN类和DataSource类已经在其他地方定义
# CNN类是一个卷积神经网络模型
# DataSource类负责加载训练数据和测试数据

# 训练类
class Train:
    def __init__(self):
        self.network = CNN()  # 初始化卷积神经网络模型
        self.data = DataSource()  # 初始化数据源对象，负责加载数据

    def train(self):
        # 自动检测可用的GPU，否则使用CPU进行训练
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.network.to(device)  # 将模型参数和缓冲区转移到指定设备，确保计算在相同设备上进行

        # 初始化Adam优化器,自适应学习率优化算法，适合大多数深度学习任务
        optimizer = optim.Adam(self.network.parameters(), lr=0.001)
        # 初始化负对数似然损失函数，通常用于分类任务.负对数似然损失，需要输入为对数概率（通常与LogSoftmax配合使用）
        criterion = nn.NLLLoss()

        # 使用pathlib的现代写法,防止./ckpt文件夹和./logs文件夹不存在
        checkpoint_dir = Path('./ckpt')
        checkpoint_dir.mkdir(parents=True, exist_ok=True)

        logdir = Path("./logs/scalars") / datetime.now().strftime("%Y%m%d-%H%M%S")
        logdir.mkdir(parents=True, exist_ok=True)

        # 定义模型检查点保存路径:格式化字符串，按epoch编号保存模型
        check_path = './ckpt/cp-{epoch:04d}.pth'
        # 定义TensorBoard日志目录，使用当前时间作为子目录名
        # 使用时间戳创建唯一目录，记录训练过程可视化数据
        logdir = "./logs/scalars/" + datetime.now().strftime("%Y%m%d-%H%M%S")
        # 初始化TensorBoard的SummaryWriter
        # SummaryWriter是用于将训练过程中的指标（如损失、准确率）和模型结构写入日志的工具
        # 之后可以通过 TensorBoard 可视化这些信息
        writer = SummaryWriter(logdir=logdir)

        # 添加模型计算图到TensorBoard中（注意：这应该在模型定义完成后立即执行一次，而不是在每个epoch后）
        # 示例输入：创建与MNIST图像尺寸匹配的随机张量（批量64，1通道，28×28）
        # 设备一致性：确保输入数据与模型在同一设备上
        # 计算图记录：将模型架构可视化到TensorBoard，便于调试和分析
        input = torch.rand(64, 1, 28, 28).to(device)  # 创建一个随机输入张量
        writer.add_graph(self.network, (input,))  # 添加模型图

        # 训练循环
        for epoch in range(10):  # 这里只训练2个epoch作为示例
            self.network.train()  # 设置模型为训练模式
            total = 0  # 初始化总样本数
            correct = 0  # 初始化正确预测数
            # 遍历训练数据加载器
            for images, labels in self.data.train_loader:
                images, labels = images.to(device), labels.to(device)  # 将数据和标签移动到设备上
                optimizer.zero_grad()  # 清零梯度
                # [64, 10]
                outputs = self.network(images)  # 前向传播
                loss = criterion(outputs, labels)  # 计算损失
                loss.backward()  # 反向传播
                optimizer.step()  # 更新模型参数

                # 计算准确率
                _, predicted = torch.max(outputs.data, 1)
                total += labels.size(0)
                correct += (predicted == labels).sum().item()

                # 打印训练结果
            writer.add_scalar('Loss/train', loss.item(), epoch)
            writer.add_scalar('Accuracy/train', 100 * correct / total, epoch)
            print(f'Epoch {epoch + 1}, Loss: {loss.item():.4f}, Accuracy: {100 * correct / total:.2f}%')

            # 验证集评估
            self.network.eval()  # 设置模型为评估模式
            test_loss = 0  # 初始化测试损失
            correct = 0  # 初始化测试正确预测数
            with torch.no_grad():  # 禁用梯度计算
                # 遍历测试数据加载器
                for images, labels in self.data.test_loader:
                    images, labels = images.to(device), labels.to(device)
                    outputs = self.network(images)
                    test_loss += criterion(outputs, labels).item()
                    _, predicted = torch.max(outputs.data, 1)
                    correct += (predicted == labels).sum().item()

                    # 计算平均测试损失和准确率
            test_loss /= len(self.data.test_loader)
            print(
                f'Test set: Average loss: {test_loss:.4f}, Accuracy: {100 * correct / len(self.data.test_loader.dataset):.2f}%')

            # 保存模型和TensorBoard记录
            torch.save(self.network.state_dict(), check_path.format(epoch=epoch + 1))  # 保存模型检查点
            # 遍历模型参数，并添加到TensorBoard中
            for name, param in self.network.named_parameters():
                writer.add_histogram(name, param, epoch)
            # 添加训练和测试损失、准确率到TensorBoard中
            # writer.add_scalar('Loss/train', loss.item(), epoch)
            # writer.add_scalar('Accuracy/train', 100 * correct / total, epoch)
            writer.add_scalar('Loss/test_images', test_loss, epoch)
            writer.add_scalar('Accuracy/test_images', 100 * correct / len(self.data.test_loader.dataset), epoch)
            # 关闭TensorBoard的SummaryWriter
        writer.close()

if __name__ == "__main__":
    mnist_train = Train()
    mnist_train.train()


#  tensorboard --logdir=./logs