# 可持续平衡生态系统（支持10分钟以上运行，带演化策略 + 可视化轨迹）
import pygame
import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
import random
from copy import deepcopy

# 游戏设置
WIDTH, HEIGHT = 700, 700
N = 70
CELL_SIZE = WIDTH // N
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Ecosystem")

# 营养源设置
x, y = np.linspace(0, N - 1, N), np.linspace(0, N - 1, N)
X, Y = np.meshgrid(x, y)
cx, sigma, move_speed = N // 2, N / 5, 0.1

# 四方向
MOVES = [[1, 0], [-1, 0], [0, 1], [0, -1]]
device = torch.device('cpu')

# 策略网络
class PolicyNet(nn.Module):
    def __init__(self):
        super().__init__()
        self.fc1 = nn.Linear(4, 16)
        self.fc2 = nn.Linear(16, 4)

    def forward(self, x):
        x = F.relu(self.fc1(x))
        return F.softmax(self.fc2(x), dim=-1)

# 个体定义
class Agent:
    def __init__(self, kind='plant', parent=None):
        self.kind = kind
        self.pos = [np.random.randint(N), np.random.randint(N)]
        self.nutrition = 8.0 if kind == 'plant' else 15.0
        self.alive = True
        self.model = deepcopy(parent.model) if parent else PolicyNet().to(device)
        if parent:
            self.mutate()
        self.traj = []

    def mutate(self):
        with torch.no_grad():
            for param in self.model.parameters():
                if random.random() < 0.1:
                    param.add_(torch.randn_like(param) * 0.03)

    def get_state(self, agents, nutrition_field):
        x, y = self.pos
        vals = []
        for dx, dy in MOVES:
            nx, ny = x + dx, y + dy
            if 0 <= nx < N and 0 <= ny < N:
                if self.kind == 'plant':
                    vals.append(nutrition_field[ny, nx])
                else:
                    vals.append(sum(1 for a in agents if a.kind == 'plant' and a.pos == [nx, ny]))
            else:
                vals.append(0)
        return torch.tensor(vals, dtype=torch.float32, device=device)

    def act(self, agents, nutrition_field):
        state = self.get_state(agents, nutrition_field).unsqueeze(0)
        probs = self.model(state).squeeze(0)
        dist = torch.distributions.Categorical(probs)
        action = dist.sample()
        log_prob = dist.log_prob(action)
        dx, dy = MOVES[action.item()]
        self.pos[0] = max(0, min(N - 1, self.pos[0] + dx))
        self.pos[1] = max(0, min(N - 1, self.pos[1] + dy))
        self.traj.append(tuple(self.pos))
        if len(self.traj) > 10:
            self.traj.pop(0)
        return log_prob

# 工具函数
def field_color(value):
    v = max(0, min(value / 10, 1))
    return (int(255 * v), int(165 * v), int(255 * (1 - v)))

# 初始种群
agents = [Agent('plant') for _ in range(200)] + [Agent('predator') for _ in range(10)]
clock = pygame.time.Clock()
MAX_AGENT = 400
running = True
steps = 0

while running:
    clock.tick(15)
    steps += 1
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # 移动营养源
    cx = (cx + move_speed) % N
    nutrition_field = np.exp(-((X - cx) ** 2 + (Y - cx) ** 2) / (2 * sigma ** 2)) * 10.0

    # 输出统计信息
    if steps % 100 == 0:
        num_plants = sum(1 for a in agents if a.kind == 'plant')
        num_preds = sum(1 for a in agents if a.kind == 'predator')
        print(f"[Step {steps}] Plants: {num_plants}, Predators: {num_preds}")

    # 画背景
    for i in range(N):
        for j in range(N):
            pygame.draw.rect(screen, field_color(nutrition_field[j, i]),
                             pygame.Rect(i * CELL_SIZE, j * CELL_SIZE, CELL_SIZE, CELL_SIZE))

    # 更新个体
    for agent in agents:
        if not agent.alive:
            continue
        log_prob = agent.act(agents, nutrition_field)
        reward = 0
        if agent.kind == 'plant':
            agent.nutrition += nutrition_field[agent.pos[1], agent.pos[0]] * 0.05
            agent.nutrition -= 0.03
        else:
            agent.nutrition -= 0.05
            prey = next((a for a in agents if a.kind == 'plant' and a.pos == agent.pos and a.alive), None)
            if prey:
                prey.alive = False
                agent.nutrition += 1.0
                reward = 1.0
            else:
                reward = 0.05 * sum(
                    1 for a in agents if a.kind == 'plant' and abs(a.pos[0] - agent.pos[0]) <= 1 and abs(a.pos[1] - agent.pos[1]) <= 1)

        # 策略更新
        loss = -log_prob * reward
        agent.model.zero_grad()
        loss.backward()
        with torch.no_grad():
            for param in agent.model.parameters():
                param.data -= 1e-3 * param.grad

        # 克隆条件
        if agent.kind == 'plant' and agent.nutrition >= 25:
            agent.nutrition -= 20
            agents.append(Agent('plant', parent=agent))
        elif agent.kind == 'predator' and agent.nutrition >= 30:
            agent.nutrition -= 20
            agents.append(Agent('predator', parent=agent))

        if agent.nutrition <= 0:
            agent.alive = False

    # 种群控制
    agents = [a for a in agents if a.alive]
    if len(agents) > MAX_AGENT:
        agents = sorted(agents, key=lambda a: a.nutrition, reverse=True)[:MAX_AGENT]

    # 画个体 + 轨迹
    for agent in agents:
        color = (0, 255, 0) if agent.kind == 'plant' else (128, 0, 128)
        for pt in agent.traj:
            pygame.draw.circle(screen, (200, 200, 200),
                               (pt[0] * CELL_SIZE + CELL_SIZE // 2, pt[1] * CELL_SIZE + CELL_SIZE // 2), 2)
        pygame.draw.circle(screen, color,
                           (agent.pos[0] * CELL_SIZE + CELL_SIZE // 2, agent.pos[1] * CELL_SIZE + CELL_SIZE // 2),
                           CELL_SIZE // 2)

    pygame.display.flip()

pygame.quit()
