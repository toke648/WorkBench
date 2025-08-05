# # move_mouse.py
# import pyautogui
# pyautogui.moveTo(900, 65, duration=2)  # Move to (900, 500) over 2 seconds

# pyautogui.click()

# pyautogui.moveTo(200, 300, duration=1)  # Move to (200, 300) over 1 second


# import torch
# import torch.nn as nn
# import torch.optim as optim

# # 简单RNN作为动力学模型
# class Dynamics(nn.Module):
#     def __init__(self, input_size=1, hidden_size=3):
#         super().__init__()
#         self.rnn = nn.RNN(input_size, hidden_size, batch_first=True)
#         self.decoder = nn.Linear(hidden_size, input_size)

#     def forward(self, x, h=None):
#         out, h = self.rnn(x, h)
#         pred = self.decoder(out)
#         return pred, h

# # 初始化模型与优化器
# model = Dynamics()
# print(model)
# opt = optim.Adam(model.parameters(), lr=1e-3)

# # 模拟连续输入流
# for step in range(1000):
#     inp = torch.randn(1,1,1)  # 当前时刻输入（噪声）
#     target = torch.randn(1,1,1)  # 下一时刻输入（也用噪声模拟环境演化）
#     pred, h = model(inp)
#     loss = (pred - target).pow(2).mean()
#     print(f"Step {step}, Loss: {loss.item()}")
#     # 反向传播与优化
#     loss.backward()
#     opt.step()
#     opt.zero_grad()



# import numpy as np

# class Env:
#     def __init__(self):
#         self.nutrition = 10.0  # 初始营养
#         self.noise_var = 0.5

#     def get_observation(self):
#         noise = np.random.randn() * self.noise_var
#         return self.nutrition + noise

#     def step(self, action):
#         # action 可以是 "eat"(0) 或者 "do nothing"(1)
#         if action == 0:  # 吃东西
#             self.nutrition += 2.0
#         # 营养随时间减少
#         self.nutrition -= 1.0

#     def is_dead(self):
#         return self.nutrition <= 0

# # 模型逻辑：当感觉营养很低时就吃东西
# env = Env()
# step = 0
# while not env.is_dead() and step < 100:
#     obs = env.get_observation()
#     # 策略：当感受到的营养< 5 时吃东西
#     action = 0 if obs < 5 else 1
#     env.step(action)
#     print(f"Step {step}: obs={obs:.2f}, nutrition={env.nutrition:.2f}, action={action}")
#     step += 1

# print("Dead" if env.is_dead() else "Survived!")


