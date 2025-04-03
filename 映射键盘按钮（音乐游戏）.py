import keyboard

"""
实现输出按下的按键
"""

# def on_key(key):
#     print(key.name)

# keyboard.hook(on_key)
# keyboard.wait()


""" 由于更新速度太快，所以需要加上延时
    因此设定一个条件，当按键按下时，才输出按键
    这样才不会出现按键抬起时，输出两次按键的问题 """
# import keyboard

# def on_key(event):
#     if event.event_type == 'down':  # 仅在按下时输出
#         print(event.name)

# keyboard.hook(on_key)
# keyboard.wait()


""" 也可以使用 event_type == 'up' 来实现按键抬起时输出 """
def on_key(event):
    if event.event_type == 'up':  # 仅在抬起时输出
        print(event.name)

keyboard.hook(on_key)
keyboard.wait()

import numpy as np

print(np.array([1, 2, 3]))
print(np.sum([1, 2, 3]))
print(np.mean([1, 2, 3]))
print(np.std([1, 2, 3]))
