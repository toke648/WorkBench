"""
第19周

sort() 从小到大排序

sum() 列表数字相加

pop() 通过索引删除数组


"""

import numpy as np

arr = np.random.randint(0, 100, 20).tolist()
arr.sort()

arr.pop(0)
arr.pop(-1)

result = sum(arr) / len(arr)
print("result = %02d" % result)







