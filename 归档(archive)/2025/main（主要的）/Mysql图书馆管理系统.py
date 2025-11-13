import pymysql
from pymysql.cursors import DictCursor
import re
from datetime import date, timedelta

class DBConnection:
    """数据库连接类，负责与MySQL交互"""
    def __init__(self):
        self.conn = pymysql.connect(
            host='localhost',
            user='root',
            password='123456',  # 请替换为实际密码
            database='library_management',
            charset='utf8mb4',
            cursorclass=DictCursor
        )
        self.cursor = self.conn.cursor()

    def execute(self, sql, params=None):
        """执行SQL语句（增删改）"""
        try:
            self.cursor.execute(sql, params)
            self.conn.commit()
            return self.cursor.rowcount
        except pymysql.Error as e:
            self.conn.rollback()
            print(f"数据库错误: {e}")
            return 0

    def query(self, sql, params=None):
        """执行查询语句"""
        self.cursor.execute(sql, params)
        return self.cursor.fetchall()

    def close(self):
        """关闭数据库连接"""
        self.cursor.close()
        self.conn.close()


class BookManager:
    """图书管理类，负责图书相关操作"""
    def __init__(self, db):
        self.db = db

    def add_book(self, title, author, publisher, year, category, price, stock):
        """添加新书"""
        sql = """
        INSERT INTO books (书名, 作者, 出版社, 出版年份, 分类, 价格, 库存数量)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        """
        result = self.db.execute(sql, (title, author, publisher, year, category, price, stock))
        return "添加成功" if result > 0 else "添加失败"

    def update_book(self, book_id, **kwargs):
        """更新图书信息（可选择性更新部分字段）"""
        if not kwargs:
            return "至少需要提供一个更新字段"
        
        set_clause = ", ".join([f"{key} = %s" for key in kwargs.keys()])
        params = list(kwargs.values()) + [book_id]
        
        sql = f"UPDATE books SET {set_clause} WHERE 图书编号 = %s"
        result = self.db.execute(sql, params)
        return "更新成功" if result > 0 else "更新失败或图书ID不存在"

    def delete_book(self, book_id):
        """删除图书（同时删除相关借阅记录）"""
        # 先删除借阅记录
        self.db.execute("DELETE FROM borrow_records WHERE 图书编号 = %s", (book_id,))
        # 再删除图书
        result = self.db.execute("DELETE FROM books WHERE 图书编号 = %s", (book_id,))
        return "删除成功" if result > 0 else "删除失败或图书ID不存在"

    def search_books(self, title=None, author=None, category=None, min_price=None, max_price=None):
        """多条件搜索图书"""
        conditions = []
        params = []
        
        if title:
            conditions.append("书名 LIKE %s")
            params.append(f"%{title}%")
        
        if author:
            conditions.append("作者 LIKE %s")
            params.append(f"%{author}%")
        
        if category:
            conditions.append("分类 = %s")
            params.append(category)
        
        if min_price is not None:
            conditions.append("价格 >= %s")
            params.append(min_price)
        
        if max_price is not None:
            conditions.append("价格 <= %s")
            params.append(max_price)
        
        where_clause = " AND ".join(conditions) if conditions else "1=1"
        sql = f"SELECT * FROM books WHERE {where_clause} ORDER BY 图书编号"
        
        return self.db.query(sql, params)

    def search_books_by_regex(self, regex_pattern, field="书名"):
        """使用正则表达式搜索图书"""
        if field not in ["书名", "作者", "出版社"]:
            return []
        
        # 构建正则查询（MySQL使用REGEXP）
        sql = f"SELECT * FROM books WHERE {field} REGEXP %s"
        return self.db.query(sql, (regex_pattern,))

    def get_book_count_by_category(self):
        """统计各类图书数量"""
        sql = "SELECT 分类, COUNT(*) AS 数量 FROM books GROUP BY 分类"
        return self.db.query(sql)


