# import tkinter as tk
#
# def run_program():
#     result = "Hello World"
#     return result
#
# result = run_program()
# root = tk.Tk()
# label = tk.Label(root, text=result)
# label.pack()
# root.mainloop()

# from tqdm import tqdm
# import time
#
# for i in tqdm(range(10)):
#     time.sleep(1)

x = tuple(range(10))

print(x[-1])

print(int(4 ** 0.5))

list(range(1, 5))
print(list(range(1, 5)))

print(tuple(range(1, 100, 2)))
print(list(range(1, 100, 2)))

x = [10, 20, 30]
x.insert(1, 40)
print(x)

x = [1, 2, 3]

print(sum(x) / len(x))


from random import randint
import random

n = 0
random_numbers = [random.randint(0, 100) for _ in range(45)]

for i in random_numbers:
    i = int(i)
    if int(i) >= 60:
        pass
    elif 0 <= i < 60:
        n += 1

print(f'共{n}人 不及格')

