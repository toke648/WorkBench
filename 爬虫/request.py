#导入 requests 模块
import requests
#声明请求的URL地址
url = 'http://172.16.123.41:8888/Spider/Http/headerReturn'
#------------------------示例1：通过get/post不同请求方式，来发起请求-----------------------------------#
#使用get请求方式，发送请求并获取响应，将所有响应信息封装成一个response响应对象
response = requests.get(url)
#使用post请求方式
requests.post(url)
#------------------------示例2：通过get/post发送请求时，使用表单，发送参数---------------------------------------#
#get请求方式发送参数1：可以在url后面通过   url?参数名1=参数值1&参数名2=参数值2来设置和传递参数
response = requests.get(url+'?account=zhangsan&password=123456')
#get请求方式发送参数2：通过一个字符串字典来组织和传递参数
information = {'name': 'jiangshihao', 'sex': 'man','hobby':['football', 'basketball']}
response = requests.get(url,params=information)
#post请求方式发送参数：通过一个字符串字典来组织和传递参数
requests.post(url,params=information)
#-------------------------示例3：发送请求时，定制请求头信息--------------------------------------------#
#组织一个请求头的字典，格式是{'参数名':'参数值'}
headInfo = {
    'Connection':'keep-alive',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36 Edg/134.0.0.0'}
#发送请求时，指定请求头使用自定义字典
response = requests.get(url,headers=headInfo)
#-------------------------示例4：发送请求时，设定超时时间--------------------------------------------#
#requests 在经过以 timeout 参数设定的秒数时间之后停止等待响应。基本上所有的生产代码都应该使用这一参数。如果不使用，你的程序可能会永远失去响应
#timeout 仅对连接过程有效，与响应体的下载无关。
# timeout 并不是整个下载响应的时间限制，而是如果服务器在 timeout 秒内没有应答，将会引发一个异常（更精确地说，是在 timeout 秒内没有从基础套接字上接收到任何字节的数据时）。
# 如果未显式指定超时参数，则请求不会超时，一直等待响应。
requests.get(url, timeout=0.001)