class ReaderManager:
    """读者管理类，负责读者相关操作"""
    def __init__(self, db):
        self.db = db

    def add_reader(self, name, gender, age, contact, reader_type):
        """添加读者"""
        sql = """
        INSERT INTO readers (姓名, 性别, 年龄, 联系方式, 读者类型)
        VALUES (%s, %s, %s, %s, %s)
        """
        result = self.db.execute(sql, (name, gender, age, contact, reader_type))
        return "添加成功" if result > 0 else "添加失败"

    def update_reader(self, reader_id, **kwargs):
        """更新读者信息"""
        if not kwargs:
            return "至少需要提供一个更新字段"
        
        set_clause = ", ".join([f"{key} = %s" for key in kwargs.keys()])
        params = list(kwargs.values()) + [reader_id]
        
        sql = f"UPDATE readers SET {set_clause} WHERE 读者编号 = %s"
        result = self.db.execute(sql, params)
        return "更新成功" if result > 0 else "更新失败或读者ID不存在"

    def delete_reader(self, reader_id):
        """删除读者（同时删除相关借阅记录）"""
        # 先删除借阅记录
        self.db.execute("DELETE FROM borrow_records WHERE 读者编号 = %s", (reader_id,))
        # 再删除读者
        result = self.db.execute("DELETE FROM readers WHERE 读者编号 = %s", (reader_id,))
        return "删除成功" if result > 0 else "删除失败或读者ID不存在"

    def search_readers(self, name=None, reader_type=None, min_age=None, max_age=None):
        """多条件搜索读者"""
        conditions = []
        params = []
        
        if name:
            conditions.append("姓名 LIKE %s")
            params.append(f"%{name}%")
        
        if reader_type:
            conditions.append("读者类型 = %s")
            params.append(reader_type)
        
        if min_age is not None:
            conditions.append("年龄 >= %s")
            params.append(min_age)
        
        if max_age is not None:
            conditions.append("年龄 <= %s")
            params.append(max_age)
        
        where_clause = " AND ".join(conditions) if conditions else "1=1"
        sql = f"SELECT * FROM readers WHERE {where_clause} ORDER BY 读者编号"
        
        return self.db.query(sql, params)


class BorrowManager:
    """借阅管理类，负责借阅相关操作"""
    def __init__(self, db, book_mgr, reader_mgr):
        self.db = db
        self.book_mgr = book_mgr
        self.reader_mgr = reader_mgr

    def borrow_book(self, reader_id, book_id, borrow_days=15):
        """借阅图书"""
        # 检查读者是否存在
        readers = self.reader_mgr.search_readers(reader_id=reader_id)
        if not readers:
            return "借阅失败：读者ID不存在"
        
        # 检查图书是否存在且可借
        books = self.book_mgr.search_books(book_id=book_id)
        if not books:
            return "借阅失败：图书ID不存在"
        
        book = books[0]
        if book['库存数量'] <= 0:
            return "借阅失败：图书库存不足"
        
        # 计算借阅日期和应归还日期
        borrow_date = date.today()
        return_date = borrow_date + timedelta(days=borrow_days)
        
        # 插入借阅记录
        sql = """
        INSERT INTO borrow_records (读者编号, 图书编号, 借阅日期, 归还日期, 是否逾期)
        VALUES (%s, %s, %s, %s, %s)
        """
        result = self.db.execute(sql, (reader_id, book_id, borrow_date, return_date, 0))
        
        if result > 0:
            # 更新图书库存
            self.book_mgr.update_book(book_id, 库存数量=book['库存数量'] - 1)
            return f"借阅成功！应在 {return_date} 前归还"
        else:
            return "借阅失败：数据库操作错误"

    def return_book(self, borrow_id):
        """归还图书"""
        # 获取借阅记录
        sql = "SELECT * FROM borrow_records WHERE 借阅编号 = %s"
        records = self.db.query(sql, (borrow_id,))
        
        if not records:
            return "归还失败：借阅记录不存在"
        
        record = records[0]
        if record['归还日期']:
            return "归还失败：该图书已归还"
        
        # 更新归还日期和逾期状态
        return_date = date.today()
        is_overdue = 1 if return_date > record['归还日期'] else 0
        
        sql = """
        UPDATE borrow_records 
        SET 归还日期 = %s, 是否逾期 = %s 
        WHERE 借阅编号 = %s
        """
        result = self.db.execute(sql, (return_date, is_overdue, borrow_id))
        
        if result > 0:
            # 更新图书库存
            book_id = record['图书编号']
            books = self.book_mgr.search_books(book_id=book_id)
            if books:
                self.book_mgr.update_book(book_id, 库存数量=books[0]['库存数量'] + 1)
            
            overdue_days = (return_date - record['归还日期']).days if is_overdue else 0
            return f"归还成功！{'已逾期 ' + str(overdue_days) + ' 天' if is_overdue else '未逾期'}"
        else:
            return "归还失败：数据库操作错误"

    def get_borrow_records(self, reader_id=None, book_id=None, is_overdue=None):
        """查询借阅记录"""
        conditions = []
        params = []
        
        if reader_id is not None:
            conditions.append("读者编号 = %s")
            params.append(reader_id)
        
        if book_id is not None:
            conditions.append("图书编号 = %s")
            params.append(book_id)
        
        if is_overdue is not None:
            conditions.append("是否逾期 = %s")
            params.append(1 if is_overdue else 0)
        
        where_clause = " AND ".join(conditions) if conditions else "1=1"
        sql = f"""
        SELECT 
            br.*, 
            b.书名 AS 图书名称, 
            r.姓名 AS 读者姓名 
        FROM borrow_records br
        JOIN books b ON br.图书编号 = b.图书编号
        JOIN readers r ON br.读者编号 = r.读者编号
        WHERE {where_clause}
        ORDER BY br.借阅日期 DESC
        """
        
        return self.db.query(sql, params)


