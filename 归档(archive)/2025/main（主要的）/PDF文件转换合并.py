from fpdf import FPDF
from PIL import Image
import os
import re

def natural_sort_key(text):
    """提取字符串中的数字用于排序"""
    return [int(s) if s.isdigit() else s for s in re.split(r'(\d+)', text)]

def get_file_list(directory):
    """获取文件夹内的图片文件，并按文件名排序"""
    file_list = [os.path.join(directory, file) for file in os.listdir(directory) if file.lower().endswith((".jpg", ".jpeg", ".png", ".webp"))]
    return sorted(file_list, key=natural_sort_key)  # 按文件名中的数字排序

def images_to_pdf(image_paths, output_pdf_path):
    """将图片合并为 PDF，并自适应宽度"""
    if not image_paths:
        print(f"⚠ 目录 {output_pdf_path} 为空，跳过")
        return

    pdf = FPDF(unit="mm")  # 使用毫米作为单位

    for image_path in image_paths:
        try:
            img = Image.open(image_path)
            width, height = img.size

            # 计算 PDF 页面尺寸（像素转毫米）
            width_mm = width * 0.264583
            height_mm = height * 0.264583

            # 设置横向或纵向
            orientation = "P" if height >= width else "L"

            # **修正 add_page() 方式**
            pdf.set_auto_page_break(auto=False)  # 关闭自动分页
            pdf.add_page(orientation=orientation)
            pdf.image(image_path, x=0, y=0, w=width_mm, h=height_mm)

        except Exception as e:
            print(f"❌ 处理 {image_path} 时出错: {e}")

    pdf.output(output_pdf_path, "F")
    print(f"✅ PDF 生成完成: {output_pdf_path}")

# 处理 Blue Archive 文件夹
base_dir = "Blue Archive"
output_dir = "Blue Archive/PDFs"

if not os.path.exists(output_dir):
    os.makedirs(output_dir)

# **对章节文件夹进行自然排序**
sorted_folders = sorted(os.listdir(base_dir), key=natural_sort_key)

for folder in sorted_folders:
    dir_path = os.path.join(base_dir, folder)

    if os.path.isdir(dir_path):
        images_path = get_file_list(dir_path)
        output_pdf = os.path.join(output_dir, f"{folder}.pdf")
        images_to_pdf(images_path, output_pdf)
