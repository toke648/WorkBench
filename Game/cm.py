# import os
# import time
#
# def clear_console():
#     # Windows
#     if os.name == 'nt':
#         os.system('cls')
#     # 类 Unix 系统
#     else:
#         os.system('clear')
#
# # 示例用法
# while True:
#     clear_console()
#     print("这里是更新的矩阵或游戏界面")
#     time.sleep(1)  # 暂停 1 秒以便查看更新


# import time
#
# def clear_console():
#     print("\033[H\033[J", end='')
#
# # 示例用法
# while True:
#     clear_console()
#     print("这里是更新的矩阵或游戏界面")
#     time.sleep(1)
#


import os
import time

def clear_console():
    os.system('cls' if os.name == 'nt' else 'clear')

def draw_matrix(matrix):
    # 绘制矩阵到控制台
    for row in matrix:
        print("\r ".join(row), end=' ')

# 示例矩阵游戏主循环
def matrix_game():
    # 初始矩阵
    matrix = [
        ["O", " ", " ", " "],
        [" ", "O", " ", " "],
        [" ", " ", "O", " "],
        [" ", " ", " ", "O"]
    ]
    while True:
        # 每次绘制前清屏
        clear_console()
        draw_matrix(matrix)
        # 模拟矩阵更新
        matrix = update_matrix(matrix)
        time.sleep(0.5)

def update_matrix(matrix):
    # 矩阵中元素向右移动，模拟动态变化
    new_matrix = []
    for row in matrix:
        new_row = [" "] + row[:-1]  # 移动一格
        new_matrix.append(new_row)
    return new_matrix

# 启动游戏
matrix_game()
