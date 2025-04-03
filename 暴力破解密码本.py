import itertools
import string
from tqdm import tqdm
from concurrent.futures import ThreadPoolExecutor

# 定义字符集
charset_numbers = string.digits  # 数字
charset_letters = string.ascii_letters  # 字母（大小写）

# 排除特殊字符
excluded_symbols = "!@#$%^&*"
charset_all = charset_numbers + charset_letters  # 排除特殊字符后的字符集

# 常用密码列表（加入了大小写版本）
common_passwords = [
    "123456", "password", "12345678", "qwerty", "abc123", "12345",
    "password1", "123123", "admin", "welcome", "123qwe", "letmein",
    "123456A", "Password", "Qwerty", "Abc123", "Admin123"  # 加入大小写密码
]

# 设置最小和最大密码长度
min_length = 6
max_length = 8  # 可以根据需求调整最大密码长度

# 输出文件路径
output_file = "passwords.txt"


# 写入常用密码的函数
def write_common_passwords(f):
    for password in common_passwords:
        f.write(password + "\n")


# 生成密码并写入文件
def generate_passwords_for_length(length, charset_all, f):
    # 生成给定长度的所有密码组合
    total_combinations = len(charset_all) ** length  # 计算当前长度下的密码数量
    for password in tqdm(itertools.product(charset_all, repeat=length), total=total_combinations,
                         desc=f"生成长度 {length} 的密码"):
        f.write(''.join(password) + "\n")


# 主生成函数，使用多线程并行化生成密码
def generate_passwords(min_length, max_length, charset_all, output_file):
    with open(output_file, "w") as f:
        # 首先写入常用密码
        write_common_passwords(f)

        # 使用多线程生成所有密码
        with ThreadPoolExecutor() as executor:
            # 对于每个长度的密码，启动一个线程生成
            for length in range(min_length, max_length + 1):
                executor.submit(generate_passwords_for_length, length, charset_all, f)


# 调用主函数
if __name__ == "__main__":
    generate_passwords(min_length, max_length, charset_all, output_file)
    print(f"密码本已生成，所有密码已保存在 '{output_file}' 文件中。")
