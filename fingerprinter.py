# -*- coding: utf-8 -*-
"""
指纹图案生成器 (黑白风格)
"""
import numpy as np
from PIL import Image

def generate_fingerprint_image(width=512, height=512, line_spacing=6, seed=None):
    """
    生成黑白指纹风格图案
    :param width: 宽度
    :param height: 高度
    :param line_spacing: 线条间距
    :param seed: 随机种子（可复现）
    :return: PIL.Image
    """
    if seed is not None:
        np.random.seed(seed)

    img = np.zeros((height, width), dtype=np.uint8)

    # 中心点（指纹的核心）
    cx, cy = width // 2, height // 2

    for y in range(height):
        for x in range(width):
            # 极坐标距离
            dx, dy = x - cx, y - cy
            r = np.sqrt(dx**2 + dy**2)

            # 添加扰动，模拟纹路
            angle = np.arctan2(dy, dx)
            wave = np.sin(r / line_spacing + 5 * np.sin(angle * 3))

            # 判断画黑还是白
            val = 255 if wave > 0 else 0
            img[y, x] = val

    return Image.fromarray(img, mode="L")

if __name__ == "__main__":
    # 生成指纹
    fingerprint = generate_fingerprint_image(seed=42)
    fingerprint.save("fingerprint_bw.png")
    print("已生成 fingerprint_bw.png")
