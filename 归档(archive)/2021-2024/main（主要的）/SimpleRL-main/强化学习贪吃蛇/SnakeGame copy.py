import random
import numpy as np
import gym
from gym import spaces

class SnakeGame(gym.Env):
    def __init__(self):
        super(SnakeGame, self).__init__()
        
        self.grid_size = 10  # 游戏网格大小
        self.snake = [(5, 5)]  # 初始蛇的位置
        self.food = (random.randint(0, self.grid_size - 1), random.randint(0, self.grid_size - 1))  # 食物的位置
        self.direction = (0, 1)  # 初始方向（向右）
        self.done = False
        self.reward = 0
        
        # 定义动作空间和状态空间
        self.action_space = spaces.Discrete(4)  # 上，下，左，右
        self.observation_space = spaces.Box(low=0, high=self.grid_size-1, shape=(2, self.grid_size, self.grid_size), dtype=np.int32)
    
    def step(self, action):
        if action == 0:  # 上
            self.direction = (-1, 0)
        elif action == 1:  # 下
            self.direction = (1, 0)
        elif action == 2:  # 左
            self.direction = (0, -1)
        elif action == 3:  # 右
            self.direction = (0, 1)

        head_x, head_y = self.snake[0]
        new_head = (head_x + self.direction[0], head_y + self.direction[1])

        # 碰到墙壁或者自己
        if (new_head[0] < 0 or new_head[1] < 0 or new_head[0] >= self.grid_size or new_head[1] >= self.grid_size or new_head in self.snake):
            self.done = True
            self.reward = -1  # 撞墙或撞到自己
            return self._get_obs(), self.reward, self.done, {}
        
        # 吃到食物
        if new_head == self.food:
            self.snake.insert(0, new_head)
            self.food = (random.randint(0, self.grid_size - 1), random.randint(0, self.grid_size - 1))  # 随机生成新的食物
            self.reward = 1  # 吃到食物
        else:
            self.snake = [new_head] + self.snake[:-1]  # 移动蛇
            self.reward = 0  # 无奖励

        return self._get_obs(), self.reward, self.done, {}

    def reset(self):
        self.snake = [(5, 5)]  # 初始蛇的位置
        self.food = (random.randint(0, self.grid_size - 1), random.randint(0, self.grid_size - 1))  # 随机生成食物
        self.direction = (0, 1)  # 初始方向（向右）
        self.done = False
        return self._get_obs()

    def render(self):
        grid = np.zeros((self.grid_size, self.grid_size), dtype=int)
        for segment in self.snake:
            grid[segment[0], segment[1]] = 1  # 蛇身
        grid[self.food[0], self.food[1]] = 2  # 食物
        print(grid)
        
    def _get_obs(self):
        grid = np.zeros((2, self.grid_size, self.grid_size), dtype=int)
        for segment in self.snake:
            grid[0, segment[0], segment[1]] = 1  # 蛇身
        grid[1, self.food[0], self.food[1]] = 1  # 食物
        return grid

import torch
import torch.nn as nn
import torch.optim as optim
import random
from collections import deque

class DQN(nn.Module):
    def __init__(self, input_shape, n_actions):
        super(DQN, self).__init__()
        self.conv1 = nn.Conv2d(input_shape[0], 32, kernel_size=3, stride=1)
        self.conv2 = nn.Conv2d(32, 64, kernel_size=3, stride=1)
        self.fc1 = nn.Linear(64 * 6 * 6, 512)
        self.fc2 = nn.Linear(512, n_actions)
        
    def forward(self, x):
        x = torch.relu(self.conv1(x))
        x = torch.relu(self.conv2(x))
        x = x.view(x.size(0), -1)  # Flatten
        x = torch.relu(self.fc1(x))
        return self.fc2(x)

class Agent:
    def __init__(self, input_shape, n_actions):
        self.input_shape = input_shape
        self.n_actions = n_actions
        self.policy_net = DQN(input_shape, n_actions).to(device)
        self.target_net = DQN(input_shape, n_actions).to(device)
        self.target_net.load_state_dict(self.policy_net.state_dict())
        self.target_net.eval()
        
        self.optimizer = optim.Adam(self.policy_net.parameters(), lr=0.0001)
        self.memory = deque(maxlen=10000)
        self.batch_size = 32
        self.gamma = 0.99
        self.epsilon = 0.1
        self.epsilon_decay = 0.995
        self.epsilon_min = 0.01

    def select_action(self, state):
        if random.random() < self.epsilon:
            return random.randint(0, self.n_actions - 1)  # 探索
        else:
            with torch.no_grad():
                state = torch.tensor(state, dtype=torch.float32).unsqueeze(0).to(device)
                q_values = self.policy_net(state)
                return torch.argmax(q_values).item()  # 利用

    def store_transition(self, state, action, reward, next_state, done):
        self.memory.append((state, action, reward, next_state, done))

    def train(self):
        if len(self.memory) < self.batch_size:
            return
        
        batch = random.sample(self.memory, self.batch_size)
        states, actions, rewards, next_states, dones = zip(*batch)
        
        states = torch.tensor(states, dtype=torch.float32).to(device)
        next_states = torch.tensor(next_states, dtype=torch.float32).to(device)
        actions = torch.tensor(actions).to(device)
        rewards = torch.tensor(rewards).to(device)
        dones = torch.tensor(dones).to(device)
        
        q_values = self.policy_net(states)
        next_q_values = self.target_net(next_states)
        
        target_q_values = rewards + (1 - dones) * self.gamma * next_q_values.max(1)[0]
        
        loss = nn.MSELoss()(q_values.gather(1, actions.unsqueeze(1)), target_q_values.unsqueeze(1))
        
        self.optimizer.zero_grad()
        loss.backward()
        self.optimizer.step()
        
        self.epsilon = max(self.epsilon_min, self.epsilon * self.epsilon_decay)

    def update_target_net(self):
        self.target_net.load_state_dict(self.policy_net.state_dict())

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# 创建游戏环境
env = SnakeGame()
input_shape = (2, env.grid_size, env.grid_size)
n_actions = env.action_space.n

# 创建智能体
agent = Agent(input_shape, n_actions)

num_episodes = 1000
for episode in range(num_episodes):
    state = env.reset()
    state = state.transpose((1, 2, 0))  # 调整为 [height, width, channels]
    done = False
    total_reward = 0
    
    while not done:
        action = agent.select_action(state)
        next_state, reward, done, _ = env.step(action)
        next_state = next_state.transpose((1, 2, 0))  # 确保输入形状为 [height, width, channels]
        
        agent.store_transition(state, action, reward, next_state, done)
        agent.train()
        
        state = next_state
        total_reward += reward

        env.render()

    print(f"Episode {episode + 1}/{num_episodes}, Total Reward: {total_reward}")

    # 每50轮更新一次目标网络
    if (episode + 1) % 50 == 0:
        agent.update_target_net()

env.close()
