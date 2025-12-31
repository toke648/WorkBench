import cv2
import torch
from ultralytics import YOLO
import numpy as np

# 加载YOLOv8姿态检测模型
# 可选模型: yolov8n-pose.pt, yolov8s-pose.pt, yolov8m-pose.pt, yolov8l-pose.pt, yolov8x-pose.pt
model = YOLO('yolov8n-pose.pt')  # 自动下载如果本地没有

# 定义COCO关键点名称
KEYPOINT_NAMES = [
    "nose", "left_eye", "right_eye", "left_ear", "right_ear",
    "left_shoulder", "right_shoulder", "left_elbow", "right_elbow",
    "left_wrist", "right_wrist", "left_hip", "right_hip",
    "left_knee", "right_knee", "left_ankle", "right_ankle"
]

# 骨骼连接和颜色
SKELETON = [
    ((0, 1), (255, 0, 0)),  # 鼻子到左眼
    ((0, 2), (0, 255, 0)),  # 鼻子到右眼
    ((1, 3), (255, 0, 0)),  # 左眼到左耳
    ((2, 4), (0, 255, 0)),  # 右眼到右耳
    ((5, 7), (255, 255, 0)),  # 左肩到左肘
    ((7, 9), (255, 255, 0)),  # 左肘到左手腕
    ((6, 8), (0, 255, 255)),  # 右肩到右肘
    ((8, 10), (0, 255, 255)),  # 右肘到右手腕
    ((5, 6), (255, 0, 255)),  # 左肩到右肩
    ((5, 11), (255, 165, 0)),  # 左肩到左臀
    ((6, 12), (0, 165, 255)),  # 右肩到右臀
    ((11, 13), (255, 165, 0)),  # 左臀到左膝
    ((13, 15), (255, 165, 0)),  # 左膝到左脚踝
    ((12, 14), (0, 165, 255)),  # 右臀到右膝
    ((14, 16), (0, 165, 255)),  # 右膝到右脚踝
    ((11, 12), (128, 128, 128)),  # 左臀到右臀
]

# 打开摄像头
cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

print("YOLOv8 姿态检测 - 按 'q' 键退出")

while True:
    success, frame = cap.read()
    if not success:
        break
    
    # 运行姿态检测
    results = model(frame, conf=0.5, verbose=False)
    
    # 绘制结果
    annotated_frame = results[0].plot()
    
    # 添加详细的关键点信息
    if results[0].keypoints is not None:
        keypoints = results[0].keypoints.data.cpu().numpy()
        num_people = keypoints.shape[0]
        
        # 在左上角显示检测到的人数
        cv2.putText(annotated_frame, f"Persons: {num_people}", (10, 60),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        
        # 对每个人显示关键点置信度
        for i in range(num_people):
            # 计算平均置信度
            confidences = keypoints[i, :, 2]
            avg_conf = np.mean(confidences[confidences > 0])
            
            # 显示在图像上
            cv2.putText(annotated_frame, f"Person {i+1}: {avg_conf:.2%}", 
                       (10, 90 + i*30), cv2.FONT_HERSHEY_SIMPLEX, 
                       0.6, (0, 200, 255), 2)
    
    # 显示图像
    cv2.imshow('YOLOv8 Pose Estimation', annotated_frame)
    
    # 在控制台输出详细信息
    if results[0].keypoints is not None and len(results[0].keypoints) > 0:
        print(f"\n检测到 {len(results[0].keypoints)} 个人:")
        for i, kpts in enumerate(results[0].keypoints):
            visible_kpts = sum(kpt[2] > 0.3 for kpt in kpts.data[0])
            print(f"  人物{i+1}: {visible_kpts}/17 个关键点可见")
    
    # 按q退出
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()