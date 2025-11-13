
import matplotlib.pyplot as plt
import numpy as np


def bubble_sort_visualization(arr):
    n = len(arr)

    # 设置绘图窗口
    plt.ion()  # 开启交互模式
    fig, ax = plt.subplots()

    # 初始化图形
    bars = ax.bar(range(len(arr)), arr, color='b')
    ax.set_ylim(0, max(arr) + 1)  # 设置 y 轴范围
    plt.xlabel('Index')
    plt.ylabel('Value')
    plt.title('Bubble Sort Visualization')

    # 冒泡排序及可视化
    for i in range(n):
        for j in range(0, n - i - 1):
            # 交换并可视化当前状态
            if arr[j] > arr[j + 1]:
                arr[j], arr[j + 1] = arr[j + 1], arr[j]  # 交换

                # 更新条形图
                for k in range(len(arr)):
                    bars[k].set_height(arr[k])

                plt.pause(0.005)  # 暂停以观察变化

    plt.ioff()  # 关闭交互模式
    plt.show()


def selection_sort_visualization(arr):
    n = len(arr)

    # 设置绘图窗口
    plt.ion()  # 开启交互模式
    fig, ax = plt.subplots()

    # 初始化图形
    bars = ax.bar(range(len(arr)), arr, color='b')
    ax.set_ylim(0, max(arr) + 1)  # 设置 y 轴范围
    plt.xlabel('Index')
    plt.ylabel('Value')
    plt.title('Selection Sort Visualization')

    # 选择排序及可视化
    for i in range(n):
        min_index = i  # 假定当前位置的元素为最小值
        for j in range(i + 1, n):
            # 更新最小值的索引
            if arr[j] < arr[min_index]:
                min_index = j

                # 交换当前元素与找到的最小元素
        arr[i], arr[min_index] = arr[min_index], arr[i]

        # 更新条形图
        for k in range(len(arr)):
            bars[k].set_height(arr[k])

        plt.pause(0.05)  # 暂停以观察变化

    plt.ioff()  # 关闭交互模式
    plt.show()


def merge_sort_visualization(arr, ax, step):
    if len(arr) > 1:
        mid = len(arr) // 2  # 找到中点
        left_half = arr[:mid]  # 左半部分
        right_half = arr[mid:]  # 右半部分

        merge_sort_visualization(left_half, ax, step)
        merge_sort_visualization(right_half, ax, step)

        # 归并
        i = j = k = 0

        while i < len(left_half) and j < len(right_half):
            if left_half[i] < right_half[j]:
                arr[k] = left_half[i]
                i += 1
            else:
                arr[k] = right_half[j]
                j += 1
            k += 1

        while i < len(left_half):
            arr[k] = left_half[i]
            i += 1
            k += 1

        while j < len(right_half):
            arr[k] = right_half[j]
            j += 1
            k += 1

            # 更新条形图
        for m in range(len(arr)):
            bars[m].set_height(arr[m])
        plt.title(f'Merge Sort Step {step[0]}')
        step[0] += 1
        plt.pause(0.00005)  # 暂停以观察变化



# 主可视化函数
def visualize_merge_sort(arr):
    global bars
    step = [1]  # 用于跟踪步骤数

    # 设置绘图窗口
    plt.ion()  # 开启交互模式
    fig, ax = plt.subplots()

    # 初始化图形
    bars = ax.bar(range(len(arr)), arr, color='b')
    ax.set_ylim(0, max(arr) + 1)  # 设置 y 轴范围
    plt.xlabel('Index')
    plt.ylabel('Value')
    plt.title('Merge Sort Visualization')

    # 执行归并排序并可视化
    merge_sort_visualization(arr, ax, step)

    plt.ioff()  # 关闭交互模式
    plt.show()



def insertion_sort_visualization(arr):
    n = len(arr)

    # 设置绘图窗口
    plt.ion()  # 开启交互模式
    fig, ax = plt.subplots()

    # 初始化图形
    bars = ax.bar(range(len(arr)), arr, color='b')
    ax.set_ylim(0, max(arr) + 1)  # 设置 y 轴范围
    plt.xlabel('Index')
    plt.ylabel('Value')
    plt.title('Insertion Sort Visualization')

    # 插入排序及可视化
    for i in range(1, n):
        key = arr[i]  # 当前要插入的元素
        j = i - 1

        # 持续向左移动已排序部分的元素，直到找到适当的位置
        while j >= 0 and key < arr[j]:
            arr[j + 1] = arr[j]  # 移动元素
            j -= 1

        arr[j + 1] = key  # 插入当前元素

        # 更新条形图
        for k in range(len(arr)):
            bars[k].set_height(arr[k])

        plt.title(f'Inserting Element at Index {i}')
        plt.pause(0.01)  # 暂停以观察变化

    plt.ioff()  # 关闭交互模式
    plt.show()


def heapify(arr, n, i, ax, step):
    largest = i  # 初始化最大值为根
    left = 2 * i + 1  # 左子节点
    right = 2 * i + 2  # 右子节点

    # 如果左子节点比根节点大
    if left < n and arr[left] > arr[largest]:
        largest = left

        # 如果右子节点比当前最大值大
    if right < n and arr[right] > arr[largest]:
        largest = right

        # 如果最大值不是根节点
    if largest != i:
        arr[i], arr[largest] = arr[largest], arr[i]  # 交换

        # 更新条形图
        for m in range(len(arr)):
            bars[m].set_height(arr[m])
        ax.set_title(f'Heapify Step {step[0]}')
        plt.pause(0.05)  # 暂停以观察变化
        step[0] += 1

        # 递归地堆化受影响的子树
        heapify(arr, n, largest, ax, step)


