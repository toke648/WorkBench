import gym
from matplotlib import pyplot as plt
# %matplotlib inline
import os

os.environ['SDL_VIDEODRIVER']='dummy' # 隐藏窗口

# 创建环境
# is_slippery=False ：不考虑冰上的滑水
# map_name='4x4' ：4x4的冰湖
# desc决定地形

env = gym.make('FrozenLake-v1', is_slippery=False,
               map_name='4x4',  # 修正：添加缺失的引号
               desc=['SFFF',
                     'FHFH',
                     'FFFH',
                     'HFFG'])
env.reset() # 重置环境

# 解封装才能访问状态转移矩阵P
env = env.unwrapped

def show():
    plt.imshow(env.render('rgb_array'))
    plt.show()

# 查看冰湖这个游戏的状态列表
# 一共4*4=16个状态
# 每个状态下都可以进行4个动作
# 每个动作执行完，都有概率得到3个结果
# (0.333333333333, 0, 0, 0, False)这个数据结构表示（概率， 下一个状态，奖励，是否结束）

print(len(env.P), env.P[0])

# show()

import numpy as np

# 初始化每个格子的价值
values = np.zeros(16)

# 初始化每个格子下采用动作的概率
pi = np.ones([16, 4]) * 0.25 # 每个状态下，每个动作的概率都是0.25

# 两个算法都是可以的，但是价值迭代的速度更快
algorithm = '策略迭代'
algorithm = '价值迭代'

print(values, pi)

# 计算qsa
def get_qsa(state, action):
    """
    获取状态s下，动作a的价值
    """
    value = 0

    # 每个动作都会有三个不同的结果，这里要按概率把他们加权求和
    for prop, next_state, reward, over in env.P[state][action]:

        #计算下个状态的分数，取values当中记录的分数即可，0.9是折扣因子
        next_value = values[next_state] * 0.9

        # 如果下个状态是终点或者陷阱，则下一个状态的分数是0
        if over:
            next_value = 0

        # 获取当前状态的分数
        next_value += reward

        # 因为下个状态是概率出现了，所以要乘以概率
        next_value *= prop

        value += next_value

    return value

print(get_qsa(0, 0)) # 0状态下，0动作的价值

# 策略评估
def get_value():
    # 初始化一个新的values，重新评估所有格子的分数
    new_values = np.zeros([16])

    # 遍历所有格子
    for state in range(16):
        # 计算当前格子4个动作分别的分数
        action_value = np.zeros(4)

        # 遍历所有动作
        for action in range(4):
            action_value[action] = get_qsa(state, action)
        
        if algorithm == '策略迭代':
            # 每个动作的分数和它的概率相乘
            action_value  *= pi[state]
            # 最后这个格子的分数，等于该格子下所有动作的分数求和
            new_values[state] = action_value.sum()
        
        if algorithm == '价值迭代':
            # 价值迭代，直接取最大的分数
            new_values[state] = action_value.max()
    
    return new_values

print(get_value())

# 策略提升
def get_pi():
    # 重新初始化每个格子下采用动作的概率，重新评估
    new_pi = np.zeros([16, 4])

    # 遍历所有动作
    for state in range(16):
        # 计算当前格子4个动作分别的分数
        action_value = np.zeros(4)

        #遍历所有动作
        for action in range(4):
            action_value[action] = get_qsa(state, action)
        
        # 在每个状态内部计算count
        count = (action_value == action_value.max()).sum() # 概率 = 当前格子下，该动作的分数除以所有动作的分数之和

        # 让这些动作均分概率
        for action in range(4):
            if action_value[action] == action_value.max(): # 如果当前行动值 == 行动表最大值
                new_pi[state, action] = 1 / count # 均分概率
            else:
                new_pi[state, action] = 0

    return new_pi

print(get_pi())

for _ in range(1000):
    values = get_value()

pi = get_pi()

print(values, pi)

from IPython import display
import time

def play():
    env.reset()

    # 起点0
    index = 0

    # 最多玩N步
    for i in range(100):
        # 选择一个动作
        action = np.random.choice(4, size=1, p=pi[index])[0]

        # 执行动作
        index, reward, terminated, truncated, _ = env.step(action)

        display.clear_output(wait=True)
        time.sleep(0.1)
        show()

        # 获取当前状态，如果状态时中带你或者掉进陷阱则终止
        if terminated or truncated:
            break
    
    print(i)

play()