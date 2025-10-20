import numpy as np

# 线性回归模型的梯度下降
def linear_regression(X, y, lr=0.01, epochs=1000):
    """
    1.1.2 线性回归模型的构建
    线性回归公式： y_i = w * x^i + b

    :param X: 二维特征如 价格 距离 大小 等
    :param y: 目标变量
    :param lr: 学习率
    :param epochs: 训练次数
    :return: W,b 权重，偏置
    """
    m = len(y)  # 样本数
    W = np.zeros(X.shape[1])  # 初始化权重，假设 X 是多维特征
    b = 0  # 初始化偏置

    for epoch in range(epochs):
        # 计算预测值
        y_pred = np.dot(X, W) + b

        # 计算损失（均方误差）
        loss = (1 / m) * np.sum((y_pred - y) ** 2)

        # 计算梯度
        dW = (2 / m) * np.dot(X.T, (y_pred - y))
        db = (2 / m) * np.sum(y_pred - y)

        # 更新权重和偏置
        W -= lr * dW
        b -= lr * db

        if epoch % 100 == 0:
            print(f"Epoch {epoch}, Loss: {loss}, W: {W}, b: {b}")

    return W, b


# 测试数据
# 假设 X 是二维特征，y 是目标变量
X = np.array([[1, 2], [2, 3], [3, 4], [4, 5], [5, 6]])
y = np.array([5, 7, 9, 11, 13])

# 训练模型
W, b = linear_regression(X, y, lr=0.01, epochs=1000)

print(f"Final W: {W}, Final b: {b}")







