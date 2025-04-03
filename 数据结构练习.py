# import hashlib
# from collections import defaultdict
#
# # 哈希表存储
# password_hash_table = defaultdict(lambda: defaultdict(list))
#
# # 生成密码本
# def generate_passwords():
#     # 假设我们限制密码长度为4个字符
#     for length in range(1, 5):  # 遍历长度 1 到 4
#         for password in generate_by_length(length):
#             # 判断密码类型：数字、字母、特殊字符
#             if password.isdigit():
#                 password_hash_table[length]["digits"].append(password)
#             elif password.isalpha():
#                 if password.islower():
#                     password_hash_table[length]["lowercase"].append(password)
#                 elif password.isupper():
#                     password_hash_table[length]["uppercase"].append(password)
#             else:
#                 password_hash_table[length]["special"].append(password)
#
# # 假设我们用这种方式生成密码
# def generate_by_length(length):
#     # 生成一个简单的密码组合，实际中会根据字符集来生成
#     chars = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ!@#"
#     for i in range(len(chars) ** length):  # 生成所有组合
#         password = ''.join(chars[i % len(chars)] for i in range(length))
#         yield password
#
# # 生成密码本
# generate_passwords()
#
# # 打印出存储的哈希表
# print(password_hash_table)


def many_param(num_one, *args):
    print(args)


many_param(1, 2, 3, 4, 5)


x = 'C++ language'
x.replace('C++', 'Python')
print(x)

d = {'a': 1, 'b': 2, 'c': 3}

temp = d.get("c", 5)

print(temp)


x =tuple(range(10))
print(x)


print(list(range(10, 20, 2)))



x =list(range(10))

n = [i%2==1 for i in x]
print(n)


x = list(range(10))
new_list = x[0::2] + x[1::2]

print(new_list)


class Phone:
    def __init__(self, bnd, mod, ss, pro):
        self.bnd = bnd
        self._mod = mod
        self.ss = ss
        self.pro = pro

    def show_info(self):
        print(self.bnd, self._mod, self.ss, self.pro)

p = Phone('安卓', 14, 1600*900, 'inter-8')
p.show_info()