import os
import time
import random
import msvcrt


def main():
    W, H = 20, 12  # 宽度和高度
    S = W * H  # 总格子数
    l = 0  # 长度
    p = 0  # 当前位置
    d = 1  # 方向
    a = 0  # 食物位置
    m = [0] * S  # 地图
    h = {b'a': -1, b'd': 1, b'w': -W, b's': W}  # 方向映射

    random.seed(time.time())

    while a == p or m[p] == 0:
        if a == p:  # 生成新的食物
            a = random.randint(0, S - 1)
            l += 1

        # 更新地图
        os.system('cls' if os.name == 'nt' else 'clear')
        m[p] = l
        for i in range(S):
            if i % W == 0:
                print("|", end="")
            if m[i]:
                m[i] -= 1
                print("()", end="")
            elif i == a:
                print("00", end="")
            else:
                print("  ", end="")
            if (i + 1) % W == 0:
                print("|")

        # 延迟和读取输入
        time.sleep(0.1)
        if msvcrt.kbhit():  # 检测键盘输入
            key = msvcrt.getch()
            if key in h:
                d = h[key]

        # 更新蛇的位置
        p = (S + p + d) % S


if __name__ == "__main__":
    main()
