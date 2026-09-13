# # -------------------------------------------------------------------------------------------------
# import requests
# # 定义工具函数：在电脑上打开URL网址


# import logging

# logger = logging.getLogger(__name__)


# def 酷狗API搜歌(url: str) -> dict:
#     """
#     搜索歌曲并返回基础信息与播放链接。提供歌曲名即可。
#     适用于获取歌曲播放链接、歌手、专辑等元信息。
#     """
#     try:
#         response = requests.get(
#             f"http://mobilecdn.kugou.com/api/v3/search/song?format=json&keyword={song_name}&page=1")
#         data = response.json()
#         song = data['data']['info'][0]
        
#         songname = song['songname']
#         singername = song['singername']
#         album_id = song['album_id']
#         audio_id = song['audio_id']
#         hash = song['hash']
#         duration = song['duration']
#         pay_type = song['pay_type']

#         if pay_type == 0: pay_type="免费"
#         elif pay_type == 3: pay_type == "付费"

#         hash_url = f"http://m.kugou.com/app/i/getSongInfo.php?cmd=playInfo&hash={hash}"
#         song_info = requests.get(hash_url).json()
#         mp3_url = song_info.get('url')
#         backup_url = song_info.get('backup_url')

        

#         return {
#             "success": True,
#             "songname": songname,
#             "singer": singername,
#             "album_id": album_id,
#             "audio_id": audio_id,
#             "duration": duration,
#             "pay_type": pay_type,
#             "url": mp3_url,
#             "backup_url": backup_url
#         }

#     except Exception as e:
#         logger.error(f"Error searching song: {e}")
#         return {"success": False, "error": str(e)}
# # -------------------------------------------------------------------------------------------------

# print(酷狗API搜歌("Moon"))  








# import requests
# import logging
# import time

# # 配置日志记录
# # 日志级别设为INFO, 输出格式为%(asctime)s - %(name)s - %(levelname)s - %(message)s, 颜色为绿色
# logging.basicConfig(level=logging.INFO, format='\033[32m%(asctime)s - %(name)s - %(levelname)s - %(message)s\033[0m')
# logger = logging.getLogger(__name__)
# logger.setLevel(logging.INFO)

# song_name = "世界计划"

# response = requests.get(
#     f"http://mobilecdn.kugou.com/api/v3/search/song?format=json&keyword={song_name}&page=1")
# logger.info("\033[34m" + response.url + "\033[0m")

# # 获取数据
# data = response.json()
# logger.info("\033[34m" + "歌曲数量：" + str(len(data['data']['info'])) + "\033[0m")
# for song in data['data']['info']:
#     # 获取歌曲信息
#     song = data['data']['info'][0]

#     songname = song['songname']
#     singername = song['singername']
#     album_id = song['album_id']
#     audio_id = song['audio_id']
#     hash = song['hash']
#     duration = song['duration']
#     pay_type = song['pay_type']

#     if pay_type == 0: pay_type="免费"
#     elif pay_type == 3: pay_type="付费"

#     logger.info("\033[34m" + "歌曲名：" + songname + "\033[0m")
#     logger.info("\033[34m" + "歌手：" + singername + "\033[0m")
#     logger.info("\033[34m" + "专辑ID：" + str(album_id) + "\033[0m")
#     logger.info("\033[34m" + "音频ID：" + str(audio_id) + "\033[0m")
#     logger.info("\033[34m" + "Hash值：" + hash + "\033[0m")
#     logger.info("\033[34m" + "时长：" + str(duration) + "秒" + "\033[0m")
#     logger.info("\033[34m" + "支付类型：" + str(pay_type) + "\033[0m")

#     print()
#     time.sleep(1)


#     hash_url = f"http://m.kugou.com/app/i/getSongInfo.php?cmd=playInfo&hash={song['hash']}"

#     response = requests.get(hash_url)
#     logger.info("\033[34m" + response.url + "\033[0m")

#     song_info = requests.get(hash_url).json()
#     mp3_url = song_info.get('url')
#     # TypeError: can only concatenate str (not "dict") to str
#     backup_url = song_info.get('backup_url')

#     # 打印播放链接
#     logger.info("\033[34m" + "播放链接：" + mp3_url + "\033[0m")
#     logger.info("\033[34m" + "备份链接：" + backup_url[0] + "\033[0m")











# import requests
# import logging
# import time
# import pandas as pd

