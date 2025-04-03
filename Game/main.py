import numpy as np
import keyboard


# n = np.ones(12)
n = np.zeros(16)
N = n.reshape(4, 4)
print(N)
print(type(N))
nn = list(N)

print(nn)


# n = [0,0,0,0,
#      0,0,0,0,
#      0,0,0,0,
#      0,0,0,0]
#
# ln = [[0,0,0,0],
#       [0,0,0,0],
#       [0,0,0,0],
#       [0,0,0,0]]

print(N)

i = 2
j = 3
print(i)
print(j)
print(N)






"""
def on_key_press(event):
#     print(event)
#     print(f"Key {event.name} pressed")
# 
# 
# # 监听键盘事件，指定回调函数
# keyboard.hook(on_key_press)
# keyboard.wait('esc')  # 等待直到按下 Esc 键来停止监听
"""


size = 16
play = 'o'
refresh = ' '
n = np.zeros(16)
N = np.full(size, size, refresh)
N[i // 2][j // 2 ] = play
print(N)

# 定义一个回调函数，当按键事件发生时调用
def on_key_press(event):
    # print(event)
    # print(f"Key {event.name} pressed")
    global i, j

    if event.name == 'up':
        N[i][j] = 0
        if i > 0:
            i -= 1
            N[i][j] = 1
            print(N)
    if event.name == 'down':
        N[i][j] = 0
        if i < size - 1:
            i += 1
            N[i][j] = 1
            print(N)
    if event.name == 'left':
        if j > 0:
            j -= 1

    if event.name == 'right':
        if j < size - 1:
            j += 1

    N[i][j] = refresh
    print(N)


# 监听键盘事件，指定回调函数
keyboard.hook(on_key_press)
keyboard.wait('esc')  # 等待直到按下 Esc 键来停止监听
