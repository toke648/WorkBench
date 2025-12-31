from ultralytics import YOLO
import cv2
import os

# 设置摄像头
cap = cv2.VideoCapture(0)
if not cap.isOpened():
    print("无法打开摄像头")
    exit()

# 检测并加载YOLOv8模型
model_path = "yolov8n.pt"
if not os.path.exists(model_path):
    print("正在下载YOLOv8n模型...")
    model = YOLO('yolov8n.pt')  # 这会自动下载
    model.save(model_path)  # 保存到本地
else:
    print("加载本地YOLOv8模型...")
    model = YOLO(model_path)

print("按 'q' 键退出程序...")

while True:
    ret, frame = cap.read()
    if not ret:
        print("无法获取视频帧")
        break
    
    # 执行检测
    results = model(frame, verbose=False)
    
    # 绘制检测结果
    annotated_frame = results[0].plot()
    
    # 显示画面
    cv2.imshow('YOLOv8 实时检测', annotated_frame)
    
    # 打印检测结果
    if len(results[0].boxes) > 0:
        print(f"\n检测到 {len(results[0].boxes)} 个对象:")
        for box in results[0].boxes:
            label = model.names[int(box.cls)]
            confidence = float(box.conf)
            print(f"  {label}: {confidence:.2%}")
    
    # 按'q'退出
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()