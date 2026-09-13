import torch
import cv2
import numpy as np
from torch import nn
import torch.nn.functional as F

# 检测模型
# 加载YOLOv5模型（如果本地有就用本地的，没有就下载）
yolo_model = torch.hub.load('ultralytics/yolov5', 'yolov5s', pretrained=True)
yolo_model.eval()  # 设置为评估模式

class BasicBlock(nn.Module):
    def __init__(self, in_channels, out_channels, stride=1):
        super().__init__()

        self.conv1 = nn.Conv2d(in_channels, out_channels, kernel_size=3, stride=stride, padding=1, bias=False)
        self.bn1 = nn.BatchNorm2d(out_channels)
        self.relu = nn.ReLU(inplace=True)
        self.conv2 = nn.Conv2d(out_channels, out_channels, kernel_size=3, stride=1, padding=1, bias=False)
        self.bn2 = nn.BatchNorm2d(out_channels)

        # 下采样
        self.downsample = None
        if stride != 1 or in_channels != out_channels:
            self.downsample = nn.Sequential(
                nn.Conv2d(in_channels, out_channels, kernel_size=1, stride=stride, bias=False),
                nn.BatchNorm2d(out_channels)
            )

    def forward(self, x):
        identity = x

        out = self.conv1(x)
        out = self.bn1(out)
        out = self.relu(out)

        out = self.conv2(out)
        out = self.bn2(out)

        if self.downsample is not None:
            identity = self.downsample(x)

        out += identity
        out = self.relu(out)

        return out
    

class ResNet(nn.Module):
    def __init__(self, num_classes=1):
        super().__init__()

        self.conv1 = nn.Conv2d(3, 64, kernel_size=7, stride=2, padding=3, bias=False)
        self.bn1 = nn.BatchNorm2d(64)
        self.relu = nn.ReLU(inplace=True)
        self.maxpool = nn.MaxPool2d(kernel_size=3, stride=2, padding=1)

        # 创建各个层
        self.layer1 = self._make_layer(64, 64, 2, stride=1)
        self.layer2 = self._make_layer(64, 128, 2, stride=2)
        self.layer3 = self._make_layer(128, 256, 2, stride=2)
        self.layer4 = self._make_layer(256, 512, 2, stride=2)

        # 创建全连接层
        self.avgpool = nn.AdaptiveAvgPool2d((1, 1))
        self.fc = nn.Linear(512, num_classes)

    def _make_layer(self, in_channels, out_channels, blocks, stride):
        layers = []
        layers.append(BasicBlock(in_channels, out_channels, stride))

        for _ in range(1, blocks):
            layers.append(BasicBlock(out_channels, out_channels))

        return nn.Sequential(*layers)
    
    def forward(self, x):
        x = self.conv1(x)
        x = self.bn1(x)
        x = self.relu(x)
        x = self.maxpool(x)

        x = self.layer1(x)
        x = self.layer2(x)
        x = self.layer3(x)
        x = self.layer4(x)

        x = self.avgpool(x)
        x = torch.flatten(x, 1)
        x = self.fc(x)
        
        return x
    

def object_detection(frame):
    """检测并截取人物图像"""
    # 使用YOLOv5进行检测
    results = yolo_model(frame)
    
    # 获取渲染后的图像（复制一份用于修改）
    rendered_frame = results.render()[0].copy()
    
    person_detected = False
    person_img = None
    
    # 打印结果
    for *box, conf, cls in results.xyxy[0]:
        label = results.names[int(cls)]
        confidence = float(conf)
        print(f"{label}: {confidence:.2%}")

        if label == "person" and confidence > 0.5:
            # 获取检测框的坐标
            x1, y1, x2, y2 = map(int, box)
            
            # 确保坐标在图像范围内
            x1, y1 = max(0, x1), max(0, y1)
            x2, y2 = min(frame.shape[1], x2), min(frame.shape[0], y2)
            
            # 检查区域是否有效
            if x2 > x1 and y2 > y1:
                # 在复制的图像上绘制矩形框
                cv2.rectangle(rendered_frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                
                # 截取人物区域图像
                person_img = frame[y1:y2, x1:x2]
                if person_img.size > 0:  # 确保图像非空
                    # 调整大小为模型输入大小
                    person_img = cv2.resize(person_img, (224, 224))  # ResNet通常使用224x224
                    person_detected = True
                    break  # 只处理第一个检测到的人物
    
    return person_img, rendered_frame, person_detected


def preprocess_image(img):
    """预处理图像以供模型使用"""
    if img is None:
        return None
    
    # 转换为RGB
    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    
    # 标准化
    img_normalized = img_rgb.astype(np.float32) / 255.0
    
    # 转换为Tensor
    img_tensor = torch.from_numpy(img_normalized).float()
    
    # 调整维度顺序
    img_tensor = img_tensor.permute(2, 0, 1)  # (C, H, W)
    
    # 标准化（ImageNet标准）
    mean = torch.tensor([0.485, 0.456, 0.406]).view(3, 1, 1)
    std = torch.tensor([0.229, 0.224, 0.225]).view(3, 1, 1)
    img_tensor = (img_tensor - mean) / std
    
    return img_tensor


def main():
    # 初始化摄像头
    cap = cv2.VideoCapture(0)
    
    if not cap.isOpened():
        print("无法打开摄像头")
        return
    
    # 创建模型
    model = ResNet(num_classes=1)
    print("模型架构:")
    print(model)
    
    # 加载预训练权重（如果有的话）
    # model.load_state_dict(torch.load('model.pth'))
    
    # 设置为评估模式
    model.eval()
    
    print("\n开始检测，按 'q' 键退出...")
    
    while True:
        ret, frame = cap.read()
        if not ret:
            print("无法获取帧")
            break
        
        # 进行目标检测
        person_img, rendered_frame, person_detected = object_detection(frame)
        
        if person_detected and person_img is not None:
            # 显示截取的人物图像
            cv2.imshow('Person ROI', person_img)
            
            # 预处理图像
            processed_img = preprocess_image(person_img)
            
            if processed_img is not None:
                # 添加batch维度
                processed_img = processed_img.unsqueeze(0)  # (1, C, H, W)
                
                # 模型推理
                with torch.no_grad():
                    output = model(processed_img)
                    print(f"模型输出: {output.item():.4f}")
                    
                    # 可以根据输出做二分类判断
                    prediction = torch.sigmoid(output).item()
                    if prediction > 0.5:
                        status = "Positive"
                        color = (0, 255, 0)
                    else:
                        status = "Negative"
                        color = (0, 0, 255)
                    
                    # 在图像上显示状态
                    cv2.putText(rendered_frame, f"Status: {status} ({prediction:.2f})", 
                               (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)
        
        # 显示检测结果
        cv2.imshow('Person Detection', rendered_frame)
        
        # 按'q'退出
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    
    # 释放资源
    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()