import os

log_dir = 'logs'
if os.path.exists(log_dir):
    if os.path.isfile(log_dir):  # 如果是文件
        os.remove(log_dir)       # 删除文件
    elif not os.path.isdir(log_dir):  # 如果既不是文件也不是目录
        raise ValueError(f"Path conflict: {log_dir} is not a valid directory or file.")

os.makedirs(log_dir, exist_ok=True)  # 确保日志目录存在

import os

print("Current Working Directory:", os.getcwd())
print("Log Directory:", os.path.abspath(log_dir))

