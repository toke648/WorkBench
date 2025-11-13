# # #尝试自主实现策略神经网络
# # import numpy as np
# # import random

# # # pords = (random.uniform(0, 1) for _ in range(10))

# # # print(pords)

# # echos = 500 # 迭代次数

# # pords = np.random.uniform(size=10) # 每个栏杆的中奖率
# # print(pords)

# # rewards = [[1] for _ in range(10)] # 每个拉杆的奖励列表
# # # print(rewards)

# # def chooes_one():

# #     # reward = 0
# #     # chiose = np.random.rand()
# #     # print(chiose)
# #     # if chiose <= 0.9:
# #     #     reward + 1
# #     # rewards.remove

# #     # 小概率随机选择一个数
# #     if random.random() < 0.01:
# #         return random.randint(0,9)
    
# #     rewards_mean = [np.mean(i) for i in rewards] # 

# #     # print(rewards_mean)
# #     # print(np.argmax(rewards_mean))

# #     return np.argmax(rewards_mean) # 返回奖励平均值最大的拉杆的索引位置

# # def play():
# #     for i in range(echos):
# #         reward = 0
# #         chooise = chooes_one()
# #         # print(chooise) 检查抽奖问题

# #         # print(chooise)
# #         # print(pords[chooise])

# #         # 日志统计/dialog cll
# #         if i % 50 == 0:
# #             print("迭送", i, "选择次数", [len(r) for r in rewards]) # 每个拉杆被选择的次数

# #         # 如果抽中了就加再次抽的概率
# #         if random.random() < pords[chooise]: # 会在choose_one中的reward_mean处看到明显的效果
# #             reward += 1

# #         # rewards.append(rewards[chooise], reward) #是往 某个拉杆的奖励列表 里追加新的 reward，而不是给 rewards 追加两个值。
# #         # rewards[chooise]
# #         rewards[chooise].append(reward) # 将奖励值添加到对应的奖励列表中

# # play()

# # # print([len(r) for r in rewards]) # 每个拉杆被选择的次数
# # # print([len(r) for r in rewards])

# # print(pords[np.argmax(pords)] * echos) # 期望的最好结果
# # #numpy 数组不能直接和普通 Python 列表相乘。✅ 正确做法是先把列表转成 numpy 数组：
# # print(sum(pords * np.array([len(r) for r in rewards]))) # 实际获得的分数


# # -------------------------------------------

# # 策略练习

# import numpy as np
# import random
# import IPython as ipy


# row, cols = 6, 12 # 状态

# state = 'start' # 状态
# actions = {
#     0: (-1, 0), # up
#     1: (0, 1), # right
#     2: (1, 0), # down
#     3: (0, -1), # left
# }
# rewards = np.zeros((row, cols))

# def get_state(rew, col):
#     """

#     """
#     if (rew, col) == (0, 0):
#         state = 'start'
#     elif (rew, col) == (5, 11):
#         state = 'terminal' # terminal: 终止状态
#     elif (rew, col) in [(2, 2), (4, 2), (3, 5)]:
#         state = 'trap' # trap: 陷阱状态
#     else:
#         state = rew, col # 普通状态：返回坐标

#     return state

# print(rewards)

# # # 测试
# # print(get_state(0, 0))   # start
# # print(get_state(5, 11))  # terminal
# # print(get_state(2, 2))   # trap
# # print(get_state(2, 6))   # (2, 6)

# # print("now_action: ", action[0])
# # now_state = get_state(0, 0)
# # print(now_state)
# # print(rewards[now_state])

# def get_pi(rewards, actions=None):
#     """
#     其他格子
#     可以全是 0，也可以给一个小负值（鼓励智能体快点找到出口）

#     获得当前状态下的策略
#     根据环境情况设置一个初始的环境奖励及参数初始化
#     """
#     # 陷阱
#     traps = [(2 ,2), (4, 2), (3, 5)]
#     for r,c in traps:
#         rewards[r, c] = -100
    
#     # 出口
#     terminal = (5, 11)
#     rewards[terminal] = 100

