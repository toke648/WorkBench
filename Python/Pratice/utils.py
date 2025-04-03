# print("12")
from PIL.ImImagePlugin import number
from docutils.parsers.rst.directives.misc import Class
from fontTools.misc.cython import returns
from scipy.constants import stone

# list_o = [5,8,1,9,0,7,2,4,3,6,10]

# def public_function():
#     print(12)




# # 公有变量和私有变量
# # class Person():
# #     name = 'text'
# #     __name = 'test'
# # a = Person()
# # print(a.name)
# # print(a.__name)


# class Person():
#     __name = 'test'
#     def test(self):
#         return self.__name
    

# b = Person()
# print(b.test())
# print(b._Person__name)


# class Pravite():
#     def number():
#         # 共有变量
#         a = 1
#         # 共有变量
#         _b = 2
#         #私有变量
#         __c = 3
#         #公有变量
#         __d__ = 4
#         def __init__(self):
#             print('calling __init__....')
#         def print_C(self):
#             return(self.c)

# ac = Pravite()

# # print(ac.a,ac._b,ac.__c,ac.__d__)

# bc = ac()
# print(bc.a,bc._b,bc.__c,bc.__d__)



# list_o = [5,8,1,9,0,7,2,4,3,6,10]
# longer = len(list_o)
#
#
#
# for i in range(longer):
#     try:
#         ty = list_o[i]
#         tp = list_o[i + 1]
#         if ty > tp:
#             temp = ty
#             ty = tp
#             tp = temp
#             print(temp)
#         else:
#             continue
#         #
#         # print('tige = ', i)
#         # print('ty = ', ty)
#         # print('tp = ', tp)
#
#     except IndexError:
#         pass
#
# print(list_o)



#
#
# def count():
#     for it in range(len(list_o) - 1):
#
#         if list_o[it] < list_o[it + 1]:
#             temp = list_o[it]
#
#             list_o[it] = list_o[it + 1]
#             list_o[it + 1] = temp
#
#     print(list_o)
#
#
# if __name__ == '__main__':
#     list_o = [5, 8, 1, 9, 0, 7, 2, 4, 3, 6, 10]
#     for i in range(len(list_o) - 1):
#         if list_o[i] < list_o[i + 1]:
#             count(list_o)



# list_o = [5, 8, 1, 9, 0, 7, 2, 4, 3, 6, 10]
#
# longer = len(list_o)
# for i in range(longer):
#     for j in range(longer-1-i):
#         if list_o[j] > list_o[j + 1]:
#             list_o[j],list_o[j+1] = list_o[j+1],list_o[j]
#
#
# print(list_o)

# for i in range(0, 10):
#     print('')
#     for j in range(1, i):
#         # print('*', end=' ')
#         print(f'{j}*{i}={i*j}', end=" ")


# 冒泡算法
# 循环嵌套复习
list_o = [5, 8, 1, 9, 0, 7, 2, 4, 3, 6, 10]

longer = len(list_o)
for i in range(longer):
    print('')
    # 所以为什么要减i?
    for j in range(longer - 1 - i):
        # 懂了
        # 检测循环嵌套结构
        # print(f'{j} {i}', end='  ')

        # 大小检测
        if list_o[j] > list_o[j+1]:
            # 检测列表反转结构
            # print(list_o)

            # 反转变量
            list_o[j+1],list_o[j] = list_o[j],list_o[j+1]

            # 第二种反转方法
            # number = list_o[0]
            # list_o[0] = list_o[i+1]
            # list_o[i+1] = number

        else:
            # 跳过判断
            continue

print(list_o)


# 判断回文数
massage = '11213'

print(massage)
print(massage[::-1])
# 直接元组反转
if massage[::-1] == massage:
    print('回文数')
else: print('不是回文数')


# 石头剪刀布
# 面向对象复习

# stone = '石头'
# scissor = '剪刀'
# cloth = '布'
#
# class类
# class Function:
#
#     # __init__初始化变量
#     def __init__(self, stone, scissor, cloth):
#         self.stone = stone
#         self.scissor = scissor
#         self.cloth = cloth
#
#     def Game(self):
#         print(stone)
#         print(cloth)
#         print(scissor)
#
# f = Function(stone,cloth,scissor)
# f.Game()


# Class
# 面向对象学习
#
# class Game:
#
#     def __init__(self, stone, scissor, cloth):
#         self.stone = stone
#         self.scissor = scissor
#         self.cloth = cloth
#
#     def human(self):
#         pass
#
#     def robot(self):
#         pass
#
#     def play_game(self):
#         print(stone)
#
# if __name__ == '__main__':
#     for i in range(10):
#         g = Game('石头', '剪刀', '布')
#         g.play_game()

