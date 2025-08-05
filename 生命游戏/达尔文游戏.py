import pygame
import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
import torch.nn.functional as F
import random

pygame.init()
WIDTH, HEIGHT = 500, 500
N = 50
CELL_SIZE = WIDTH // N
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Predator-Prey Ecosystem")

# 环境
x = np.linspace(0, N-1, N)
y = np.linspace(0, N-1, N)
X, Y = np.meshgrid(x, y)
cx = N//2
sigma = N/5
move_speed = 0.1 # 营养源移动速度
nutrition_field = np.exp(-((X-cx)**2+(Y-cx)**2)/(2*sigma**2)) * 10.0 # 初始化营养场

# 颜色
def field_color(value):
    v = max(0, min(value/10,1))
    r = int(255*(v)) 
    g = int(165*(v)) 
    b = int(255*(1-v))
    return (r, g, b)

# 策略网络
class PolicyNet(nn.Module):
    def __init__(self):
        super().__init__()
        self.fc1 = nn.Linear(4, 16)
        self.fc2 = nn.Linear(16, 4)
    def forward(self, x):
        x = F.relu(self.fc1(x))
        return F.softmax(self.fc2(x), dim=-1)

device = torch.device('cpu')
model = PolicyNet().to(device)
optimizer = optim.Adam(model.parameters(), lr=1e-3)

# Agent类
class Agent:
    def __init__(self, kind='plant'):
        self.kind = kind  # 'plant' or 'predator'
        self.pos = [np.random.randint(N), np.random.randint(N)]
        self.nutrition = 8.0 if kind == 'plant' else 10.0 # 初始营养
        self.alive = True

# 四方向
MOVES = np.array([[1,0], [-1,0], [0,1], [0,-1]])

def get_state(agent, agents):
    x, y = agent.pos
    vals = []
    for dx, dy in MOVES:
        nx, ny = x+dx, y+dy
        if 0 <= nx < N and 0 <= ny < N:
            if agent.kind == 'plant':
                vals.append(nutrition_field[ny, nx])
            else:
                # 捕食者感知邻近是否有猎物
                vals.append(sum(1 for a in agents if a.kind=='plant' and a.pos == [nx, ny]))
        else:
            vals.append(0)
    return torch.tensor(vals, dtype=torch.float32, device=device)

# 初始化群体
agents = [Agent('plant') for _ in range(100)] + [Agent('predator') for _ in range(5)] # 50植物和5捕食者

clock = pygame.time.Clock()

running = True
while running:
    clock.tick(15)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # 移动营养源
    cx = (cx + move_speed) % N
    nutrition_field = np.exp(-((X-cx)**2+(Y-cx)**2)/(2*sigma**2)) * 10.0 # 更新营养场

    # 环境显示
    for i in range(N):
        for j in range(N):
            color = field_color(nutrition_field[j,i])
            rect = pygame.Rect(i*CELL_SIZE, j*CELL_SIZE, CELL_SIZE, CELL_SIZE)
            pygame.draw.rect(screen, color, rect)

    # 更新个体
    for agent in agents:
        if not agent.alive:
            continue
        state = get_state(agent, agents).unsqueeze(0)
        probs = model(state).squeeze(0)
        dist = torch.distributions.Categorical(probs)
        action = dist.sample()
        log_prob = dist.log_prob(action)

        dx, dy = MOVES[action.item()]
        agent.pos[0] = max(0, min(N-1, agent.pos[0]+dx))
        agent.pos[1] = max(0, min(N-1, agent.pos[1]+dy))

        # 营养逻辑
        """
        每个个体都有自己的行为逻辑，并不共享学习到的内容，但克隆体能够继承被克隆个体所学习到的经验，并且每个个体都有小概率获得突变出新的行为逻辑。
        克隆体，生成在被克隆体的旁边，并继承被克隆体的行为逻辑。
        非捕食者：
        非捕食者行为属性：
        生命值：8
        消耗能量：-0.03
        获取能量：+0.05

        捕食者：
        能量消耗大，需要不停的获取食物
        非捕食者行为属性：
        生命值：10
        消耗能量：-0.05
        获取能量：+0.1
        """

        reward = 0
        if agent.kind == 'plant':
            agent.nutrition += nutrition_field[agent.pos[1], agent.pos[0]] * 0.05 # 植物获取营养
            agent.nutrition -= 0.03 # 植物消耗能量
        else:  # predator
            agent.nutrition -= 0.1 # 捕食者消耗能量
            prey = next((a for a in agents if a.kind=='plant' and a.pos==agent.pos), None)
            if prey:
                prey.alive = False
                agent.nutrition += 5.0 # 捕食成功获得营养
                reward += 1 # 捕食奖励

        # 策略梯度更新
        loss = -log_prob * reward
        optimizer.zero_grad()
        loss.backward()
        optimizer.step()

        # 克隆
        if agent.nutrition >= 20: # 营养足够克隆
            agent.nutrition -= 15 # 克隆消耗
            agents.append(Agent(agent.kind))
        
        # 捕食者克隆
        if agent.kind == 'predator':
            if agent.nutrition >= 50: # 营养足够克隆
                agent.nutrition -= 40 # 克隆消耗
                agents.append(Agent('predator'))

        if agent.nutrition <= 0: # 死亡
            agent.alive = False

    # 移除死掉个体
    agents = [a for a in agents if a.alive]

    # 绘制
    for agent in agents:
        color = (0,255,0) if agent.kind=='plant' else (128,0,128)
        pygame.draw.circle(screen, color,
                           (agent.pos[0]*CELL_SIZE+CELL_SIZE//2, agent.pos[1]*CELL_SIZE+CELL_SIZE//2),
                           CELL_SIZE//2)
    pygame.display.flip()

pygame.quit()
