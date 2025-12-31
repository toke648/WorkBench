import cv2
import os

def video_to_images_cv(video_path, output_folder, interval=1, prefix='frame'):
    """
    使用OpenCV将视频截取为图片
    
    参数:
    video_path: 视频文件路径
    output_folder: 输出图片文件夹
    interval: 每隔多少帧保存一张图片（默认每帧）
    prefix: 图片文件名前缀
    """
    # 创建输出文件夹
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    
    # 打开视频文件
    cap = cv2.VideoCapture(video_path)
    
    if not cap.isOpened():
        print("无法打开视频文件")
        return
    
    # 获取视频信息
    fps = cap.get(cv2.CAP_PROP_FPS)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    
    print(f"视频信息: {width}x{height}, FPS: {fps}, 总帧数: {total_frames}")
    
    frame_count = 0
    saved_count = 0
    
    while True:
        ret, frame = cap.read()
        
        if not ret:
            break
        
        # 按间隔保存图片
        if frame_count % interval == 0:
            # 生成文件名
            filename = f"{prefix}_{saved_count:06d}.jpg"
            filepath = os.path.join(output_folder, filename)
            
            # 保存图片
            cv2.imwrite(filepath, frame)
            saved_count += 1
            
            print(f"已保存: {filename}", end='\r')
        
        frame_count += 1
    
    cap.release()
    print(f"\n完成! 共保存 {saved_count} 张图片")
    return saved_count

# 使用方法
if __name__ == "__main__":
    video_to_images_cv(
        video_path="C:/Users/16673/Desktop/崩坏3 2025-12-02 20-21-45.mkv",
        output_folder="output_frames",
        interval=30,  # 每隔30帧保存一张（每秒保存1张，如果FPS=30）
        prefix="frame"
    )