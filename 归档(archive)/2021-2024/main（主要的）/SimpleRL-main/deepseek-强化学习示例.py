import numpy as np

# 初始化参数
grid_size = 4
actions = ['up', 'down', 'left', 'right']
num_actions = len(actions)
Q = np.zeros((grid_size, grid_size, num_actions))

# 超参数
alpha = 0.1  # 学习率
gamma = 0.9  # 折扣因子
epsilon = 0.1  # 探索率
num_episodes = 1000

# Q-learning 算法
for episode in range(num_episodes):
    state = (0, 0)  # 初始状态
    while state != (3, 3):  # 未到达目标
        # 选择动作
        if np.random.rand() < epsilon:
            action = np.random.choice(num_actions)  # 随机探索
        else:
            action = np.argmax(Q[state[0], state[1], :])  # 选择最优动作

        # 执行动作
        next_state = list(state)
        if actions[action] == 'up':
            next_state[0] = max(0, state[0] - 1)
        elif actions[action] == 'down':
            next_state[0] = min(3, state[0] + 1)
        elif actions[action] == 'left':
            next_state[1] = max(0, state[1] - 1)
        elif actions[action] == 'right':
            next_state[1] = min(3, state[1] + 1)
        next_state = tuple(next_state)

        # 计算奖励
        reward = 1 if next_state == (3, 3) else 0

        # 更新 Q 值
        Q[state[0], state[1], action] += alpha * (reward + gamma * np.max(Q[next_state[0], next_state[1], :]) - Q[state[0], state[1], action])

        # 更新状态
        state = next_state

# 输出学习后的 Q 表
print("Q 表：")
print(Q)