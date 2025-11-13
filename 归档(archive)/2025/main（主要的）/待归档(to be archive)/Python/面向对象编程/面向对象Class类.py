#
# class Ai:
#     def ai_large_language_model(self):
#         pass
#
#     def prt(self):
#         print(self)
#         print(self.__class__)
#
#     if __name__ == '__main__':
#         pass
#
#     # Class 中函数(方法)的第一个变量是类的实体,代表了变量储存的物理地址
#     def add(self,x,y):
#         result = x+y
#
# t = Ai()
# # 这是创建出的变量的物理地址
# print(t)
# t.prt()
# print(t.prt())

# class Calculator:
#       class_variable = 'I am a class variable'  # 这是一个类变量（固有属性）
#       name = 'Good calculator'  # name：类变量（固有属性）
#
#       price = 18  # price：类变量（固有属性）
#
#       def __init__(self, hig, wid, wei):
#           self.hight = hig  # 实际变量（自定义属性）
#           self.width = wid  # width：实际变量（自定义属性）
#           self.weight = wei # weight：实例变量（自定义属性）
#
#       def add(self,x,y):  # add() 方法
#           result = x+y
#           print(result)
#       def minus(self,x,y):  # minus() 方法
#           result = x+y
#           print(result)
#       def times(self,x,y):  # times() 方法
#           print(x*y)
#       def divide(self,x,y):  # divide() 方法
#           print(x/y)
#
#
# cal2 = Calculator(1,5,12)
#
# print(cal2.name)
# print(cal2.hight)
# print(cal2.add(1,2))
# print(cal2.price)
# cal2.price = 25
# print(cal2.price)


# 类定义
# class people:
#     name = ''
#     age = 0
#
#     _weight = 0
#
#     def __init__(self,n,a,w,g):
#         self.name = n
#         self.age = a
#         self._weight = w
#
#     def speak(self):
#         print("%s 说：我 %d 岁：" %(self.name, self._weight))
#
# # 单继承实例
# class student:
#     grade = ''
#     def __init__(self,n,a,w,g):
#         # 调用父类结构
#         people.__init__(self, n,a,w)
#         self.grade = g
#
#     def speak(self):
#         print('%s 说： 我 %d 岁了，我在读%d年纪'%(self.name, self.age,self.grade))
#
# s = student('ken', 10, 60, 3)
# s.speak()


# # def 方法实现
# def student(n, o, a):
#     total = '%s %d %d' % (n, o, a)
#     return total
#
#
# s = student(10, 15, 3)
# print(s)

# class 类实现

# class student:
#     def speak(self,name,old,age):
#         result = '%s %d %d'%(name,old,age)
#         return result
#
# s = student()
# print(s.speak(10,15,3))


# class people:
#     name = ''
#     age = 0
#     __weight = 0
#
#     def __init__(self,n,a,w):
#         self.name = n
#         self.age = a
#         self.__weight = w
#
#     def speak(self):
#         print("%s %d %d"%(self.name,self.age,self.__weight))
#
#
# class student:
#     grade = ''
#     def __init__(self,n,a,w,g):
#         people.__init__(self,n,a,w,g)
#         self.grade = g
#     def speak(self):
#         print('%s %d %d'%(self.name,self.age,self.grade))
#
# s = student('ken', 10,60,3)
# print(s.speak())


'''
1.类 class
2.方法 def
3.继承-
1).单继承
2).多继承
4.方法重写
四、实际变量、局部变量、类变量


涉及到的名词
名词定义
类(Class): 用来描述具有相同的属性和方法的对象的集合。它定义了该集合中每个对象所共有的属性和方法。对象是类的实例。
方法： 类中定义的 函数 。
类变量： 类变量在整个实例化的对象中是公用的。
一般位置 ：类变量定义在类中且在函数体之外。
固有属性由类变量表示。
类变量通常不作为实例变量使用。
对类变量的修改会影响到类的所有实例。
数据成员： 类变量或者实例变量用于处理类及其实例对象的相关的数据。
方法重写： 如果从父类继承的方法不能满足子类的需求，可以对其进行改写，这个过程叫方法的覆盖（override），也称为方法的重写。
实例变量：
一般位置 ：在类的 __init__ 声明中。
属性 是用变量来表示的，这种变量就称为实例变量，且一般是自定义属性。
局部变量：
一般位置 ：定义在方法中的变量。
只作用于当前实例（对象）的类。
一旦函数或方法执行完毕，局部变量就会被销毁。
局部变量与类本身无关，无论是在类的内部还是外部定义的方法中，都可以有局部变量。
继承： 即一个派生类（derived class）继承基类（base class）的属性和方法。继承也允许把一个派生类的对象作为一个基类对象对待。
实例化： 创建一个类的实例，即创建一个类的具体对象。
实例是可以更改、删除原属性的。
对象： 通过类定义的数据结构实例，实例即对象。对象包括两个数据成员（类变量和实例变量）和方法。
————————————————

                            版权声明：本文为博主原创文章，遵循 CC 4.0 BY-SA 版权协议，转载请附上原文出处链接和本声明。

原文链接：https://blog.csdn.net/qq_51409113/article/details/141268789

'''