#     # 初始化
#     for r in range(row):
#         for c in range(cols):
#             if (r, c) not in traps and (r, c) != terminal:
#                 rewards[r, c] = -1


# get_pi(rewards)
# # print(rewards)


# # 智能体策略实现
# def next_action(state, pi):
#     """
#     思路
#     如果状态是普通状态，则随机选择一个动作
#     根据获得的奖励值，以及危险情况，对动作进行选择

#     智能体可以提前观测到周围四个位置的状态信息

#     用类似梯度下降的算法，对动作的奖励值不断累积
#     使智能体能够学习到策略

#     # 输入周围环境以及分数奖励，输出下一步的动作策略
#     """
#     print(state)
#     print("pi: ", pi)

#     # for r, c in rewards: # 获取周围四个环境的状态信息


# random_action = actions[random.randint(0,3)]
# print(random_action)


# next_action(state, rewards)


# def step(state, action):
#     """
#     输入: 
#         state: 当前状态 (row, col) 或 'start'
#         action: 一个动作 (dr, dc)
#     输出:
#         next_state: 下一个状态
#         reward: 该步的奖励
#         done: episode 是否结束
#     """

#     # 如果是特殊状态（字符串），转成坐标
#     if state == 'start':
#         r, c = (0, 0)
#     elif state == 'terminal':
#         return 'terminal', 0, True   # 已经结束
#     elif state == 'trap':
#         return 'trap', -100, True    # 已经掉坑
#     else:
#         r, c = state

#     # 计算下一步位置
#     dr, dc = action
#     new_r, new_c = r + dr, c + dc

#     # 边界检查
#     if new_r < 0 or new_r >= row or new_c < 0 or new_c >= cols:
#         new_r, new_c = r, c   # 撞墙留在原地

#     # 判断状态
#     if (new_r, new_c) == (5, 11):   # 终点
#         return 'terminal', 100, True
#     elif (new_r, new_c) in [(2, 2), (4, 2), (3, 5)]:  # 陷阱
#         return 'trap', -100, True
#     else:   # 普通状态
#         return (new_r, new_c), -1, False

# # 初始化 Q 表
# Q = np.zeros((row, cols, len(actions)))

# alpha = 0.1      # 学习率
# gamma = 0.9      # 折扣因子
# epsilon = 0.1    # 探索率

# def choose_action(state):
#     """epsilon-greedy 策略"""
#     if np.random.rand() < epsilon:
#         return random.choice(list(actions.keys()))
#     else:
#         r, c = state if state not in ['start', 'terminal', 'trap'] else (0, 0)
#         return np.argmax(Q[r, c, :])

# def q_learning_episode():
#     state = 'start'
#     total_reward = 0
    
#     while True:
#         # 转坐标
#         r, c = (0, 0) if state == 'start' else state
        
#         # 选动作
#         action_idx = choose_action((r, c))
#         action = actions[action_idx]
        
#         # 与环境交互
#         next_state, reward, done = step((r, c), action)
#         total_reward += reward
        
#         # 更新 Q 表
#         if state not in ['terminal', 'trap']:
#             nr, nc = (0, 0) if next_state == 'start' else (5, 11) if next_state == 'terminal' else \
#                      (-1, -1) if next_state == 'trap' else next_state
            
#             if next_state in ['terminal', 'trap']:
#                 Q[r, c, action_idx] += alpha * (reward - Q[r, c, action_idx])
#             else:
#                 Q[r, c, action_idx] += alpha * (reward + gamma * np.max(Q[nr, nc, :]) - Q[r, c, action_idx])
        
#         # 结束
#         if done:
#             break
#         state = next_state
    
#     return total_reward

# # 跑一堆 episode
# for ep in range(500):
#     reward = q_learning_episode()
#     if ep % 50 == 0:
#         print(f"Episode {ep}, reward={reward}")

# from IPython import display
# import time

# #在一个格子里做一个动作
# def move(row, col, action):
#     # 如果当前已经在陷阱或终点，则不能执行任何动作
#     if get_state(row, col) in ['trap', 'terminal']:
#         return row, col, 0
    
#     # -是向上，+是向下，不要搞反了