# # 配置日志记录
# # 日志级别设为INFO, 输出格式为%(asctime)s - %(name)s - %(levelname)s - %(message)s, 颜色为绿色
# logging.basicConfig(level=logging.INFO, format='\033[32m%(asctime)s - %(name)s - %(levelname)s - %(message)s\033[0m')
# logger = logging.getLogger(__name__)
# logger.setLevel(logging.INFO)
# """
# 日志内容划分：
# 主要的：绿色
# 提示：蓝色
# 错误：红色
# 重复获取：黄色

# """


# def kudogoAPI_get(
#         song_name= "25时",
#         headers = dict
#         ) -> dict:
#     """
#     搜索歌曲并返回基础信息与播放链接。提供歌曲名即可。
#     适用于获取歌曲播放链接、歌手、专辑等元信息。
#     """

#     url = f"http://mobilecdn.kugou.com/api/v3/search/song?format=json&keyword={song_name}&page=1"

#     response = requests.get(url, headers=headers)
#     logger.info("\033[34m" + url + "\033[0m")

#     # 获取数据
#     data = response.json()
#     logger.info("\033[34m" + "歌曲数量：" + str(len(data['data']['info'])) + "\033[0m")

#     # 获取歌曲信息
#     # song = data['data']['info'][0]

#     time.sleep(2)

#     song_meta = {}

#     for song in data['data']['info']:

#         hash = song['hash']
#         pay_type = song['pay_type']

#         pay_type="免费" if pay_type == 0 else "付费" if pay_type == 3 else f"未知{pay_type}"

#         for key, value in song.items():
#             if key in ['songname', 'singername', 'album_id', 'audio_id', 'duration', 'pay_type']:
#                 logger.info("\033[34m" + str(key) + "：" + str(value) + "\033[0m")
#             song_meta[key] = value
#             print()

#         logger.info("\033[34m" + "支付类型：" + str(pay_type) + "\033[0m")

#     return song_meta


# def kudogoAPI_get_hash_url(
#         hash_list: list,
#         headers: dict
#         ) -> dict:
#     """
#     获取歌曲播放链接。提供Hash值即可。
#     适用于获取歌曲播放链接、歌手、专辑等元信息。
#     """
    
#     mp3_download_url = {}

#     # 获取失败的重试机制

#     for hash in hash_list:
#         try:
#             print(mp3_download_url)
#             hash_url = f"http://m.kugou.com/app/i/getSongInfo.php?cmd=playInfo&hash={hash}"
#             response = requests.get(hash_url, headers=headers).json()

            
#             logger.info("\033[34m" + f"http://m.kugou.com/app/i/getSongInfo.php?cmd=playInfo&hash={hash}" + "\033[0m")

#             for key, value in response.items():
#                 if key in ['singerName', 'songName', 'url', 'backup_url', 'errcode', 'status', 'error']:
#                     logger.info("\033[34m" + str(key) + "：" + str(value) + "\033[0m")

#                     if key == 'url':
#                         mp3_download_url[f'{response['songName']}_url'] = value
#                     if key == 'backup_url':
#                         mp3_download_url[f'{response['songName']}_backup_url'] = value

#             print(f"{response['errcode']}")


#             if response['errcode'] == 1002:
#                 logger.warning("\033[33m" + "获取失败，正在重试..." + "\033[0m")
#                 for i in range(5):
#                     # 重复获取日志颜色为黄色
#                     logger.warning("\033[33m" + f"第{i+1}次重试" + "\033[0m")
#                     hash_url = f"http://m.kugou.com/app/i/getSongInfo.php?cmd=playInfo&hash={hash}"
#                     response = requests.get(hash_url, headers=headers).json()

#                     for key, value in response.items():
#                         name = response['songName']
#                         if key in ['singerName', 'songName', 'url', 'backup_url', 'errcode', 'status', 'error']:
#                             logger.info("\033[34m" + str(key) + "：" + str(value) + "\033[0m")

#                             if key == 'url':
#                                 mp3_download_url[f'{name}_url'] = value
#                             if key == 'backup_url':
#                                 mp3_download_url[f'{name}_backup_url'] = str(response['backup_url'])

#                     time.sleep(10)

#                     if response['errcode'] != 1002:
#                         logger.info("\033[34m" + "获取成功" + "\033[0m")
#                         break
#                     if i > 4:
#                         logger.error("\033[31m" + "获取失败，请检查网络" + "\033[0m")
            
#             print()
#             time.sleep(5)

#         except KeyboardInterrupt:
             
             
#             logger.info("\033[34m" + "程序被用户中断" + "\033[0m")
#             break
#         # except Exception as e:
#         #     # 红色字体
#         #     logger.error("\033[31m" + str(e) + "\033[0m")


#     return mp3_download_url

# from concurrent.futures import ThreadPoolExecutor
# import re

