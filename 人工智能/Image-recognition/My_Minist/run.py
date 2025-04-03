import torch
from torch.utils.data import DataLoader
from torchvision import transforms
from torchvision.datasets import MNIST
import matplotlib.pyplot as plt
from PIL import Image
import os

# 定义模型
class Net(torch.nn.Module):
    def __init__(self):
        super().__init__()
        self.fc1 = torch.nn.Linear(28 * 28, 128)
        self.fc2 = torch.nn.Linear(128, 64)
        self.fc3 = torch.nn.Linear(64, 10)
        self.dropout = torch.nn.Dropout(0.2)

    def forward(self, x):
        x = torch.nn.functional.relu(self.fc1(x))
        x = self.dropout(torch.nn.functional.relu(self.fc2(x)))
        x = torch.nn.functional.log_softmax(self.fc3(x), dim=1)
        return x

# 获取数据加载器
def get_data_loader(is_train):
    to_tensor = transforms.Compose([transforms.ToTensor()])
    data_set = MNIST("", is_train, transform=to_tensor, download=True)
    return DataLoader(data_set, batch_size=15, shuffle=True)

# 评估模型
def evaluate(test_data, net):
    n_correct = 0
    n_total = 0
    with torch.no_grad():
        for (x, y) in test_data:
            outputs = net.forward(x.view(-1, 28 * 28))
            for i, output in enumerate(outputs):
                if torch.argmax(output) == y[i]:
                    n_correct += 1
                n_total += 1
    return n_correct / n_total

# 预处理真实图片
def preprocess_image(image_path):
    image = Image.open(image_path).convert('L')  # 转换为灰度图
    image = image.resize((28, 28))  # 调整大小为 28x28
    transform = transforms.Compose([
        transforms.ToTensor(),
        transforms.Normalize((0.5,), (0.5,))  # 归一化到 [-1, 1]
    ])
    image = transform(image).unsqueeze(0)  # 增加 batch 维度
    return image

# 使用模型预测图片
def predict_image(image_path, model):
    image = preprocess_image(image_path)
    with torch.no_grad():
        output = model(image)
        _, predicted = torch.max(output, 1)
    return predicted.item()

# 主函数
def main():
    # 设备配置
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    os.environ['KMP_DUPLICATE_LIB_OK'] = 'True'

    # 加载数据
    train_data = get_data_loader(is_train=True)
    test_data = get_data_loader(is_train=False)

    # 初始化模型
    net = Net().to(device)

    # 定义优化器和学习率调度器
    optimizer = torch.optim.Adam(net.parameters(), lr=0.001)
    scheduler = torch.optim.lr_scheduler.StepLR(optimizer, step_size=1, gamma=0.9)

    # 训练模型
    for epoch in range(5):
        for (x, y) in train_data:
            x, y = x.to(device), y.to(device)
            optimizer.zero_grad()
            output = net(x.view(-1, 28 * 28))
            loss = torch.nn.functional.nll_loss(output, y)
            loss.backward()
            optimizer.step()
        scheduler.step()
        print(f"epoch {epoch}, accuracy: {evaluate(test_data, net)}")

    # 保存模型
    torch.save(net.state_dict(), 'model.pth')
    print("Model saved to model.pth")

    # 评估模式

    # 使用模型预测真实图片
    image_path = '1.jpg'  # 替换为你的图片路径
    predicted_class = predict_image(image_path, net)
    print(f'Predicted class: {predicted_class}')

if __name__ == "__main__":
    main()