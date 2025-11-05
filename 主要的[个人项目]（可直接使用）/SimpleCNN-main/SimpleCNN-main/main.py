import torch
from torch import nn
from torch.utils.data import DataLoader, Dataset
from torchvision import transforms
from PIL import Image
import os
import matplotlib.pyplot as plt

os.environ["KMP_DUPLICATE_LIB_OK"] = "True"

# 图像预处理（保持不变）
transform = transforms.Compose([
    transforms.Resize((28, 28)),
    transforms.ToTensor(),
    transforms.Normalize((0.5,), (0.5,))
])

# 自定义数据集（保持不变）
class CustomImageDataset(Dataset):
    def __init__(self, image_folder, transform=transform):
        self.image_folder = image_folder
        self.transform = transform
        self.image_paths = []
        self.labels = []
        for label in range(0, 10):
            folder_path = os.path.join(image_folder, str(label))
            if not os.path.exists(folder_path):
                continue  # 跳过不存在的类别文件夹
            for img_name in os.listdir(folder_path):
                img_path = os.path.join(folder_path, img_name)
                self.image_paths.append(img_path)
                self.labels.append(label)

    def __len__(self):
        return len(self.image_paths)

    def __getitem__(self, idx):
        img_path = self.image_paths[idx]
        label = self.labels[idx]
        img = Image.open(img_path).convert('L')
        if self.transform:
            img = self.transform(img)
        return img, label

# CNN模型（保持不变）
class CNNModel(nn.Module):
    def __init__(self) -> None:
        super(CNNModel, self).__init__()
        self.conv1 = nn.Conv2d(1,32, kernel_size=3, padding=2)
        self.pool = nn.MaxPool2d(2, 2)
        self.conv2 = nn.Conv2d(32, 64, kernel_size=3, padding=1)
        self.fc1 = nn.Linear(64 * 7 * 7, 128)
        self.fc2 = nn.Linear(128, 10)

    def forward(self, x):
        x = torch.relu(self.conv1(x))
        x = self.pool(x)
        x = torch.relu(self.conv2(x))
        x = self.pool(x)
        x = torch.flatten(x, 1)
        x = torch.relu(self.fc1(x))
        x = self.fc2(x)
        return x

    def visualize_feature_map(self, feature_map, title):
        feature_map = feature_map.detach().cpu().numpy()
        num_channels = feature_map.shape[1]
        for i in range(min(num_channels, 8)):
            plt.subplot(2, 4, i + 1)
            plt.imshow(feature_map[0, i, :, :], cmap="gray")
            plt.axis("off")
            plt.title(f"Channel {i + 1}")
        plt.suptitle(title)
        plt.show()

# 训练部分（保持不变）
image_folder = "train_images"  # 替换为你的训练集路径
train_dataset = CustomImageDataset(image_folder=image_folder, transform=transform)
train_loader = DataLoader(train_dataset, batch_size=32, shuffle=True)

model = CNNModel()
criterion = nn.CrossEntropyLoss()
optimizer = torch.optim.Adam(model.parameters(), lr=0.001)

num_epochs = 20  # 减少epoch数，避免过拟合
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

torch.save(model.state_dict(), 'cnn_digit_model.pth')

# 测试函数：增加图像绘制功能
model.eval()
def predict_and_plot(image_path):
    # 加载图像并预处理
    img = Image.open(image_path).convert('L')  # 转为灰度图
    original_img = img.copy()  # 保存原始图像用于显示（未归一化）
    img_tensor = transform(img).unsqueeze(0)  # 预处理并增加batch维度

    # 预测
    with torch.no_grad():
        output = model(img_tensor)
        predicted_class = torch.argmax(output, dim=1).item()
        # 计算每个类别的概率（通过softmax）
        probabilities = torch.softmax(output, dim=1).squeeze().numpy()

    # 绘制图像和预测结果
    plt.figure(figsize=(10, 4))
    
    # 左侧：显示原始图像
    plt.subplot(1, 2, 1)
    plt.imshow(original_img, cmap='gray')
    plt.title(f'Input Image')
    plt.axis('off')
    
    # 右侧：显示预测概率分布
    plt.subplot(1, 2, 2)
    plt.bar(range(10), probabilities, color='skyblue')
    plt.xticks(range(10))
    plt.xlabel('Digit Class')
    plt.ylabel('Probability')
    plt.title(f'Predicted: {predicted_class} (Confidence: {probabilities[predicted_class]:.2f})')
    plt.ylim(0, 1)  # 概率范围0-1
    
    plt.tight_layout()
    plt.show()  # 现场显示图像

# 测试单张图片（替换为你的测试图片路径）
test_image = "1.jpg"  # 例如：测试一张数字"1"的图片
if os.path.exists(test_image):
    predict_and_plot(test_image)
else:
    print(f"Error: 图片路径 {test_image} 不存在！")