# import random
#
#
# class Player:
#     def __init__(self, name):
#         self.name = name
#
#     def choose(self):
#         choices = ['石头', '剪刀', '布']
#         return random.choice(choices)
#
#
# class Game:
#     def __init__(self, player1, player2):
#         self.player1 = player1
#         self.player2 = player2
#
#     def determine_winner(self, choice1, choice2):
#         if choice1 == choice2:
#             return "平局"
#         elif (choice1 == '石头' and choice2 == '剪刀') or \
#                 (choice1 == '剪刀' and choice2 == '布') or \
#                 (choice1 == '布' and choice2 == '石头'):
#             return self.player1.name
#         else:
#             return self.player2.name
#
#     def play(self):
#         choice1 = self.player1.choose()
#         choice2 = self.player2.choose()
#         print(f"{self.player1.name} 选择了: {choice1}")
#         print(f"{self.player2.name} 选择了: {choice2}")
#         winner = self.determine_winner(choice1, choice2)
#         print(f"胜利者是: {winner}")
#
#
# # 使用示例
# if __name__ == "__main__":
#     for i in range(10):
#         player1 = Player("玩家1")
#         player2 = Player("玩家2")
#         Game = Game(player1, player2)
#         Game.play()


# from random import randint
#
# def play_game(player_score, computer_score):
#     # 判断胜负
#     if player == computer:
#         print("平局！")
#     elif ((player == 1 and computer == 2) or
#           (player == 2 and computer == 3) or
#           (player == 3 and computer == 1)):
#         player_score += 10
#         computer_score -= 10
#         print(f'player + 10\ncomputer - 10')
#     else:
#         computer_score += 10
#         player_score -= 10
#         print('computer + 10\nplayer - 10')
#
# # 开始游戏
# if __name__ == '__main__':
#     player_score = 100
#     computer_score = 100
#
#     while True:
#         # 玩家出拳
#         player = input('input 1石头/2剪刀/3布：')
#         int(player)
#         # 电脑出拳
#         computer = randint(1,3)
#         print(computer)
#
#         play_game(player_score, computer_score)
#         print(player_score)
#         print(computer_score)
#
#         if computer_score == 200 or player_score == 0:
#             print('电脑胜！')
#             break
#         elif player_score == 200 or computer_score == 0:
#             print('玩家胜！')
#             break


# # 要死了，伪随机算法真的
# # 要打400局是什么鬼？？？
#
# from random import randint
#
# def play_game(player_score, computer_score, player, computer):
#     # 判断胜负
#     if player == computer:
#         print("平局！")
#     elif ((player == 1 and computer == 2) or
#           (player == 2 and computer == 3) or
#           (player == 3 and computer == 1)):
#         player_score += 10
#         computer_score -= 10
#         print(f'玩家 + 10\n电脑 - 10')
#     else:
#         computer_score += 10
#         player_score -= 10
#         print(f'电脑 + 10\n玩家 - 10')
#
#     return player_score, computer_score  # 返回更新后的分数
#
# # 开始游戏
# if __name__ == '__main__':
#     player_score = 100
#     computer_score = 100
#     num = 0
#
#     while True:
#         num += 1
#         print('---------------------------')
#         print('第%d局' % num)
#
#         # 玩家出拳
#         player = input('输入 1石头/2剪刀/3布：')
#
#         # 确保输入是整数
#         if player.isdigit():
#             player = int(player)
#             if player not in [1, 2, 3]:
#                 print('请输入1/2/3')
#                 continue  # 输入不合法时继续
#
#             # 电脑出拳
#             computer = randint(1, 3)
#             print(f'电脑选择: {computer}')
#
#             # 调用游戏函数
#             player_score, computer_score = play_game(player_score, computer_score, player, computer)
#             print(f'当前分数 - 玩家: {player_score}, 电脑: {computer_score}')
#
#             # 判断胜负
#             if computer_score >= 200:
#                 print('---------------------------')
#                 print('电脑胜！')
#                 print(f"达成成就'而你我的朋友 你才是真正的人机'")
#                 break
#             elif player_score >= 200:
#                 print('---------------------------')
#                 print('玩家胜！')
#                 print(f"达成成就'大战{num}回合'")
#
#                 break
#         else:
#             print('请输入有效的数字')


# 感觉还不错，用unity开发成游戏效果绝对惊艳
# 方法1

# 第一串数字（下标列表）
indices =  [4, 1, 2, 3, 0]
# 第二串数字（ASCII码列表）
ascii_codes = [100, 111, 114, 108, 119, 33, 65, 98, 99, 100, 101, 102, 103]

word = ''
for i in indices:
    word += chr(ascii_codes[i])
print(word)

# 方法2 （语法糖）
word = ''.join([chr(ascii_codes[i]) for i in indices])
print(word)

