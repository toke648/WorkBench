import torch
import cv2
import numpy as np
from torch import nn
import torch.nn.functional as F
from facenet_pytorch import MTCNN, InceptionResnetV1
import torchvision.transforms as transforms
from PIL import Image

# 初始化MTCNN进行人脸检测
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
mtcnn = MTCNN(keep_all=True, device=device)

# 初始化FaceNet模型
facenet = InceptionResnetV1(pretrained='vggface2').eval().to(device)

class ArcFaceHead(nn.Module):
    """ArcFace头部，用于人脸识别"""
    def __init__(self, in_features=512, out_features=1000, s=64.0, m=0.5):
        super().__init__()
        self.in_features = in_features
        self.out_features = out_features
        self.s = s
        self.m = m
        
        self.weight = nn.Parameter(torch.FloatTensor(out_features, in_features))
        nn.init.xavier_uniform_(self.weight)
        
    def forward(self, input, label=None):
        # 归一化
        cosine = F.linear(F.normalize(input), F.normalize(self.weight))
        
        if label is not None:
            # 计算theta
            theta = torch.acos(torch.clamp(cosine, -1.0 + 1e-7, 1.0 - 1e-7))
            
            # 添加margin
            target_logit = torch.cos(theta + self.m)
            
            # 重构logits
            one_hot = torch.zeros_like(cosine)
            one_hot.scatter_(1, label.view(-1, 1).long(), 1)
            output = self.s * (one_hot * target_logit + (1 - one_hot) * cosine)
        else:
            output = self.s * cosine
            
        return output

class FaceRecognitionSystem(nn.Module):
    """完整的人脸识别系统"""
    def __init__(self, num_classes=1000, embed_size=512):
        super().__init__()
        
        # 使用预训练的FaceNet作为特征提取器
        self.backbone = InceptionResnetV1(pretrained='vggface2')
        
        # 冻结backbone参数
        for param in self.backbone.parameters():
            param.requires_grad = False
        
        # ArcFace分类头
        self.arcface = ArcFaceHead(embed_size, num_classes)
        
        # 特征库（用于存储已知人脸的特征向量）
        self.feature_bank = {}
        
    def extract_features(self, img):
        """提取人脸特征向量"""
        with torch.no_grad():
            embeddings = self.backbone(img)
        return embeddings
    
    def register_face(self, name, img):
        """注册新人脸到特征库"""
        features = self.extract_features(img)
        features = F.normalize(features, p=2, dim=1)
        
        if name not in self.feature_bank:
            self.feature_bank[name] = []
        
        self.feature_bank[name].append(features.cpu())
        print(f"已注册人脸: {name}")
        
    def recognize_face(self, img, threshold=0.7):
        """识别人脸"""
        features = self.extract_features(img)
        features = F.normalize(features, p=2, dim=1)
        
        best_match = None
        best_score = -1
        
        for name, stored_features in self.feature_bank.items():
            for stored in stored_features:
                stored = stored.to(features.device)
                # 计算余弦相似度
                similarity = F.cosine_similarity(features, stored).item()
                
                if similarity > best_score:
                    best_score = similarity
                    best_match = name
        
        if best_match and best_score > threshold:
            return best_match, best_score
        else:
            return "Unknown", best_score if best_score > 0 else 0
    
    def forward(self, x, label=None):
        """训练时的前向传播"""
        features = self.backbone(x)
        output = self.arcface(features, label)
        return output

