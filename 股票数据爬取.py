"""
python实现的东方财富网站股票数据爬取
但因为官网数据是用JS渲染出来的，没法直接爬取

我用的方法是去后台查json文件，然后找到包含股票数据的url链接，然后使用正则匹配出数据的
（是用来训练模型的）

也可以试试用selenium来实现，看看能不能获取到数据
Ciallo～(∠・ω< )⌒☆

"""

import re
import requests
import json

url = 'https://push2his.eastmoney.com/api/qt/stock/kline/get?cb=jQuery351016702133557143928_1757311398446&secid=1.000300&ut=fa5fd1943c7b386f172d6893dbfba10b&fields1=f1%2Cf2%2Cf3%2Cf4%2Cf5%2Cf6&fields2=f51%2Cf52%2Cf53%2Cf54%2Cf55%2Cf56%2Cf57%2Cf58%2Cf59%2Cf60%2Cf61&klt=101&fqt=1&beg=0&end=20500101&smplmt=460&lmt=1000000&_=1757311398447'

repsonse = requests.get(url)
text = repsonse.text
# print(repsonse.text)
# print(repsonse.status_code)

# 数据示例
"""
jQuery35109392514059566558_1756826314307({"rc":0,"rt":17,"svr":181669694,"lt":1,"full":0,"dlmkts":"","data":{"code":"000300","market":1,"name":"沪深300","decimal":2,"dktotal":5021,"preKPrice":3941.42,"klines":["2025-03-12,3946.86,3927.23,3953.61,3921.47,156732190,309627267364.80,0.82,-0.36,-14.19,0.48","2025-03-13,3925.74,3911.58,3939.29,3897.38,
"""

# 提取 JSON 数据 // 因为内部有括号，所以用正则匹配先去除掉里面的括号
match = re.search(r'\((\{.*\})\)', text)

json_str = match.group(1) # 获取括号中的内容
data = json.loads(json_str) # 将字符串转为字典

gupiao_name = data['data']['name']
gupiao_size = len(data['data']['klines'])

# for line in data['data']['klines']:
#     print(line.split(','))

data_list = [line.split(',') for line in data['data']['klines']]


import pandas as pd

df = pd.DataFrame(data_list)
df.columns = ["date", "open", "close", "high", "low", 
           "volume", "amount", "amplitude", "change_pct", 
           "change_val", "turnover"]
df['date'] = pd.to_datetime(df['date'])
df.set_index('date', inplace=True)
df.to_csv(f'{gupiao_name}-{gupiao_size}.csv', index=False)

print(df)

data = pd.read_csv('/沪深300-120.csv')

