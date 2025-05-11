from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS

app = Flask(__name__, static_folder="static")  # 指定静态文件夹
CORS(app)

# 初始配置
settings = {
    "openai_api_key": "your-api-key",
    "openai_base_url": "http://localhost:11434",
    "models": "qwen-plus"
}

# 提供前端页面
@app.route('/')
def index():
    return send_from_directory("static", "index.html")

# 获取当前设置
@app.route('/settings', methods=['GET'])
def get_settings():
    return jsonify(settings)

# 更新设置
@app.route('/update_settings', methods=['POST'])
def update_settings():
    data = request.json
    settings.update(data)
    return jsonify({"message": "Settings updated", "new_settings": settings})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)  # 开启 debug 方便调试
