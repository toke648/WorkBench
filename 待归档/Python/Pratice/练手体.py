# 百钱百鸡
from astropy.units.quantity_helper.function_helpers import insert

# hug = 5
# hng = 3
# check = 3
#
# money = 100
#
# quantity = 100
#
# for i in reversed(range(1, 101)):
#     print(i)


# newlist = [x*3 for x in range(20)]
# print(newlist)
# print(type(newlist))
#
#
# g = (x*3 for x in range(20))
# print(type(g))
#
# # 方法
# print(g.__next__())
# print(g.__next__())
# print(g.__next__())
#
# # 函数
# print(next(g))
# print(next(g))
# print(next(g))


# g = (x*3 for x in range(20))
#
#
# # try: except:
#
# while True:
#
#     try:
#         total = next(g)
#         print(total)
#     except:
#         print('没有更多元素了！')
#         break
#
#
# def func():
#     n = 100
#     list1 = [3, 6 ,9]
#
#     def inner_func():
#         for index,i in enumerate(list1):
#             list1[index] = i + n
#             print(list1)
#
#         list1.sort()
#
#
# func()
# print(func())
# f = func()
# print(f)


# for i in range(1, 10):
#     print()
#     for j in range(1, i):
#         print(' ' * j, '*')
#         print(end='')
#
# print("  *")
# print(" ***")
# print("*****")
# print(" ***")
# print("  *")
#
#
# def print_rhombus(n):
#     # 打印上半部分
#     for i in range(n // 2 + 1):
#         # 打印前导空格
#         print(' ' * (n // 2 - i), end='')
#         # 打印星号
#         print('*' * (2 * i + 1))
#
#         # 打印下半部分
#     for i in range(n // 2 - 1, -1, -1):
#         # 打印前导空格
#         print(' ' * (n // 2 - i), end='')
#         # 打印星号
#         print('*' * (2 * i + 1))
#
#     # 对角线长度为 5
#
#
# print_rhombus(12)
#
#
#
# Game = """
#                 ********
#                ************
#                ####....#.
#              #..###.....##....
#              ###.......######              ###            ###
#                 ...........               #...#          #...#
#                ##*#######                 #.#.#          #.#.#
#             ####*******######             #.#.#          #.#.#
#            ...#***.****.*###....          #...#          #...#
#            ....**********##.....           ###            ###
#            ....****    *****....
#              ####        ####
#            ######        ######
# ##############################################################
# #...#......#.##...#......#.##...#......#.##------------------#
# ###########################################------------------#
# #..#....#....##..#....#....##..#....#....#####################
# ##########################################    #----------#
# #.....#......##.....#......##.....#......#    #----------#
# ##########################################    #----------#
# #.#..#....#..##.#..#....#..##.#..#....#..#    #----------#
# ##########################################    ############
#
# """
#
#
# print(Game)
#
#
# def diamond(n):
#     for i in range(n):
#         print(' ' * (n - i - 1) + '*' * (2 * i + 1))
#     for i in range(n - 2, -1, -1):
#         print(' ' * (n - i - 1) + '*' * (2 * i + 1))
#
# if __name__ == '__main__':
#     diamond(5)  # 5 个字符的菱形
#
#
#
# a = '你好     世界 hello world'
#
# print(a.split(' ', 2))
#
#


# def func(num):
#
#     n = 2
#
#     while num > 1:
#         if num % n == 0:
#             num //= n
#         elif num % n != 0:
#             print(num)
#         else:
#             n += 1
#
#
# if __name__ == '__main__':
#     # num = int(input())
#     # num = 100
#     print('----------------')
#     for num in range(100, 200):
#         func(num)


# def is_prime(num):
#     # 排除小于等于1的数
#     if num <= 1:
#         return False
#     # 只需检查到 num 的平方根
#     for n in range(2, int(num**0.5) + 1):
#         if num % n == 0:
#             return False
#     return True
#
# if __name__ == '__main__':
#     # 遍历100到199之间的每一个数字
#     for num in range(100, 200):
#         if is_prime(num):  # 如果是素数，则打印
#             print(num)


a = [1,2,3,4,5,6,7]

print(a[-6:-3:-1])

print('abc', 'klo9', sep='\n')