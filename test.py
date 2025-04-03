import pyopencl as cl
import numpy as np

# 选择平台和设备（通常选择Intel OpenCL设备）
platform = cl.get_platforms()[0]  # 获取第一个平台
device = platform.get_devices()[0]  # 获取第一个设备（一般是GPU）

# 创建OpenCL上下文和命令队列
context = cl.Context([device])
queue = cl.CommandQueue(context, device)

# 创建输入数据（例如，两个数组相加）
a = np.array([1, 2, 3, 4, 5], dtype=np.float32)
b = np.array([5, 4, 3, 2, 1], dtype=np.float32)

# 创建缓冲区
a_buffer = cl.Buffer(context, cl.mem_flags.READ_ONLY | cl.mem_flags.COPY_HOST_PTR, hostbuf=a)
b_buffer = cl.Buffer(context, cl.mem_flags.READ_ONLY | cl.mem_flags.COPY_HOST_PTR, hostbuf=b)
result_buffer = cl.Buffer(context, cl.mem_flags.WRITE_ONLY, a.nbytes)

# 编写OpenCL程序（代码在GPU上执行）
program_src = """
__kernel void add_arrays(__global const float *a, __global const float *b, __global float *result)
{
    int id = get_global_id(0);
    result[id] = a[id] + b[id];
}
"""
program = cl.Program(context, program_src).build()

# 执行OpenCL程序
program.add_arrays(queue, a.shape, None, a_buffer, b_buffer, result_buffer)

# 获取结果
result = np.empty_like(a)
cl.enqueue_copy(queue, result, result_buffer).wait()

print("结果:", result)