#     # up
#     if action == 0:
#         row -= 1
    
#     #down
#     if action == 1:
#         row += 1
    
#     #left
#     if action == 2:
#         col -= 1

#     #right
#     if action == 3:
#         col += 1

#     # 不允许走到地图外面去
#     row = max(0, row)
#     row = min(3, row)
#     col = max(0, col)
#     col = min(11, col)
#     # 以上逻辑是判断是否越界，通过设置最大值和最小值来限制

#     # 是陷阱的话，奖励是-100，否则都是-1
#     # 这样强迫了机器尽快结束游戏，因为每走一步都要扣一分
#     # 结束最好是以走到终点的形式，避免被扣100分
#     reward = -1

#     if get_state(row, col) == 'trap':
#         reward = -100

#     return row, col, reward

# pi = np.ones([4, 12, 4]) * 0.25 
# def test():
#     def show(row, col, action=None):
#         symbols = ['↑','↓','←','→']
#         for r in range(4):
#             line = ''
#             for c in range(12):
#                 if (r,c) == (row,col):
#                     if action is None:
#                         line += 'A '  # Agent
#                     else:
#                         line += symbols[action] + ' '
#                 elif get_state(r,c) == 'terminal':
#                     line += 'G '
#                 elif get_state(r,c) == 'trap':
#                     line += 'C '
#                 elif (r,c) == (3,0):
#                     line += 'S '
#                 else:
#                     line += '. '
#             print(line)


#     row, col = 0, 0 # 初始位置

    

#     #最多步数
#     for _ in range(200):

#         #选择动作
#         # action = np.random.choice(4, p=pi[row, col])
#         action = np.argmax(pi[row, col]) # 选择动作

#         #打印这个动作
#         display.clear_output(wait=True)
#         time.sleep(0.1)

#         show(row, col, action)


#         #执行动作
#         row, col, reward = move(row, col, action)

#         if get_state(row, col) == 'terminal':
#             print('Game Over')
#             break


# test()
# print(pi) # 打印策略
# # print(values) # 评估价值
    


# for i in range(6):
#     for j in range(12):
#         print('.', end=' ')

#         if (i, j) == (0, 0):
#             print('S', end=' ')
#         elif (i, j) == (5, 11):
#             print('G', end=' ')
#         elif (i, j) == (2, 2):
#             print('C', end=' ')
#         elif (i, j) == (4, 2):
#             print('C', end=' ')
#         elif (i, j) == (3, 5):
#             print('C', end=' ')

    
#     print(

#     )


def get_state(row, col):
    """
    输入行列返回状态

    """
    if (row, col) == (0, 0):
        return 'start' # start: 起始状态
    if (row, col) == (5, 11):
        return'terminal' # terminal: 终止状态
    if (row, col) in [(2, 2), (4, 2), (3, 5), (5, 7)]:
        return 'trap' # trap: 陷阱状态
    else:
        return "ground" # ground: 地板状态

# for row in range(6):
#     for col in range(12):
#         print(get_state(row, col), end='\t')

#     print()

def move(row, col, action):
    """
    输入行列动作返回新行列和奖励

    **如果当前已经在陷阱或终点，则不能执行任何动作**

    """

    # 如果当前已经在陷阱或终点，则不能执行任何动作
    if get_state(row, col) in ['trap', 'terminal']:
        return row, col, 0
    
    if action == 0: # up
        row -= 1
    elif action == 1: # down
        row += 1
    elif action == 2: # left
        col -= 1
    elif action == 3: # right
        col += 1

    # 不允许走到地图外面去
    row = max(0, row) # 意思是：如果row小于0，则row等于0
    row = min(5, row) # 意思是：如果row大于5，则row等于5
    col = max(0, col) # 意思是：如果col小于0，则col等于0
    col = min(11, col) # 意思是：如果col大于11，则col等于11
    # 以上逻辑是判断是否越界，通过设置最大值和最小值来限制

    # 是陷阱的话，奖励是-100，否则都是-1
    # 这样强迫了机器尽快结束游戏，因为每走一步都要扣一分
    # 结束最好是以走到终点的形式，避免被扣100分
    reward = -1

    if get_state(row, col) == 'trap':
        reward = -100
    elif get_state(row, col) == 'terminal':
        reward = 100

    return row, col, reward

