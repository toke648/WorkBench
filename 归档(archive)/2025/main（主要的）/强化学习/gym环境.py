import gym
import os
from matplotlib import pyplot as plt

os.environ["SDL_VIDEODRIVER"] = "dummy" # 这个环境是SDL // KMP_DUPLICATE_LIB_OK ：解决多线程问题

# 创建一个游戏环境
env = gym.make('CartPole-v0')

# 初始化游戏
env.reset()

plt.imshow(env.render(mode='rgb_array')) # render() ：返回游戏画面 // mode='rgb_array' ：返回游戏画面的数组
plt.show() # 显示游戏画面

# 关闭游戏
env.close()
