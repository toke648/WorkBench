# main.py
# 总练习，随手写的代码都放在这里


L1 = list(range(1, 5))
print(L1)
L2 = L1.copy()
print(L2)
L2.reverse() # 翻转
print(L2)


# print(L1.center(5)) # center 函数 用于将列表居中
# print(L1.replace(1, 2)) # replace 函数 用于替换列表中的元素
# print(L1.strip()) # strip 函数 用于去除列表中的空字符
# print(L1.split(2)) # split 函数 用于截取列表的一部分，如将列表L1从索引2开始截取，返回一个新的列表
print(L1.index(2, 0)) # index 函数 用于查找列表中元素的索引
print(round(3.1415926, 2)) # round 函数 用于四舍五入

ls = [1, 2, 3]
lt = [4, 5, 6]

print(ls + lt)
# 怎么实现列表ls he lt的数字的相加
for i in range(len(ls)):
    ls[i] += lt[i]
print(ls)

print([ls[i]+lt[i] for i in range(len(ls))]) # ???什么情况？

print(sum(ls) + sum(lt))

a = [3, 2, 1]
b = a[:] # 列表翻转
print(b)

import random
print(random.randint(1, 999))


ran = 10
for i in range(ran):
    print(random.randint(1, 999), end=",")

import random
ran = [54,275,90,788,418,273,111,859,923,896]
for i in range(len(ran)):
    print(ran[i], end=",")

random.seed(0) # 设置随机数种子

import random
brandlist = ['华为','苹果','诺基亚','OPPO','小米']
random.seed(0)
name = brandlist[random.randint(0, len(brandlist)-1)]
print(name)

s = "请写代码替换横线，不修改其他代码，实现以下功能："

print(s.replace("-", "1")) # 替换
# 翻转
print(s[::-1])
print(len(s))


D = {}

vote = "张三\n"  # 从文件读取的一行
name = vote[:-1]  # "张三"（去掉换行符）
print(D.get(name, 0) + 1)
print(name)

# D.get("张三", 0) → 字典中没有"张三"，返回默认值0
# 0 + 1 = 1
D["张三"] = 1
# 现在 D = {"张三": 1}

# with open("vote.txt", 'r', encoding='utf-8') as f:
#     for line in f:
#         name = line[:-1]  # 去掉换行符
#         D[name] = D.get(name, 0) + 1

# book = open('命运.txt', 'r', encoding='utf-8').read(100) # 读取文件
# # print(book)
# print(f"输出文件长度：", len(book))
# print(f"输出前100个字符：", repr(book[:100])) # repr() 函数用于将参数转化为字符串

# d = {}
# for char in book:
#     if char not in d:
#         d[char] = d.get(char, 0) + 1
        
# print("总不同字符数:", len(d))
# print("统计结果:", d)


# import os

# # 检查文件大小
# file_size = os.path.getsize('命运.txt')
# print("文件大小:", file_size, "字节")

# # 完整读取文件
# with open('命运.txt', 'r', encoding='utf-8') as f:
#     full_book = f.read()

# print("完整文件长度:", len(full_book))
# print("不同字符数:", len(set(full_book)))

# # 统计结果
# d = {}
# for char in full_book:
#     d[char] = d.get(char, 0) + 1

# # 找出出现次数最多的字符
# sorted_chars = sorted(d.items(), key=lambda x: x[1], reverse=True)
# print("出现次数最多的前10个字符:")
# for char, count in sorted_chars[:10]:
#     print(f"'{char}': {count}")

# book = open('命运.txt', 'r', encoding='utf-8').read() 这种写法和下面那种写法有不完全一致性
# 完整读取文件
with open('命运.txt', 'r', encoding='utf-8') as f:
    full_book = f.read()

print("完整文件长度:", len(full_book))
print("不同字符数:", len(set(full_book)))

# 统计结果
d = {}
for char in full_book:
    d[char] = d.get(char, 0) + 1

print("统计结果:", d)

# 找出出现次数最多的字符
sorted_chars = sorted(d.items(), key=lambda x: x[1], reverse=True)
print("出现次数最多的前10个字符:")
for char, count in sorted_chars[:10]:
    # print(f"'{char}': {count}")
    print(char, end="")

# 出现最多的字符
max_char = max(d, key=d.get)
print("出现次数最多的字符:", max_char)

# 第二大的字符及其出现次数
sorted_chars = sorted(d.items(), key=lambda x: x[1], reverse=True)
second_max_char = sorted_chars[1][0]
print("第二大的字符:", second_max_char)
print("第二大的字符出现次数:", sorted_chars[1][1])

print("{}:{}".format(sorted_chars[1][0], sorted_chars[1][1]))



# txt = open("命运.txt", "r", encoding="utf-8").read()
# txt = txt.replace('\n', "")  # 去除换行符
# d = {}
# for ch in txt:
#     d[ch] = d.get(ch, 0) + 1
# ls = list(d.items())
# ls.sort(key=lambda x: x[1], reverse=True)
# for i in range(10):
#     print(ls[i][0], end="")

with open('命运.txt', 'r', encoding='utf-8') as f:
    txt = f.read()
d = {}
for ch in txt:
    d[ch] = d.get(ch, 0) + 1
ls = list(d.items())
ls.sort(key=lambda x: x[1], reverse=True) # 此行可以按照词频由高到低排序

# print(ls)
print(len(ls))
result = ""
for i in range(len(ls)):
    # print("{}:{},".format(ls[i][0], ls[i][1]), end=",")
    result += "{}:{},".format(ls[i][0], ls[i][1])

print(result)
open("命运-频次排序.txt", "w", encoding="utf-8").write(result)