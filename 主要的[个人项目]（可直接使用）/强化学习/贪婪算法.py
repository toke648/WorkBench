# 代码示例

# import numpy as np

# probs = np.random.uniform(size=10)
# # 生成10个0到1之间的随机数
# print("生成随机奖励值：", probs)

# rewards = [[1] for _ in range(10)] # 初始化奖励列表 # 每个动作的奖励列表
# print("初始化奖励列表：", rewards)

# probs, rewards

# import random

# # 判断，如果随机生成的数值小于0.01，就随机返回一个0到9之间的整数
# # 否则，计算每个动作的奖励平均值，返回奖励平均值最大的拉杆

# def choose_one():
#     if random.random() < 0.01: # 随机生成的数值如果小于0.01
#         return random.randint(0, 9) # 随机返回一个0到9之间的整数
    
#     # 计算每个动作的奖励平均值
#     rewards_mean = [np.mean(i) for i in rewards] # .mean() 计算平均值
#     return np.argmax(rewards_mean) # 返回奖励平均值最大的拉杆的索引位置

# def try_and_play():
#     i = choose_one() # 选择一个拉杆
    
#     reward = 0
#     if random.random() < probs[i]: # 随机生成的数值如果小于概率
#         reward = 1

#     rewards[i].append(reward) # 将奖励值添加到对应的奖励列表中

# try_and_play()
# def get_result():
#     for _ in range(5000): # 模拟5000次拉杆
#         try_and_play()

#     # 期望的最好结果
#     target = probs.max() * 5000 # 5000次模拟的期望结果

#     result = sum([sum(i) for i in rewards]) # 计算实际获得的分数

#     return target, result


# # -*- coding: utf-8 -*-
# target, result = get_result()
# print("期望的最好结果：", target)
# print("实际获得的分数：", result)



"""
整理下逻辑
也就是说，先有了按钮，然后每个按钮有随机奖励值，
默认不显示，点击后显示奖励值

设计目的：实现最大化奖励值
也就是贪婪算法

行吧那我自己试试
"""

# 好吧，先是 初始化环境（return）、拉杆（action）、以及奖励值（reward） 而这个整体属于一个智能体（agent）

# # 贪婪算法
# import numpy as np
# import random
# # 定义一个老虎机
# class targer_machine():

#     def __init__(self):
#         """
#         老虎机上有10个按钮，每个按钮有随机奖励值
#         """
#         # buttons = [i for i in range(10)] # 初始化10个老虎机
#         # print(buttons)

#         self.probs = np.random.uniform(size=10) # 每个拉杆的中奖概率
#         print("每个拉杆的中奖概率：", self.probs)

#         self.rewards = [[1] for i in range(10)] # 初始化每个老虎机的中奖次数为0
#         print("每个拉杆的奖励列表：", self.rewards)


#     # 选择一个拉杆(随机拉杆，或者选择奖励值最大的拉杆)
#     def choose_action(self):
#         """
#         选择一个拉杆
#         """

#         if random.random() < 0.01: # 以0.01的概率随机选择一个拉杆
#             return random.randint(0, 9) # 随机选择一个0-9索引中的拉杆
        
#         # 计算每个拉杆的奖励平均值
#         rewards_mean = [np.mean(i) for i in self.rewards] # 计算每个拉杆的奖励平均值
#         print("每个拉杆的奖励平均值：", rewards_mean)
#         return np.argmax(rewards_mean) # 返回奖励平均值最大的拉杆的索引位置
    
#     def try_and_play(self, ages):
#         """
#         选择一个拉杆并尝试拉动
#         """
#         for _ in range(ages):
#             print("第%d次尝试" % (_ + 1))
#             i = self.choose_action()
#             print("选择的拉杆索引位置：", i)

#             reward = 0
#             if random.random() < self.probs[i]: # 如果小于中奖概率，则中奖，否则失败（中奖概率）
#                 reward = 1
                
#             self.rewards[i].append(reward) # 将奖励值添加到对应的奖励列表中

#         # print("每个拉杆的奖励列表：", self.rewards)

#         targer = self.probs.max() * ages # 5000次模拟的期望结果（人话：对最大的选项连点5000次）
#         result = sum([sum(i) for i in self.rewards]) # 将奖励中的值相加，得到实际获得的分数

