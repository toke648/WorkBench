# import json

# # /读取jsonl文件
# with open("train.jsonl", 'r', encoding='utf-8') as f:
#     # train = [json.loads(line) for line in f]  # 读取每一行，并转换为json格式
#     # print(len(train))  # 读取的数据量
#     data = [json.loads(line) for line in f]

# print(data[0])



import numpy as np

da = np.array([1, 2, 3, 0.5, 5, 0])
print(da)

print(np.asarray(da, bool))

print(np.zeros((4, 6)))

print(np.ones((4, 6)))

# 生成等差数列
print(np.arange(1, 100, 2))
print(np.linspace(0, 100, 5))

print(np.random.randn(4, 6))

# numpy
# array asarray() 基础数据类型
arr1 = np.array([1, 2, 3, 4, 5])
arr2 = np.asarray(arr1)
print(arr1)
print(arr2)

# zeros ones linspace logspace eye diag 特殊数组
arr3 = np.zeros((4, 6), float)
arr4 = np.ones((4, 6), float)
arr5 = np.linspace(0,100,5)
arr6 = np.logspace(0,100,5)
arr7 = np.eye(8)
arr8 = np.diag([1, 2, 3])

print(arr3)
print(arr4)
print(arr5)
print(arr6)
print(arr7)
print(arr8)

# random rand randint randn 随机数组
arr9 = np.random.rand(4, 6)
arr10 = np.random.randint(0,100,(4, 6))
arr11 = np.random.randn(4, 6)

print(arr9)
print(arr10)
print(arr11)

