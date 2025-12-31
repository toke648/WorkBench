import cv2
import numpy as np
from ultralytics import YOLO

class PanoramicSegmentation:
    def __init__(self):
        # 加载YOLO分割模型
        self.yolo_model = YOLO('yolov8n-seg.pt')
        
    def create_panoramic_view(self, image_path):
        """创建全景分割视图"""
        # 读取图像
        img = cv2.imread(image_path)
        if img is None:
            print(f"无法读取图像: {image_path}")
            return None
        
        # 运行YOLO分割
        results = self.yolo_model(img)
        
        # 创建全景分割图
        panoramic = np.zeros_like(img)
        
        if results[0].masks is not None:
            masks = results[0].masks.data.cpu().numpy()
            boxes = results[0].boxes.data.cpu().numpy()
            
            # 定义类别颜色映射
            class_colors = {
                0: (220, 20, 60),    # 人 - 红色
                2: (0, 0, 255),      # 车 - 蓝色
                5: (0, 255, 0),      # 公交车 - 绿色
                7: (255, 0, 0),      # 卡车 - 深红
                15: (255, 255, 0),   # 狗 - 青色
                16: (255, 165, 0),   # 猫 - 橙色
            }
            
            for i, (mask, box) in enumerate(zip(masks, boxes)):
                cls_id = int(box[5])
                color = class_colors.get(cls_id, (128, 128, 128))
                
                # 应用掩码
                binary_mask = (mask > 0.3).astype(np.uint8)
                for c in range(3):
                    panoramic[:, :, c] = np.where(
                        binary_mask == 1,
                        color[c],
                        panoramic[:, :, c]
                    )
        
        return img, panoramic

# 使用示例
if __name__ == "__main__":
    ps = PanoramicSegmentation()
    
    # 实时摄像头全景分割
    cap = cv2.VideoCapture(0)
    
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        
        # 运行全景分割
        results = ps.yolo_model(frame)
        panoramic = np.zeros_like(frame)
        
        if results[0].masks is not None:
            masks = results[0].masks.data.cpu().numpy()
            
            for i, mask in enumerate(masks):
                # 随机颜色
                color = np.random.randint(0, 256, 3).tolist()
                binary_mask = (mask > 0.3).astype(np.uint8)
                
                for c in range(3):
                    panoramic[:, :, c] = np.where(
                        binary_mask == 1,
                        color[c],
                        panoramic[:, :, c]
                    )
        
        # 显示
        combined = np.hstack([frame, panoramic])
        cv2.putText(combined, "原始图像", (10, 30), 
                   cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        cv2.putText(combined, "全景分割", (frame.shape[1]+10, 30), 
                   cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        
        cv2.imshow('Panoramic Segmentation', combined)
        
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    
    cap.release()
    cv2.destroyAllWindows()