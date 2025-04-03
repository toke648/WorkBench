# import unittest
#
#
# class MyTestCase(unittest.TestCase):
#     def test_something(self):
#         self.assertEqual(True, False)  # add assertion here
#
#
# if __name__ == '__main__':
#     unittest.main()
from h5py.h5r import get_obj_type
from mypy.plugins.default import typed_dict_get_callback
from numpy.ma.core import product

a,*b,c = 1,2,3,4,5

print(a)
print(b)
print(c)


a,b,*c = 1,2,3,4,5

print(a)
print(b)
print(c)

*a,b,c = 1,2,3,4,5

print(a)
print(b)
print(c)

import json

def get_sun(*args):
    print(args)

    s = 0
    for i in args:
        s += i
    print('和', s)


get_sun(1,2)
get_sun(1,2,3,4,5)
get_sun(1,2,3)
print(type(get_sun(1,2,3)))
get_sun()


a,b,c = (1,2,3)

print(a,b,c)

a,b,*c = (1,2,3,4,5,6,7,8,9)

print(a)
print(b)
print(c)

ran_list = [23,45,12,44,78,39,29]

get_sun(*ran_list)


t = lambda: "Hello,world!"

print(t())

f = lambda a : a ** 2

print(f(12))

x = lambda a,b,c : a+b+c

print(x(1,2,3))


numbers = [1,2,3,4,5]
squared = list(map(lambda x: x**2,numbers))
print(squared)


o = [1,2,3,4,5]

s = list(map(lambda x: x**2,o))

print(s)


number = [1,2,3,4,5,6,7,8]
even_number = list(filter(lambda x: x%2 == 0,number))
print(even_number)


from  functools import reduce

numb = [1,2,3,4]

product = reduce(lambda x,y: x* y, numb)
print(product)