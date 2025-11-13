import torch
from torchvision import transforms
from PIL import Image
import matplotlib.pyplot as plt
import numpy as np
import os

# 为了避免环境变量冲突
os.environ["KMP_DUPLICATE_LIB_OK"] = "True"

# 载入图片并转换为RGB
image_path = 'dcaga48-163e52a2-f51f-44c1-a52c-7142d6be5add.jpg'
image = Image.open(image_path).convert('RGB')

# 将图像转换为Numpy数组
image_array = np.array(image)

# 分离颜色通道
red_channel = image_array[:, :, 0]
green_channel = image_array[:, :, 1]
blue_channel = image_array[:, :, 2]

# 创建一个3行1列的子图
fig, ax = plt.subplots(1, 3, figsize=(16, 9))

# 可视化每个通道
ax[0].imshow(red_channel, cmap='Reds')
ax[0].set_title('Red Channel')
ax[0].axis('off')  # 关闭坐标轴

ax[1].imshow(green_channel, cmap='Greens')
ax[1].set_title('Green Channel')
ax[1].axis('off')  # 关闭坐标轴

ax[2].imshow(blue_channel, cmap='Blues')
ax[2].set_title('Blue Channel')
ax[2].axis('off')  # 关闭坐标轴

# 展示图像
plt.tight_layout()
plt.show()


# 定义转换
transform = transforms.Compose(
    [transforms.Resize((28, 28)),  # 定义张量大小28*28
     transforms.ToTensor(),  # 转换为张量并归一化到[0, 1]
])

# 应用转换，到此步骤即可用于深度学习训练
image_tensor = transform(image)
# 查看张量的数值
print(image_tensor)
