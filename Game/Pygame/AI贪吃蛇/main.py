import torch
import torch.nn as nn
import torch.optim as optim
import random
import pygame
import numpy as np
from collections import deque

# 游戏参数
GRID_WIDTH = 10
GRID_HEIGHT = 10
GRID_SIZE = 30  # 每个方格的像素大小

# 定义CNN模型
class CNNModel(nn.Module):
    def __init__(self):
        super(CNNModel, self).__init__()
        self.conv1 = nn.Conv2d(1, 32, kernel_size=3, padding=1)  # 输入通道1，输出通道32，卷积核大小3x3
        self.pool = nn.MaxPool2d(2, 2)  # 2x2池化
        self.conv2 = nn.Conv2d(32, 64, kernel_size=3, padding=1)  # 输入通道32，输出通道64
        # 假设输入图像大小是 10x10，经池化后输出 2x2 特征图
        self.fc1 = nn.Linear(64 * 2 * 2, 128)  # 输入维度是 64*2*2，输出128维
        self.fc2 = nn.Linear(128, 4)  # 输出 4 个动作

    def forward(self, x):
        # 第一层卷积
        x = torch.relu(self.conv1(x))
        # 第一层池化
        x = self.pool(x)
        # 第二层卷积
        x = torch.relu(self.conv2(x))
        # 第二层池化
        x = self.pool(x)
        # 展平
        x = torch.flatten(x, 1)  # 展平张量
        x = torch.relu(self.fc1(x))
        x = self.fc2(x)
        return x

# 初始化pygame
pygame.init()
screen = pygame.display.set_mode((GRID_WIDTH * GRID_SIZE, GRID_HEIGHT * GRID_SIZE))
pygame.display.set_caption('AI Snake Game')

class SnakeGame:
    def __init__(self):
        self.reset()

    def reset(self):
        self.snake = [[5, 5]]  # 蛇的初始位置
        self.food = [random.randint(0, GRID_WIDTH - 1), random.randint(0, GRID_HEIGHT - 1)]
        self.direction = [0, -1]  # 初始方向向上
        self.done = False  # 游戏是否结束

    def step(self, action):
        if action == 0:  # 上
            self.direction = [0, -1]
        elif action == 1:  # 下
            self.direction = [0, 1]
        elif action == 2:  # 左
            self.direction = [-1, 0]
        elif action == 3:  # 右
            self.direction = [1, 0]

        # 移动蛇
        new_head = [self.snake[0][0] + self.direction[0], self.snake[0][1] + self.direction[1]]
        reward = 0  # 默认奖励为 0

        # 检查是否撞墙或撞到自己
        if (new_head[0] < 0 or new_head[0] >= GRID_WIDTH or
                new_head[1] < 0 or new_head[1] >= GRID_HEIGHT or
                new_head in self.snake):
            self.done = True
            reward = -10  # 撞墙或撞到自己，负奖励
            return self.get_state(), reward, self.done

        self.snake.insert(0, new_head)

        # 判断是否吃到食物
        if self.snake[0] == self.food:
            self.food = [random.randint(0, GRID_WIDTH - 1), random.randint(0, GRID_HEIGHT - 1)]
            reward = 10  # 吃到食物，正奖励
        else:
            self.snake.pop()

            # 基于距离的奖励：靠近食物获得小奖励
            if len(self.snake) > 1:  # 确保蛇的长度大于 1 才计算距离
                old_distance = abs(self.snake[1][0] - self.food[0]) + abs(self.snake[1][1] - self.food[1])
                new_distance = abs(self.snake[0][0] - self.food[0]) + abs(self.snake[0][1] - self.food[1])
                if new_distance < old_distance:
                    reward = 1  # 靠近食物
                else:
                    reward = -1  # 远离食物

        return self.get_state(), reward, self.done

    def get_state(self):
        state = np.zeros((GRID_HEIGHT, GRID_WIDTH))  # 初始化状态矩阵
        for x, y in self.snake:
            state[y][x] = 1  # 设置蛇的位置为 1
        state[self.food[1]][self.food[0]] = 2  # 设置食物的位置为 2
        return state

    def render(self):
        screen.fill((0, 0, 0))  # 清空屏幕
        for x, y in self.snake:
            pygame.draw.rect(screen, (0, 255, 0), pygame.Rect(x * GRID_SIZE, y * GRID_SIZE, GRID_SIZE, GRID_SIZE))
        pygame.draw.rect(screen, (255, 0, 0), pygame.Rect(self.food[0] * GRID_SIZE, self.food[1] * GRID_SIZE, GRID_SIZE, GRID_SIZE))
        pygame.display.flip()

# epsilon-greedy 策略
def select_action(model, state, epsilon):
    if random.random() < epsilon:  # 探索
        return random.randint(0, 3)
    else:  # 利用
        state_tensor = torch.tensor(state, dtype=torch.float32).unsqueeze(0).unsqueeze(0)
        with torch.no_grad():
            q_values = model(state_tensor)
        return torch.argmax(q_values).item()

def train_model():
    model = CNNModel()
    optimizer = optim.Adam(model.parameters(), lr=0.001)
    game = SnakeGame()
    episodes = 300
    epsilon = 1.0  # 初始epsilon
    epsilon_decay = 0.995  # 衰减系数
    min_epsilon = 0.1  # 最小epsilon
    memory = deque(maxlen=10000)  # 经验回放
    batch_size = 64

    for episode in range(episodes):
        state, reward, done = game.reset(), 0, False
        total_reward = 0

        while not done:
            action = select_action(model, state, epsilon)
            next_state, reward, done = game.step(action)
            total_reward += reward

            # 保存经验到回放池
            memory.append((state, action, reward, next_state, done))

            state = next_state

            # 训练模型
            if len(memory) > batch_size:
                batch = random.sample(memory, batch_size)
                states, actions, rewards, next_states, dones = zip(*batch)

                # 在每个回合结束时收集状态
                states = [state]  # 如果只是单个状态，确保它是列表形式

                # 如果有多个状态，在这里收集
                states = np.array(states)  # 转换为 NumPy 数组

                # 然后再转换为 PyTorch tensor
                states_tensor = torch.tensor(states, dtype=torch.float32).unsqueeze(1)
                next_states_tensor = torch.tensor(next_states, dtype=torch.float32).unsqueeze(1)
                rewards_tensor = torch.tensor(rewards, dtype=torch.float32)
                dones_tensor = torch.tensor(dones, dtype=torch.float32)

                # Q学习更新
                current_q_values = model(states_tensor).gather(1, torch.tensor(actions).view(-1, 1))
                next_q_values = model(next_states_tensor).max(1)[0].detach()
                target_q_values = rewards_tensor + (0.95 * next_q_values) * (1 - dones_tensor)

                loss = torch.mean((current_q_values.squeeze() - target_q_values) ** 2)

                optimizer.zero_grad()
                loss.backward()
                optimizer.step()

        # 衰减epsilon
        epsilon = max(min_epsilon, epsilon * epsilon_decay)

        print(f"Episode {episode}, Total Reward: {total_reward}, Epsilon: {epsilon:.2f}")

    return model

if __name__ == "__main__":
    model = train_model()
