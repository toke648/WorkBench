import torch

# 创建一个3行4列的全0张量
x = torch.zeros(3, 4)

print(x)

"""
torch.randn函数
torch.randn函数返回一个张量，张量中的元素是从标准正态分布中随机采样的。

torch.matmul() 矩阵乘法

"""
A = torch.randn(3, 4)
print(A)
B = torch.randn(5, 4)
print(B)

result = torch.matmul(A, B.T)  # B的转置 // torch.t() 矩阵转置
print(result)

"""
张量操作（torch.unsqueeze()）
# 张量操作（torch.unsqueeze()）
# torch.unsqueeze()函数用于在指定维度上添加一个维度，返回一个新的张量。
# 例如，将一个形状为(3, 4)的张量在第0个维度上添加一个维度，得到的张量形状为(1, 3, 4)。
"""

image = torch.randn(3, 244, 244) # 单张图像
image_batch = image.unsqueeze(0) # 增加一个批次维度
print(image_batch.shape)

# torch.where() 条件筛选
torch.where()