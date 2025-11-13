import gym
import random
import torch
import numpy as np
from nes_py.wrappers import JoypadSpace
from gym_super_mario_bros.actions import SIMPLE_MOVEMENT
from gym.wrappers import GrayScaleObservation

# 自定义 Mario 速度加倍
class MaxAndSkipEnv(gym.Wrapper):
    def __init__(self, env, skip=4):
        super().__init__(env)
        self._skip = skip

    def step(self, action):
        total_reward = 0.0
        for _ in range(self._skip):
            state, reward, done, truncated, info = self.env.step(action)
            total_reward += reward
            if done:
                break
        return state, total_reward, done, truncated, info

# Mario 运行环境
env = gym.make("SuperMarioBros-1-1-v0", apply_api_compatibility=True, render_mode=None)
env = JoypadSpace(env, SIMPLE_MOVEMENT)
env = MaxAndSkipEnv(env, skip=4)  # 让 Mario 速度 X4
env = GrayScaleObservation(env, keep_dim=True)  # 变成黑白，加快计算

# 训练循环
for episode in range(10):
    state, _ = env.reset()
    total_reward = 0

    while True:
        action = env.action_space.sample()  # 随机行动
        state, reward, done, truncated, info = env.step(action)

        total_reward += reward
        if done:
            break

    print(f"Episode {episode}, Total Reward: {total_reward}")
env.close()
