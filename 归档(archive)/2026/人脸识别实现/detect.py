import cv2
import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
from torchvision import transforms, models
import time
from collections import deque
import os

# ============ 1. 增强版人脸检测器 ============
class EnhancedFaceDetector:
    """使用OpenCV DNN模型的更准确检测器"""  # DNN 模型

    def __init__(self, confidence_threshold=0.7):
        self.confidence_threshold = confidence_threshold

        # 加载OpenCV的深度学习人脸检测器
        # 优先使用本地 models 目录中的文件，不存在则自动下载
        base_dir = os.path.dirname(__file__)
        model_dir = os.path.join(base_dir, "models")
        os.makedirs(model_dir, exist_ok=True)

        prototxt_path = os.path.join(model_dir, "deploy.prototxt") # 模型裱框位置信息权重
        caffemodel_path = os.path.join(model_dir, "res10_300x300_ssd_iter_140000.caffemodel")  # 模型的权重文件，基于opencv14000图片训练的基底模型，能够识别人脸

        prototxt_url = "https://raw.githubusercontent.com/opencv/opencv/master/samples/dnn/face_detector/deploy.prototxt"
        caffemodel_url = "https://raw.githubusercontent.com/opencv/opencv_3rdparty/master/dnn_models/res10_300x300_ssd_iter_140000.caffemodel"

        def _download(url, dst):
            try:
                import urllib.request  # 新增：在函数内导入，避免未导入导致报错
                urllib.request.urlretrieve(url, dst)
                return True
            except Exception as e:
                print(f"下载失败: {url} -> {dst}, 错误: {e}")
                return False

        if not os.path.exists(prototxt_path):
            print("未找到 deploy.prototxt，正在下载...")
            _download(prototxt_url, prototxt_path)

        if not os.path.exists(caffemodel_path):
            print("未找到 res10_300x300_ssd_iter_140000.caffemodel，正在下载...")
            _download(caffemodel_url, caffemodel_path)

        self.net = None
        try:
            if os.path.exists(prototxt_path) and os.path.exists(caffemodel_path):
                self.net = cv2.dnn.readNetFromCaffe(prototxt_path, caffemodel_path)
                # 使用GPU加速（如果可用）
                if cv2.cuda.getCudaEnabledDeviceCount() > 0:
                    self.net.setPreferableBackend(cv2.dnn.DNN_BACKEND_CUDA)
                    self.net.setPreferableTarget(cv2.dnn.DNN_TARGET_CUDA)
                    print("使用GPU加速")
                else:
                    print("使用CPU")
            else:
                print("DNN模型文件仍不存在，将使用Haar级联作为备用检测器。")
        except Exception as e:
            print(f"DNN模型加载失败，将使用Haar级联作为备用检测器。错误: {e}")
            self.net = None

        # 备用：Haar 级联
        if self.net is None:
            self.face_cascade = cv2.CascadeClassifier(
                cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
            )
    
    def detect(self, image, show_fps=False):
        """
        检测图像中的人脸
        Returns: [(x1, y1, x2, y2, confidence), ...]
        """
        start_time = time.time()

        # 如果DNN可用，优先使用DNN
        if self.net is not None:
            (h, w) = image.shape[:2]
            blob = cv2.dnn.blobFromImage(
                cv2.resize(image, (300, 300)),
                1.0,
                (300, 300),
                (104.0, 177.0, 123.0)
            )
            self.net.setInput(blob)
            detections = self.net.forward()

            faces = []
            for i in range(0, detections.shape[2]):
                confidence = detections[0, 0, i, 2]
                if confidence > self.confidence_threshold:
                    box = detections[0, 0, i, 3:7] * np.array([w, h, w, h])
                    (x1, y1, x2, y2) = box.astype("int")
                    x1 = max(0, x1); y1 = max(0, y1)
                    x2 = min(w, x2); y2 = min(h, y2)
                    faces.append((x1, y1, x2, y2, confidence))

            if show_fps:
                fps = 1.0 / (time.time() - start_time)
                return faces, fps
            return faces

        # 否则使用Haar级联作为备用检测
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        haar_faces = self.face_cascade.detectMultiScale(
            gray,
            scaleFactor=1.1,
            minNeighbors=5,
            minSize=(30, 30)
        )
        detections = []
        for (x, y, w, h) in haar_faces:
            detections.append((x, y, x + w, y + h, 0.9))

        if show_fps:
            fps = 1.0 / (time.time() - start_time)
            return detections, fps
        return detections

