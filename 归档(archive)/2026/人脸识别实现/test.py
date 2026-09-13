import cv2
import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
from torchvision import transforms, models

# ============ 1. 自定义简易人脸检测器 ============
class SimpleFaceDetector:
    """使用OpenCV Haar Cascade的简易检测器"""
    def __init__(self):
        self.face_cascade = cv2.CascadeClassifier(
            cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
        )
    
    def detect(self, image):
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        faces = self.face_cascade.detectMultiScale(
            gray, 
            scaleFactor=1.1, 
            minNeighbors=5, 
            minSize=(30, 30)
        )
        return faces

# ============ 2. 自定义特征提取模型 ============
class SimpleFaceNet(nn.Module):
    """简化的FaceNet风格模型"""
    def __init__(self, embedding_size=128):
        super(SimpleFaceNet, self).__init__()
        
        # 使用预训练的ResNet作为骨干
        self.backbone = models.resnet18(pretrained=True)
        
        # 移除最后的全连接层
        num_features = self.backbone.fc.in_features
        self.backbone.fc = nn.Identity()
        
        # 添加自定义的嵌入层
        self.embedding = nn.Sequential(
            nn.Linear(num_features, 512),
            nn.BatchNorm1d(512),
            nn.ReLU(),
            nn.Dropout(0.5),
            nn.Linear(512, embedding_size)
        )
        
        # ArcFace的Margin参数
        self.margin = 0.3
        self.scale = 64
    
    def forward(self, x, labels=None):
        # 提取特征
        features = self.backbone(x)
        embeddings = self.embedding(features)
        
        # L2归一化（重要！）
        embeddings = F.normalize(embeddings, p=2, dim=1)
        
        return embeddings

# ============ 3. 人脸对齐预处理 ============
class FaceAligner:
    """简单的人脸对齐"""
    def __init__(self, output_size=(112, 112)):
        self.output_size = output_size
        
    def align(self, image, face_box):
        """基于眼睛位置对齐人脸"""
        x, y, w, h = face_box
        
        # 简单裁剪（实际应用中应使用关键点对齐）
        face = image[y:y+h, x:x+w]
        
        if face.size == 0:
            return None
            
        # 调整大小
        face_resized = cv2.resize(face, self.output_size)
        
        # 标准化
        face_normalized = face_resized.astype(np.float32) / 255.0
        face_normalized = (face_normalized - 0.5) / 0.5
        
        # 转换为CHW格式
        face_normalized = np.transpose(face_normalized, (2, 0, 1))
        
        return face_normalized

# ============ 4. 完整流程整合 ============
class LightweightFaceRecognition:
    def __init__(self, device='cpu'):
        self.device = device
        
        # 初始化组件
        self.detector = SimpleFaceDetector()
        self.aligner = FaceAligner()
        self.model = SimpleFaceNet().to(device)
        self.model.eval()
        
        # 图像预处理
        self.transform = transforms.Compose([
            transforms.ToTensor(),
            transforms.Normalize([0.5, 0.5, 0.5], [0.5, 0.5, 0.5])
        ])
        
        # 数据库
        self.database = {}
    
    def preprocess_image(self, image_path):
        """预处理单张图像"""
        image = cv2.imread(image_path)
        if image is None:
            return None
        
        # 检测人脸
        faces = self.detector.detect(image)
        if len(faces) == 0:
            return None
        
        # 取最大的人脸
        x, y, w, h = max(faces, key=lambda rect: rect[2] * rect[3])
        
        # 对齐和预处理
        face_aligned = self.aligner.align(image, (x, y, w, h))
        
        if face_aligned is None:
            return None
        
        # 转换为tensor
        face_tensor = torch.from_numpy(face_aligned).float().unsqueeze(0)
        
        return face_tensor
    
    def extract_embedding(self, image_tensor):
        """提取特征向量"""
        with torch.no_grad():
            embedding = self.model(image_tensor.to(self.device))
        return embedding.cpu().numpy().flatten()
    
    def register(self, image_path, name):
        """注册新人脸"""
        face_tensor = self.preprocess_image(image_path)
        if face_tensor is None:
            print(f"无法从 {image_path} 提取人脸")
            return False
        
        embedding = self.extract_embedding(face_tensor)
        self.database[name] = embedding
        print(f"注册成功: {name}")
        return True
    
    def recognize(self, image_path, threshold=0.6):
        """识别人脸"""
        # 提取查询人脸的特征
        query_tensor = self.preprocess_image(image_path)
        if query_tensor is None:
            return "未检测到人脸", 0.0
        
        query_embedding = self.extract_embedding(query_tensor)
        
        # 与数据库比对
        best_match = None
        best_similarity = -1
        
        for name, db_embedding in self.database.items():
            # 计算余弦相似度
            similarity = np.dot(query_embedding, db_embedding) / (
                np.linalg.norm(query_embedding) * np.linalg.norm(db_embedding)
            )
            
            if similarity > best_similarity:
                best_similarity = similarity
                best_match = name
        
        if best_similarity > threshold:
            return best_match, best_similarity
        else:
            return "Unknown", best_similarity

