class Mytorch:
    def __init__(self, nums):
        self.nums = nums

    @staticmethod
    def arrages(nums):
        r"""
        any(input) -> Tensor

        Tests if any element in :attr:`input` evaluates to `True`.
        .. note:: This function matches the behaviour of NumPy in returning
            output of dtype `bool` for all supported dtypes except `uint8`.
            For `uint8` the dtype of output is `uint8` itself.

        this is a function,you can input an int number like: a = 1
        """
        result_list = []
        for num in range(nums):
            result_list.append(num)
        print(result_list)
        return result_list

    @staticmethod
    def ones(self):
        pass

Mytorch.arrages(12)


# class MyTorch:
#     def __init__(self, nums):
#         self.nums = nums
#
#     @staticmethod
#     def arange(nums):
#         r"""
#         any(input) -> Tensor
#
#         Tests if any element in :attr:`input` evaluates to `True`.
#         .. note:: This function matches the behaviour of NumPy in returning
#             output of dtype `bool` for all supported dtypes except `uint8`.
#             For `uint8` the dtype of output is `uint8` itself.
#
#         this is a function,you can input an int number like: a = 1
#         """
#         # result_list = []
#         # for num in range(nums):
#         #     result_list.append(num)
#         # print(result_list)
#
#         return list(range(nums))
#
#     @staticmethod
#     def ones(self):
#         pass