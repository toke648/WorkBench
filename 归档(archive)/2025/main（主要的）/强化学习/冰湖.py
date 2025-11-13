"""
练习项目：冰湖

让小人躲避冰湖，并抵达终点获得奖励
"""

import numpy as np

ROW, COL = 4, 4
ACTIONS = ['up', 'down', 'left', 'right']
NUM_ACTIONS = len(ACTIONS)
GAMMA = 0.9


def get_state(row, col):
    """
    根据行和列获取状态编号
    """
    if (row, col) in [(0, 0)]: return 'start' 
    if (row, col) in [(1, 2), (2, 2), (2, 1), (1, 3)]: return 'hole'
    if (row, col) in [(3, 3)]: return 'goal'
    return 'ground'

for r in range(ROW):
    for c in range(COL):
        print(get_state(r, c), end='\t')
    print()

def move(row, col, action):
    """
    根据动作移动，并返回新的行和列，以及奖励
    """
    # 结束状态
    if get_state(row, col) in ['hole', 'goal']:
        return row, col, 0

    if action == 'up': row -= 1
    elif action == 'down': row += 1
    elif action == 'left': col -= 1
    elif action == 'right': col += 1

    # 边界限制
    row = min(max(row, 0), ROW-1)
    col = min(max(col, 0), COL-1)

    # 默认奖励为-1，促使智能体尽快到达终点
    reward = -1

    # 事件处理
    state = get_state(row, col)
    if state == 'hole': reward = -100
    elif state == 'goal': reward = 100

    return row, col, reward

for r in range(ROW):
    for c in range(COL):
        for a in ACTIONS:
            print(move(r, c, a), end='\t')
            # print(move(r, c, ACTIONS[c]), end='\t')
        print()

epoch = 100
values = np.zeros((ROW, COL))
policy = np.zeros((ROW, COL))

for _ in range(epoch):
    # """
    # 根据奖励判断当前的位置状态，根据周围四个格子的状态选择最佳动作，并更新价值函数和策略

    # 说明
    # 环境会逐级递减，因为策略函数的原因，在之后的训练当中，价值越高的格子，越会被优先选择，所以价值函数会越来越高
    # 同时智能体也能够获取到周围格子的状态价值，因此高价值的格子，被智能体所选择概率会更高，奖励会逐渐累加
    # """
    new_values = np.zeros((ROW, COL))
    for r in range(ROW):
        for c in range(COL):
            # 如果当前位置是冰洞或终点，跳过
            if get_state(r, c) in ['hole', 'goal']:
                continue

            # 计算当前位置价值
            q_values = []

            # 计算当前位置价值列表
            for a in ACTIONS: # 获取当前位置的周围四个格子的状态和价值，价值存储在q_values列表中
                nr, nc, reward = move(r, c, a) # 循环遍历，获取四个方向的奖励，格子状态和格子位置
                v = 0 if get_state(nr, nc) in ['hole', 'goal'] else values[nr, nc] # 获取下一个状态价值
                q_values.append(reward + GAMMA * v) # 计算当前位置的四个方向的价值，存储在q_values列表中
            
            # 更新当前位置价值
            new_values[r, c] = np.max(q_values) # 获取最大动作价值状态
            policy[r, c] = np.argmax(q_values) # 获取最大动作价值状态的索引
            print(q_values) # 打印当前位置价值列表

        values = new_values # 更新价值函数
        print(new_values)

print(values)
print(policy)
