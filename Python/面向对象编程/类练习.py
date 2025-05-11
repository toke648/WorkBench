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