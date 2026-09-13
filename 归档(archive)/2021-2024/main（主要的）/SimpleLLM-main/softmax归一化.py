import numpy as np
from numpy import random

# 模拟实现softmax函数
def softmax(array):
    """
    t 对每一个元素取幂
    s 幂的相加求和
    result 元素除以s得到对应概率的数组

    :param array: 输入数组
    :return: 返回概率
    """
    t = np.exp(array)
    s = sum(t)
    result = t / s
    return result

# 定义数组
a = np.array([1, 3, 5])
# a = random.randint(0, 3, 256)
result = softmax(a)
print(result)
print(sum(result))