# def kudogoAPI_Song_choose(
#         song_name: str,
#         headers: dict
#         ) -> None:
#     """
#     选择歌曲。提供歌曲名称即可。
#     适用于选择歌曲。
#     """

#     input_song_name = input("\033[34m" + "请输入歌曲名称：" + "\033[0m")
#     song_meta = kudogoAPI_get(input_song_name)

#     for song_name, hash in song_meta.items():
#         # 可选择音乐模式，将列表中的音乐对应1/2/3/...
#         print(f"{song_name}：{hash}")
#         choice = input("\033[34m" + "请选择：" + "\033[0m")
#         if choice == "":
#             print(f"请输入选择")
#         elif re.match(r"^\d+$", choice):
#             print(f"您选择了{song_name}")
#             return hash
#         else:
#             print(f"请输入正确的选择")

# import random

# def url_Proxy_Pool(
#         # url_list: list,
#         # headers: dict
#         ):
#     """
#     多线程下载歌曲。提供歌曲名称即可。
#     适用于多线程下载歌曲。
#     """

#     headers_loop = {
#         0 : "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36 Edg/91.0.8640.59",
#         1 : "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36 Edg/143.0.0.0",
#         2 : "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36 Edg/91.0.8640.59 Safari/537.36",
#         3 : "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36 OPR/77.0.4054.277",
#     }

#     ip_proxy_pool = {

#     }

#     # 创建线程池
#     # with ThreadPoolExecutor(max_workers=10) as executor:
#     #     # 提交任务
#     #     for url in url_list:
#     #         executor.submit(requests.get, url, headers=headers)
    
#     return random.choice(headers_loop)


# def kudogoAPI_Download(
#         song_name: str,
#         headers: dict
#         ) -> None:
#     """
#     下载歌曲。提供歌曲名称即可。
#     适用于下载歌曲。
#     """

# # 内部链接查询/缓存机制
# # 1. 先查询缓存中是否有该歌曲的链接
# # 2. 如果有，直接返回链接
# # 3. 如果没有，查询酷狗音乐API，获取链接
# # 4. 将链接缓存到本地，方便下次查询
# def kudogoAPI_Cache(
#         song_name: str,
#         headers: dict
#         ) -> None:
#     """
#     缓存歌曲链接。提供歌曲名称即可。
#     适用于缓存歌曲链接。
#     """

# # 数据库实现
# def Dataset_Cache(
#         song_name: str,
#         headers: dict
#         ) -> None:
#     """
#     缓存数据集。提供歌曲名称即可。
#     适用于缓存数据集。
#     """

# import flask
# from flask import Flask
# # 前端交互

# def run():
#     """
#     运行程序。
#     """

# app = Flask(__name__)

# @app.route("/")

# def appa():
#     return "Hello, World!"

# app.run(debug=True)

# @app.route("/")
# def index():
#     return "Hello, World!"

# app.run(debug=True)

# if __name__ == "__main__":
#     """
#     测试用例
#     """
#     song_name = "崩坏"

#     HEADERS = {
#         "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
#         "accept-encoding": "gzip, deflate",
#         "accept-language": "zh-TW,zh-CN;q=0.9,zh;q=0.8,en-US;q=0.7,en;q=0.6",
#         "cache-control": "max-age=0",
#         "cookie": "kg_dfid=4XVLMI3XM1Rq3tUcNz1SqkXi; Hm_lvt_aedee6983d4cfc62f509129360d6bb3d=1765031628; kg_dfid_collect=d41d8cd98f00b204e9800998ecf8427e; KuGoo=KugooID=2111223165&KugooPwd=3B9AA2AB4CD38A7F0DEC02B19AFF14A3&NickName=%u5c71%u7530%u51c9&Pic=http://imge.kugou.com/kugouicon/165/20230518/20230518161740791882.jpg&RegState=1&RegFrom=&t=ae12c87b02377a8a1ae3a089e01c0164405fb6c40084bf6cfed366c3806dc82b&a_id=1014&ct=1765721203&UserName=%u006b%u0067%u006f%u0070%u0065%u006e%u0032%u0031%u0031%u0031%u0032%u0032%u0033%u0031%u0036%u0035&t1=; KugooID=2111223165; t=ae12c87b02377a8a1ae3a089e01c0164405fb6c40084bf6cfed366c3806dc82b; a_id=1014; UserName=kgopen2111223165; mid=250c116d6a1522bb2a012e852527b842; dfid=4XVLMI3XM1Rq3tUcNz1SqkXi; kg_mid_temp=250c116d6a1522bb2a012e852527b842",
#         "user-agent": f"{url_Proxy_Pool()}"
#     }
    