# ============ 2. 轻量级特征提取模型 ============
class MobileFaceNet(nn.Module):
    """为实时应用优化的轻量级人脸识别模型"""
    # 简易的神经网络模型，用于特征提取
    

    def __init__(self, embedding_size=128):
        super(MobileFaceNet, self).__init__()
        
        # 使用MobileNetV2作为骨干网络
        self.backbone = models.mobilenet_v2(pretrained=True)
        
        # 修改分类器
        num_features = self.backbone.classifier[1].in_features
        self.backbone.classifier = nn.Identity()
        
        # 嵌入层
        self.embedding = nn.Sequential(
            nn.Linear(num_features, 256),
            nn.BatchNorm1d(256),
            nn.ReLU(inplace=True),
            nn.Dropout(0.2),
            nn.Linear(256, embedding_size)
        )
    
    def forward(self, x):
        # 主要实现的流程是：
        # 1. 获取特征向量
        # 2. 获取分类权重
        # 3. 计算分类得分
        # 4. 计算损失
        # 5. 返回分类得分和损失

        features = self.backbone(x)
        embeddings = self.embedding(features)
        # L2归一化
        embeddings = F.normalize(embeddings, p=2, dim=1)
        return embeddings

# ============ 3. 实时摄像头人脸识别系统 ============
class RealTimeFaceRecognition:
    def __init__(self, camera_id=0, display_size=(800, 600)):
        """
        初始化实时人脸识别系统
        camera_id: 摄像头ID（0为默认摄像头）
        display_size: 显示窗口尺寸
        """
        self.camera_id = camera_id
        self.display_size = display_size
        
        # 初始化设备
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        print(f"使用设备: {self.device}")
        
        # 初始化组件
        self.detector = EnhancedFaceDetector(confidence_threshold=0.7)
        self.model = self.load_model()
        
        # 人脸数据库
        self.face_database = {}
        
        # 性能监控
        self.fps_queue = deque(maxlen=30)
        self.processing_times = deque(maxlen=30)
        
        # 颜色配置
        self.colors = {
            'box': (0, 255, 0),      # 绿色框
            'unknown': (0, 0, 255),  # 红色框（未知人脸）
            'text': (255, 255, 255), # 白色文字
            'landmark': (0, 255, 255) # 黄色关键点
        }
        
        # 注册一些示例人脸（实际使用时从文件加载）
        self.init_sample_faces()
        
        # 新增：识别结果缓存与注册输入状态（避免使用 input() 阻塞）
        self.last_recognitions = []  # 缓存最近一次识别结果，供每帧显示
        self.register_mode = False   # 是否处于注册输入模式
        self.name_buffer = ""        # 注册模式下的姓名输入缓冲

        # 开启摄像头
        self.cap = cv2.VideoCapture(camera_id)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        
        if not self.cap.isOpened():
            raise ValueError(f"无法打开摄像头 {camera_id}")
        
        print("摄像头初始化完成")
    
    def load_model(self):
        """加载预训练模型"""
        model = MobileFaceNet(embedding_size=128).to(self.device)
        model.eval()
        
        # 这里应该加载预训练权重
        # checkpoint = torch.load('face_model.pth', map_location=self.device)
        # model.load_state_dict(checkpoint['model_state_dict'])
        
        print("模型加载完成")
        return model
    
    def init_sample_faces(self):
        """初始化示例人脸数据库"""
        # 实际使用时应该从文件加载
        print("初始化示例人脸数据库...")
        
        # 这里创建一些虚拟特征向量用于演示
        # 实际应用中应该通过注册流程添加真实人脸
        
        # 示例1: 管理员
        self.face_database['Admin'] = {
            'feature': np.random.randn(128),  # 实际应为真实特征
            'color': (255, 215, 0)  # 金色
        }
        
        # 示例2: 访客
        self.face_database['Guest'] = {
            'feature': np.random.randn(128),
            'color': (0, 255, 255)  # 青色
        }
        
        print(f"数据库已加载 {len(self.face_database)} 个人脸")
    
    def preprocess_face(self, frame, face_box):
        """预处理检测到的人脸"""
        x1, y1, x2, y2, confidence = face_box
        
        # 提取人脸区域
        face_roi = frame[y1:y2, x1:x2]
        
        if face_roi.size == 0:
            return None
        
        # 调整大小
        face_resized = cv2.resize(face_roi, (112, 112))
        
        # 转换为RGB
        face_rgb = cv2.cvtColor(face_resized, cv2.COLOR_BGR2RGB)
        
        # 归一化
        face_normalized = face_rgb.astype(np.float32) / 255.0
        face_normalized = (face_normalized - [0.485, 0.456, 0.406]) / [0.229, 0.224, 0.225]
        
        # 转换为tensor [C, H, W]
        face_tensor = torch.from_numpy(face_normalized.transpose(2, 0, 1)).float()
        face_tensor = face_tensor.unsqueeze(0)  # [1, C, H, W]
        
        return face_tensor.to(self.device)
    
    def extract_embedding(self, face_tensor):
        """提取特征向量"""
        with torch.no_grad():
            embedding = self.model(face_tensor)
        return embedding.cpu().numpy().flatten()
    
    def recognize_face(self, face_tensor, threshold=0.5):
        """识别人脸"""
        # 提取特征
        query_embedding = self.extract_embedding(face_tensor)
        
        # 与数据库比对
        best_match = "Unknown"
        best_similarity = 0
        match_color = self.colors['unknown']
        
        for name, data in self.face_database.items():
            db_feature = data['feature']
            
            # 计算余弦相似度
            similarity = np.dot(query_embedding, db_feature) / (
                np.linalg.norm(query_embedding) * np.linalg.norm(db_feature)
            )
            
            if similarity > best_similarity:
                best_similarity = similarity
                best_match = name
                match_color = data.get('color', self.colors['box'])
        
        # 判断是否匹配成功
        if best_similarity < threshold:
            best_match = "Unknown"
            match_color = self.colors['unknown']
        
        return best_match, best_similarity, match_color
    
    def draw_detection_results(self, frame, detections, recognitions=None):
        """在图像上绘制检测和识别结果"""
        frame_draw = frame.copy()
        
        # 绘制检测框和识别结果
        for i, (x1, y1, x2, y2, confidence) in enumerate(detections):
            # 获取识别结果
            if recognitions and i < len(recognitions):
                name, similarity, color = recognitions[i]
                label = f"{name}: {similarity:.2f}"
                box_color = color
            else:
                label = f"Face: {confidence:.2f}"
                box_color = self.colors['box']
            
            # 绘制人脸框
            cv2.rectangle(frame_draw, (x1, y1), (x2, y2), box_color, 2)
            
            # 绘制置信度条
            bar_height = 5
            bar_width = int((x2 - x1) * confidence)
            cv2.rectangle(frame_draw, 
                         (x1, y1 - bar_height - 25), 
                         (x1 + bar_width, y1 - 20), 
                         box_color, -1)
            
            # 绘制文本背景
            text_size = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 2)[0]
            cv2.rectangle(frame_draw,
                         (x1, y1 - text_size[1] - 30),
                         (x1 + text_size[0] + 10, y1 - 10),
                         (0, 0, 0),
                         -1)
            
            # 绘制文本
            cv2.putText(frame_draw, label,
                       (x1 + 5, y1 - 20),
                       cv2.FONT_HERSHEY_SIMPLEX,
                       0.5, self.colors['text'], 2)
            
            # 绘制人脸序号
            cv2.putText(frame_draw, f"#{i+1}",
                       (x1, y2 + 20),
                       cv2.FONT_HERSHEY_SIMPLEX,
                       0.5, box_color, 2)
        
        return frame_draw
    
    def draw_metrics(self, frame, fps, processing_time):
        """在图像上绘制性能指标"""
        # 绘制FPS
        fps_text = f"FPS: {fps:.1f}"
        cv2.putText(frame, fps_text, (10, 30),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        
        # 绘制处理时间
        time_text = f"Process: {processing_time*1000:.1f}ms"
        cv2.putText(frame, time_text, (10, 60),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        
        # 绘制人脸数量
        face_text = f"Faces: {len(self.face_database)}"
        cv2.putText(frame, face_text, (10, 90),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        
        # 绘制状态栏
        cv2.putText(frame, "Real-Time Face Recognition - Press 'q' to quit",
                   (10, frame.shape[0] - 10),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (200, 200, 200), 1)
    
    def register_new_face(self, frame, name):
        """注册新的人脸"""
        # 检测人脸
        detections = self.detector.detect(frame)
        
        if len(detections) != 1:
            print(f"请确保画面中有且只有一张人脸 (检测到 {len(detections)} 张)")
            return False
        
        # 提取并注册人脸
        face_box = detections[0]
        face_tensor = self.preprocess_face(frame, face_box)
        
        if face_tensor is None:
            print("无法提取人脸特征")
            return False
        
        # 提取特征
        embedding = self.extract_embedding(face_tensor)
        
        # 保存到数据库
        self.face_database[name] = {
            'feature': embedding,
            'color': tuple(np.random.randint(0, 255, 3).tolist())
        }
        
        print(f"成功注册: {name}")
        return True
    
    def run_real_time(self):
        """运行实时识别"""
        print("启动实时人脸识别...")
        print("快捷键:")
        print("  'q' - 退出")
        print("  's' - 保存当前帧")
        print("  'r' - 注册新人脸")
        print("  'c' - 清除识别结果")
        
        # 新增：显式创建窗口，确保接收键盘事件
        cv2.namedWindow('Real-Time Face Recognition', cv2.WINDOW_NORMAL)

        # 控制变量
        last_recognition_time = time.time()
        recognition_interval = 0.5  # 每0.5秒识别一次（减少计算量）
        
        while True:
            start_time = time.time()
            
            # 读取帧
            ret, frame = self.cap.read()
            if not ret:
                print("无法读取帧")
                break
            
            # 调整显示尺寸
            display_frame = cv2.resize(frame, self.display_size)
            
            # 检测人脸（每帧都检测）
            detections, fps = self.detector.detect(display_frame, show_fps=True)
            self.fps_queue.append(fps)
            avg_fps = np.mean(self.fps_queue) if self.fps_queue else fps

            # 新增：实时在控制台输出检测结果
            if detections:
                print(f"[{time.strftime('%H:%M:%S')}] 检测到 {len(detections)} 张人脸 (FPS: {avg_fps:.1f})")
                for idx, (x1, y1, x2, y2, conf) in enumerate(detections, start=1):
                    print(f"  #{idx}: box=({x1},{y1},{x2},{y2}), conf={conf:.2f}")
            else:
                print(f"[{time.strftime('%H:%M:%S')}] 未检测到人脸 (FPS: {avg_fps:.1f})")

            # 定期进行识别（减少计算负载）
            current_time = time.time()
            recognitions = []
            if current_time - last_recognition_time > recognition_interval:
                if detections:
                    recognitions = []
                    for face_box in detections:
                        face_tensor = self.preprocess_face(display_frame, face_box)
                        if face_tensor is not None:
                            name, similarity, color = self.recognize_face(face_tensor, threshold=0.4)
                            recognitions.append((name, similarity, color))
                    # 缓存本次识别结果，用于后续帧显示身份
                    self.last_recognitions = recognitions
                last_recognition_time = current_time
            else:
                # 使用上次识别结果，让每一帧都显示身份
                recognitions = self.last_recognitions

            # 绘制结果
            result_frame = self.draw_detection_results(display_frame, detections, recognitions)
            
            # 新增：注册模式下在画面上显示输入提示与当前缓冲
            if self.register_mode:
                prompt = f"注册模式: 输入姓名 (Enter确认, Esc取消): {self.name_buffer}"
                cv2.rectangle(result_frame, (10, 100), (10 + 520, 130), (0, 0, 0), -1)
                cv2.putText(result_frame, prompt, (15, 120),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)

            # 计算处理时间
            processing_time = time.time() - start_time
            self.processing_times.append(processing_time)
            avg_processing_time = np.mean(self.processing_times)
            
            # 绘制性能指标
            self.draw_metrics(result_frame, avg_fps, avg_processing_time)
            
            # 显示
            cv2.imshow('Real-Time Face Recognition', result_frame)
            
            # 键盘控制（不再使用 input()）
            key = cv2.waitKey(1) & 0xFF

            if self.register_mode:
                # 注册输入模式：处理文本输入
                if key == 13:  # Enter确认
                    if self.name_buffer.strip():
                        self.register_new_face(display_frame, self.name_buffer.strip())
                    self.register_mode = False
                    self.name_buffer = ""
                elif key == 27:  # Esc取消
                    self.register_mode = False
                    self.name_buffer = ""
                elif key == 8:  # Backspace删除
                    self.name_buffer = self.name_buffer[:-1]
                elif 32 <= key <= 126:  # 可见字符
                    if len(self.name_buffer) < 32:
                        self.name_buffer += chr(key)
                # 在注册模式下不处理其他快捷键
                continue

            # 非注册模式的快捷键
            if key == ord('q'):  # 退出
                break
            elif key == ord('s'):  # 保存当前帧
                timestamp = time.strftime("%Y%m%d_%H%M%S")
                filename = f"screenshot_{timestamp}.jpg"
                cv2.imwrite(filename, result_frame)
                print(f"已保存截图: {filename}")
            elif key == ord('r'):  # 进入注册输入模式
                self.register_mode = True
                self.name_buffer = ""
            elif key == ord('c'):  # 清除识别结果
                print("识别结果已清除")
                self.last_recognitions = []
        
        # 清理
        self.cleanup()
    
    def cleanup(self):
        """清理资源"""
        self.cap.release()
        cv2.destroyAllWindows()
        print("资源已释放")

# ============ 4. 辅助功能：图片文件识别 ============
def recognize_image_file(image_path, recognizer):
    """识别单张图片文件"""
    # 读取图片
    image = cv2.imread(image_path)
    if image is None:
        print(f"无法读取图片: {image_path}")
        return
    
    # 调整大小
    image = cv2.resize(image, (800, 600))
    
    # 检测人脸
    detections = recognizer.detector.detect(image)
    
    print(f"检测到 {len(detections)} 张人脸")
    
    # 识别人脸
    recognitions = []
    for i, face_box in enumerate(detections):
        face_tensor = recognizer.preprocess_face(image, face_box)
        if face_tensor is not None:
            name, similarity, color = recognizer.recognize_face(face_tensor, threshold=0.4)
            recognitions.append((name, similarity, color))
            print(f"人脸 {i+1}: {name} (相似度: {similarity:.3f})")
    
    # 绘制结果
    result_image = recognizer.draw_detection_results(image, detections, recognitions)
    
    # 显示结果
    cv2.imshow('Image Recognition', result_image)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
    
    # 保存结果
    output_path = image_path.replace('.', '_result.')
    cv2.imwrite(output_path, result_image)
    print(f"结果已保存至: {output_path}")

# ============ 5. 主程序入口 ============
def main():
    """主函数"""
    print("=" * 50)
    print("实时人脸识别系统")
    print("=" * 50)
    
    # 创建识别器实例
    recognizer = RealTimeFaceRecognition(
        camera_id=0,  # 默认摄像头
        display_size=(800, 600)
    )
    
    try:
        # 运行实时识别
        recognizer.run_real_time()
        
    except KeyboardInterrupt:
        print("\n程序被用户中断")
    except Exception as e:
        print(f"发生错误: {str(e)}")
    finally:
        recognizer.cleanup()

# ============ 6. 备用方案：使用OpenCV Haar Cascade ============
class FallbackFaceDetector:
    """备用的人脸检测器（当DNN模型不可用时）"""
    def __init__(self):
        # 加载Haar级联分类器
        self.face_cascade = cv2.CascadeClassifier(
            cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
        )
        self.eye_cascade = cv2.CascadeClassifier(
            cv2.data.haarcascades + 'haarcascade_eye.xml'
        )
    
    def detect(self, image, show_fps=False):
        start_time = time.time()
        
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # 检测人脸
        faces = self.face_cascade.detectMultiScale(
            gray,
            scaleFactor=1.1,
            minNeighbors=5,
            minSize=(30, 30)
        )
        
        # 转换为统一格式
        detections = []
        for (x, y, w, h) in faces:
            detections.append((x, y, x+w, y+h, 0.9))  # 固定置信度
        
        if show_fps:
            fps = 1.0 / (time.time() - start_time)
            return detections, fps
        
        return detections

# ============ 7. 运行示例 ============
if __name__ == "__main__":
    # 检查依赖
    try:
        import cv2
        import torch
        import numpy as np
    except ImportError as e:
        print(f"缺少依赖库: {e}")
        print("请运行: pip install opencv-python torch torchvision numpy")
        exit(1)
    
    # 检查摄像头
    cap_test = cv2.VideoCapture(0)
    if not cap_test.isOpened():
        print("警告：无法访问摄像头")
        print("请确保摄像头已连接，或尝试其他摄像头ID")
        use_image_mode = input("是否使用图片模式？(y/n): ").lower()
        if use_image_mode == 'y':
            # 图片模式
            recognizer = RealTimeFaceRecognition(0, (800, 600))
            image_path = input("请输入图片路径: ")
            recognize_image_file(image_path, recognizer)
        else:
            print("程序退出")
    else:
        cap_test.release()
        # 正常运行实时识别
        main()