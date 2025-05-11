# python 中几种常用的Web通信框架
import flask
import socket
import fastapi
from flask import Flask
from fastapi import FastAPI

# app = FastAPI()  # 创建 api 对象
#
#
# @app.get("/")  # 根路由
# def root():
#     return {"武汉": "加油！！！"}
#
#
# @app.get("/say/{data}")
# def say(data: str, q: int):
#     return {"data": data, "item": q}


# from flask import Flask, jsonify
#
# app = Flask(__name__)
#
# @app.route('/greet/<name>')
# def greet(name):
#     return jsonify(message=f'你好, {name}!')
#
# if __name__ == '__main__':
#     app.run(debug=True)


from flask import Flask, jsonify, render_template

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/greet/<name>')
def greet(name):
    return jsonify(message=f'你好, {name}!')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)