#     song_meta = kudogoAPI_get(song_name, HEADERS)
#     hash_list = []
#     for song_name, hash in song_meta.items():
#         hash_list.append(hash)

#     mp3_download_url = kudogoAPI_get_hash_url(hash_list, HEADERS)
#     print(mp3_download_url)

#     # 转换为DataFrame
#     df = pd.DataFrame(mp3_download_url, index=[0])
#     print(df)

#     df.to_csv('mp3_download_url.csv', index=False)







import requests
import logging
import time
import pandas as pd
import os

# 配置日志记录
# 日志级别设为INFO, 输出格式为%(asctime)s - %(name)s - %(levelname)s - %(message)s, 颜色为绿色
logging.basicConfig(level=logging.INFO, format='\033[32m%(asctime)s - %(name)s - %(levelname)s - %(message)s\033[0m')
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
"""
日志内容划分：
主要的：绿色
提示：蓝色
错误：红色
重复获取：黄色

"""

def kudogoAPI_get(
        song_name= "25时",
        headers= None
        ) -> list:
    """
    搜索歌曲并返回基础信息与播放链接。提供歌曲名即可。
    适用于获取歌曲播放链接、歌手、专辑等元信息。
    """

    r = requests.get(
        f"http://mobilecdn.kugou.com/api/v3/search/song?format=json&keyword={song_name}&page=1",
        headers=headers)
    logger.info("\033[34m" + f"http://mobilecdn.kugou.com/api/v3/search/song?format=json&keyword={song_name}&page=1" + "\033[0m")

    # 获取数据
    data = r.json()
    logger.info("\033[34m" + "歌曲数量：" + str(len(data['data']['info'])) + "\033[0m")

    # 获取歌曲信息
    # song = data['data']['info'][0]

    time.sleep(1)

    song_list = []

    for song in data['data']['info']:

        hash = song['hash']
        pay_type = song['pay_type']

        pay_type="免费" if pay_type == 0 else "付费" if pay_type == 3 else f"未知{pay_type}"

        for key, value in song.items():
            if key in ['songname', 'singername', 'album_id', 'audio_id', 'duration', 'pay_type']:
                logger.info("\033[34m" + str(key) + "：" + str(value) + "\033[0m")

        logger.info("\033[34m" + "支付类型：" + str(pay_type) + "\033[0m")

        song_list.append({
            'songname': song['songname'],
            'hash': hash,
        })

    return song_list


def kudogoAPI_get_hash_url(
        hash: str,
        headers: dict
        ) -> list:
    """
    获取歌曲播放链接。提供Hash值即可。
    适用于获取歌曲播放链接、歌手、专辑等元信息。
    """

    mp3_url = []

    # 获取失败的重试机制
    try:
        # print(mp3_url)
        hash_url = f"http://m.kugou.com/app/i/getSongInfo.php?cmd=playInfo&hash={hash}"

        r = requests.get(hash_url, headers=headers).json()
        logger.info("\033[34m" + f"http://m.kugou.com/app/i/getSongInfo.php?cmd=playInfo&hash={hash}" + "\033[0m")

        for key, value in r.items():
            if key in ['singerName', 'songName', 'url', 'backup_url', 'errcode', 'status', 'error']:
                logger.info("\033[34m" + str(key) + "：" + str(value) + "\033[0m")

        backup_url = r['url']
        url = r['backup_url']

        mp3_url.append({
            'url': url,
            'backup_url': backup_url,
        })

        print(f"{r['errcode']}")

        if r['errcode'] == 1002:
            logger.warning("\033[33m" + "获取失败，正在重试..." + "\033[0m")
            for i in range(5):
                # 重复获取日志颜色为黄色
                logger.warning("\033[33m" + f"第{i+1}次重试" + "\033[0m")
                hash_url = f"http://m.kugou.com/app/i/getSongInfo.php?cmd=playInfo&hash={hash}"
                r = requests.get(hash_url, headers=headers).json()

                mp3_url.append({
                    'url': url,
                    'backup_url': backup_url,
                })

                time.sleep(5)

                if r['errcode'] != 1002:
                    logger.info("\033[34m" + "获取成功" + "\033[0m")
                    break
                if i > 4:
                    logger.error("\033[31m" + "获取失败，请检查网络" + "\033[0m")
        
        print()
        time.sleep(5)

        return mp3_url

    except KeyboardInterrupt:
        logger.info("\033[34m" + "程序被用户中断" + "\033[0m")
        return []

    # except Exception as e:
    #     # 红色字体
    #     logger.error("\033[31m" + str(e) + "\033[0m")




