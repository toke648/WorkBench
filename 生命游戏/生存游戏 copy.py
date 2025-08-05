import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
import random

# 环境大小
N = 50
POP_SIZE = 50 # 种群大小
MAX_STEPS_PER_GEN = 100 # 每代最大步数
MAX_GENERATIONS = 500 # 训练代数

# 初始化营养场
x = np.linspace(0, N-1, N)
y = np.linspace(0, N-1, N)
X, Y = np.meshgrid(x, y)
cx, cy = N//2, N//2
sigma = N/5
nutrition_field = np.exp(-((X-cx)**2+(Y-cy)**2)/(2*sigma**2)) * 10.0

# 网络定义
class AgentNet(nn.Module):
    def __init__(self, input_size=4, hidden_size=16, output_size=4):
        super(AgentNet, self).__init__()
        self.fc1 = nn.Linear(input_size, hidden_size)
        self.fc2 = nn.Linear(hidden_size, output_size)

    def forward(self, x):
        x = F.relu(self.fc1(x))
        return F.softmax(self.fc2(x), dim=-1)

# Agent 定义
class Agent:
    def __init__(self):
        self.pos = [np.random.randint(N), np.random.randint(N)]
        self.nutrition = 10.0 # 初始营养
        self.alive = True

def get_surrounding_nutrition_batch(agents, field):
    vals = []
    for agent in agents:
        x, y = agent.pos
        vals.append([
            field[y, x+1] if x+1<N else 0,
            field[y, x-1] if x-1>=0 else 0,
            field[y+1, x] if y+1<N else 0,
            field[y-1, x] if y-1>=0 else 0
        ])
    return torch.tensor(vals, dtype=torch.float32)

# 遗传算法选择与变异
def evolve_population(model, agents, mutate_rate=0.2):
    # 按营养排序
    agents.sort(key=lambda a: a.nutrition, reverse=True)
    survivors = agents[:len(agents)//2]

    # 克隆模型权重
    state_dict = model.state_dict()

    new_agents = []
    while len(survivors) + len(new_agents) < len(agents):
        child = Agent()
        # 克隆网络权重并变异
        new_state = {}
        for k, v in state_dict.items():
            new_state[k] = v + mutate_rate * torch.randn_like(v)
        model.load_state_dict(new_state)
        new_agents.append(child)

    return survivors + new_agents

# 初始化
model = AgentNet()
agents = [Agent() for _ in range(POP_SIZE)]
MOVES = torch.tensor([[1,0], [-1,0], [0,1], [0,-1]])

# 训练迭代
for generation in range(MAX_GENERATIONS):
    for step in range(MAX_STEPS_PER_GEN):
        # 获取输入并前向计算
        inputs = get_surrounding_nutrition_batch(agents, nutrition_field)
        probs = model(inputs)  # shape (pop_size, 4)
        moves = torch.multinomial(probs, num_samples=1).squeeze(1)

        for i, agent in enumerate(agents):
            if not agent.alive:
                continue
            dx, dy = MOVES[moves[i]].tolist()
            agent.pos[0] = max(0, min(N-1, agent.pos[0]+dx))
            agent.pos[1] = max(0, min(N-1, agent.pos[1]+dy))
            # 消耗能量，获取营养
            sensed = nutrition_field[agent.pos[1], agent.pos[0]] + np.random.randn()*0.1
            agent.nutrition -= 0.3
            agent.nutrition += sensed * 0.05
            if agent.nutrition <= 0:
                agent.nutrition = 0
                agent.alive = False

    agents = evolve_population(model, agents, mutate_rate=0.05) # 遗传算法选择与变异
    avg_nutrition = sum(a.nutrition for a in agents)/len(agents)
    print(f"Generation {generation}: avg_nutrition={avg_nutrition:.2f}")

# 保存模型权重
torch.save(model.state_dict(), "final_model.pt")
print("Training complete. Model saved to final_model.pt")


# # 测试模型
# model.load_state_dict(torch.load("final_model.pt"))
# model.eval()
# # 测试环境
# test_agents = [Agent() for _ in range(POP_SIZE)]
# test_field = np.zeros((N, N))
# test_field = evolve_population(test_agents, retain_fraction=0.5, mutate_rate=0.1)
# # 测试迭代
# for step in range(100):
#     # 测试环境更新
#     for agent in test_agents:
#         if not agent.alive:
#             continue
#         inputs = get_surrounding_nutrition_batch([agent], test_field)
#         probs = model(inputs)
#         move = torch.argmax(probs).item()
#         dx, dy = MOVES[move].tolist()
#         agent.pos[0] = max(0, min(N-1, agent.pos[0]+dx))





