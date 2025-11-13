import pywifi
from pywifi import const
import time

def scan_wifi():
    wifi = pywifi.PyWiFi()
    iface = wifi.interfaces()[0]  # 使用第一个WiFi接口
    iface.scan()  # 扫描附近的WiFi网络
    time.sleep(2)  # 等待扫描完成
    
    networks = iface.scan_results()
    print("发现以下WiFi网络：")

    
    for network in networks:
        print(f"SSID: {network.ssid}, 信号强度: {network.signal}")

if __name__ == "__main__":
    try:
        scan_wifi()
    except Exception as e:
        print(f"发生错误: {e}")


import subprocess
import re

def get_local_wifi_info():
    try:
        # 获取所有 WiFi 配置文件
        result = subprocess.run(
            ["netsh", "wlan", "show", "profiles"],
            capture_output=True,
            text=True,
            check=True
        )
        output = result.stdout

        # 提取 WiFi 名称（SSID）
        profiles = re.findall(r"All User Profile\s*:\s*(.+)", output)
        if not profiles:
            print("未找到已保存的 WiFi 配置文件。")
            return

        print("本地保存的 WiFi 网络：")
        for profile in profiles:
            profile = profile.strip()
            # 获取每个 WiFi 配置文件的详细信息（包括密码）
            profile_info = subprocess.run(
                ["netsh", "wlan", "show", "profile", f"name={profile}", "key=clear"],
                capture_output=True,
                text=True,
                check=True
            )
            profile_output = profile_info.stdout

            # 提取 SSID 和密码
            ssid_match = re.search(r"SSID name\s*:\s*\"(.+)\"", profile_output)
            key_match = re.search(r"Key Content\s*:\s*(.+)", profile_output)

            ssid = ssid_match.group(1) if ssid_match else profile
            key = key_match.group(1) if key_match else "未找到密码（可能是开放网络或无权限）"

            print(f"SSID: {ssid}")
            print(f"密码: {key}")
            print("-" * 40)

    except subprocess.CalledProcessError as e:
        print(f"执行 netsh 命令时出错: {e}")
    except Exception as e:
        print(f"发生错误: {e}")

if __name__ == "__main__":
    get_local_wifi_info()


import subprocess
import re

def get_local_wifi_info():
    try:
        # 获取所有 WiFi 配置文件
        result = subprocess.run(
            ["netsh", "wlan", "show", "profiles"],
            capture_output=True,
            text=True,
            encoding='utf-8',  # 使用 UTF-8 编码
            errors='ignore'    # 忽略无法解码的字符
        )
        output = result.stdout

        # 提取 WiFi 名称（SSID）
        profiles = re.findall(r"All User Profile\s*:\s*(.+)", output)
        if not profiles:
            print("未找到已保存的 WiFi 配置文件。")
            return

        print("本地保存的 WiFi 网络：")
        for profile in profiles:
            profile = profile.strip()
            # 获取每个 WiFi 配置文件的详细信息（包括密码）
            try:
                profile_info = subprocess.run(
                    ["netsh", "wlan", "show", "profile", f"name={profile}", "key=clear"],
                    capture_output=True,
                    text=True,
                    encoding='utf-8',  # 使用 UTF-8 编码
                    errors='ignore'    # 忽略无法解码的字符
                )
                profile_output = profile_info.stdout

                # 提取 SSID 和密码
                ssid_match = re.search(r"SSID name\s*:\s*\"(.+)\"", profile_output)
                key_match = re.search(r"Key Content\s*:\s*(.+)", profile_output)

                ssid = ssid_match.group(1) if ssid_match else profile
                key = key_match.group(1) if key_match else "未找到密码（可能是开放网络或无权限）"

                print(f"SSID: {ssid}")
                print(f"密码: {key}")
                print("-" * 40)

            except subprocess.CalledProcessError as e:
                print(f"无法获取 {profile} 的详细信息: {e}")
            except UnicodeDecodeError as e:
                print(f"解码 {profile} 的信息时出错: {e}")
            except Exception as e:
                print(f"处理 {profile} 时发生错误: {e}")

    except subprocess.CalledProcessError as e:
        print(f"执行 netsh 命令时出错: {e}")
    except Exception as e:
        print(f"发生错误: {e}")

if __name__ == "__main__":
    get_local_wifi_info()