if __name__ == "__main__":
    """
    测试用例

    0.搜索歌曲
    1.获取歌曲列表
    2.判断是否在数据库(csv/db)中 有——>跳过，没有——>添加到数据库
    3.选择下载歌曲
    4.判断下载链接是否在数据库中，有——>跳过，没有——>添加到数据库
    5.获得下载链接
    """
    
    """0. 输入搜索关键词"""

    df = pd.DataFrame()
    # 没有mp3_download_url.csv文件就创建一个，否则读取mp3_download_url.csv文件
    if not os.path.exists("mp3_download_url.csv"):
        df.to_csv("mp3_download_url.csv", index=False)
    else:
        df = pd.read_csv("mp3_download_url.csv")
    print(df)

    # df_song_db = song_names_value = df['songname'].values
    # print(df_song_db)
        
    search_name = input("请输入搜索内容：")
    if search_name == "":
        search_name = "崩坏"

    HEADERS = {
        "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
        "accept-encoding": "gzip, deflate",
        "accept-language": "zh-TW,zh-CN;q=0.9,zh;q=0.8,en-US;q=0.7,en;q=0.6",
        "cache-control": "max-age=0",
        "cookie": "kg_dfid=4XVLMI3XM1Rq3tUcNz1SqkXi; Hm_lvt_aedee6983d4cfc62f509129360d6bb3d=1765031628; kg_dfid_collect=d41d8cd98f00b204e9800998ecf8427e; KuGoo=KugooID=2111223165&KugooPwd=3B9AA2AB4CD38A7F0DEC02B19AFF14A3&NickName=%u5c71%u7530%u51c9&Pic=http://imge.kugou.com/kugouicon/165/20230518/20230518161740791882.jpg&RegState=1&RegFrom=&t=ae12c87b02377a8a1ae3a089e01c0164405fb6c40084bf6cfed366c3806dc82b&a_id=1014&ct=1765721203&UserName=%u006b%u0067%u006f%u0070%u0065%u006e%u0032%u0031%u0031%u0031%u0032%u0032%u0033%u0031%u0036%u0035&t1=; KugooID=2111223165; t=ae12c87b02377a8a1ae3a089e01c0164405fb6c40084bf6cfed366c3806dc82b; a_id=1014; UserName=kgopen2111223165; mid=250c116d6a1522bb2a012e852527b842; dfid=4XVLMI3XM1Rq3tUcNz1SqkXi; kg_mid_temp=250c116d6a1522bb2a012e852527b842",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36"
    }
    
    """1. 从 API 搜索 → 得到 song_list（list[dict]）"""

    # 解析存储操作，如果有搜索过的音乐从列表中读取，否则从API获取, 并添加到列表中
    song_list = kudogoAPI_get(search_name, HEADERS)
    print(song_list)
            
    # 显示效果对比如下
    df_song_list = pd.DataFrame(song_list)
    print(df_song_list)

    print(df_song_list['songname'].values)


    """3. 用户选择要下载的歌曲（name / index / all）"""

    song_name = input("请根据表单中的歌曲，输入需要下载的歌曲名称/索引号/或输入all下载所有歌曲：")
    
    if song_name == "":
        song_name = "Moon Halo"

    print(song_name)

    """
    4. 对选中的歌曲：
        - 如果 hash 不在 playinfo_db：
            → 调用 getSongInfo API
            → 存 url / backup_url
        - 否则：
            → 直接从数据库读
    """

    song_names_value = df_song_list['songname'].values

    for song in song_list:
        name = song['songname']
        print(name)

        # 检查歌曲是否在数据库中
        if name in song_names_value:
            # logger.info("\033[34m" + "歌曲 " + name + " 已在列表中" + "\033[0m")

            # 获取歌曲的播放链接
            if song_name == name:
                # 从API获取歌曲播放链接，并添加到列表中
                hash = song['hash']
                print(hash)

                mp3_url = kudogoAPI_get_hash_url(hash, HEADERS)
                song_list.append({
                    'songname': name,
                    'hash': hash,
                    'mp3_url': mp3_url,
                })
                break
            else:
                # 从数据库中获取歌曲播放链接
                mp3_url = song['mp3_url']
                song_list.append({
                    'songname': name,
                    'hash': hash,
                    'mp3_url': mp3_url,
                })
                break
        elif name not in song_names_value:
            logger.info("\033[34m" + "歌曲不在列表中" + "\033[0m")
    
"""5. 返回下载链接"""

print(song_list)

# 转换为DataFrame, 并保存到文件,保存模式为追加
df = pd.DataFrame(song_list)
df.to_csv('mp3_download_url.csv', index=False, mode='a', header=False)