class ConsoleUI:
    """控制台交互界面"""
    def __init__(self):
        self.db = DBConnection()
        self.book_mgr = BookManager(self.db)
        self.reader_mgr = ReaderManager(self.db)
        self.borrow_mgr = BorrowManager(self.db, self.book_mgr, self.reader_mgr)
        
    def display_books(self, books):
        """格式化显示图书列表"""
        if not books:
            print("没有找到匹配的图书")
            return
        
        print("\n图书列表：")
        print("{:<5} {:<20} {:<15} {:<15} {:<8} {:<8} {:<8}".format(
            "ID", "书名", "作者", "出版社", "分类", "价格", "库存"))
        print("-" * 80)
        
        for book in books:
            print("{:<5} {:<20} {:<15} {:<15} {:<8} {:<8.2f} {:<8}".format(
                book['图书编号'], 
                book['书名'][:18] + '..' if len(book['书名']) > 20 else book['书名'],
                book['作者'][:13] + '..' if len(book['作者']) > 15 else book['作者'],
                book['出版社'][:13] + '..' if len(book['出版社']) > 15 else book['出版社'],
                book['分类'],
                book['价格'],
                book['库存数量']
            ))
    
    def display_readers(self, readers):
        """格式化显示读者列表"""
        if not readers:
            print("没有找到匹配的读者")
            return
        
        print("\n读者列表：")
        print("{:<5} {:<8} {:<5} {:<5} {:<15} {:<8}".format(
            "ID", "姓名", "性别", "年龄", "联系方式", "读者类型"))
        print("-" * 60)
        
        for reader in readers:
            print("{:<5} {:<8} {:<5} {:<5} {:<15} {:<8}".format(
                reader['读者编号'],
                reader['姓名'],
                reader['性别'],
                reader['年龄'] or '未知',
                reader['联系方式'],
                reader['读者类型']
            ))
    
    def display_borrow_records(self, records):
        """格式化显示借阅记录"""
        if not records:
            print("没有找到匹配的借阅记录")
            return
        
        print("\n借阅记录：")
        print("{:<5} {:<8} {:<20} {:<8} {:<10} {:<10} {:<8}".format(
            "ID", "读者", "图书", "借阅日期", "应归还日期", "实际归还", "是否逾期"))
        print("-" * 80)
        
        for record in records:
            print("{:<5} {:<8} {:<20} {:<10} {:<10} {:<10} {:<8}".format(
                record['借阅编号'],
                record['读者姓名'],
                record['图书名称'][:18] + '..' if len(record['图书名称']) > 20 else record['图书名称'],
                record['借阅日期'],
                record['归还日期'] or '未归还',
                record['归还日期'] or '未归还',
                "是" if record['是否逾期'] else "否"
            ))
    
    def run(self):
        """主程序入口"""
        print("\n欢迎使用图书管理系统")
        print("=" * 30)
        
        while True:
            print("\n主菜单：")
            print("1. 图书管理")
            print("2. 读者管理")
            print("3. 借阅管理")
            print("4. 统计分析")
            print("0. 退出系统")
            
            choice = input("请选择操作 (0-4): ")
            
            if choice == "1":
                self.manage_books()
            elif choice == "2":
                self.manage_readers()
            elif choice == "3":
                self.manage_borrows()
            elif choice == "4":
                self.show_statistics()
            elif choice == "0":
                print("感谢使用，再见！")
                self.db.close()
                break
            else:
                print("无效选择，请重新输入")
    
    def manage_books(self):
        """图书管理子菜单"""
        while True:
            print("\n图书管理：")
            print("1. 添加图书")
            print("2. 查询图书")
            print("3. 更新图书信息")
            print("4. 删除图书")
            print("5. 正则搜索图书")
            print("0. 返回主菜单")
            
            choice = input("请选择操作 (0-5): ")
            
            if choice == "1":
                title = input("书名: ")
                author = input("作者: ")
                publisher = input("出版社: ")
                year = input("出版年份 (YYYY): ")
                category = input("分类: ")
                price = float(input("价格: "))
                stock = int(input("库存数量: "))
                
                result = self.book_mgr.add_book(title, author, publisher, year, category, price, stock)
                print(result)
            
            elif choice == "2":
                title = input("书名 (留空跳过): ")
                author = input("作者 (留空跳过): ")
                category = input("分类 (留空跳过): ")
                min_price = input("最低价格 (留空跳过): ")
                max_price = input("最高价格 (留空跳过): ")
                
                min_price = float(min_price) if min_price else None
                max_price = float(max_price) if max_price else None
                
                books = self.book_mgr.search_books(title, author, category, min_price, max_price)
                self.display_books(books)
            
            elif choice == "3":
                book_id = int(input("请输入要更新的图书ID: "))
                print("请输入要更新的信息（留空则不更新）")
                title = input("新书名: ")
                author = input("新作者: ")
                publisher = input("新出版社: ")
                year = input("新出版年份: ")
                category = input("新分类: ")
                price = input("新价格: ")
                stock = input("新库存: ")
                
                update_data = {}
                if title: update_data["书名"] = title
                if author: update_data["作者"] = author
                if publisher: update_data["出版社"] = publisher
                if year: update_data["出版年份"] = year
                if category: update_data["分类"] = category
                if price: update_data["价格"] = float(price)
                if stock: update_data["库存数量"] = int(stock)
                
                result = self.book_mgr.update_book(book_id, **update_data)
                print(result)
            
            elif choice == "4":
                book_id = int(input("请输入要删除的图书ID: "))
                result = self.book_mgr.delete_book(book_id)
                print(result)
            
            elif choice == "5":
                pattern = input("请输入正则表达式: ")
                field = input("请选择搜索字段 (书名/作者/出版社，默认书名): ") or "书名"
                
                books = self.book_mgr.search_books_by_regex(pattern, field)
                self.display_books(books)
            
            elif choice == "0":
                break
            else:
                print("无效选择，请重新输入")
    
    def manage_readers(self):
        """读者管理子菜单"""
        while True:
            print("\n读者管理：")
            print("1. 添加读者")
            print("2. 查询读者")
            print("3. 更新读者信息")
            print("4. 删除读者")
            print("0. 返回主菜单")
            
            choice = input("请选择操作 (0-4): ")
            
            if choice == "1":
                name = input("姓名: ")
                gender = input("性别 (男/女): ")
                age = int(input("年龄: "))
                contact = input("联系方式: ")
                reader_type = input("读者类型 (学生/教师): ")
                
                result = self.reader_mgr.add_reader(name, gender, age, contact, reader_type)
                print(result)
            
            elif choice == "2":
                name = input("姓名 (留空跳过): ")
                reader_type = input("读者类型 (留空跳过): ")
                min_age = input("最小年龄 (留空跳过): ")
                max_age = input("最大年龄 (留空跳过): ")
                
                min_age = int(min_age) if min_age else None
                max_age = int(max_age) if max_age else None
                
                readers = self.reader_mgr.search_readers(name, reader_type, min_age, max_age)
                self.display_readers(readers)
            
            elif choice == "3":
                reader_id = int(input("请输入要更新的读者ID: "))
                print("请输入要更新的信息（留空则不更新）")
                name = input("新姓名: ")
                gender = input("新性别: ")
                age = input("新年龄: ")
                contact = input("新联系方式: ")
                reader_type = input("新读者类型: ")
                
                update_data = {}
                if name: update_data["姓名"] = name
                if gender: update_data["性别"] = gender
                if age: update_data["年龄"] = int(age)
                if contact: update_data["联系方式"] = contact
                if reader_type: update_data["读者类型"] = reader_type
                
                result = self.reader_mgr.update_reader(reader_id, **update_data)
                print(result)
            
            elif choice == "4":
                reader_id = int(input("请输入要删除的读者ID: "))
                result = self.reader_mgr.delete_reader(reader_id)
                print(result)
            
            elif choice == "0":
                break
            else:
                print("无效选择，请重新输入")
    
    def manage_borrows(self):
        """借阅管理子菜单"""
        while True:
            print("\n借阅管理：")
            print("1. 借阅图书")
            print("2. 归还图书")
            print("3. 查询借阅记录")
            print("4. 查询逾期记录")
            print("0. 返回主菜单")
            
            choice = input("请选择操作 (0-4): ")
            
            if choice == "1":
                reader_id = int(input("读者ID: "))
                book_id = int(input("图书ID: "))
                borrow_days = int(input("借阅天数 (默认15天): ") or "15")
                
                result = self.borrow_mgr.borrow_book(reader_id, book_id, borrow_days)
                print(result)
            
            elif choice == "2":
                borrow_id = int(input("借阅记录ID: "))
                result = self.borrow_mgr.return_book(borrow_id)
                print(result)
            
            elif choice == "3":
                reader_id = input("读者ID (留空跳过): ")
                book_id = input("图书ID (留空跳过): ")
                is_overdue = input("是否只显示逾期记录 (y/n，留空跳过): ")
                
                reader_id = int(reader_id) if reader_id else None
                book_id = int(book_id) if book_id else None
                is_overdue = True if is_overdue.lower() == 'y' else False if is_overdue.lower() == 'n' else None
                
                records = self.borrow_mgr.get_borrow_records(reader_id, book_id, is_overdue)
                self.display_borrow_records(records)
            
            elif choice == "4":
                records = self.borrow_mgr.get_borrow_records(is_overdue=True)
                self.display_borrow_records(records)
            
            elif choice == "0":
                break
            else:
                print("无效选择，请重新输入")
    
    def show_statistics(self):
        """统计分析菜单"""
        while True:
            print("\n统计分析：")
            print("1. 各类图书数量")
            print("2. 读者类型分布")
            print("3. 热门图书（借阅次数排行）")
            print("0. 返回主菜单")
            
            choice = input("请选择操作 (0-3): ")
            
            if choice == "1":
                categories = self.book_mgr.get_book_count_by_category()
                print("\n各类图书数量：")
                for cat in categories:
                    print(f"{cat['分类']}: {cat['数量']}本")
            
            elif choice == "2":
                reader_types = self.reader_mgr.search_readers(reader_type=None)
                type_count = {}
                
                for reader in reader_types:
                    reader_type = reader['读者类型']
                    type_count[reader_type] = type_count.get(reader_type, 0) + 1
                
                print("\n读者类型分布：")
                for t, count in type_count.items():
                    print(f"{t}: {count}人")
            
            elif choice == "3":
                sql = """
                SELECT 
                    b.书名, 
                    COUNT(br.图书编号) AS 借阅次数 
                FROM borrow_records br
                JOIN books b ON br.图书编号 = b.图书编号
                GROUP BY br.图书编号
                ORDER BY 借阅次数 DESC
                LIMIT 10
                """
                hot_books = self.db.query(sql)
                
                print("\n热门图书排行：")
                for i, book in enumerate(hot_books, 1):
                    print(f"{i}. {book['书名']}: {book['借阅次数']}次")
            
            elif choice == "0":
                break
            else:
                print("无效选择，请重新输入")


if __name__ == "__main__":
    app = ConsoleUI()
    app.run()