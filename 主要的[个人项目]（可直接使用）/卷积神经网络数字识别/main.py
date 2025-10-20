import torch
from torch import nn
from torch.utils.data import DataLoader, Dataset
from torchvision import transforms
from PIL import Image
import os
import matplotlib.pyplot as plt

os.environ["KMP_DUPLICATE_LIB_OK"] = "True"

# 图像预处理
transform = transforms.Compose([
    transforms.Resize((28, 28)),  # 将图片统一调整为28x28大小
    transforms.ToTensor(),  # 转为Tensor
    transforms.Normalize((0.5,), (0.5,))  # 归一化处理
])

# 自定义数据集
class CustomImageDataset(Dataset):
    def __init__(self, image_folder, transform=transform):
        self.image_folder = image_folder
        self.transform = transform
        self.image_paths = []
        self.labels = []
        # 遍历所有子文件夹和图像文件，加载路径
        for label in range(0, 10):  # 假设图像是0-9的数字
            folder_path = os.path.join(image_folder, str(label))
            for img_name in os.listdir(folder_path):
                img_path = os.path.join(folder_path, img_name)
                self.image_paths.append(img_path)
                self.labels.append(label)  # 标签为0-9 打标

    # 类内部调用私有变量
    def __len__(self):
        return len(self.image_paths)

    # CustomImageDataset.__getitem__()
    def __getitem__(self, idx):
        img_path = self.image_paths[idx]
        label = self.labels[idx]
        img = Image.open(img_path).convert('L')  # 转为灰度图
        if self.transform:
            img = self.transform(img)
        return img, label

# 定义CNN模型
class CNNModel(nn.Module):
    def __init__(self) -> None:
        super(CNNModel, self).__init__()
        self.conv1 = nn.Conv2d(1,32, kernel_size=3, padding=2)
        self.pool = nn.MaxPool2d(2, 2)
        self.conv2 = nn.Conv2d(32, 64, kernel_size=3, padding=1)
        self.fc1 = nn.Linear(64 * 7 * 7, 128)
        self.fc2 = nn.Linear(128, 10)

    def forward(self, x):
        # 第一层卷积
        x = torch.relu(self.conv1(x))
        # self.visualize_feature_map(x, "Conv1 Output")
        # 第一层池化
        x = self.pool(x)
        # 第二层卷积
        x = torch.relu(self.conv2(x))
        # self.visualize_feature_map(x, "Conv2 Output")
        # 第二层池化
        x = self.pool(x)
        # self.visualize_feature_map(x, "Pool2 Output")
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

# 创建训练数据集和DataLoader
image_folder = "train_images"  # 修改为你数据集的路径
train_dataset = CustomImageDataset(image_folder=image_folder, transform=transform)
train_loader = DataLoader(train_dataset, batch_size=32, shuffle=True)

# 创建模型实例
model = CNNModel()

# 使用交叉熵损失函数和Adam优化器
criterion = nn.CrossEntropyLoss()
# torch 内部
optimizer = torch.optim.Adam(model.parameters(), lr=0.001)
print(optimizer)

# 训练模型
num_epochs = 150  # 为了快速测试，设置为2，实际训练可以设更高
for epoch in range(num_epochs):
    model.train()
    running_loss = 0.0
    for images, labels in train_loader:
        optimizer.zero_grad()
        outputs = model(images)
        loss = criterion(outputs, labels)
        loss.backward()
        optimizer.step()
        running_loss += loss.item()

    print(f'Epoch [{epoch + 1}/{num_epochs}], Loss: {running_loss / len(train_loader):.4f}')

# 保存训练好的模型
torch.save(model.state_dict(), 'cnn_digit_model.pth')

# 测试单张图片
model.eval()
def predict(image_path):
    img = Image.open(image_path).convert('L')
    img = transform(img).unsqueeze(0)  # 加一个batch维度
    with torch.no_grad():
        output = model(img)
        predicted_class = torch.argmax(output, dim=1).item()  # 返回最大值的索引（预测类别）
    return predicted_class

test_image = "1.jpg"
predicted_digit = predict(test_image)
print(f'Predicted digit: {predicted_digit}')

