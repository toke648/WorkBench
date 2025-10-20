# from flask import Flask
#
# app = Flask(__name__)
#
# @app.route('/')
# def hello_world():
#     return 'Hello, World!'
#
# if __name__ == '__main__':
#     app.run(debug=True)




""" 自定义配置
# 获取目录下的templates中的index.html文件作为首页
app.template_folder = os.path.join(os.getcwd(), 'templates')
# 设置静态文件目录
app.static_folder = os.path.join(os.getcwd(), 'static')

"""

# U: 按道理来说，这些配置不是默认的吗？
# A: 但是我还是加上了，免得出错
# U: 那么如果直接默认配置应该怎么写？
# A: 直接使用 Flask 的默认配置即可，不需要手动设置
# A: 但是如果你需要自定义静态文件目录和模板目录，可以使用上面的代码
# U: 你能给我一个完整的例子吗？
# A: 当然可以，下面是一个完整的例子

from flask import Flask, render_template
from flask import Flask, request, jsonify
from flask import send_from_directory
from flask_cors import CORS
import edge_tts
import os

app = Flask(__name__) # 创建 Flask 应用
CORS(app) # 启用跨域请求支持

@app.route('/')
def home():
    return render_template('index.html')  # 从 templates 文件夹中渲染 index.html 模板



if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000)