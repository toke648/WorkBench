from PIL import Image
import matplotlib.pyplot as plt

# 读取图片
image_path = "./test_images/3_59.png"  # 替换为您的图片路径
img = Image.open(image_path)

# 黑白互换：将每个像素值用255减去
inverted_img = Image.eval(img, lambda x: 255 - x)

# 显示结果对比
plt.figure(figsize=(10, 5))

plt.subplot(1, 2, 1)
plt.imshow(img, cmap='gray')
plt.title('原始图片')
plt.axis('off')

plt.subplot(1, 2, 2)
plt.imshow(inverted_img, cmap='gray')
plt.title('黑白互换后')
plt.axis('off')

plt.show()

# 保存结果（可选）
inverted_img.save('./test2/3_59_inverted.png')