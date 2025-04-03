from flask import Flask, request, jsonify, render_template
import mysql.connector

app = Flask(__name__)

# 连接到 MySQL 数据库
def connect_to_database():
    return mysql.connector.connect(
        host="localhost",
        user="root",  # 替换为你的 MySQL 用户名
        password="srd217",  # 替换为你的 MySQL 密码
        database="library"
    )

# 首页路由，渲染前端页面
@app.route('/')
def index():
    return render_template('index.html')

# 添加书籍
@app.route('/add_book', methods=['POST'])
def add_book():
    data = request.json
    title = data['title']
    author = data['author']
    isbn = data['isbn']

    conn = connect_to_database()
    cursor = conn.cursor()
    query = "INSERT INTO books (title, author, isbn) VALUES (%s, %s, %s)"
    values = (title, author, isbn)
    cursor.execute(query, values)
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({"message": "Book added successfully!"}), 201

# 删除书籍
@app.route('/delete_book/<int:book_id>', methods=['DELETE'])
def delete_book(book_id):
    conn = connect_to_database()
    cursor = conn.cursor()
    query = "DELETE FROM books WHERE id = %s"
    values = (book_id,)
    cursor.execute(query, values)
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({"message": "Book deleted successfully!"}), 200

# 查找书籍
@app.route('/find_book/<string:title>', methods=['GET'])
def find_book(title):
    conn = connect_to_database()
    cursor = conn.cursor()
    query = "SELECT * FROM books WHERE title = %s"
    values = (title,)
    cursor.execute(query, values)
    result = cursor.fetchall()
    cursor.close()
    conn.close()
    if result:
        return jsonify(result), 200
    else:
        return jsonify({"message": "No book found with that title."}), 404

# 显示所有书籍
@app.route('/books', methods=['GET'])
def show_all_books():
    conn = connect_to_database()
    cursor = conn.cursor()
    query = "SELECT * FROM books"
    cursor.execute(query)
    result = cursor.fetchall()
    cursor.close()
    conn.close()
    if result:
        return jsonify(result), 200
    else:
        return jsonify({"message": "No books in the library."}), 404

if __name__ == "__main__":
    app.run(debug=True)