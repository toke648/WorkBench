# ResNet(残差神经网络)

import torch
from torch import nn  # 导入神经网络模块
from torch.utils.data import DataLoader  # 数据包管理工具，打包数据
from torchvision import datasets  # 封装了很对与图像相关的模型，数据集
from torchvision.transforms import ToTensor  # 数据转换，张量，将其他类型的数据转换成tensor张量
import torch.nn.functional as F # 用于应用 ReLU 激活函数


'''下载训练数据集(包含训练集图片+标签)'''
training_data = datasets.MNIST(  # 跳转到函数的内部源代码，pycharm 按下ctrl+鼠标点击
    root='data',  # 表示下载的手写数字 到哪个路径。60000
    train=True,  # 读取下载后的数据中的数据集
    download=True,  # 如果你之前已经下载过了，就不用再下载了
    transform=ToTensor(),  # 张量，图片是不能直接传入神经网络模型
    # 对于pytorch库能够识别的数据一般是tensor张量
)

'''下载测试数据集（包含训练图片+标签）'''
test_data = datasets.MNIST(
    root='data',
    train=False,
    download=True,
    transform=ToTensor(),  # Tensor是在深度学习中提出并广泛应用的数据类型，它与深度学习框架（如pytorch，TensorFlow）
)  # numpy数组只能在cpu上运行。Tensor可以在GPU上运行，这在深度学习应用中可以显著提高计算速度。
print(len(training_data))
print(len(test_data))

train_dataloader = DataLoader(training_data, batch_size=64) # # 建议用2的指数当作一个包的数量
test_dataloader = DataLoader(test_data, batch_size=64)

'''判断是否支持GPU'''
device = 'cuda' if torch.cuda.is_available() else 'mps' if torch.backends.mps.is_available() else 'cpu'
print(f'Using {device} device')

# 定义残差块类，继承自 nn.Module
class ResBlock(nn.Module):
    def __init__(self, channels_in):
        # 调用父类的构造函数
        super().__init__()
        # 定义第一个卷积层，输入通道数为 channels_in，输出通道数为 30，卷积核大小为 5，填充为 2
        self.conv1 = torch.nn.Conv2d(channels_in, 30, 5, padding=2)
        # 定义第二个卷积层，输入通道数为 30，输出通道数为 channels_in，卷积核大小为 3，填充为 1
        self.conv2 = torch.nn.Conv2d(30, channels_in, 3, padding=1)

    def forward(self, x):
        # 输入数据通过第一个卷积层
        out = self.conv1(x)
        # 经过第一个卷积层的输出再通过第二个卷积层
        out = self.conv2(out)
        # 将输入 x 与卷积输出 out 相加，并通过 ReLU 激活函数
        return F.relu(out + x)


# 定义 ResNet 网络类，继承自 nn.Module
class ResNet(nn.Module):
    def __init__(self):
        # 调用父类的构造函数
        super().__init__()
        # 定义第一个卷积层，输入通道数为 1，输出通道数为 20，卷积核大小为 5
        self.conv1 = torch.nn.Conv2d(1, 20, 5)
        # 定义第二个卷积层，输入通道数为 20，输出通道数为 15，卷积核大小为 3
        self.conv2 = torch.nn.Conv2d(20, 15, 3)
        # 定义最大池化层，池化核大小为 2
        self.maxpool = torch.nn.MaxPool2d(2)
        # 定义第一个残差块，输入通道数为 20
        self.resblock1 = ResBlock(channels_in=20)
        # 定义第二个残差块，输入通道数为 15
        self.resblock2 = ResBlock(channels_in=15)
        # 定义全连接层，输入特征数为 375，输出特征数为 10
        self.full_c = torch.nn.Linear(375, 10)

    def forward(self, x):
        # 获取输入数据的批次大小
        size = x.shape[0]
        # 输入数据通过第一个卷积层，然后进行最大池化，最后通过 ReLU 激活函数
        x = F.relu(self.maxpool(self.conv1(x)))
        # 经过第一个卷积和池化的输出通过第一个残差块
        x = self.resblock1(x)
        # 经过第一个残差块的输出通过第二个卷积层，然后进行最大池化，最后通过 ReLU 激活函数
        x = F.relu(self.maxpool(self.conv2(x)))
        # 经过第二个卷积和池化的输出通过第二个残差块
        x = self.resblock2(x)
        # 将输出数据展平为一维向量
        x = x.view(size, -1)
        # 展平后的向量通过全连接层
        x = self.full_c(x)
        return x


model = ResNet().to(device)
print(model)

# 定义训练函数
def train(dataloader, model, loss_fn, optimizer):
    # 将模型设置为训练模式，这会影响一些层（如 Dropout、BatchNorm 等）的行为
    model.train()
    # 初始化批次编号
    batch_size_num = 1
    # 遍历数据加载器中的每个批次
    for x, y in dataloader:
        # 将输入数据和标签移动到指定设备（如 GPU）
        x, y = x.to(device), y.to(device)
        # 前向传播，计算模型的预测结果
        pred = model.forward(x)
        # 通过交叉熵损失函数计算预测结果与真实标签之间的损失值
        loss = loss_fn(pred, y)
        # 反向传播步骤：
        # 清零优化器中的梯度信息，防止梯度累积
        optimizer.zero_grad()
        # 反向传播计算每个参数的梯度
        loss.backward()
        # 根据计算得到的梯度更新模型的参数
        optimizer.step()
        # 从张量中提取损失值的标量
        loss_value = loss.item()
        # 每 100 个批次打印一次损失值
        if batch_size_num % 100 == 0:
            print(f'loss:{loss_value:7f}  [number:{batch_size_num}]')
        # 批次编号加 1
        batch_size_num += 1

# 定义测试函数
def test(dataloader, model, loss_fn):
    # 获取数据集的总样本数
    size = len(dataloader.dataset)
    # 获取数据加载器中的批次数量
    num_batches = len(dataloader)
    # 将模型设置为评估模式，这会影响一些层（如 Dropout、BatchNorm 等）的行为
    model.eval()
    # 初始化测试损失和正确预测的样本数
    test_loss, correct = 0, 0
    # 上下文管理器，关闭梯度计算，减少内存消耗
    with torch.no_grad():
        # 遍历数据加载器中的每个批次
        for x, y in dataloader:
            # 将输入数据和标签移动到指定设备（如 GPU）
            x, y = x.to(device), y.to(device)
            # 前向传播，计算模型的预测结果
            pred = model.forward(x)
            # 累加每个批次的损失值
            test_loss += loss_fn(pred, y).item()
            # 计算每个批次中预测正确的样本数并累加
            correct += (pred.argmax(1) == y).type(torch.float).sum().item()
    # 计算平均测试损失
    test_loss /= num_batches
    # 计算平均准确率
    correct /= size
    # 打印测试结果
    print(f'Test result: \n Accuracy:{(100 * correct)}%,Avg loss:{test_loss}')

# 创建交叉熵损失函数对象
loss_fn = nn.CrossEntropyLoss()
# 创建 Adam 优化器，用于更新模型的参数
optimizer = torch.optim.Adam(model.parameters(), lr=0.001)
scheduler = torch.optim.lr_scheduler.StepLR(optimizer,step_size=3,gamma=0.1)

# 定义训练的轮数
epochs = 26
# 开始训练循环
for t in range(epochs):
    print(f'epoch{t + 1}\n--------------------')
    # 调用训练函数进行一轮训练
    train(train_dataloader, model, loss_fn, optimizer)
print('Done!')
# 调用测试函数进行测试
test(test_dataloader, model, loss_fn)
