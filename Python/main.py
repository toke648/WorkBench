
# from random import randint
#
# def fun(money):
#     for day in range(1, days):
#         print(f'day{day}')
#         money_float = randint(1, 10)
#         commodities_float = commodities + money_float
#
#         print(f'com_f: {commodities_float}')
#
#         if money - commodities_float > 0:
#             money -= commodities_float
#             print(f'money: {money}')
#             print('\n')
#
#         else:
#             print(f'\nyou still have {money} money.')
#             print('you have no more money...')
#             print('Game over...')
#             break
#
# # 主函数
# if __name__ == '__main__':
#
#     # 自定义变量
#     days = 15
#     money = 100
#     commodities = 3
#
#     print('\n---------------Welcome is Game!---------------')
#     print(f'You have {money} money now.\n')
#
#     fun(money)

# from random import randint
#
# # 自定义函数func
# def func():
#     global money
#
#     # 循环
#     for day in range(1, days):
#         # 商品随机涨幅
#         money_float = randint(1, 10)
#         commodities_float = commodities + money_float
#
#         # 检测剩余钱数
#         if money - commodities_float > 0:
#             money -= commodities_float
#         else:
#             print(f'\nyou still have {money} money.')
#             print('you have no more money...')
#             print('Game over...')
#             break
#
# # 自定义变量
# days = 15
# money = 100
# commodities = 3
#
# func()  # 运行func函数

# import torch
# import numpy as np
# from torch import MyTorch
#
# x = 12
# print(MyTorch.arange(12))

# print(list('Hello World'))
#
#
# alphabet_title = "abcdefjhijklmnowqrstuvwxyz"
#
# alphabet_title_list = list(range(len(alphabet_title)))
#
# print(np.array(alphabet_title_list))
# print(np.eye(len(alphabet_title) + 1)[alphabet_title_list])
# print(torch.eye(len(alphabet_title) + 1))


# import numpy as np
# import matplotlib.pyplot as plt
#
# # 定义函数
# def f(x):
#     return np.sin(x)  # 你可以将这个改为你想要的任何函数
#
# # 创建 x 值
# x = np.linspace(-10, 10, 400)  # 从 -10 到 10，生成 400 个点
#
# # 计算 y 值
# y = f(x)
#
# # 绘图
# plt.plot(x, y, label='y = sin(x)')
# plt.title('Function Plot')
# plt.xlabel('x')
# plt.ylabel('f(x)')
# plt.axhline(0, color='black',linewidth=0.5, ls='--')
# plt.axvline(0, color='black',linewidth=0.5, ls='--')
# plt.grid(color = 'gray', linestyle = '--', linewidth = 0.5)
# plt.legend()
# plt.show()




# 学习 = 12
#
# for 作业 in range(学习):
#     print(作业)

# class Solution(object):
#     def twoSum(self, nums, target):
#         """
#         :type nums: List[int]
#         :type target: int
#         :rtype: List[int]
#         """
#         # for i in range(len(nums)):
#         #     for j in range(i + 1):
#         #         if i != j:
#         #             if nums[j] + nums[i] == target:
#         #                 return [j, i]
#         num_map = {}
#         for i, num in enumerate(nums):
#             complement = target - num
#             if complement in num_map:
#                 return [num_map[complement], i]
#             num_map[num] = i
#             print(num_map)
#
#
# s = Solution()
# print(s)
# print(s.twoSum(nums = [3,2,3], target = 6))




# class Solution(object):
#     def twoSum(self, nums, target):
#         """
#         :type nums: List[int]
#         :type target: int
#         :rtype: List[int]
#         """
#         num_map = {}
#         for index, num in enumerate(nums):
#             complement = target - num  # 计算所需的补数
#             if complement in num_map:  # 检查补数是否已经存在于字典中
#                 return [num_map[complement], index]  # 返回两个数的索引
#             num_map[num] = index  # 存储当前数和它的索引
#         return None  # 如果没有找到合适的组合，返回 None
#
# s = Solution()
# result = s.twoSum(nums=[3, 2, 3], target=6)
# print(result)


