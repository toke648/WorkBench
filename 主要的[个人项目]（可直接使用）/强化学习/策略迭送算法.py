# # # 策略迭送算法

# # blank = np.array([[0,0,0,0,0,0,0,0,0,0,0,0]] * 4)

# # end = blank[3, 11] = 1
# # start = blank[3, 0] = 0

# # print(blank)

# # # 越向终点移动，获得的分数越高

# # action = {'up': [1, 0], 'down': [-1, 0], 'left': [0, -1], 'right': [0, 1]}
# # rewards = 0

# row, cols = 4, 12

# #陷阱英文：trap

# for r in range(row):
#     for c in range(cols):
#         if r == 3 and 2 <= c <= cols - 2:
#             print('C', end=' ')  # 悬崖
#         elif (r, c) == (3, 1):
#             print('S', end=' ')  # 起点
#         elif (r, c) == (3, cols - 1):
#             print('G', end=' ')  # 终点
#         else:
#             print('.', end=' ')  # 普通格子
#     print()  # 换行
# print()
# print('*' * 50)


# for i in range(1, 10):
#     for j in range(i, 10):
#         print(f"{i} * {j} = {i*j:2}", end=' | ')
#     print()
# print()
# print('*' * 50)

# row, cols = 4, 12

# for i in range(row):
#     for j in range(cols):
#         print(f"({i},{j})", end=' ')
#     print()

# print()
# print('*' * 50)
# for i in range(row):
#     for j in range(cols):
#         print(f".", end=' ')
#     print()

# print()
# print('*' * 50)



# # 环境初始化
# for i in range(row):
#     for j in range(cols):
#         if i == 3 and 1 <= j < cols - 1:
#             print('C', end=' ')  # 悬崖
#         elif (i, j) == (3, 0):
#             print('S', end=' ')
#         elif (i, j) == (3, cols - 1):
#             print('G', end=' ')

#         else:
#             print('.', end=' ') # 普通格子
#     print()

# ---------------------------------------------- beggin



# 对环境完全已知
# 获取格子的状态
def get_state(row, col):
    if row != 3:
        return 'ground'
    if row == 3 and col == 0:
        return 'ground'
    if row == 3 and col == 11:
        return 'terminal'
    return 'trap'

# print(get_state(0, 0))

#在一个格子里做一个动作
def move(row, col, action):
    # 如果当前已经在陷阱或终点，则不能执行任何动作
    if get_state(row, col) in ['trap', 'terminal']:
        return row, col, 0
    
    # -是向上，+是向下，不要搞反了

    # up
    if action == 0:
        row -= 1
    
    #down
    if action == 1:
        row += 1
    
    #left
    if action == 2:
        col -= 1

    #right
    if action == 3:
        col += 1

    # 不允许走到地图外面去
    row = max(0, row)
    row = min(3, row)
    col = max(0, col)
    col = min(11, col)
    # 以上逻辑是判断是否越界，通过设置最大值和最小值来限制

    # 是陷阱的话，奖励是-100，否则都是-1
    # 这样强迫了机器尽快结束游戏，因为每走一步都要扣一分
    # 结束最好是以走到终点的形式，避免被扣100分
    reward = -1

    if get_state(row, col) == 'trap':
        reward = -100

    return row, col, reward

import numpy as np

#初始化每个格子的价值
values = np.zeros([4, 12])

#初始化每个格子下采用动作的概率
pi = np.ones([4, 12, 4]) * 0.25 

# print(values, pi[0])


"""
Q函数的定义：Q(s, a) = r + γ * max(Q(s', a'))
求state,action的分数
"""
#计算在一个状态下执行动作的分数，得到下一个状态和reward
def get_qsa(row, col,action):
    """
    当前价值=即时奖励+下个状态的价值*折扣因子

    """

    #在当前状态下执行动作，得到下一个状态和reward
    next_row, next_col, reward = move(row, col, action)

    #计算下一个状态的分数，取values当中记录的分数即可，0.9是折扣因子
    value = values[next_row, next_col] * 0.9

    # 如果下个状态时终点或陷阱，则下一个状态的分数是0
    if get_state(next_row, next_col) in ['trap', 'terminal']:
        value = 0 # 评估其价值为0

    return reward + value # 返回当前状态下执行动作的分数


get_qsa(0, 0, 0)

#策略评估
def get_values():

    #初始化一个新的values，重新评估所有格子的分数
    new_values = np.zeros([4, 12])

    #遍历所有格子
    for row in range(4):
        for col in range(12):
            
            #计算当前格子个4给动作分别的分数
            action_value = np.zeros(4)

            #遍历所有动作
            for action in range(4):
                action_value[action] = get_qsa(row, col, action)

            #每个动作的分数和它的概率相乘
            action_value  *= pi[row, col]

            #最后这个格子的分数，等于该格子下所有动作的分数求和
            new_values[row, col] = action_value.sum()

    return new_values

