import torch
from torch import nn
from torch.utils.data import DataLoader, Dataset
from torchvision import transforms
from PIL import Image, ImageDraw
import os
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import tkinter as tk
from tkinter import messagebox
import numpy as np

os.environ["KMP_DUPLICATE_LIB_OK"] = "True"

# --------------------------
# 1. 数据预处理和模型定义（保持不变）
# --------------------------
transform = transforms.Compose([
    transforms.Resize((28, 28)),
    transforms.ToTensor(),
    transforms.Normalize((0.5,), (0.5,))
])

class CustomImageDataset(Dataset):
    def __init__(self, image_folder, transform=transform):
        self.image_folder = image_folder
        self.transform = transform
        self.image_paths = []
        self.labels = []
        for label in range(0, 10):
            folder_path = os.path.join(image_folder, str(label))
            if not os.path.exists(folder_path):
                continue
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

# --------------------------
# 2. 训练模型（如果已有模型可注释）
# --------------------------
def train_model():
    image_folder = "train_images"  # 替换为你的训练集路径
    if not os.path.exists(image_folder):
        messagebox.showerror("错误", "训练集路径不存在！")
        return None

    train_dataset = CustomImageDataset(image_folder=image_folder, transform=transform)
    train_loader = DataLoader(train_dataset, batch_size=32, shuffle=True)

    model = CNNModel()
    criterion = nn.CrossEntropyLoss()
    optimizer = torch.optim.Adam(model.parameters(), lr=0.001)

    num_epochs = 20
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
    return model

# --------------------------
# 3. 实时绘画和预测功能
# --------------------------
class DigitDrawer:
    def __init__(self, model):
        self.model = model
        self.model.eval()  # 切换为评估模式
        self.canvas_size = 200  # 绘画画布大小
        self.img_size = 28  # 模型输入大小
        self.init_ui()

    def init_ui(self):
        # 创建主窗口
        self.root = tk.Tk()
        self.root.title("数字绘画识别器")

        # 创建绘画画布
        self.fig, (self.ax_draw, self.ax_pred) = plt.subplots(1, 2, figsize=(10, 5))
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.root)
        self.canvas.get_tk_widget().pack()

        # 初始化绘画区域
        self.ax_draw.set_title("在左侧画布手写数字（鼠标拖动）")
        self.ax_draw.set_xlim(0, self.canvas_size)
        self.ax_draw.set_ylim(0, self.canvas_size)
        self.ax_draw.invert_yaxis()  # 使坐标原点在左上角（符合绘画习惯）
        self.ax_draw.axis('off')
        self.draw_points = []  # 存储绘画的点

        # 初始化预测结果区域
        self.ax_pred.set_title("预测概率分布")
        self.ax_pred.set_xlabel("数字类别")
        self.ax_pred.set_ylabel("概率")
        self.ax_pred.set_xticks(range(10))
        self.ax_pred.set_ylim(0, 1)

        # 绑定鼠标事件
        self.cid_press = self.fig.canvas.mpl_connect('button_press_event', self.on_press)
        self.cid_motion = self.fig.canvas.mpl_connect('motion_notify_event', self.on_drag)
        self.cid_release = self.fig.canvas.mpl_connect('button_release_event', self.on_release)

        # 添加按钮
        self.btn_clear = tk.Button(self.root, text="清除画布", command=self.clear_canvas)
        self.btn_clear.pack(side=tk.LEFT, padx=10)
        self.btn_predict = tk.Button(self.root, text="识别数字", command=self.predict)
        self.btn_predict.pack(side=tk.LEFT, padx=10)

    def on_press(self, event):
        # 鼠标按下时记录起点
        if event.inaxes == self.ax_draw:
            self.draw_points.append([event.xdata, event.ydata])
            self.update_draw()

    def on_drag(self, event):
        # 鼠标拖动时记录轨迹
        if event.inaxes == self.ax_draw and self.draw_points:
            self.draw_points.append([event.xdata, event.ydata])
            self.update_draw()

    def on_release(self, event):
        # 鼠标释放时完成绘画
        self.update_draw()

    def update_draw(self):
        # 更新绘画显示
        self.ax_draw.clear()
        self.ax_draw.set_title("在左侧画布手写数字（鼠标拖动）")
        self.ax_draw.set_xlim(0, self.canvas_size)
        self.ax_draw.set_ylim(0, self.canvas_size)
        self.ax_draw.invert_yaxis()
        self.ax_draw.axis('off')
        if self.draw_points:
            # 绘制连续线条
            x = [p[0] for p in self.draw_points]
            y = [p[1] for p in self.draw_points]
            self.ax_draw.plot(x, y, 'black', linewidth=8)  # 粗线条模拟手写
        self.canvas.draw()

    def clear_canvas(self):
        # 清除画布
        self.draw_points = []
        self.update_draw()
        # 清除预测结果
        self.ax_pred.clear()
        self.ax_pred.set_title("预测概率分布")
        self.ax_pred.set_xlabel("数字类别")
        self.ax_pred.set_ylabel("概率")
        self.ax_pred.set_xticks(range(10))
        self.ax_pred.set_ylim(0, 1)
        self.canvas.draw()

    def predict(self):
        # 将绘画转为模型输入格式
        if not self.draw_points:
            messagebox.showinfo("提示", "请先在画布上绘制数字！")
            return

        # 创建空白图像并绘制轨迹
        img = Image.new('L', (self.canvas_size, self.canvas_size), 255)  # 白色背景
        draw = ImageDraw.Draw(img)
        if len(self.draw_points) >= 2:
            draw.line(self.draw_points, fill=0, width=10)  # 黑色线条

        # 预处理（缩放到28x28，归一化）
        img = img.resize((self.img_size, self.img_size), Image.LANCZOS)
        img_tensor = transform(img).unsqueeze(0)  # 增加batch维度

        # 模型预测
        with torch.no_grad():
            output = self.model(img_tensor)
            probabilities = torch.softmax(output, dim=1).squeeze().numpy()
            predicted_class = np.argmax(probabilities)

        # 显示预测结果
        self.ax_pred.clear()
        self.ax_pred.bar(range(10), probabilities, color='skyblue')
        self.ax_pred.set_title(f"预测结果: {predicted_class} (置信度: {probabilities[predicted_class]:.2f})")
        self.ax_pred.set_xlabel("数字类别")
        self.ax_pred.set_ylabel("概率")
        self.ax_pred.set_xticks(range(10))
        self.ax_pred.set_ylim(0, 1)
        self.canvas.draw()

    def run(self):
        self.root.mainloop()

# --------------------------
# 4. 主程序入口
# --------------------------
if __name__ == "__main__":
    # 加载模型（如果已有模型，可直接加载而不训练）
    if os.path.exists('cnn_digit_model.pth'):
        model = CNNModel()
        model.load_state_dict(torch.load('cnn_digit_model.pth'))
        print("已加载预训练模型")
    else:
        print("未找到预训练模型，开始训练...")
        model = train_model()
        if model is None:
            exit()

    # 启动绘画识别界面
    drawer = DigitDrawer(model)
    drawer.run()