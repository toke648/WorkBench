# 平衡生态系统 v2（捕食者优化 + 感知扩展 + 克隆抑制）
import pygame
import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
import random
from copy import deepcopy

WIDTH, HEIGHT = 700, 700 # 窗口大小
N = 70 # 地图大小
CELL_SIZE = WIDTH // N
pygame.init() # 初始化pygame
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Ecosystem")

x, y = np.linspace(0, N - 1, N), np.linspace(0, N - 1, N) # 生成网格
X, Y = np.meshgrid(x, y)
cx, sigma, move_speed = N // 2, N / 5, 0.1
MOVES = [[1, 0], [-1, 0], [0, 1], [0, -1]] # 移动方向
device = torch.device('cpu') # 设备选择cpu/gpu

# 建立神经网络模型
class PolicyNet(nn.Module): # 策略网络
    """
    总的来说就是：输入是当前状态，输出是下一步的动作
    分别输入四个动作up、down、left、right，然后通过神经网络进行预测，并返回概率(softmax)最大的动作。
    这个神经网络模型的话，属于策略网络，用于预测下一个动作。
    算是一个简单的神经网络，输入为4维向量，输出为4维向量，然后通过softmax进行概率归一化，返回概率最大的动作。

    """
    def __init__(self):
        super().__init__()
        self.fc1 = nn.Linear(9, 32) # 输入9个特征，输出4个动作
        self.fc2 = nn.Linear(32, 4) # 隐藏层32个神经元

    def forward(self, x):
        x = F.relu(self.fc1(x)) # 激活函数
        return F.softmax(self.fc2(x), dim=-1) # 输出动作概率
    


# 创建代理（植物/捕食者）
class Agent:
    """
    代理类，继承自nn.Module
    """
    def __init__(self, kind='plant', parent=None):
        """
        代理初始化
        kind: 代理类型
        parent: 父代理

        """
        self.kind = kind # 植物/捕食者
        self.pos = [np.random.randint(N), np.random.randint(N)] # 随机位置
        self.nutrition = 8.0 if kind == 'plant' else 15.0 # 初始营养
        self.alive = True # 代理是否存活
        self.model = deepcopy(parent.model) if parent else PolicyNet().to(device) # 从父代理中复制模型，模型为自定义的策略网络模型，输入4个参数，输出4个动作概率
        if parent: # 如果有父代理，则进行变异
            self.mutate()
        self.traj = []

    # 代理的决策
    def mutate(self):
        with torch.no_grad(): # 禁用梯度计算
            for param in self.model.parameters():
                if random.random() < 0.1: # 随机突变（表象为做出随机行为）
                    param.add_(torch.randn_like(param) * 0.03) # 添加一个随机向量

    # 代理状态
    def get_state(self, agents, nutrition_field):
        x, y = self.pos # 获取代理位置
        vals = []
        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                nx, ny = x + dx, y + dy
                if 0 <= nx < N and 0 <= ny < N:
                    if self.kind == 'plant':
                        vals.append(nutrition_field[ny, nx])
                    else:
                        vals.append(sum(1 for a in agents if a.kind == 'plant' and a.pos == [nx, ny]))
                else:
                    vals.append(0)
        return torch.tensor(vals, dtype=torch.float32, device=device)
    
    # 获取当前位置的周围格子的信息
    def act(self, agents, nutrition_field):
        """
        获取当前位置的周围格子的信息
        :param agents: 当前位置的周围格子的信息
        :param nutrition_field: 当前位置的周围格子的信息
        :return: 当前位置的周围格子的信息

        """
        state = self.get_state(agents, nutrition_field).unsqueeze(0) # 添加一个维度
        probs = self.model(state).squeeze(0) # 去掉一个维度
        dist = torch.distributions.Categorical(probs) # 创建概率分布
        action = dist.sample()
        log_prob = dist.log_prob(action)
        dx, dy = MOVES[action.item()]
        self.pos[0] = max(0, min(N - 1, self.pos[0] + dx))
        self.pos[1] = max(0, min(N - 1, self.pos[1] + dy))
        self.traj.append(tuple(self.pos))
        if len(self.traj) > 10:
            self.traj.pop(0)
        return log_prob

# 网格颜色
def field_color(value):
    v = max(0, min(value / 10, 1))
    return (int(255 * v), int(165 * v), int(255 * (1 - v)))

# 获取周围营养
def can_clone(agent, agents):
    cx, cy = agent.pos # 当前位置
    return sum(1 for a in agents if abs(a.pos[0] - cx) <= 1 and abs(a.pos[1] - cy) <= 1) < 6