'''
#通俗举例：
定义一个人（男性）要吃饭、喝水、睡觉；
现在有个具体的人，他被赋予上述定义，所以他便是男人，会吃饭，会喝水，会睡觉。
#类名：一个人
#属性：男性
#方法：吃饭、喝水、睡觉
#对象：这个具体的人（赋予这个人相同的属性、方法的过程叫“实例化”）
'''

# 类
class People:
    # 属性
    gender = 'man'

    # 方法
    def eat(self):
        pass

    def drink(self):
        pass

    def sleep(self):
        sleep_time = '10:30'
        print(sleep_time)

# 实例化，实例即对象
p = People()
print(p.sleep())


'''
（1）self
在用 def 定义方法时，第一个参数一定得是 self 。

self 代表的是类的实例（对象），本质是代表当前对象的地址，不是类；而 self.class 则指向类。
'''


class Test:
    def prt(self):
        print(self)
        print(self.__class__)


t = Test()
t.prt()


'''
方法
在类的内部，使用 def 关键字来定义一个方法。
与一般函数不同，类的方法在定义时必须包含参数 self，且为第一个参数，self 代表的是类的实例。
self 不是 python 的关键字，所以可以用别的单词来代替 self 。
但按照惯例，最好就用 self 。
'''

def add(self,x,y): # add即为方法名，x和y为调用该函数需要输入的参数
    result=x+y



'''
__init__
__init__() 作为类的构造方法，用来初始化类的实例，
一种特殊的方法，可称之为“构造方法”，初始化（Initialize的缩写）

前后各两个下划线

'''

# __init__ 代码举例（没给出默认自定义属性，实例化时需要手动给出）：
#
# 下方代码要注意一点，自定义属性是 hight 这些，不是 hig 这些，hig 只是输入参数。
class Calculator:  # Calculator：类名
    class_variable = "I am a class variable"  # 这是一个类变量（固有属性）
    name = 'Good calculator'  # name：类变量（固有属性）
    price = 18  # price：类变量（固有属性）

    # *****************************
    def __init__(self, hig, wid, wei):  # *
        self.hight = hig  # hight：实例变量（自定义属性）      *
        self.width = wid  # width：实例变量（自定义属性）      *
        self.weight = wei  # weight：实例变量（自定义属性）     *
        # *****************************

    def add(self, x, y):  # add()：方法
        result = x + y  # result：局部变量
        print(result)

    def minus(self, x, y):  # minus()：方法
        result = x - y  # result：局部变量
        print(result)

    def times(self, x, y):  # times()：方法
        print(x * y)

    def divide(self, x, y):  # divide()：方法
        print(x / y)


#  __init__ 代码举例（给出默认自定义属性）：
def __init__(self, hight=1, width=5, weight=12):
    self.hight = hight  # hight：自定义属性            *
    self.width = width  # width：自定义属性            *
    self.weight = weight  # weight：自定义属性


'''
继承
就是先定义了一个 基准类，后面想再定义一个 派生类，该派生类想沿用基准类的属性和方法，这种沿用过程就叫“继承”。

子类（派生类 DerivedClassName）会继承父类（基类 BaseClassName）的属性和方法。


'''


# 例1

class student(object):
    def speak(self):
        # 设定形参
        john.name = '约翰'
        john.age = 19

        print('%s %d'%(self.name, self.age))


john = student()

# # 在输出时给出形参
# john.name = '约翰'
# john.age = 19

john.speak()

# 例2
class student(object):
    def __init__(self):
        pass

print(f'{1323}')


class table:
    def __init__(self, a, b ,c):
        self.a = a
        self.b = b
        self.c = c

    def one(self):
        print(self.a)
        print(self.b)
        print(self.c)

if __name__ == '__main__':

    t = table(1, 2, 3)
    print(t.a)
    print(t.b)
    print(t.c)

    t.one()


# class House:
#     def __init__(self, 颜色, 位置, 卧室数):
#         self.颜色 = 颜色
#         self.位置 = 位置
#         self.卧室数 = 卧室数
#
# house1 = House("紫色", "长沙", 4)
# house2 = House("红色", "深圳", 3)
#
# print(house1.__init__())
# print(house2.__init__())


# class CuteCat:
#     # 只有在有self的情况下，所生成的变量才能被解释成对象，否则就会被python认为是普通变量
#     def __init__(self, cat_name):
#         self.name = "Lambton"
#         self.name = cat_name
#
# # 变量的物理内存地址
# print(CuteCat("Jojo"))
# cat1 = CuteCat("Jojo")
# print(cat1.name)


# class CuteCat:
#     # 只有在有self的情况下，所生成的变量才能被解释成对象，否则就会被python认为是普通变量
#     def __init__(self, cat_name, cat_age, cat_color):
#         self.name = "Lambton"
#         self.name = cat_name
#
# # 变量的物理内存地址
# print(CuteCat("Jojo", 2, "橘色"))
# cat1 = CuteCat("Jojo", 2, "橘色")
# print(cat1.name)


class CuteCat:
    # 只有在有self的情况下，所生成的变量才能被解释成对象，否则就会被python认为是普通变量
    def __init__(self, cat_name, cat_age, cat_color):
        self.name = cat_name
        self.age = cat_age
        self.color = cat_color

    def speak(self):
        pass


# 变量的物理内存地址
cat1 = CuteCat("Jojo", 2, "橘色")


import asyncio

async def founc1():
    pass

async def founc2():
    pass



