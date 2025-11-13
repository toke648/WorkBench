import numpy as np

def get_state(row, col):
    """
    初始化环境的状态，输出当且格子的状态
    """

    # 如果要改地图大小，请修改这里
    if (row, col) in [(0, 0)]:
        return 'start'
    if (row, col) in [(11, 11)]:
        return 'terminal'
    if (row, col) in [(1, 5), (2, 2), (2, 4), (3, 7), (4, 3), (5, 1), (7, 6), (8, 8), (9, 4), (10, 9)]:
        return 'trap'
    return 'ground'

# # 环境状态可视化
# for r in range(12):
#     for c in range(12):
#         print(get_state(r, c), end='\t')
#     print()

def move(row, col, action):
    """
    移动智能体，根据当前位置和动作，返回新的位置和奖励

    状态 & 策略 初始化
    """
    # 结束状态
    if get_state(row, col) in ['trap', 'terminal']:
        return row, col, 0
    
    # 移动实现
    if action == 'up': row -= 1
    elif action == 'down': row += 1
    elif action == 'left': col -= 1
    elif action == 'right': col += 1

    # 边界限制
    row = min(max(row, 0), 11)
    col = min(max(col, 0), 11)

    # 默认奖励为-1，促使智能体尽快到达终点
    reward = -1

     # 事件处理
    state = get_state(row, col)
    if state == 'trap': reward = -100
    elif state == 'terminal': reward = 100

    return row, col, reward

ROWS, COLS, ACTIONS = 12, 12, {0:'up', 1:'down', 2:'left', 3:'right'}
NUM_ACTIONS = len(ACTIONS)
GAMMA = 0.9 # 折扣因子

epoch = 100
# 价值函数初始化
values = np.zeros((ROWS, COLS))
policy = np.zeros((ROWS, COLS), dtype=int)  # 初始化策略为随机策略

# # 测试
# for r in range(row):
#     for c in range(col):
#         print(move(r, c, random.choice(['up', 'down', 'left', 'right'])))


# 策略迭送
for _ in range(epoch):
    """
    根据奖励判断当前的位置状态，根据周围四个格子的状态选择最佳动作，并更新价值函数和策略

    说明
    环境会逐级递减，因为策略函数的原因，在之后的训练当中，价值越高的格子，越会被优先选择，所以价值函数会越来越高
    同时智能体也能够获取到周围格子的状态价值，因此高价值的格子，被智能体所选择概率会更高，奖励会逐渐累加
    """
    new_values = np.copy(values)
    # 遍历所有格子
    for r in range(ROWS):
        for c in range(COLS):
            if get_state(r, c) in ['trap', 'terminal']: # 跳过障碍物和终点
                continue
            q_values = [] # 初始化动作价值列表
            for a in range(NUM_ACTIONS): # 遍历所有动作
                nr, nc, reward = move(r, c, ACTIONS[a])
                v = 0 if get_state(nr, nc) in ['trap', 'terminal'] else values[nr, nc] # 获取下一个状态价值 // 如果下一个状态是障碍物或者终点，则价值为0，否则输出当前该点的价值
                q_values.append(reward + GAMMA * v) # 计算动作价值 // 奖励加上折扣因子乘以下一个状态价值
            new_values[r, c] = max(q_values) # 更新价值函数 // 获取最大动作价值
            policy[r, c] = np.argmax(q_values) # 更新策略 // 获取最大动作索引
        values = new_values # 更新价值函数

    print(q_values)
    # print(values)


def show_policy(policy):
    """
    可视化策略
    """
    symbols = ['↑','↓','←','→']

    for r in range(ROWS):
        line = ' '
        for c in range(COLS):
            s = get_state(r, c)
            if s == 'terminal': line += 'G '
            elif s == 'trap': line += 'C '
            elif (r,c) == (0,0): line += 'S '
            else: line += symbols[policy[r,c]] + ' '
        print(line)

show_policy(policy)