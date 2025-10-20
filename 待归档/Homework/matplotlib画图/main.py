import matplotlib.pyplot as plt
import numpy as np

# plt.rcParams["line.linestyle"] = "--"


plt.figure(figsize=(10, 5), facecolor="green") # 设置图形大小和分辨率

plt.title("14days temperature of beijing") # 14天北京气温
plt.xlabel("date") # 日期
plt.ylabel("temperature") # 温度

# 12个
x = np.arange(1, 13) # 1-12月
# 10 - 50的12个随机数
y = np.random.randint(10, 50, 12) # 温度

plt.plot(x, y, '-.o', linewidth=2) # 绘制折线图

plt.show() # 显示图形