get_values()
values = get_values()
print(values)


#策略提升
def get_pi():
    #重新初始化每个格子下采用动作的概率，重新评估
    new_pi = np.zeros([4, 12, 4]) # 4行12列4个动作
    
    #遍历所有格子
    for row in range(4):
        for col in range(12):
            
            #计算当前格子4个动作分别的分数
            action_value = np.zeros(4)

            #遍历所有动作
            for action in range(4):
                action_value[action] = get_qsa(row, col, action)
            
            #计算当前状态下，达到最大分数的动作有几个
            count = (action_value == action_value.max()).sum() # 计算当前状态下，达到最大分数的动作有几个
            
            #让这些动作均分概率
            for action in range(4):
                if action_value[action] == action_value.max():
                    new_pi[row, col, action] = 1 / count # 均分概率
                else:
                    new_pi[row, col, action] = 0 # 否则概率为0

            # print(new_pi[row, col])
            # print(new_pi)

    return new_pi # 返回新的策略

# 循环迭送
for _ in range(250):
    values = get_values()
    pi = get_pi()

print(values) 
# print(pi)

from IPython import display
import time
# 控制台刷新实现
def refresh():
    display.clear_output(wait=True)
    time.sleep(0.1)

def test():
    def show(row, col, action=None):
        symbols = ['↑','↓','←','→']
        for r in range(4):
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
                elif (r,c) == (3,0):
                    line += 'S '
                else:
                    line += '. '
            print(line)


    row, col = 0, 0 # 初始位置

    #最多步数
    for _ in range(200):

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

test()
print(pi) # 打印策略
print(values) # 评估价值

# ---------------------------------------------- end --------------------------------------------------




# print(np.array([4, 12, 4])) # 创建一个4行12列的数组，每个元素都是0



# r = random.randint(0,1)
# c = random.randint(0,1)

# print(r, c)

# print(random.random())  # random.random生成随机1以内的数
# print(random.randint(0,1))  # random.random生成随机1以内的数
# print([random.randint(0,1) for _ in range(50)])




# import numpy as np

# rows, cols = 4, 12
# gamma = 0.9  # 折扣因子
# actions = ['up', 'down', 'left', 'right']
# action_delta = {'up':(-1,0), 'down':(1,0), 'left':(0,-1), 'right':(0,1)}

# def step(state, action):
#     r, c = state
#     dr, dc = action_delta[action]
#     nr, nc = max(0, min(rows-1, r+dr)), max(0, min(cols-1, c+dc))
#     new_state = (nr, nc)

#     # 奖励规则
#     if new_state == (3, cols-1):  # 终点
#         return new_state, 1
#     elif (r == 3 and 1 <= c <= cols-2):  # 悬崖区
#         return (3,0), -1
#     else:
#         return new_state, -0.01  # 每走一步的小惩罚


# # 初始化
# V = np.zeros((rows, cols))  
# policy = { (r,c): np.random.choice(actions) for r in range(rows) for c in range(cols) }

# # 策略迭代循环
# for it in range(50):
#     # 策略评估
#     for _ in range(100):  # 迭代更新 V
#         new_V = np.zeros_like(V)
#         for r in range(rows):
#             for c in range(cols):
#                 a = policy[(r,c)]
#                 (nr,nc), reward = step((r,c), a)
#                 new_V[r,c] = reward + gamma * V[nr,nc]
#         V = new_V

#     # 策略提升
#     stable = True
#     for r in range(rows):
#         for c in range(cols):
#             old_action = policy[(r,c)]
#             values = []
#             for a in actions:
#                 (nr,nc), reward = step((r,c), a)
#                 values.append(reward + gamma * V[nr,nc])
#             policy[(r,c)] = actions[np.argmax(values)]
#             if policy[(r,c)] != old_action:
#                 stable = False
    
#     if stable:
#         break


# # 图形化打印策略
# def print_policy(policy):
#     symbols = {'up':'↑','down':'↓','left':'←','right':'→'}
#     grid = [[' ']*cols for _ in range(rows)]
    
#     for r in range(rows):
#         for c in range(cols):
#             if (r,c) == (3,0):
#                 grid[r][c] = 'S'   # 起点
#             elif (r,c) == (3,cols-1):
#                 grid[r][c] = 'G'   # 终点
#             elif r == 3 and 1 <= c <= cols-2:
#                 grid[r][c] = 'C'   # 悬崖
#             else:
#                 grid[r][c] = symbols[policy[(r,c)]]
    
#     for row in grid:
#         print(' '.join(row))

# print("最终价值函数 V：\n", V)
# print("\n最终策略 π：")
# print_policy(policy)





# 自己来一遍