"""
哈希表（Hash Table）是一种数据结构，它通过使用哈希函数将键（key）映射到数组的索引（或桶）中，从而实现快速的数据存取。哈希表可以在平均情况下实现常数时间复杂度的插入、删除和查找操作。下面是关于哈希表的详细解释：

1. 基本概念
键（Key）：用于唯一标识存储在哈希表中的数据。例如，一个人的姓名或者一个产品的ID。

值（Value）：与键关联的数据，例如这个人的电话号码或产品的价格。

哈希函数（Hash Function）：将键转换为数组索引的函数。好的哈希函数能均匀地将键分散到数组中，尽量避免冲突。

冲突（Collision）：当两个不同的键经过哈希函数哈希后得到相同的索引时，称为冲突。解决冲突的方法有很多，常用的有链表法和开放地址法。

2. 数据结构
哈希表内部通常使用以下结构：

数组：基础数据结构，存储实际的数据（值）。

链表或其它集合（如红黑树）：用于处理冲突，确保多个值能够存放在同一个索引位置。

3. 操作
插入（Insert）：通过哈希函数计算键对应的索引，将值存放在该索引位置。如果发生冲突，按冲突解决策略存储。

查找（Search）：通过哈希函数计算键的索引，直接访问该索引获取值。如果索引中有多个元素（因为冲突），则需要进一步查找。

删除（Delete）：找到对应键的索引，删除该位置的值，同时根据冲突处理方式更新相关数据。

4. 优点
快速访问：在理想情况下，哈希表可以在 O(1) 的时间复杂度内完成插入、删除和查找操作。

灵活性：哈希表可以存储任意类型的数据，尤其适合处理需要快速查找的应用场景。

5. 缺点
存储空间：哈希表通常需要额外的空间来处理冲突，因此可能会浪费一些空间。

冲突处理：如果冲突处理不当，可能导致性能下降（接近 O(n)）。

哈希函数的设计：效率的好坏取决于哈希函数的设计，如果哈希函数质量差，可能导致大量冲突。

6. 使用场景
数据库索引：用于快速访问和查询。
缓存实现：例如，LRU 缓存使用哈希表来进行快速查找。
计数和频率统计：统计元素出现的次数，常用于数据分析和报告。

7. Python 中的哈希表实现
在 Python 中，字典（dict）就是一种哈希表的实现。你可以通过键快速访问和管理数据：

"""
# nums = [3,2,3]
# target = 6
#
# num_map = {}
# for i, num in enumerate(nums):
#     if num not in num_map:
#         num_map[num] = []
#     num_map[num].append(i)
#
# print(num_map)
#
# # 创建一个字典
# my_dict = {
#     'apple': 1,
#     'banana': 2,
#     'orange': 3
# }
#
# # 查找
# print(my_dict['banana'])  # 输出：2
#
# # 插入
# my_dict['grape'] = 4
#
# # 删除
# del my_dict['apple']
#
# # 遍历
# for key in my_dict:
#     print(key, my_dict[key])


import openai  # 假设使用OpenAI接口，Ollama的接口类似
from openai import OpenAI

# 设置OpenAI的API密钥
openai.api_key = 'your-openai-api-key'  # 替换为你自己的API密钥

client = OpenAI(
    api_key="sk-707613869ffe4b06b165e396e580f847",
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
)

# 对话历史管理
dialog_history = [
    {"role": "system", "content": "你是一个可以进行自我思考和生成思维链的AI"},
    {"role": "user", "content": "今天天气怎么样？"},
    {"role": "AI", "content": "今天是晴天，气温适宜。"}
]


# 思维链生成函数
def generate_thought(dialog_history, max_depth=3):
    # 从历史记录中提取上下文（去除“mine”）
    context = " ".join([entry["content"] for entry in dialog_history if entry["role"] != "mine"])

    # 控制深度并生成思维链
    prompt = f"基于以下对话历史生成自我思维链（深度限制为{max_depth}步）：\n{context}"

    # 调用OpenAI接口生成思维链
    response = client.chat.completions.create(
        model="qwen-plus",  # 使用GPT-3引擎
        messages=dialog_history,
        max_tokens=150,  # 最大token数限制
        temperature=0.7  # 控制生成的多样性
    )

    # 返回生成的思维链
    return response.choices[0].text.strip()


# 添加自我思维到对话历史
def add_mine_thought(dialog_history):
    # 生成新的思维链
    new_thought = generate_thought(dialog_history)

    # 将新生成的思维链添加到历史记录
    dialog_history.append({"role": "mine", "content": new_thought})


# 示例：用户提问，AI生成思维链
dialog_history.append({"role": "user", "content": "天亮了，今天有什么计划？"})
dialog_history.append({"role": "AI", "content": "天亮了，阳光明媚，今天可以去散步或者做点运动。"})

# AI生成思维链并存储
add_mine_thought(dialog_history)

# 打印更新后的对话历史
for entry in dialog_history:
    print(f"Role: {entry['role']}, Content: {entry['content']}")
