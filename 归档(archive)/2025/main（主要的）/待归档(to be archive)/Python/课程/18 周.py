# 全局变量&局部变量
def func():
    global a
    print(a)

a = 1
func()

# 嵌套函数
def func(num):
    if num <= 2:
        return 1
    else:
        return func(num - 1) + func(num - 2)

print(func(12))


# 匿名函数
temp = lambda x, y: pow(x, y)

print(temp(2, 3))


# 程序时钟
import time

minute = int(input("minute: "))

for i in range(minute - 1, -1, -1):
    for j in range(59, -1, -1):
        print(f"\r{i:02d}:{j:02d}", end='')
        time.sleep(0.1)

print("\ntime out...")