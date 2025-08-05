import pygame
import numpy as np
import sys
import random

pygame.init()

WIDTH, HEIGHT = 500, 500
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Multi-Agent Nutrition Evolution")

N = 50
cell_size = WIDTH // N

x = np.linspace(0, N-1, N)
y = np.linspace(0, N-1, N)
X, Y = np.meshgrid(x, y)
cx, cy = N//2, N//2
sigma = N/5
nutrition_field = np.exp(-((X-cx)**2+(Y-cy)**2)/(2*sigma**2)) * 10.0

# 颜色映射函数
def nutrition_to_color(nutrition, max_nutrition=10.0):
    ratio = max(0, min(nutrition / max_nutrition, 1))  # 限制 ratio 在 0~1
    r = int(255 * (1 - ratio))
    g = int(255 * ratio)
    b = 0
    return (r, g, b)


def field_color(value):
    v = max(0, min(value/10,1))
    if v < 0.5:
        r = int(255 * (v*2))
        g = int(165 * (v*2))
        b = int(255 * (1 - v*2))
    else:
        r = 255
        g = int(165 + (90 * (v-0.5)*2))
        b = 0
    return (r, g, b)

def draw_field():
    for i in range(N):
        for j in range(N):
            color = field_color(nutrition_field[j,i])
            rect = pygame.Rect(i*cell_size, j*cell_size, cell_size, cell_size)
            pygame.draw.rect(screen, color, rect)

# 简单神经网络类，输入8维(周围8格营养)，输出4维(四方向概率)
class SimpleNN:
    def __init__(self):
        self.W = np.random.randn(4,4) * 0.5
        self.b = np.zeros(4)
    def forward(self, x):
        z = x @ self.W + self.b
        e = np.exp(z - np.max(z))
        return e / e.sum()
    
    def mutate(self, rate=0.1):
        self.W += np.random.randn(*self.W.shape) * rate
        self.b += np.random.randn(*self.b.shape) * rate

# 方向偏移
MOVES = [(1,0), (-1,0), (0,1), (0,-1)]

class Agent:
    def __init__(self):
        self.pos = [np.random.randint(N), np.random.randint(N)]
        self.nutrition = 10.0
        self.net = SimpleNN()
        print(self.net.W) # 打印初始权重
        self.alive = True
    
    def get_surrounding_nutrition(self, field):
        vals = []
        x,y = self.pos
        for dx, dy in MOVES:
            nx, ny = x + dx, y + dy
            if 0 <= nx < N and 0 <= ny < N:
                vals.append(field[ny,nx])
            else:
                vals.append(0)
        return np.array(vals)
    
    def decide_move(self, field):
        if not self.alive:
            return self.pos
        inputs = self.get_surrounding_nutrition(field)
        probs = self.net.forward(inputs)
        move_idx = np.random.choice(4, p=probs)
        dx, dy = MOVES[move_idx]
        new_x = max(0, min(N-1, self.pos[0] + dx))
        new_y = max(0, min(N-1, self.pos[1] + dy))
        return [new_x, new_y]
    
    def step(self, field):
        if not self.alive:
            return
        self.pos = self.decide_move(field)
        sensed = field[self.pos[1], self.pos[0]] + np.random.randn()*0.1
        self.nutrition -= 0.3
        self.nutrition += sensed * 0.05
        if self.nutrition <= 0:
            self.nutrition = 0
            self.alive = False

# 遗传选择与繁殖
def evolve_population(pop, retain_fraction=0.5, mutate_rate=0.1):
    # 按营养排序，保留top retain_fraction
    pop = sorted(pop, key=lambda a: a.nutrition, reverse=True)
    retain_len = int(len(pop)*retain_fraction)
    survivors = pop[:retain_len]
    
    # 繁殖，简单复制+变异，补齐到原始大小
    children = []
    while len(survivors) + len(children) < len(pop):
        parent = random.choice(survivors)
        child = Agent()
        # 复制神经网络权重
        child.net.W = np.copy(parent.net.W)
        child.net.b = np.copy(parent.net.b)
        # 变异
        child.net.mutate(rate=mutate_rate)
        children.append(child)
    return survivors + children

POP_SIZE = 20
agents = [Agent() for _ in range(POP_SIZE)]

clock = pygame.time.Clock()
generation = 0
step_counter = 0
max_steps_per_gen = 200

running = True
while running:
    clock.tick(15)  # FPS
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    if step_counter >= max_steps_per_gen:
        generation += 1
        agents = evolve_population(agents)
        step_counter = 0
        print(f"Generation {generation} evolved")

    # 更新所有agent
    for agent in agents:
        agent.step(nutrition_field)

    # 绘制环境和agent
    draw_field()
    for agent in agents:
        color = nutrition_to_color(agent.nutrition)
        pygame.draw.circle(screen, color,
                           (agent.pos[0]*cell_size + cell_size//2, agent.pos[1]*cell_size + cell_size//2),
                           cell_size//2)
    pygame.display.flip()
    step_counter += 1

pygame.quit()
sys.exit()