# ============ 5. 训练代码示例 ============
def train_face_recognition_model():
    """
    训练人脸识别模型的简化示例
    实际训练需要大规模人脸数据集
    """
    # 这里展示ArcFace损失函数的实现
    class ArcFaceLoss(nn.Module):
        def __init__(self, num_classes, embedding_size, margin=0.3, scale=64):
            super(ArcFaceLoss, self).__init__()
            self.num_classes = num_classes
            self.embedding_size = embedding_size
            self.margin = margin
            self.scale = scale
            
            # 分类权重
            self.W = nn.Parameter(torch.Tensor(num_classes, embedding_size))
            nn.init.xavier_normal_(self.W)
        
        def forward(self, embeddings, labels):
            # 归一化权重和特征
            W_norm = F.normalize(self.W, p=2, dim=1)
            embeddings_norm = F.normalize(embeddings, p=2, dim=1)
            
            # 计算余弦相似度
            cosine = F.linear(embeddings_norm, W_norm)
            
            # 添加角度边界
            theta = torch.acos(torch.clamp(cosine, -1.0 + 1e-7, 1.0 - 1e-7))
            
            # 创建one-hot编码
            one_hot = torch.zeros_like(cosine)
            one_hot.scatter_(1, labels.view(-1, 1), 1)
            
            # 应用margin
            cosine_margin = torch.cos(theta + self.margin)
            output = cosine + one_hot * (cosine_margin - cosine)
            
            # 缩放
            output = output * self.scale
            
            # 计算交叉熵损失
            loss = F.cross_entropy(output, labels)
            
            return loss

# ============ 6. 实际部署优化建议 ============
"""
1. 模型量化加速：
   model_quantized = torch.quantization.quantize_dynamic(
       model, {nn.Linear}, dtype=torch.qint8
   )

2. 使用ONNX导出：
   torch.onnx.export(model, dummy_input, "face_recog.onnx")

3. 向量数据库优化：
   - 使用FAISS或Milvus进行快速向量检索
   - 实现分桶索引加速

4. 多线程处理：
   - 摄像头捕获、检测、识别分不同线程
   - 使用队列传递数据

5. 模型蒸馏：
   - 用大模型训练小模型
   - 保持精度，提升速度
"""

# ============ 使用示例 ============
def usage_example():
    # 初始化
    recognizer = LightweightFaceRecognition(device='cpu')
    
    # 注册人脸（需要真实图片路径）
    # recognizer.register("path/to/person1.jpg", "Alice")
    recognizer.register("4dc6d1888962a3c0bb64615537ea037e.jpg", "Tim")

    print(recognizer.database)
    
    # 识别
    # result, confidence = recognizer.recognize("path/to/test.jpg")
    result, confidence = recognizer.recognize("4dc6d1888962a3c0bb64615537ea037e.jpg")
    print(f"识别结果: {result}, 置信度: {confidence:.3f}")
    
    pass

if __name__ == "__main__":
    usage_example()
    print("代码框架已就绪，需要实际图片数据运行")