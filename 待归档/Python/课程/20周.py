"""
上期回顾
全局变量 gloabl lambda

字典可变参数 *karg **kargs

面向对象编程

面向对象 class __init__
静态对象 vaule _value __value
注： __value__ 系统私有对象

析构对象 __del__
装饰器 @

类 对象 属性

全局变量 局部变量

实例对象 静态对象

封装 集成 多态
"""


"""
类 对象 属性

"""
# 类
# class Person:
#     def __init__(self):
#         # 属性
#         self.age = 15
#         self.name = 'Tim'
#         self.list = list
#
#     # 对象
#     def search(self):
#         print(self.name)
#     def __del__(self):
#         print('对象析构...')
#
#
# p = Person()
# p.search()


"""
实例方法
静态方法 _key __key __key___

Python中
_xx、__xx、__xx__
的区别
Python中
_xx、__xx、__xx__
的区别 - 简书

1.
_xx
前导单下划线
_xx
表示一个变量、方法或属性是
内部使用
的。它是一个
约定，意味着该成员是“私有的”，不应该在类外部直接访问。

Python并不会强制实施这种约定，_xx
只是为了提示程序员，这个变量是“内部使用”，不应在类的外部使用或修改。"""

class MyClass:
    def __init__(self):
        self._internal_variable = 42  # 这是内部变量


obj = MyClass()
print(obj._internal_variable)  # 不推荐直接访问
"""2.
__xx
前导和尾随双下划线
__xx
主要用于表示
名称重整（name
mangling）。当你在类中定义一个变量或方法名时，如果它以双下划线开头但没有以双下划线结尾，Python会自动更改其名称，以避免与子类中的同名变量或方法冲突。"""

class MyClass:
    def __init__(self):
        self.__private_variable = 42  # 会被改名为 _MyClass__private_variable


obj = MyClass()
# print(obj.__private_variable)  # 会引发 AttributeError
print(obj._MyClass__private_variable)  # 访问修改后的变量

"""3.
__xx__
前后都有双下划线
__xx__
是
Python的魔法方法（也叫做双下划线方法或特殊方法）。这些方法由Python解释器自动调用，通常用来实现一些内建的行为。例如：

__init__
用于对象的构造方法。
__str__
用于定义如何将对象转换为字符串。
__add__
用于定义加法操作的行为。
这些方法一般由Python内部实现，但你也可以自定义它们来实现自定义行为。"""

class MyClass:
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return f"MyClass with value: {self.value}"


obj = MyClass(10)
print(obj)  # 会调用 __str__ 方法，输出: MyClass with value: 10
"""总结：

_xx
是内部使用的变量，表示该变量不应在外部访问。
__xx
会被名称重整，用于避免子类重写时的命名冲突。
__xx__
是魔法方法（特殊方法），用于定义Python中的内置行为或操作。"""

class A:
    age1 = 10
    _age2 = 30
    __age3 = 30

    def method_a1(self):
        print("类内部调用公共变量：{}".format(self.age1))

    def _method_a2(self):
        print("类内部调用保护变量：{}".format(self._age2))

    def __method_a3(self):
        print("类内部调用私有变量：{}".format(self.__age3))


class B(A):
    def method_b(self):
        print("子类调用父类的公共变量: {}".format(self.age1))
        print("子类调用父类的保护变量: {}".format(self._age2))
        # print("子类调用父类的私有变量: {}".format(self.__age3))  # 会报错，不能这样调用
        print("子类调用父类的私有变量: {}".format(self._A__age3))


a = A()
print(f"类的内存地址: {a}")  # 类的内存地址
# print(a.__age3)  # 会报错，不能这样调用
print(a._A__age3)  # 通过 实例对象._类名__私有变量 调用
# print(A.__age3)  # 会报错，不能这样调用
print(A._A__age3)  # 通过 类对象._类名__私有变量 调用

b = B()
b.method_b()  # 子类的实例对象调用父类中的公共方法
b.method_a1()  # 子类实例对象调用父类中受保护的方法
b._method_a2()  # 子类实例对象调用父类中受保护的方法
# b.__method_a3()  # 会报错，不能这样调用
b._A__method_a3()



"""
装饰器 @

"""

import math

class Circle:
    def __init__(self, radius: int):
        """
        这个类用于计算圆的面积、周长
        :param radius: int
        """
        # 集成父类对象
        # super.__init__(self, None)
        self.radius = radius

    def get_perimeter(self) -> float:
        """
        求周长
        :return: float
        """
        result = math.pi * self.radius * 2
        return result

    def get_area(self) -> float:
        """
        求面积
        :return: float
        """
        result = math.pi * (self.radius ** 2)
        return result

size = 4
c = Circle(size)
area = c.get_area()
perimeter = c.get_perimeter()

print(c)
print(f'area: {area:.2f}')
print(f'perimeter: {perimeter:.2f}')



"""
    匿名函数 lambda
"""
# 定义一个匿名函数，接受两个参数x和y并返回它们的和
add = lambda x, y: x + y

# 使用匿名函数
result = add(10, 20)
print(result)  # 输出: 30