def heap_sort_visualization(arr):
    n = len(arr)
    step = [1]  # 记录步骤数

    # 设置绘图窗口
    plt.ion()  # 开启交互模式
    fig, ax = plt.subplots()

    # 初始化图形
    global bars
    bars = ax.bar(range(len(arr)), arr, color='b')
    ax.set_ylim(0, max(arr) + 1)  # 设置 y 轴范围
    plt.xlabel('Index')
    plt.ylabel('Value')
    plt.title('Heap Sort Visualization')

    # 构建最大堆
    for i in range(n // 2 - 1, -1, -1):
        heapify(arr, n, i, ax, step)

        # 一个个从堆中取出元素
    for i in range(n - 1, 0, -1):
        arr[0], arr[i] = arr[i], arr[0]  # 交换
        # 更新条形图
        for m in range(len(arr)):
            bars[m].set_height(arr[m])
        ax.set_title(f'Swap Step {step[0]}: Swap max with index {i}')
        plt.pause(0.5)  # 暂停以观察交换
        step[0] += 1
        heapify(arr, i, 0, ax, step)

    plt.ioff()  # 关闭交互模式
    plt.show()



def shell_sort_visualization(arr):
    n = len(arr)
    gap = n // 2  # 初始增量

    # 设置绘图窗口
    plt.ion()  # 开启交互模式
    fig, ax = plt.subplots()

    # 初始化图形
    bars = ax.bar(range(len(arr)), arr, color='b')
    ax.set_ylim(0, max(arr) + 1)  # 设置 y 轴范围
    plt.xlabel('Index')
    plt.ylabel('Value')
    plt.title('Shell Sort Visualization')

    while gap > 0:
        # 对当前增量的子序列进行插入排序
        for i in range(gap, n):
            temp = arr[i]
            j = i

            # 移动间隔为 gap 的元素到已排序部分
            while j >= gap and arr[j - gap] > temp:
                arr[j] = arr[j - gap]
                j -= gap

            arr[j] = temp

            # 更新条形图
            for k in range(len(arr)):
                bars[k].set_height(arr[k])
            ax.set_title(f'Gap: {gap}, Inserting: {temp} at index {j}')
            plt.pause(0.00005)  # 暂停以观察变化

        gap //= 2  # 减小增量

    plt.ioff()  # 关闭交互模式
    plt.show()


# 快速排序可视化
def quick_sort_visualization(arr, low, high):
    if low < high:
        pi = partition(arr, low, high)  # 调用分区函数
        quick_sort_visualization(arr, low, pi - 1)  # 对左半部分进行递归
        quick_sort_visualization(arr, pi + 1, high)  # 对右半部分进行递归

# 分区函数
def partition(arr, low, high):
    pivot = arr[high]  # 选择最后一个元素作为基准
    i = low - 1  # 小于基准的元素最后一个索引
    for j in range(low, high):
        if arr[j] <= pivot:
            i += 1
            arr[i], arr[j] = arr[j], arr[i]  # 交换
            update_bars(arr)  # 更新可视化
            plt.pause(0.00005)  # 暂停以进行可视化
    arr[i + 1], arr[high] = arr[high], arr[i + 1]  # 将基准放到合适的位置
    update_bars(arr)  # 更新可视化
    plt.pause(0.00005)
    return i + 1

# 更新条形图
def update_bars(arr):
    plt.clf()  # 清空当前图形
    bars = plt.bar(range(len(arr)), arr, color='b')  # 绘制条形图
    plt.title('Quick Sort Visualization')
    plt.ylim(0, max(arr) + 1)  # 设置y轴范围
    plt.pause(0.1)  # 短暂暂停以便可视化


from threading import Thread


if __name__ == '__main__':
    # 示例数组
    array = [85, 19, 99, 31, 87, 97, 98, 13, 10, 79, 83, 58, 21, 54, 92, 46, 22, 86, 90, 68, 56, 63, 96, 6, 84, 33, 26,
             38, 61, 15, 64, 12, 36, 65, 48, 14, 8, 37, 88, 59, 66, 11, 16, 94, 34, 45, 35, 57, 70, 93, 69, 49, 4, 2,
             82, 5, 24, 74, 73, 7, 41, 44, 29, 32, 72, 28, 89, 71, 18, 77, 76, 3, 9, 62, 55, 80, 17, 20, 42, 52, 50, 78,
             53, 81, 60, 95, 91, 67, 1, 27, 39, 23, 43, 47, 25, 30, 40, 51, 75]
    # 用于更新条形图的全局变量
    bars = []

    # # 冒泡排序
    # bubble_sort_visualization(array)
    # 快速排序
    # quick_sort_visualization(array, 0, len(array) - 1)
    # # 选择排序
    # selection_sort_visualization(array)
    # # 并归排序
    # visualize_merge_sort(array)
    # # 插入排序
    # insertion_sort_visualization(array)
    # # 堆排序
    # heap_sort_visualization(array)
    # # 希尔排序
    # shell_sort_visualization(array)