from PIL import Image
import os

def resize_images(input_folder, output_folder, target_size=(48, 48)):
    # 若输出文件夹不存在，则创建它
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    # 遍历输入文件夹中的所有文件
    for filename in os.listdir(input_folder):
        file_path = os.path.join(input_folder, filename)
        if os.path.isfile(file_path) and filename.lower().endswith(('.png', '.jpg', '.jpeg')):
            try:
                # 打开图片
                with Image.open(file_path) as img:
                    # 调整图片大小
                    resized_img = img.resize(target_size, Image.LANCZOS)
                    # 构建输出文件路径
                    output_path = os.path.join(output_folder, filename)
                    # 保存调整大小后的图片
                    resized_img.save(output_path)
                print(f"已调整 {filename} 的大小")
            except Exception as e:
                print(f"处理 {filename} 时出错: {e}")

if __name__ == "__main__":
    input_folder = "imgs"  # 输入图片文件夹路径修改为 imgs
    output_folder = "output_images"  # 输出图片文件夹路径
    resize_images(input_folder, output_folder)