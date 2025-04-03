# from http import HTTPStatus
# import dashscope
#
# dashscope.api_key = 'sk-707613869ffe4b06b165e396e580f847'
# messages = [{'role': 'system', 'content': 'You are a helpful assistant.'},
#             {'role': 'user', 'content': '如何做西红柿鸡蛋？'}]
#
# response = dashscope.Generation.call(
#     model='qwen-turbo',
#     messages=messages,
#     result_format='message',  # set the result to be "message" format.
# )
#
# if response.status_code == HTTPStatus.OK:
#     print(response)
# else:
#     print('Request id: %s, Status code: %s, error code: %s, error message: %s' % (
#         response.request_id, response.status_code,
#         response.code, response.message
#     ))
# import os
# from openai import OpenAI
#
# client = OpenAI(
#     api_key=os.getenv("sk-707613869ffe4b06b165e396e580f847"),
#     base_url="https://dashscope.aliyuncs.com/compatible-mode/v1"
# )
# completion = client.chat.completions.create(
#     model="qwen-plus",
#     # 规则为系统,传入数值
#     # 规则为用户，传入数值
#     messages=[{'role': 'system', 'content': 'You are a helpful assistant.'},
#               {'role': 'user', 'content': 'Who you are?'}],
#     stream=True,
#     stream_options={"include_usage": True}
# )
# for chunk in completion:
#     print(chunk.model_dump_json())

# import os
import json
from openai import OpenAI


content = input('Input your question:')

system_content = None
user_content = None

client = OpenAI(
    # 若没有配置环境变量，请用百炼API Key将下行替换为：api_key="sk-xxx",
    api_key="sk-707613869ffe4b06b165e396e580f847",
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
)
completion = client.chat.completions.create(
    model="qwen-plus",  # 模型列表：https://help.aliyun.com/zh/model-studio/getting-started/models
    messages=[
        {'role': 'system', 'content': '你的名字是neuro—sama,你是一名Vtuber主播。现在正在直播。你的性格非常邪恶，你喜欢到处搞破坏，将别人的事情搞砸，并以此为乐。',},
        {'role': 'user', 'content': f'{content}'}],
)

qwen_plus = completion.model_dump_json()
data = json.loads(qwen_plus)

content = data['choices'][0]['message']['content']

print(content)


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
# def student(n,o,a):
#
#     total = '%s %d %d' %(n,o,a)
#     return total
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