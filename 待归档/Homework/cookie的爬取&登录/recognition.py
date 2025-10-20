# -*- coding: utf-8 -*-
import json
import base64
import os
import ssl

try:
    from urllib.error import HTTPError
    from urllib.request import Request, urlopen
except ImportError:
    from urllib2 import Request, urlopen, HTTPError

context = ssl._create_unverified_context()


def get_img(img_file):
    """将本地图片转成base64编码的字符串，或者直接返回图片链接"""
    # 简单判断是否为图片链接
    if img_file.startswith("http"):
        return img_file
    else:
        with open(os.path.expanduser(img_file), 'rb') as f:  # 以二进制读取本地图片
            data = f.read()
    try:
        encodestr = str(base64.b64encode(data), 'utf-8')
    except TypeError:
        encodestr = base64.b64encode(data)

    return encodestr

# 请求接口
REQUEST_URL = "https://gjbsb.market.alicloudapi.com/ocrservice/advanced"
def posturl(headers, body):
    """发送请求，获取识别结果"""
    try:
        params = json.dumps(body).encode(encoding='UTF8')
        req = Request(REQUEST_URL, params, headers)
        r = urlopen(req, context=context)
        html = r.read()
        return html.decode("utf8")
    except HTTPError as e:
        print(e.code)
        print(e.read().decode("utf8"))


def request(appcode, img_file, params):
    # 请求参数
    if params is None:
        params = {}
    img = get_img(img_file)
    if img.startswith('http'):  # img 表示图片链接
        params.update({'url': img})
    else:  # img 表示图片base64
        params.update({'img': img})

    # 请求头
    headers = {
        'Authorization': 'APPCODE %s' % appcode,
        'Content-Type': 'application/json; charset=UTF-8'
    }

    response = posturl(headers, params)
    return response

def run():
    """
    运行函数
    :return:
        返回识别结果
    """
    return request(appcode, img_file, params)


if __name__ == '__main__':
    # 请求接口
    REQUEST_URL = "https://gjbsb.market.alicloudapi.com/ocrservice/advanced"

    # 配置信息
    appcode = "95eaaede7e784cb0a87ab55c8445a766"
    img_file = "./captcha.png"
    params = {
        # 是否需要识别结果中每一行的置信度，默认不需要。 true：需要 false：不需要
        "prob": False,
        # 是否需要单字识别功能，默认不需要。 true：需要 false：不需要
        "charInfo": False,
        # 是否需要自动旋转功能，默认不需要。 true：需要 false：不需要
        "rotate": False,
        # 是否需要表格识别功能，默认不需要。 true：需要 false：不需要
        "table": False,
        # 字块返回顺序，false表示从左往右，从上到下的顺序，true表示从上到下，从左往右的顺序，默认false
        "sortPage": False,
        # 是否需要去除印章功能，默认不需要。true：需要 false：不需要
        "noStamp": False,
        # 是否需要图案检测功能，默认不需要。true：需要 false：不需要
        "figure": False,
        # 是否需要成行返回功能，默认不需要。true：需要 false：不需要
        "row": False,
        # 是否需要分段功能，默认不需要。true：需要 false：不需要
        "paragraph": False,
        # 图片旋转后，是否需要返回原始坐标，默认不需要。true：需要  false：不需要
        "oricoord": True
    }

    message = request(appcode, img_file, params)

    print(message['content'])

    # import json
    # message = '{"sid":"95246a4ddeadba2492f40f4e4be26315d0abf8aae801ca51727b6c677632bd3ac000a754","prism_version":"1.0.9","prism_wnum":1,"prism_wordsInfo":[{"word":"me3xy","pos":[{"x":2,"y":8},{"x":63,"y":8},{"x":63,"y":30},{"x":2,"y":30}],"direction":0,"angle":-90,"x":21,"y":-11,"width":22,"height":61}],"height":34,"width":68,"orgHeight":34,"orgWidth":68,"content":"me3xy ","algo_version":""}'

    # # 怎么获取content中的信息
    # print(json.loads(message)['content'])

