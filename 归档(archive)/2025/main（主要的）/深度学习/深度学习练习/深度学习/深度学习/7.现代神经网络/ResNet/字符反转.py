
import torch
import torch.nn as nn

class ResNet(nn.Module):
    """
    ResNet 的 Docstring
    ResNet 是一个基于卷积层的神经网络模型，用于字符反转任务。
    输入：图片
    输出：图片

    参数：
    *args, **kwargs: 继承父类 nn.Module 的参数
    返回：
    *args, **kwargs: 继承父类 nn.Module 的返回值

    神经网络层级：


    """
    def __init__(self) -> None:
        super().__init__()
        # 卷积层, 输入通道数为1，输出通道数为32，卷积核大小为3x3，步长为1
        self.conv1 = nn.Conv2d(3, 32, 3, 1) # 卷积层 输入通道数为3，输出通道数为32，卷积核大小为3x3，步长为1
        self.bn1 = nn.BatchNorm2d(32)
        self.pool = nn.MaxPool2d(2, 2) # 池化层

        # 卷积层, 输入通道数为32，输出通道数为64，卷积核大小为3x3，步长为1
        self.conv2 = nn.Conv2d(32, 64, 3, 1) # 卷积层
        self.bn2 = nn.BatchNorm2d(64)

        # 批量归一化层 28 —> 32 —> 64 —> 32 —> 64 —> 1
        self.fc = nn.Linear(64 * 5 * 5, 2) # 全连接层

    def forward(self, x) -> torch.Tensor:
        x = self.pool(F.relu(self.bn1(self.conv1(x)))) # 卷积1
        x = self.pool(F.relu(self.bn2(self.conv2(x)))) # 卷积2
        x = torch.flatten(x, 1) # 展平
        x = self.fc(x) # 全连接层

        return x

# 输入十个猫狗图片转换为张量，用于模型输入，实现图像分类任务
# 每个图片的大小为28x28，通道数为1（灰度图）
# 输出为一个10维向量，每个元素表示对应类别的概率
# 例如，向量[0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]表示模型认为这张图片是第10类（即“狗”）的概率为100%

from torch.utils.data import TensorDataset, DataLoader, random_split
import torch.nn.functional as F
import torch
import cv2
import os

def load_data():
    path = os.path.dirname(os.path.abspath(__file__))

    cat_folder_path = os.path.join(path, "cat")
    cat_file = os.listdir(cat_folder_path)

    dog_folder_path = os.path.join(path, "dog")
    dog_file = os.listdir(dog_folder_path)

    cat_list = []
    dog_list = []

    for file in cat_file:
        img_path = os.path.join(cat_folder_path, file)
        img = cv2.imread(img_path)
        if img is None: continue

        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        img = cv2.resize(img, (28, 28))
        img = torch.from_numpy(img)
        img = img.permute(2, 0, 1)
        img = img.float() / 255.0
        cat_list.append(img)

    for file in dog_file:
        img_path = os.path.join(dog_folder_path, file)
        img = cv2.imread(img_path)
        if img is None: continue
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        img = cv2.resize(img, (28, 28))
        img = torch.from_numpy(img)
        img = img.permute(2, 0, 1)
        img = img.float() / 255.0
        dog_list.append(img)

    # 拼接数据
    X = torch.stack(cat_list + dog_list)        # shape: [N, 3, 28, 28]
    y = torch.cat([
        torch.zeros(len(cat_list), dtype=torch.long),
        torch.ones(len(dog_list), dtype=torch.long)
    ])

    print("数据加载完成:", X.shape, y.shape)
    
    return X, y

import matplotlib.pyplot as plt
# 绘制损失曲线
def plot_loss(losses):
    plt.plot(losses)
    plt.xlabel("Epoch")
    plt.ylabel("Loss")
    plt.title("Training Loss")
    # plt.show()

    if not os.path.exists("photo"):
        os.makedirs("photo")
    plt.savefig("photo/loss.png")


def train():

    model = ResNet()
    optimizer = torch.optim.Adam(model.parameters(), lr=1e-3)
    criterion = nn.CrossEntropyLoss()

    for epoch in range(10):
        model.train()
        total_loss = 0

        for images, labels in train_loader:
            optimizer.zero_grad()
            outputs = model(images)
            loss = criterion(outputs, labels)
            loss.backward()
            optimizer.step()
            total_loss += loss.item()

        print(f"Epoch {epoch+1}, Loss: {total_loss:.4f}")


    model.eval()
    correct = 0
    total = 0

    with torch.no_grad():
        for images, labels in test_loader:
            outputs = model(images)
            _, predicted = torch.max(outputs, 1)
            correct += (predicted == labels).sum().item()
            total += labels.size(0)

    acc = correct / total * 100
    print(f"Test Accuracy: {acc:.2f}%")


    if not os.path.exists("model"):
        os.makedirs("model")
    torch.save(model.state_dict(), "model/model.pth")


if __name__ == "__main__":
    model = ResNet()
    print(model)

    x = torch.randn(3, 3, 28, 28) # 随机生成一个图片张量 3通道，28*28大小
    output = model(x) # 前向传播
    print(output) # 打印输出

    X, y = load_data()
    dataset = TensorDataset(X, y)

    # 划分训练和测试集
    train_size = int(0.8 * len(dataset)) # 80%的数据集作为训练集
    test_size = len(dataset) - train_size # 剩余的作为测试集

    train_set, test_set = random_split(dataset, [train_size, test_size])
    print(len(train_set), len(test_set))

    # dataloder
    train_loader = DataLoader(train_set, batch_size=32, shuffle=True) # batch_size=32 表示每个批次的样本数量
    test_loader = DataLoader(test_set, batch_size=32)

    train()


    for i in range(len(dataset)):
        img = X[i].unsqueeze(0) # 增加一个维度，变为[1, 3, 28, 28]
        output = model(img)
        prob = F.softmax(output, dim=1) # 获取概率
        # 打印预测结果，同时打开图片
        if prob[0][0] > prob[0][1]:
            print(f"图片 {i} 预测为猫，概率为 {prob[0][0]:.4f}")
            plt.imshow(X[i].permute(1, 2, 0))
            plt.title(f"Pred: Cat, Prob: {prob[0][0]:.4f}")
            plt.axis("off")
            plt.show()
        else:
            print(f"图片 {i} 预测为狗，概率为 {prob[0][1]:.4f}")
            plt.imshow(X[i].permute(1, 2, 0))
            plt.title(f"Pred: Dog, Prob: {prob[0][1]:.4f}")
            plt.axis("off")
            plt.show()