#         print("期望的最好结果：", targer)
#         print("实际获得的分数：", result)

    
# targer_machine().try_and_play(5000)



# 贪婪算法
import numpy as np
import random
# 定义一个老虎机
class targer_machine():
    """
    动作函数优化
    
    1.
    探索度越高，探索欲望越少
    总个数 / 已经探索的个数 = 探索度
    探索度越低，探索欲望越强

    2.

    3.上置信界算法：UCB算法，多探索玩的少的机器

    4.汤普森采样算法：使用beta分布衡量期望 (最好用beta分布，因为beta分布的概率密度函数是连续的，可以进行积分)
    """

    def __init__(self):
        """
        老虎机上有10个按钮，每个按钮有随机奖励值
        """
        # buttons = [i for i in range(10)] # 初始化10个老虎机
        # print(buttons)

        self.probs = np.random.uniform(size=10) # 每个拉杆的中奖概率
        print("每个拉杆的中奖概率：", self.probs)

        self.rewards = [[1] for i in range(10)] # 初始化每个老虎机的中奖次数为0
        print("每个拉杆的奖励列表：", self.rewards)


    # # 选择一个拉杆(随机拉杆，或者选择奖励值最大的拉杆)
    # def choose_action(self):
    #     """
    #     选择一个拉杆
    #     """

    #     played_count = [len(i) for i in self.rewards] # 计算每个拉杆被玩的次数
    #     played_count = np.array(played_count)
        
    #     #求出上置信界
    #     #分子是总共玩了多少次，取根号后让他的增长速度变慢
    #     #分母是每台老虎机玩的次数，乘以2让他的增长速度变快
    #     #随着玩的次数增加，分母会很快超过分子的增长速度，导致分数越来越小
    #     #具体到每一台老虎机，则是玩的次数越多，分数就越小，也就是ucb的加权越小
    #     #所以ucb衡量了每一台老虎机的不确定性，不确定性越大，探索的价值越大

    #     fenzi = played_count.sum() ** 0.5 # 总共玩了多少次，取根号
    #     fenmu = played_count * 2 # 每台老虎机玩的次数，乘以2
    #     ucb = fenzi / fenmu # 计算ucb值

    #     #ucb本身取根号
    #     #大于1的数会被缩小，小于1的数会被放大，这样爆出ucb恒定在一定的数值范围内
    #     ucb = ucb ** 0.5 # 取根号
    #     print("每个拉杆的ucb值：", ucb)

    #     # 计算每个拉杆的奖励平均值
    #     rewards_mean = [np.mean(i) for i in self.rewards] # 计算每个拉杆的奖励平均值
    #     rewards_mean = np.array(rewards_mean)
    #     print("每个拉杆的奖励平均值：", rewards_mean)

    #     #ucb和期望求和
    #     ucb += rewards_mean

    #     return ucb.argmax() # 返回奖励平均值最大的拉杆的索引位置

        # 选择一个拉杆(随机拉杆，或者选择奖励值最大的拉杆)
    def choose_action(self):
        """
        选择一个拉杆
        """
        # 求出每个老虎机出1的此处+1
        count_1 = [sum(i) + 1 for i in self.rewards]

        # 求出每个老虎机出0的次数+1
        count_0 = [sum(1 - np.array(i)) + 1 for i in self.rewards]
        
        beta = np.random.beta(count_1, count_0) # 使用beta分布衡量期望
        print("每个拉杆的beta值：", beta)

        return beta.argmax() # 返回奖励平均值最大的拉杆的索引位置

    
    def try_and_play(self, ages):
        """
        选择一个拉杆并尝试拉动
        """
        for _ in range(ages):
            print("第%d次尝试" % (_ + 1))
            i = self.choose_action()
            print("选择的拉杆索引位置：", i)

            reward = 0
            if random.random() < self.probs[i]: # 如果小于中奖概率，则中奖，否则失败（中奖概率）
                reward = 1
                
            self.rewards[i].append(reward) # 将奖励值添加到对应的奖励列表中

        # print("每个拉杆的奖励列表：", self.rewards)

        targer = self.probs.max() * ages # 5000次模拟的期望结果（人话：对最大的选项连点5000次）
        result = sum([sum(i) for i in self.rewards]) # 将奖励中的值相加，得到实际获得的分数

        print("期望的最好结果：", targer)
        print("实际获得的分数：", result)

    
targer_machine().try_and_play(100)











