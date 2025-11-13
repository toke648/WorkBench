import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.animation import FuncAnimation

# 固定迷宫 (0 = 可走, 1 = 墙)
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

MAZE_SIZE = 12
start = (0, 0)  # 起点
goal = (11, 11)  # 终点
actions = [(-1, 0), (1, 0), (0, -1), (0, 1)]  # 上下左右
Q_table = np.zeros((MAZE_SIZE, MAZE_SIZE, len(actions)))

# Q-Learning 相关参数
alpha = 0.1   # 学习率
gamma = 0.9   # 折扣因子
epsilon = 0.2 # 探索率
num_episodes = 1000  # 训练轮数
max_steps = MAZE_SIZE * MAZE_SIZE  # 每轮最大步数

reward_history = []
step_history = []
paths = []  # 记录每轮训练的路径

def manhattan_distance(p1, p2):
    """计算曼哈顿距离"""
    return abs(p1[0] - p2[0]) + abs(p1[1] - p2[1])

# 训练 Q-Learning
for episode in range(1, num_episodes + 1):
    state = start
    total_reward = 0
    steps = 0
    path = [state]  # 记录路径
    prev_distance = manhattan_distance(state, goal)

    while state != goal and steps < max_steps:
        if np.random.rand() < epsilon:
            action = np.random.choice(len(actions))  # 随机探索
        else:
            action = np.argmax(Q_table[state[0], state[1]])  # 选择最优策略
        
        # 计算下一步
        new_state = (state[0] + actions[action][0], state[1] + actions[action][1])

        # 计算奖励
        if 0 <= new_state[0] < MAZE_SIZE and 0 <= new_state[1] < MAZE_SIZE and maze[new_state] == 0:
            new_distance = manhattan_distance(new_state, goal)
            reward = 10 if new_state == goal else 0.1 * (prev_distance - new_distance)  # 靠近终点加分
            prev_distance = new_distance
            state = new_state
            path.append(state)
        else:
            reward = -1  # 撞墙扣分

        total_reward += reward
        steps += 1  # 计步

    if steps >= max_steps:
        total_reward -= 5  # 超时扣分

    reward_history.append(total_reward)
    step_history.append(steps)
    paths.append(path)  # 记录每轮训练的完整路径

    if episode % 100 == 0:
        print(f"训练进度: {episode}/{num_episodes} | 步数: {steps} | 奖励: {total_reward:.2f}")

print("\n训练完成，Q-Table 已保存！")
np.save("q_table.npy", Q_table)

# ========================== 动画可视化 ==========================
fig, ax = plt.subplots(figsize=(6, 6))
sns.heatmap(maze, cmap="gray", cbar=False, linewidths=0.5, linecolor="black", xticklabels=False, yticklabels=False, ax=ax)
dot, = ax.plot([], [], "ro", markersize=8)  # 红点代表智能体位置

def update(frame):
    """ 更新动画帧 """
    path = paths[frame]
    x_data = [p[1] + 0.5 for p in path]  # 列坐标
    y_data = [p[0] + 0.5 for p in path]  # 行坐标
    dot.set_data(x_data, y_data)
    ax.set_title(f"训练轮次: {frame+1}/{num_episodes}")
    return dot,

ani = FuncAnimation(fig, update, frames=len(paths), interval=100, repeat=False)

# ========================== 学习曲线 ==========================
plt.figure(figsize=(12, 5))
plt.subplot(1, 2, 1)
plt.plot(step_history, label="步数")
plt.xlabel("训练轮次")
plt.ylabel("步数")
plt.title("训练过程中步数变化")
plt.legend()

plt.subplot(1, 2, 2)
plt.plot(reward_history, label="奖励", color="r")
plt.xlabel("训练轮次")
plt.ylabel("奖励")
plt.title("训练过程中奖励变化")
plt.legend()

plt.show()
