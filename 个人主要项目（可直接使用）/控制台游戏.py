# import numpy as np
# import keyboard
# import time
# import threading
# import os
#
# # 在函数外部初始化 i 和 j，以便保持其值
# i = 3
# j = 3
# size_left = 16
# size_right = 18
# play = 'o'
# refresh = ' '
# N = np.full((size_left, size_right), refresh)
# N[i][j] = play
#
# # 用于标记按键状态，防止重复触发
# key_pressed = {'up': False, 'down': False, 'left': False, 'right': False}
#
# def clear_console():
#     """清除控制台输出"""
#     os.system('cls' if os.name == 'nt' else 'clear')
#
# def print_matrix():
#     """打印当前矩阵"""
#     clear_console()
#     print(N)
#
# def move():
#     """持续移动矩阵中的1，直到按键松开"""
#     while True:
#         for key in key_pressed:
#             if key_pressed[key]:
#                 process_move(key)
#         time.sleep(0.05)  # 调整休眠时间以提高响应速度
#
# def process_move(direction):
#     global i, j, refresh
#     N[i][j] = refresh  # 清除当前位置
#     if direction == 'up' and i > 0:
#         i -= 1  # 向上移动
#     elif direction == 'down' and i < size_left - 1:
#         i += 1  # 向下移动
#     elif direction == 'left' and j > 0:
#         j -= 1  # 向左移动
#     elif direction == 'right' and j < size_right - 1:
#         j += 1  # 向右移动
#     N[i][j] = play  # 设置新位置
#     print_matrix()  # 打印矩阵
#
# def on_key_press(event):
#     if event.name in key_pressed:
#         key_pressed[event.name] = True  # 标记按键为按下
#
# def on_key_release(event):
#     if event.name in key_pressed:
#         key_pressed[event.name] = False  # 标记按键为松开
#
# # 启动一个线程以持续处理移动
# movement_thread = threading.Thread(target=move, daemon=True)
# movement_thread.start()
#
# # 监听键盘按下和释放事件
# keyboard.hook(on_key_press)
# keyboard.on_release(on_key_release)  # 处理键释放事件
# keyboard.wait('esc')  # 等待直到按下 Esc 键来停止监听




# import numpy as np
# import keyboard
# import time
# import threading
#
# # 在函数外部初始化 i 和 j，以便保持其值
# i = 3
# j = 3
# size_left = 16
# size_right = 18
# play = 'o'
# refresh = ' '
# N = np.full((size_left, size_right), refresh)
# N[i][j] = play
#
# # 用于标记按键状态，防止重复触发
# key_pressed = {'up': False, 'down': False, 'left': False, 'right': False}
#
# def move():
#     """持续移动矩阵中的1，直到按键松开"""
#     while True:
#         for key in key_pressed:
#             if key_pressed[key]:
#                 process_move(key)
#         time.sleep(0.1)  # 休眠以控制移动速度
#
# def process_move(direction):
#     global i, j, refresh
#     N[i][j] = refresh # 清除当前位置
#     if direction == 'up' and i > 0:
#         i -= 1  # 向上移动
#     elif direction == 'down' and i < size_left - 1:
#         i += 1  # 向下移动
#     elif direction == 'left' and j > 0:
#         j -= 1  # 向左移动
#     elif direction == 'right' and j < size_right - 1:
#         j += 1  # 向右移动
#     N[i][j] = play  # 设置新位置
#     print(f'\r{N}', end=' ')
#
#
# def on_key_press(event):
#     if event.name in key_pressed:
#         key_pressed[event.name] = True  # 标记按键为按下
#         # print(f"按下的键是: {event.name}")
#
# def on_key_release(event):
#     if event.name in key_pressed:
#         key_pressed[event.name] = False  # 标记按键为松开
#         # print(f"松开了键: {event.name}")
#
# # 启动一个线程以持续处理移动
# movement_thread = threading.Thread(target=move, daemon=True)
# movement_thread.start()
#
# # 监听键盘按下和释放事件
# keyboard.hook(on_key_press)
# keyboard.on_release(on_key_release)  # 处理键释放事件
# keyboard.wait('esc')  # 等待直到按下 Esc 键来停止监听


import numpy as np
import subprocess
import keyboard
import time
import threading
import os

# 矩阵尺寸
size_left = 16
size_right = 24

move_speed = 1

# 初始化矩阵和玩家位置
play = 'o'
refresh = ' '
N = np.full((size_left, size_right), refresh)
i, j = 3, 3
N[i][j] = play

# 标记按键状态
key_pressed = {'up': False, 'down': False, 'left': False, 'right': False}

def clear_console():
    """清屏函数"""
    # os.system('cls' if os.name == 'nt' else 'clear')
    subprocess.run('cls', shell=True)

def draw_matrix():
    """绘制矩阵"""
    clear_console()
    for row in N:
        print({" ".join(row)})
    print("\n使用⬆️⬇️⬅️➡️方向键移动玩家，按 Esc 退出游戏。")

def move():
    """持续移动矩阵中的玩家"""
    while True:
        for key in key_pressed:
            if key_pressed[key]:
                process_move(key)
                draw_matrix()  # 每次移动后刷新屏幕
        time.sleep(0.064)  # 控制移动速度

def process_move(direction):
    """根据方向更新玩家位置"""
    global i, j, refresh
    N[i][j] = refresh  # 清除当前位置
    if direction == 'up' and i > 0:
        i -= move_speed
    elif direction == 'down' and i < size_left - move_speed:
        i += move_speed
    elif direction == 'left' and j > 0:
        j -= move_speed
    elif direction == 'right' and j < size_right - move_speed:
        j += move_speed
    N[i][j] = play  # 更新新位置


def on_key_press(event):
    """按下键时设置按键状态"""
    if event.name in key_pressed:
        key_pressed[event.name] = True

def on_key_release(event):
    """释放键时重置按键状态"""
    if event.name in key_pressed:
        key_pressed[event.name] = False

# 启动线程持续处理移动
movement_thread = threading.Thread(target=move, daemon=True)
movement_thread.start()

# 初始绘制矩阵
draw_matrix()

# 监听键盘事件
keyboard.hook(on_key_press)
keyboard.on_release(on_key_release)
keyboard.wait('esc')  # 按 Esc 键退出


# import time
#
# # 简单的计数器示例，使用 flush=True 强制刷新输出
# for i in range(1, 11):
#     print(f"当前计数: {i}", flush=True)  # 强制刷输出
#     time.sleep(1)  # 暂停1秒，以便查看变化
#
# print("计数完成！", flush=True)  # 最后打印结束信息



import subprocess
import torch

# def get_game_map():
#     gquit = True
#     while gquit:
#         # 清除控制台输出
#         subprocess.run('cls', shell=True)
#         # 创建张量
#         # game_map = torch.tensor([[0, 1, 2, 3, 4],
#         #                          [5, 6, 7, 8, 9],
#         #                          [10, 11, 12, 13, 14],
#         #                          [15, 16, 17, 18, 19]])
#         game_map = torch.randn(4,5)
#         # 打印张量
#         print(game_map)
#         # 获取用户输入
#         ip = input("输入 'q' 退出: ")
#         if ip == "q":
#             gquit = False
#
# get_game_map()

# import subprocess
# import time
#
# for i in range(10):
#     subprocess.run('cls', shell=True)
#     print(i)
#     time.sleep(1)
