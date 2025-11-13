# import numpy as np
# import random

# # 定义环境：0 表示可走的路，1 表示障碍，2 表示终点
# maze = np.array([
#     [0, 0, 0, 1, 0],
#     [1, 1, 0, 1, 0],
#     [0, 0, 0, 0, 0],
#     [0, 1, 1, 1, 0],
#     [0, 0, 0, 2, 0]
# ])

# # 动作空间：上、下、左、右
# actions = [(0, -1), (0, 1), (-1, 0), (1, 0)]

# # 初始化 Q 表（状态-动作价值表）
# Q = np.zeros((5, 5, len(actions)))

# # 训练参数
# alpha = 0.1  # 学习率
# gamma = 0.9  # 折扣因子
# epsilon = 0.1  # ε-贪心策略
# num_episodes = 500  # 训练轮数

# # 训练 Q-learning 代理
# for episode in range(num_episodes):
#     state = (0, 0)  # 起点
#     while maze[state] != 2:  # 终点
#         if random.uniform(0, 1) < epsilon:
#             action = random.randint(0, len(actions) - 1)  # 随机探索
#         else:
#             action = np.argmax(Q[state[0], state[1]])  # 选择最大 Q 值的动作

#         # 计算新状态
#         new_state = (state[0] + actions[action][0], state[1] + actions[action][1])
        
#         # 确保新状态在边界内
#         if new_state[0] < 0 or new_state[0] >= 5 or new_state[1] < 0 or new_state[1] >= 5 or maze[new_state] == 1:
#             reward = -1  # 撞墙
#             new_state = state  # 停在原地
#         elif maze[new_state] == 2:
#             reward = 10  # 到达终点
#         else:
#             reward = -0.1  # 继续前进的轻微惩罚

#         # 更新 Q 值
#         Q[state[0], state[1], action] = (1 - alpha) * Q[state[0], state[1], action] + \
#                                         alpha * (reward + gamma * np.max(Q[new_state[0], new_state[1]]))
#         state = new_state  # 更新状态

# # 打印最终 Q 值表
# print("训练完成，Q 值表如下：")
# print(Q)


# 2 、强化学习示例
import numpy as np
import matplotlib.pyplot as plt
import time

# 迷宫环境：0=可走，1=障碍
maze = np.array([
    [0, 1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0],
    [0, 1, 0, 1, 1, 1, 0, 1, 0, 1, 1, 0],
    [0, 0, 0, 1, 0, 0, 0, 0, 0, 1, 1, 0],
    [1, 1, 0, 1, 0, 1, 1, 1, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 0],
    [0, 1, 1, 1, 1, 1, 0, 0, 0, 0, 1, 0],
    [0, 0, 0, 0, 0, 1, 1, 1, 1, 0, 1, 0],
    [1, 1, 1, 1, 0, 0, 0, 0, 1, 0, 0, 0],
    [0, 0, 0, 1, 1, 1, 1, 0, 1, 1, 1, 0],
    [0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0],
    [0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
])

# 迷宫大小
ROWS, COLS = maze.shape

# 起点和终点
start = (0, 0)
goal = (11, 11)

# 动作空间：上、下、左、右
actions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
action_dict = {0: "↑", 1: "↓", 2: "←", 3: "→"}

# Q表格初始化
Q_table = np.zeros((ROWS, COLS, len(actions)))

# Q-learning 参数
alpha = 0.1   # 学习率
gamma = 0.9   # 折扣因子
epsilon = 0.2 # 探索率
num_episodes = 200  # 训练轮次

# 计算下一步状态
def next_state(state, action):
    row, col = state
    dr, dc = actions[action]
    new_row, new_col = row + dr, col + dc
    if 0 <= new_row < ROWS and 0 <= new_col < COLS and maze[new_row, new_col] == 0:
        return (new_row, new_col)
    return state  # 碰到墙壁不变

# 训练过程
for episode in range(1, num_episodes + 1):
    state = start
    path = [state]

    while state != goal:
        # 选择动作（ε-greedy）
        if np.random.rand() < epsilon:
            action = np.random.choice(len(actions))  # 随机探索
        else:
            action = np.argmax(Q_table[state[0], state[1]])  # 利用最优策略

        # 执行动作
        next_s = next_state(state, action)
        reward = 1 if next_s == goal else -0.01  # 目标点奖励1，其它惩罚-0.01
        Q_table[state[0], state[1], action] += alpha * (reward + gamma * np.max(Q_table[next_s[0], next_s[1]]) - Q_table[state[0], state[1], action])
        
        state = next_s
        path.append(state)

    # 每 100 轮可视化一次当前策略
    if episode % 10 == 0 or episode == num_episodes:
        print(f"\n训练轮次 {episode}:")
        policy_grid = np.full((ROWS, COLS), "■", dtype=str)
        for r in range(ROWS):
            for c in range(COLS):
                if (r, c) == goal:
                    policy_grid[r, c] = "G"
                elif maze[r, c] == 0:
                    best_action = np.argmax(Q_table[r, c])
                    policy_grid[r, c] = action_dict[best_action]

        # 可视化路径
        plt.figure(figsize=(5, 5))
        plt.imshow(maze, cmap="gray_r")  # 显示迷宫
        for r, c in path:
            plt.text(c, r, "o", ha="center", va="center", fontsize=12, color="red")
        plt.title(f"Episode {episode}: Agent Path")
        plt.show()
        time.sleep(0.5)  # 让动画更流畅

# 训练结束后显示最终策略
print("\n最终学习到的最优策略：")
for row in policy_grid:
    print(" ".join(row))
