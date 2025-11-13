import gym
import time
import numpy as np
import torch
import random
from gym.wrappers import GrayScaleObservation
from nes_py.wrappers import JoypadSpace
from gym_super_mario_bros.actions import SIMPLE_MOVEMENT
from gym_super_mario_bros import SuperMarioBrosEnv

# 检查 OpenGL 兼容性问题
try:
    import pygame
except ImportError:
    print("缺少 pygame，尝试安装：pip install pygame")

# 创建马里奥环境
env = gym.make("SuperMarioBros-1-1-v0", apply_api_compatibility=True, render_mode="human")
env = JoypadSpace(env, SIMPLE_MOVEMENT)  # 约束动作空间
env = GrayScaleObservation(env, keep_dim=True)  # 灰度化

# 运行测试
state = env.reset()
done = False

for _ in range(1000):
    env.render()
    time.sleep(0.01)  # 降低 CPU 占用
    action = env.action_space.sample()  # 采样随机动作
    state, reward, done, truncated, info = env.step(action)

    if done:
        state = env.reset()

env.close()
