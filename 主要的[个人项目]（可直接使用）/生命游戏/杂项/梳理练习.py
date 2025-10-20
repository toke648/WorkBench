import pygame
import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
import random
from copy import deepcopy # 克隆抑制 + 感知扩展

WIDTH, HEIGHT = 700,700 # 窗口大小
N = 70 # 地图大小
CELL_SIZE = WIDTH // N
pygame.init() # 初始化pygame
screen = pygame.display.set_mode((WIDTH, HEIGHT))  # 设置窗口大小
pygame.display.set_caption("Ecosystem") # 设置窗口标题

# 简易的贪吃蛇实现
x, y = np.linspace(0, N - 1, N), np.linspace(0, N - 1, N) # 生成网格
X, Y = np.meshgrid(x, y) # 生成网格坐标

class Agent:
    def __init__(self, kind='plant', parent=None):
        self.kind = kind
        self.pos = [np.random.randint(N), np.random.randint(N)]
        self.nutrition = 8.0 if kind == 'plant' else 15.0
        self.alive = True
        self.model = deepcopy(parent.model) if parent else PolicyNet().to(device)
        self.traj = []

        if parent:  # 如果有父代理，则进行变异
            self.mutate()
    def mutate(self):
        """
        变异函数，随机改变模型参数
        """
        for param in self.model.parameters():
            if random.random() < 0.1:
                param.data += torch.randn_like(param) * 0.1
        self.traj.append(self.pos.copy())
        self.traj.append(self.pos.copy())