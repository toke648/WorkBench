import gym
import time
import random
import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
from collections import deque
from gym.wrappers import GrayScaleObservation
from nes_py.wrappers import JoypadSpace
from gym_super_mario_bros.actions import SIMPLE_MOVEMENT

# 1. 创建马里奥环境
env = gym.make("SuperMarioBros-1-1-v0", apply_api_compatibility=True, render_mode="human")
env = JoypadSpace(env, SIMPLE_MOVEMENT)  # 约束动作空间
env = GrayScaleObservation(env, keep_dim=True)  # 灰度化

# 2. 定义 DQN 神经网络
class MarioDQN(nn.Module):
    def __init__(self, input_shape, num_actions):
        super(MarioDQN, self).__init__()
        self.conv = nn.Sequential(
            nn.Conv2d(input_shape[0], 32, kernel_size=8, stride=4),
            nn.ReLU(),
            nn.Conv2d(32, 64, kernel_size=4, stride=2),
            nn.ReLU(),
            nn.Conv2d(64, 64, kernel_size=3, stride=1),
            nn.ReLU()
        )
        self.fc = nn.Sequential(
            nn.Linear(64 * 7 * 7, 512),
            nn.ReLU(),
            nn.Linear(512, num_actions)
        )
    
    def forward(self, x):
        x = self.conv(x)
        x = x.view(x.size(0), -1)
        return self.fc(x)

# 3. 初始化 DQN 模型
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model = MarioDQN((1, 84, 84), len(SIMPLE_MOVEMENT)).to(device)
optimizer = optim.Adam(model.parameters(), lr=1e-4)
loss_fn = nn.MSELoss()

# 4. 经验回放（Replay Buffer）
class ReplayBuffer:
    def __init__(self, capacity):
        self.buffer = deque(maxlen=capacity)

    def push(self, state, action, reward, next_state, done):
        self.buffer.append((state, action, reward, next_state, done))

    def sample(self, batch_size):
        return random.sample(self.buffer, batch_size)

buffer = ReplayBuffer(10000)

# 5. 训练循环
epsilon = 1.0  # 探索率
gamma = 0.99  # 折扣因子

for episode in range(1000):  # 训练 1000 局
    state, _ = env.reset()
    state = np.array(state, dtype=np.float32) / 255.0  # 归一化
    done = False
    total_reward = 0

    while not done:
        env.render()
        time.sleep(0.01)  # 降低 CPU 负载
        
        # ε-greedy 选择动作
        if random.random() < epsilon:
            action = env.action_space.sample()  # 随机探索
        else:
            state_tensor = torch.tensor(state, device=device).unsqueeze(0)
            with torch.no_grad():
                action = model(state_tensor).argmax().item()
        
        # 执行动作
        next_state, reward, done, truncated, info = env.step(action)
        next_state = np.array(next_state, dtype=np.float32) / 255.0  # 归一化

        buffer.push(state, action, reward, next_state, done)
        state = next_state
        total_reward += reward

    # 训练 DQN
    if len(buffer.buffer) > 1000:
        batch = buffer.sample(32)
        state_batch = torch.tensor([b[0] for b in batch], dtype=torch.float32, device=device)
        action_batch = torch.tensor([b[1] for b in batch], device=device)
        reward_batch = torch.tensor([b[2] for b in batch], dtype=torch.float32, device=device)
        next_state_batch = torch.tensor([b[3] for b in batch], dtype=torch.float32, device=device)
        done_batch = torch.tensor([b[4] for b in batch], dtype=torch.float32, device=device)

        q_values = model(state_batch).gather(1, action_batch.unsqueeze(1)).squeeze()
        next_q_values = model(next_state_batch).max(1)[0]
        expected_q_values = reward_batch + (1 - done_batch) * gamma * next_q_values

        loss = loss_fn(q_values, expected_q_values.detach())
        optimizer.zero_grad()
        loss.backward()
        optimizer.step()

    # 逐步降低探索率
    epsilon = max(0.1, epsilon * 0.995)

    print(f"Episode {episode}, Total Reward: {total_reward}")

    # 每 50 局保存模型
    if episode % 50 == 0:
        torch.save(model.state_dict(), "mario_dqn.pth")

env.close()