import numpy as np
import random

row, col = 6, 12 # 初始位置
action = {
    0: (-1, 0), # up
    1: (1, 0), # down
    2: (0, -1), # left
    3: (0, 1) # right

}

values = np.zeros((row, col))
# print(values)
pi = np.ones((row, col, len(action))) * 0.25 # 初始策略 4行12列4个动作
# print(pi)


def get_qsa(row, col,action):
    """
    计算在一个状态下执行动作的分数，得到下一个状态和reward
    """
    next_row, next_col, reward = move(row, col, action)
    # print(move(row, col, action))

    value = values[next_row, next_col] * 0.9
    # print(value)
    
    if get_state(next_row, next_col) in ['trap', 'terminal']: # 如果下个状态时终点或陷阱，则下一个状态的分数是0
        value = 0

    return reward + value

# print(action)
# get_qsa(row, col, action)
# print(get_qsa(row, col, action))

def get_values(r, c, a):
    new_values = np.zeros([r, c])

    for row in range(r):
        for col in range(c):
            action_value = np.zeros(a)

            for action in range(a):
                action_value[action] = get_qsa(row, col, action)
            
            action_value *= pi[row, col] # 概率
            new_values[row, col] = action_value.sum()

            # print(action_value)
            
    return new_values

print(get_values(row, col, len(action)))

def get_pi(r, c, a, epsilon=0.1):
    """
    ε-greedy 策略改进
    epsilon: 探索概率
    """
    new_pi = np.zeros([r, c, a])

    for row in range(r):
        for col in range(c):
            action_value = np.zeros(a)

            # 计算每个动作的Q(s,a)
            for action in range(a):
                action_value[action] = get_qsa(row, col, action)
            
            # 找到最大值
            max_value = np.max(action_value)
            count = np.sum(action_value == max_value)

            # 先给所有动作均匀分配 ε 部分
            new_pi[row, col, :] = epsilon / a

            # 把 (1-ε) 部分分配给最优动作（如果有多个最优，均分）
            for act in range(a):
                if action_value[act] == max_value:
                    new_pi[row, col, act] += (1 - epsilon) / count

    return new_pi


# print(get_pi(0, 0, 0))

# 获取Q(s,a)
epsilon = 0.1

for _ in range(250):
    values = get_values(row, col, len(action))
    pi = get_pi(row, col, len(action), epsilon=0.2)  # 给个稍大一点的探索率

print(values)
print(pi)

from IPython import display
import time
# 控制台刷新实现
def refresh():
    display.clear_output(wait=True)
    time.sleep(0.1)

def test():
    def show(row, col, action=None):
        symbols = ['↑','↓','←','→']
        for r in range(6):
            line = ''
            for c in range(12):
                if (r,c) == (row,col):
                    if action is None:
                        line += 'A '  # Agent
                    else:
                        line += symbols[action] + ' '
                elif get_state(r,c) == 'terminal':
                    line += 'G '
                elif get_state(r,c) == 'trap':
                    line += 'C '
                elif (r,c) == "start":
                    line += 'S '
                else:
                    line += '. '
            print(line)


    row, col = 0, 0 # 初始位置

    #最多步数
    for _ in range(1000):

        #选择动作
        # action = np.random.choice(4, p=pi[row, col])
        action = np.argmax(pi[row, col]) # 选择动作

        #打印这个动作
        display.clear_output(wait=True)
        time.sleep(0.1)

        refresh() # 控制台刷新
        show(row, col, action)


        #执行动作
        row, col, reward = move(row, col, action)

        if get_state(row, col) == 'terminal':
            print('Game Over')
            break

# test()

for epoch in range(250):
    values = get_values(row, col, len(action))
    pi = get_pi(row, col, len(action))

    if epoch % 5 == 0:   # 每隔50次看看策略
        print(f"=== 第 {epoch} 次迭代的轨迹 ===")
        test()

print(pi) # 打印策略
print(values) # 评估价值

