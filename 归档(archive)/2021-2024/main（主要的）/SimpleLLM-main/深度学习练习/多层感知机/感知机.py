# import numpy as np

# class Perceptron:
#     def __init__(self, input_size, lr=0.01, epochs=100):
#         self.weights = np.zeros(input_size)  # 初始化权重
#         self.bias = 0
#         self.lr = lr  # 学习率
#         self.epochs = epochs
    
#     def activation(self, x):
#         """阶跃函数"""
#         return 1 if x >= 0 else 0
    
#     def predict(self, x):
#         """预测输出"""
#         return self.activation(np.dot(self.weights, x) + self.bias)
    
#     def train(self, x, y):
#         """训练感知机"""
#         for _ in range(self.epochs):
#             for xi, target in zip(x, y):
#                 y_pred = self.predict(xi)
#                 error = target - y_pred
#                 # 更新权重和偏置
#                 self.weights += self.lr * error * xi
#                 self.bias += self.lr * error
#                 print(f"Error: {error}, Weights: {self.weights}, Bias: {self.bias}")
    


# # 训练数据 (AND 逻辑门)
# x = np.array([[0, 0], [0, 1], [1, 0], [1, 1]])
# y = np.array([0, 0, 0, 1])  # 期望输出, 与输入一一对应. AND 逻辑门的真值表

# perceptron = Perceptron(input_size = 2)  # 输入维度为 2
# perceptron.train(x, y) # 训练模型

# print("Predictions:")

# for xi in x:
#     print(xi, perceptron.predict(xi))  # 打印预测结果





# 实践，通过感知机实现猫和狗的二分类问题。
import numpy as np

import numpy as np

class Perceptron:
    def __init__(self, input_size, lr=0.1, epochs=10):
        self.weights = np.zeros(input_size)  # 初始化权重
        self.bias = 0
        self.lr = lr  # 学习率
        self.epochs = epochs

    def activation(self, x):
        """阶跃激活函数"""
        return 1 if x >= 0 else 0

    def predict(self, x):
        """预测类别"""
        return self.activation(np.dot(self.weights, x) + self.bias)

    def train(self, X, y):
        """训练感知机"""
        for _ in range(self.epochs):
            for xi, target in zip(X, y):
                y_pred = self.predict(xi)
                error = target - y_pred  # 计算误差
                # 更新权重和偏置
                self.weights += self.lr * error * xi
                self.bias += self.lr * error

# 训练数据（体型, 叫声）
X = np.array([[0, 0], [0, 1], [1, 0], [1, 1]])  # 体型 & 叫声
y = np.array([1, 0, 1, 0])  # 目标（0=猫，1=狗）

# 创建并训练感知机
perceptron = Perceptron(input_size=2)
perceptron.train(X, y)

# 测试分类
print("分类结果：")
for xi in X:
    print(f"输入 {xi} -> 预测类别: {'狗' if perceptron.predict(xi) == 1 else '猫'}")

