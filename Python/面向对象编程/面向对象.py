"""
面向对象编程
类、方法、属性、对象
封装、继承、多态
实例、私有、静态、公有
_XX 忘了
__XX 私有对象/属性/方法
__XX__  特殊对象/属性/方法
@ 装饰器： 忘了
静态方法 (@staticmethod): 静态方法不依赖于类的实例，也不依赖于类本身，只与函数参数有关。
类方法 (@classmethod): 类方法依赖于类本身，可以访问类的属性和方法，但不能访问实例的属性。

"""
class Animal:
    def __init__(self, color: str,
                 call: str
                 ) -> None:
        """
        封装 (Encapsulation)： 封装指的是将数据（属性）和操作这些数据的代码（方法）绑定在一起，并对外界隐藏内部实现细节。
        通过封装，可以通过“公开”的接口访问数据，同时限制对数据的直接访问。

        :param color:
        :param call:
        """
        # 私有对象，只能从函数内部调用，类似C#的 private、public
        self.__play = 3  # 静态属性
        self.color = color # 实例属性
        self.call = call # 实例属性

    def __func(self):  # 静态方法
        return self.__play


def decorator(func):  # 装饰器
    def wrapper(self, *args, **kwargs):
        print("Before function call")
        result = func(self, *args, **kwargs)
        print("After function call")
        return result
    return wrapper


class Dog(Animal):
    """
    @classmethod 装饰器 是用来定义类方法的。类方法的第一个参数是 cls，表示类本身。它可以访问类属性，但不能访问实例属性。
    """
    # @classmethod  # 装饰器，实例方法
    def __init__(self,
                 leg: int,
                 color: str,
                 call: str
                 ) -> None:
        """
        继承 (Inheritance)： 继承允许一个类（子类）继承另一个类（父类）的属性和方法，从而实现代码的重用。
        在你的代码中，Dog 和 Cat 类都继承自 Animal 类，因此它们可以访问 Animal 类中的属性和方法。
        比如，Dog 和 Cat 类都可以使用 Animal 类中的 __init__ 和 func 方法。

        :param leg:
        :param color:
        :param call:
        """
        # self.setting = Animal(color, call) # 集成父类方法的两种方式
        super().__init__(color, call)
        self.leg = leg # 实例属性

    @decorator  # 装饰器 是一种用于增强函数或方法功能的工具，常用来添加跨切功能（如日志、权限检查、缓存等）。
    def func(self):  # 实例方法
        print(self.leg)
        result = f'{self.color}的狗狗在{self.call}叫,其他的狗也跟着叫'
        return result


class Cat(Animal):
    def __init__(self,
                 name: str,
                 tail: str,
                 color: str,
                 call: str) -> None:
        """
        多态 (Polymorphism)： 多态指的是不同类的对象可以通过相同的方法名称表现出不同的行为。
        在你的代码中，Dog 和 Cat 类都实现了 func 方法，虽然它们的行为不同（打印不同的内容），但你可以使用相同的 func() 方法来调用它们。
        这就是多态的体现：不同的对象（不同的类）有不同的实现，但可以通过相同的接口调用。

        :param tail:
        :param color:
        :param call:
        """
        super().__init__(color, call) # 继承父类对象
        self.__name = name
        self.__tail = tail # 静态属性

    def func(self
             ) -> str:
        print(self.__tail)
        # print(self.play) # 无法访问私有变量
        return f'{self.color}的猫在{self.call}叫'

    """
    @staticmethod 装饰器 是用来定义静态方法的。静态方法没有隐式的 self 或 cls 参数，它与类和实例无关，通常用于执行某些功能但不需要访问类或实例的属性。
    """
    @staticmethod  # 定义静态方法
    def play():
        print("这是一个静态方法!")
        return "end..."

"""
关于装饰器
装饰器（decorator）是Python中的一个函数，它能够在不修改原函数代码的前提下，为函数添加额外的功能。它的常见用途包括：记录日志、权限验证、缓存结果等。

装饰器的语法
装饰器通常是通过 @ 符号来应用的，后面跟着一个函数或方法。在你的代码中，@func 这一行应用了装饰器，
但存在一个问题：你定义的 func 是一个实例方法，而装饰器通常是作用在函数上，而不是类的方法上。

装饰器 是一种用于增强函数或方法功能的工具，常用来添加跨切功能（如日志、权限检查、缓存等）。
装饰器需要接受一个函数，并返回一个新的函数。这个新函数通常会调用原始函数，并可以在调用前后执行一些额外的操作。
在面向对象编程中，装饰器也可以用于类方法，但需要注意装饰器的写法和类的使用方式。
如果你还是对装饰器的理解有疑问，可以尝试简单的例子并一步步调试，逐渐掌握它的工作原理。
"""

# print(Animal('黑色', '汪汪').__func) # 无法访问私有方法
d = Dog(4, '黑色', '汪汪')
print(d.func())
c = Cat('Tim', 'short', '黄色', '喵喵')
print(c.func())

print(d.leg) # 实例属性可以调用
print(c.play())  # 访问静态方法
# print(c.__tail) # AttributeError: 'Cat' object has no attribute '__tail'  无法访问私有方法