import unittest

class func(unittest.TestCase):

    def Nome(self):
        a = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
        for i in range(len(a) + 1):
            print(a[i])
            self.assertEqual(a[i])


f = func()
f.Nome()