# Agent类在这里被使用，用于创建Agent对象
agents = [Agent('plant') for _ in range(200)] + [Agent('predator') for _ in range(10)] # 初始化 植物：200/捕食者：10
clock = pygame.time.Clock() # 时钟
MAX_AGENT = 400 # 最大数量
running, steps = True, 0

while running: # 运行
    clock.tick(15)
    steps += 1
    for event in pygame.event.get(): # 获取事件
        if event.type == pygame.QUIT: # 退出
            running = False

    cx = (cx + move_speed) % N # 捕食者移动
    nutrition_field = np.exp(-((X - cx) ** 2 + (Y - cx) ** 2) / (2 * sigma ** 2)) * 10.0 # (辐射)营养源

    if steps % 100 == 0: # 每100步
        np_, pr_ = sum(a.kind == 'plant' for a in agents), sum(a.kind == 'predator' for a in agents) # 统计
        print(f"[Step {steps}] Plants: {np_}, Predators: {pr_}") # 输出

    for i in range(N):
        for j in range(N):
            pygame.draw.rect(screen, field_color(nutrition_field[j, i]),
                             pygame.Rect(i * CELL_SIZE, j * CELL_SIZE, CELL_SIZE, CELL_SIZE)) # 画背景

    for agent in agents: # 遍历个体
        if not agent.alive: # 如果个体已死亡，则跳过
            continue

        log_prob = agent.act(agents, nutrition_field) # 获取个体的决策概率
        reward = 0 # 初始化奖励
        if agent.kind == 'plant': # 如果是植物
            agent.nutrition += nutrition_field[agent.pos[1], agent.pos[0]] * 0.05 # 植物获取的能量为0.05
            agent.nutrition -= 0.03 # 植物消耗的能量
        else:
            agent.nutrition -= 0.03 # 捕食者消耗的能量
            prey = next((a for a in agents if a.kind == 'plant' and a.pos == agent.pos and a.alive), None) # 捕食者吃掉植物
            if prey:
                prey.alive = False # 植物死亡
                agent.nutrition += 5.0 # 捕食者吃掉植物获得5.0点能量
                reward += 1.0 # 捕食者吃掉植物奖励1.0分
            else:
                near = sum(1 for a in agents if a.kind == 'plant' and abs(a.pos[0]-agent.pos[0])<=2 and abs(a.pos[1]-agent.pos[1])<=2) # 计算附近有多少只植物
                reward += 0.1 * near # 捕食者附近的植物奖励0.1分

        loss = -log_prob * reward # 计算损失
        agent.model.zero_grad() # 清零梯度
        loss.backward() # 反向传播
        with torch.no_grad(): # 梯度更新
            for param in agent.model.parameters(): # 遍历参数
                param.data -= 1e-3 * param.grad # 更新参数

        if agent.kind == 'plant' and agent.nutrition >= 25 and can_clone(agent, agents): # 如果是植物且 nutrition >= 25 且可以克隆
            agent.nutrition -= 20 # 克隆
            agents.append(Agent('plant', parent=agent))
        elif agent.kind == 'predator' and agent.nutrition >= 30 and can_clone(agent, agents): # 如果是猎物且 nutrition >= 30 且可以克隆
            agent.nutrition -= 20
            agents.append(Agent('predator', parent=agent))

        if agent.nutrition <= 0: # 如果 nutrition <= 0 则死亡
            agent.alive = False

    agents = [a for a in agents if a.alive] # 筛选存活的
    if len(agents) > MAX_AGENT: # 如果数量超过最大数量则
        agents = sorted(agents, key=lambda a: a.nutrition, reverse=True)[:MAX_AGENT] # 按 nutrition 排序

    for agent in agents: # 绘制
        color = (0, 255, 0) if agent.kind == 'plant' else (128, 0, 128) # 颜色
        for pt in agent.traj:
            pygame.draw.circle(screen, (200, 200, 200),
                               (pt[0] * CELL_SIZE + CELL_SIZE // 2, pt[1] * CELL_SIZE + CELL_SIZE // 2), 2)
        pygame.draw.circle(screen, color,
                           (agent.pos[0] * CELL_SIZE + CELL_SIZE // 2, agent.pos[1] * CELL_SIZE + CELL_SIZE // 2),
                           CELL_SIZE // 2)

    pygame.display.flip() # 刷新屏幕

pygame.quit() # 退出游戏