def detect_and_crop_faces(frame):
    """使用MTCNN检测并裁剪人脸"""
    # 将BGR转换为RGB
    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    
    # 转换为PIL Image
    pil_img = Image.fromarray(frame_rgb)
    
    # 检测人脸
    boxes, probs = mtcnn.detect(pil_img)
    
    faces = []
    face_boxes = []
    
    if boxes is not None:
        for i, box in enumerate(boxes):
            if probs[i] > 0.9:  # 置信度阈值
                # 提取人脸区域
                x1, y1, x2, y2 = map(int, box)
                
                # 确保坐标在图像范围内
                x1, y1 = max(0, x1), max(0, y1)
                x2, y2 = min(frame.shape[1], x2), min(frame.shape[0], y2)
                
                if x2 > x1 and y2 > y1:
                    face_img = frame[y1:y2, x1:x2]
                    face_boxes.append((x1, y1, x2, y2))
                    faces.append(face_img)
    
    return faces, face_boxes

def preprocess_face(face_img):
    """预处理人脸图像以供FaceNet使用"""
    if face_img is None or face_img.size == 0:
        return None
    
    # 调整大小
    face_resized = cv2.resize(face_img, (160, 160))
    
    # 转换为RGB
    face_rgb = cv2.cvtColor(face_resized, cv2.COLOR_BGR2RGB)
    
    # 归一化
    face_normalized = face_rgb.astype(np.float32) / 255.0
    
    # 标准化（FaceNet使用的均值标准差）
    mean = np.array([0.5, 0.5, 0.5], dtype=np.float32)
    std = np.array([0.5, 0.5, 0.5], dtype=np.float32)
    face_normalized = (face_normalized - mean) / std
    
    # 转换为Tensor并调整维度
    face_tensor = torch.from_numpy(face_normalized).float()
    face_tensor = face_tensor.permute(2, 0, 1)  # (C, H, W)
    
    return face_tensor.unsqueeze(0).to(device)  # 添加batch维度

def main():
    # 初始化摄像头
    cap = cv2.VideoCapture(0)
    
    if not cap.isOpened():
        print("无法打开摄像头")
        return
    
    # 创建人脸识别系统
    face_system = FaceRecognitionSystem(num_classes=1000).to(device)
    face_system.eval()
    
    # 示例：可以预先注册一些已知人脸
    # 这里需要你有已知人脸的图片
    # face_system.register_face("Person1", preprocessed_image1)
    # face_system.register_face("Person2", preprocessed_image2)
    
    print("开始人脸检测和识别，按 'q' 键退出...")
    print("按 'r' 键注册当前人脸")
    print("按 's' 键保存当前人脸图像")
    
    while True:
        ret, frame = cap.read()
        if not ret:
            print("无法获取帧")
            break
        
        # 克隆原始帧用于绘制
        display_frame = frame.copy()
        
        # 检测人脸
        faces, boxes = detect_and_crop_faces(frame)
        
        if faces and boxes:
            for i, (face_img, box) in enumerate(zip(faces, boxes)):
                x1, y1, x2, y2 = box
                
                # 绘制人脸框
                cv2.rectangle(display_frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                
                # 预处理人脸图像
                face_tensor = preprocess_face(face_img)
                
                if face_tensor is not None:
                    # 识别人脸
                    name, confidence = face_system.recognize_face(face_tensor)
                    
                    # 显示识别结果
                    label = f"{name}: {confidence:.2f}"
                    cv2.putText(display_frame, label, (x1, y1-10), 
                               cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                    
                    # 显示人脸区域
                    cv2.imshow(f'Face {i}', face_img)
        
        # 显示整体画面
        cv2.imshow('Face Recognition', display_frame)
        
        # 按键处理
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            break
        elif key == ord('r') and faces:
            # 注册新人脸
            name = input("请输入姓名: ")
            if faces and name:
                face_tensor = preprocess_face(faces[0])
                if face_tensor is not None:
                    face_system.register_face(name, face_tensor)
        elif key == ord('s') and faces:
            # 保存人脸图像
            for i, face_img in enumerate(faces):
                filename = f"face_{i}_{len(face_system.feature_bank)}.jpg"
                cv2.imwrite(filename, face_img)
                print(f"保存人脸图像: {filename}")
    
    # 释放资源
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    # 安装依赖: pip install facenet-pytorch opencv-python pillow torch torchvision
    main()