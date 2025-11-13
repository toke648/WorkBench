def get_state(row, col):
    if row != 3:
        return 'ground'
    if row == 3 and  col == 0:
        return 'ground'
    if row == 3 and col == 11:
        return 'terminal'
    
    return 'trap'

ROWS = 4
COLS = 12
ACTIONS = ['left', 'right', 'up', 'down']
Num_actions = len(ACTIONS)

for r in range(ROWS):
    for c in range(COLS):
        state = get_state(r, c)
        print(state, end='\t')
    print()


def move(row, col, action):
    """
    如果移动到陷阱或者终点，则返回当前位置和0分
    否则返回新位置和-1分

    """

    if get_state(row, col) in ['trap', 'terminal']:
        return row, col, 0
    
    if action == 'up':
        row -= 1
    elif action == 'down':
        row += 1
    elif action == 'left':
        col -= 1
    elif action == 'right':
        col += 1

    # 不允许走到边界
    row = max(0, row)
    row = min(3, row)
    col = max(0, col)
    col = min(11, col)

    reward = -1

    # 奖励规则
    if get_state(row, col) == 'terminal':
        reward = 100
        return row, col, reward
    
    """
    简而言之就是，走到了悬崖的惩罚还没有站在原地的惩罚多？因此以最快的速度跑到悬崖？
    """
    if get_state(row, col) == 'trap':
        return row, col, -20
    
    return row, col, reward

for r in range(ROWS):
    for c in range(COLS):
        state = get_state(r, c)
        if state == 'ground':
            for a in ['up', 'down', 'left', 'right']:
                new_r, new_c, reward = move(r, c, a)
                print(f'({r}, {c}) -> ({new_r}, {new_c}) {reward}', end='\t')
            print()

# 动作函数和Qlearning算法一样

import numpy as np
import random

def get_action(row, col, episode=0):
    # 动态调整探索率，随着训练进行逐渐减少探索
    epsilon = max(0.01, 0.1 - episode/10000)  # 从0.1逐渐减少到0.01
    
    # 有小概率选择随机动作
    if random.random() < epsilon:
        return random.randint(0, Num_actions - 1)
    
    # 否则选择分数最高的动作
    return Q[row, col].argmax() % Num_actions


# 初始化在每一个格子里采取每个动作的分数，初始化都是0，因为没有任何的知识
Q = np.zeros([ROWS, COLS, Num_actions])

# 保存历史数据，键是（row，col， action）， 值是（next_row,next_col, reward）
history = {}

print(Q.shape, history)

def get_update(row, col, action, reward, next_row, next_col):
    # target为下一个格子的最高分数，这里的计算和下一步的动作无关
    target = 0.9 * Q[next_row, next_col].max()

    # 加上本步的分数
    target += reward

    # 计算value
    value = Q[row, col, action]

    # 计算更新值
    update = 0.1 * (target - value)

    return update

def q_planning():
    # 随机选择曾经遇到过的状态动作对
    row, col, action = random.choice(list(history.keys()))

    # 再获取下一个状态和反馈
    next_row, next_col, reward = history[(row, col, action)]

    # 计算分数
    update = get_update(row, col ,action, reward, next_row, next_col)

    # 更新分数
    Q[row, col, action] += update # 将上次的分数加上这次的分数，相加后得到新的分数



epoch = 5000  # 增加训练次数

def train():
    for epo in range(epoch):
        # 初始化状态，从地面起点开始
        row = 3  
        col = 0  

        # 计算反馈的和
        reward_sum = 0

        steps = 0
        max_steps = 100

        while get_state(row, col) not in ['trap', 'terminal'] and steps < max_steps:
            # 选择动作（使用动态探索率）
            epsilon = max(0.01, 0.5 - epo/2000)  # 从0.5逐渐减少到0.01
            if random.random() < epsilon:
                action = random.randint(0, Num_actions - 1)
            else:
                action = Q[row, col].argmax() % Num_actions
            
            # 执行动作
            next_row, next_col, reward = move(row, col, ACTIONS[action])
            reward_sum += reward

            # 计算更新值
            target = 0.9 * Q[next_row, next_col].max()
            target += reward
            value = Q[row, col, action]
            update = 0.1 * (target - value)

            # 更新Q值
            Q[row, col, action] += update

            # 将经验存储到模型中
            history[(row, col, action)] = (next_row, next_col, reward)

            # 进行Q-planning（适度频率）
            if len(history) > 5 and random.random() < 0.3:  # 30%概率进行规划
                for _ in range(3):
                    q_planning()

            # 更新当前位置
            row, col = next_row, next_col
            steps += 1
            
        # 输出训练进度
        if epo % 200 == 0:
            print(f"Episode {epo}: reward_sum = {reward_sum}, steps = {steps}")

train()


# 训练完成后，从Q表中提取最优策略
for r in range(ROWS):
    for c in range(COLS):
        history[r, c] = Q[r, c].argmax()  # 选择Q值最大的动作作为最优策略
def show_policy(history):
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
            else: line += symbols[history[r,c]] + ' '
        print(line)

show_policy(history)


def show(row, col, action):
    # 创建12x12的地图可视化
    graph = []
    for r in range(ROWS):
        for c in range(COLS):
            state = get_state(r, c)
            if state == 'start':
                graph.append('S ')  # 起点
            elif state == 'terminal':
                graph.append('G ')  # 终点
            elif state == 'trap':
                graph.append('T ')  # 陷阱
            else:
                graph.append('. ')  # 普通地面
    
    # 在当前位置显示动作
    symbols = ['↑','↓','←','→']
    graph[row * COLS + col] = symbols[action] + ' '
    
    # 打印地图
    graph_str = ''.join(graph)
    for i in range(0, ROWS * 2, 2):  # 每行2个字符（符号+空格）
        print(graph_str[i*COLS:(i+2)*COLS])




import IPython.display as display
import time
import os

def test():
    # 起点
    row, col = 0, 0
    
    # 最多玩N步
    for _ in range(200):
        # 获取当前状态，如果状态是终点或者掉陷阱则终止
        if get_state(row, col) in ['trap', 'terminal']:
            print(f"游戏结束！最终状态: {get_state(row, col)}")
            break
            
        # 选择最优动作
        action = history[row, col]  # 使用训练好的策略
        
        display.clear_output(wait=True)
        # 添加延时以便观察
        time.sleep(0.1)
        show(row, col, action)
        
        # 执行动作
        next_row, next_col, reward = move(row, col, ACTIONS[action])
        
        # 更新位置
        row, col = next_row, next_col
        
        

# 运行测试
test()