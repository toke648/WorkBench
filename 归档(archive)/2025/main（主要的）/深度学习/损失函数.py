# 均分误差损失函数
def mean_squared_error(y, y_hat):
    n = len(y)
    loss = 0
    for i, j in zip(y, y_hat):
        loss += (i - j) ** 2
    loss = (1 / n) * loss
    return loss

y = [5.6, 9.6, 1.3]
y_hat = [2.5, 4.1, 5.8]
loss = mean_squared_error(y, y_hat)
print(loss) # 输出：20.0
# 模型预测值与样本标签值的差异较大，均方误差较大
y = [5.6, 9.6, 1.3]
y_hat = [5.5, 9.5, 1.3]
loss = mean_squared_error(y, y_hat)
print(loss) # 输出：0.6
# 模型预测值与样本标签值的差异较小，均方误差较小

# 均分绝对误差损失函数
def mean_absolute_error(y, y_hat):
    n = len(y)
    loss = 0
    for i, j in zip(y, y_hat):  # zip()函数将两个列表中的元素对应地组合成一个元组，形成一个新的列表

        loss += abs(i - j)
    loss = (1 / n) * loss
    return loss

y = [5.6, 9.6, 1.3]
y_hat = [5.2, 8.4, 0.9]
loss = mean_absolute_error(y, y_hat)
print(loss) # 输出：0.66


# 交叉熵损失函数
import numpy as np

def cross_entropy_loss(y, y_hat):
    epsilon = 1e-7
    loss = -np.sum([y[i]*np.log(y_hat[i]) + (1-y[i])*np.log(1-y_hat[i]) for i in range(len(y))])
    return loss

y = [0, 1, 0]
y_hat = [0.1, 0.9, 0.8]
loss = cross_entropy_loss(y, y_hat)
print(loss)