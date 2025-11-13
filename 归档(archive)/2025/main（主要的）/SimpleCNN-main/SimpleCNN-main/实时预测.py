import torch
from torch import nn
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageDraw
import os

# 确保中文显示正常
plt.rcParams["font.family"] = ["SimHei", "WenQuanYi Micro Hei", "Heiti TC"]
os.environ["KMP_DUPLICATE_LIB_OK"] = "True"

# --------------------------
# 1. 模型定义（保持不变）
# --------------------------
class CNNModel(nn.Module):
    def __init__(self) -> None:
        super(CNNModel, self).__init__()
        self.conv1 = nn.Conv2d(1, 32, kernel_size=3, padding=2)
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

# 加载模型
model = CNNModel()
try:
    model.load_state_dict(torch.load('cnn_digit_model.pth', map_location=torch.device('cpu')))
    model.eval()
except FileNotFoundError:
    messagebox.showerror("错误", "未找到模型文件，请先训练模型并保存为'cnn_digit_model.pth'")
    exit()

# --------------------------
# 2. 实时绘画与实时预测
# --------------------------
class DrawingApp:
    def __init__(self, root):
        self.root = root
        self.root.title("手写数字识别 - 实时预测版")
        
        # 尺寸参数
        self.canvas_size = 280  # 显示尺寸（放大10倍）
        self.logical_size = 28  # 模型输入尺寸
        self.brush_size = 1     # 画笔粗细
        
        # 颜色设置（根据训练集调整，这里默认黑底白字）
        self.background_color = 255   # 背景黑色
        self.brush_color = 0      # 画笔白色
        
        # 创建PIL图像（逻辑尺寸）
        self.logical_img = Image.new('L', (self.logical_size, self.logical_size), self.background_color)
        self.draw = ImageDraw.Draw(self.logical_img)
        
        # 创建matplotlib画布
        self.fig, (self.ax_draw, self.ax_prob) = plt.subplots(1, 2, figsize=(10, 5))
        self.fig.canvas.mpl_connect('button_press_event', self.on_press)
        self.fig.canvas.mpl_connect('motion_notify_event', self.on_drag)
        self.fig.canvas.mpl_connect('button_release_event', self.on_release)
        
        # 绘画区域设置
        self.ax_draw.set_title("在此区域绘制数字（实时预测）")
        self.ax_draw.set_xlim(0, self.logical_size)
        self.ax_draw.set_ylim(0, self.logical_size)
        self.ax_draw.invert_yaxis()
        self.ax_draw.set_aspect('equal')
        self.draw_img = self.ax_draw.imshow(
            np.array(self.logical_img), 
            cmap='gray', 
            vmin=0, 
            vmax=255
        )
        
        # 概率分布区域
        self.ax_prob.set_title("预测概率分布")
        self.ax_prob.set_xlabel("数字类别")
        self.ax_prob.set_ylabel("概率")
        self.ax_prob.set_xticks(range(10))
        self.ax_prob.set_ylim(0, 1)
        self.bar_plot = self.ax_prob.bar(range(10), [0]*10, color='skyblue')
        
        # 清除按钮
        self.clear_btn = tk.Button(root, text="清除画布", command=self.clear_canvas)
        self.clear_btn.pack(pady=5)
        
        # 嵌入Tkinter窗口
        self.canvas = FigureCanvasTkAgg(self.fig, master=root)
        self.canvas.get_tk_widget().pack()
        
        self.drawing = False

    def on_press(self, event):
        # 鼠标按下时开始绘画，并立即预测
        if event.inaxes == self.ax_draw:
            self.drawing = True
            self.draw_point(event.xdata, event.ydata)
            self.predict()  # 按下时预测一次

    def on_drag(self, event):
        # 鼠标拖动时持续绘画，并实时预测
        if self.drawing and event.inaxes == self.ax_draw:
            self.draw_point(event.xdata, event.ydata)
            self.predict()  # 拖动时每画一笔就预测一次

    def on_release(self, event):
        # 鼠标松开时停止绘画（最后再预测一次确保结果更新）
        if self.drawing:
            self.drawing = False
            self.predict()

    def draw_point(self, x, y):
        # 绘制点（使用设置的颜色）
        x = np.clip(round(x), 0, self.logical_size-1)
        y = np.clip(round(y), 0, self.logical_size-1)
        
        # 画笔区域扩展
        for dx in range(-self.brush_size//2, self.brush_size//2 + 1):
            for dy in range(-self.brush_size//2, self.brush_size//2 + 1):
                nx = x + dx
                ny = y + dy
                if 0 <= nx < self.logical_size and 0 <= ny < self.logical_size:
                    self.draw.point((nx, ny), fill=self.brush_color)
        
        # 更新绘画显示
        self.draw_img.set_data(np.array(self.logical_img))
        self.fig.canvas.draw_idle()

    def clear_canvas(self):
        # 清除画布并重置预测
        self.logical_img = Image.new('L', (self.logical_size, self.logical_size), self.background_color)
        self.draw = ImageDraw.Draw(self.logical_img)
        self.draw_img.set_data(np.array(self.logical_img))
        # 重置概率图
        for bar in self.bar_plot:
            bar.set_height(0)
        self.ax_prob.set_title("预测概率分布")
        self.fig.canvas.draw_idle()

    def predict(self):
        # 实时预测逻辑
        img_np = np.array(self.logical_img) / 255.0  # 归一化到0-1
        img_np = (img_np - 0.5) / 0.5  # 与训练时的Normalize对应
        img_tensor = torch.tensor(img_np, dtype=torch.float32).unsqueeze(0).unsqueeze(0)
        
        # 预测
        with torch.no_grad():
            output = model(img_tensor)
            probabilities = torch.softmax(output, dim=1).squeeze().numpy()
            predicted_class = np.argmax(probabilities)
        
        # 实时更新概率图
        for i, bar in enumerate(self.bar_plot):
            bar.set_height(probabilities[i])
        self.ax_prob.set_title(f"预测结果：{predicted_class}（置信度：{probabilities[predicted_class]:.2f}）")
        self.fig.canvas.draw_idle()

# --------------------------
# 3. 运行应用
# --------------------------
if __name__ == "__main__":
    root = tk.Tk()
    app = DrawingApp(root)
    root.mainloop()