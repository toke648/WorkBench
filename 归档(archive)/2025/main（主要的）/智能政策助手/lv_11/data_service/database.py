"""
数据库管理模块
支持MySQL数据库和内存字典两种模式
"""
from typing import List, Dict, Any, Optional
import mysql.connector
from mysql.connector import Error
from config.settings import DatabaseConfig


class DatabaseManager:
    """数据库管理器 - 支持MySQL和内存模式"""
    
    def __init__(self, config: DatabaseConfig):
        """
        初始化数据库管理器
        
        Args:
            config: 数据库配置
        """
        self.config = config
        self.connection = None
        self.use_mysql = config.enable_mysql
        
        if self.use_mysql:
            self._connect()
            self._init_tables()
        else:
            # 使用内存字典存储
            self.memory_storage = {
                'policies': {},
                'documents': {},
                'conversations': {}
            }
    
    def _connect(self):
        """连接MySQL数据库"""
        try:
            self.connection = mysql.connector.connect(
                host=self.config.host,
                port=self.config.port,
                user=self.config.user,
                password=self.config.password,
                database=self.config.database,
                charset=self.config.charset
            )
            if self.connection.is_connected():
                print(f"✅ MySQL数据库连接成功: {self.config.database}")
        except Error as e:
            print(f"❌ MySQL连接失败: {e}")
            print("⚠️ 切换到内存模式")
            self.use_mysql = False
            self.memory_storage = {
                'policies': {},
                'documents': {},
                'conversations': {}
            }
    
    def _init_tables(self):
        """初始化数据库表结构"""
        if not self.use_mysql or not self.connection:
            return
        
        try:
            cursor = self.connection.cursor()
            
            # 政策表
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS policies (
                    id VARCHAR(50) PRIMARY KEY,
                    title VARCHAR(500) NOT NULL,
                    content TEXT,
                    source VARCHAR(200),
                    url VARCHAR(500),
                    effective_date DATE,
                    category VARCHAR(50),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                    INDEX idx_category (category),
                    INDEX idx_title (title(255))
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
            """)
            
            # 文档表
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS documents (
                    id VARCHAR(50) PRIMARY KEY,
                    filename VARCHAR(500) NOT NULL,
                    file_path VARCHAR(1000),
                    file_type VARCHAR(20),
                    content TEXT,
                    size BIGINT,
                    upload_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    INDEX idx_filename (filename(255))
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
            """)
            
            # 对话历史表
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS conversations (
                    id VARCHAR(50) PRIMARY KEY,
                    session_id VARCHAR(50) NOT NULL,
                    user_message TEXT,
                    assistant_message TEXT,
                    sources JSON,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    INDEX idx_session (session_id)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
            """)
            
            self.connection.commit()
            cursor.close()
            print("✅ 数据库表初始化完成")
        except Error as e:
            print(f"❌ 初始化表结构失败: {e}")
    
    def insert_policy(self, policy_data: Dict[str, Any]) -> bool:
        """插入政策数据"""
        if self.use_mysql and self.connection:
            try:
                cursor = self.connection.cursor()
                cursor.execute("""
                    INSERT INTO policies (id, title, content, source, url, effective_date, category)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                    ON DUPLICATE KEY UPDATE
                        title=VALUES(title),
                        content=VALUES(content),
                        source=VALUES(source),
                        url=VALUES(url),
                        effective_date=VALUES(effective_date),
                        category=VALUES(category)
                """, (
                    policy_data.get('id'),
                    policy_data.get('title'),
                    policy_data.get('content'),
                    policy_data.get('source'),
                    policy_data.get('url'),
                    policy_data.get('effective_date'),
                    policy_data.get('category')
                ))
                self.connection.commit()
                cursor.close()
                return True
            except Error as e:
                print(f"❌ 插入政策失败: {e}")
                return False
        else:
            # 内存模式
            policy_id = policy_data.get('id', policy_data.get('title', ''))
            self.memory_storage['policies'][policy_id] = policy_data
            return True
    
    def search_policies(self, query: str, category: Optional[str] = None, limit: int = 10) -> List[Dict[str, Any]]:
        """搜索政策"""
        if self.use_mysql and self.connection:
            try:
                cursor = self.connection.cursor(dictionary=True)
                sql = """
                    SELECT * FROM policies 
                    WHERE title LIKE %s OR content LIKE %s
                """
                params = [f"%{query}%", f"%{query}%"]
                
                if category:
                    sql += " AND category = %s"
                    params.append(category)
                
                sql += " ORDER BY updated_at DESC LIMIT %s"
                params.append(limit)
                
                cursor.execute(sql, params)
                results = cursor.fetchall()
                cursor.close()
                return results
            except Error as e:
                print(f"❌ 搜索政策失败: {e}")
                return []
        else:
            # 内存模式简单搜索
            results = []
            query_lower = query.lower()
            for policy_id, policy in self.memory_storage['policies'].items():
                if (query_lower in policy.get('title', '').lower() or 
                    query_lower in policy.get('content', '').lower()):
                    if not category or policy.get('category') == category:
                        results.append(policy)
                        if len(results) >= limit:
                            break
            return results
    
    def insert_document(self, doc_data: Dict[str, Any]) -> bool:
        """插入文档数据"""
        if self.use_mysql and self.connection:
            try:
                cursor = self.connection.cursor()
                cursor.execute("""
                    INSERT INTO documents (id, filename, file_path, file_type, content, size)
                    VALUES (%s, %s, %s, %s, %s, %s)
                    ON DUPLICATE KEY UPDATE
                        filename=VALUES(filename),
                        file_path=VALUES(file_path),
                        file_type=VALUES(file_type),
                        content=VALUES(content),
                        size=VALUES(size)
                """, (
                    doc_data.get('id'),
                    doc_data.get('filename'),
                    doc_data.get('file_path'),
                    doc_data.get('file_type'),
                    doc_data.get('content'),
                    doc_data.get('size')
                ))
                self.connection.commit()
                cursor.close()
                return True
            except Error as e:
                print(f"❌ 插入文档失败: {e}")
                return False
        else:
            # 内存模式
            doc_id = doc_data.get('id', doc_data.get('filename', ''))
            self.memory_storage['documents'][doc_id] = doc_data
            return True
    
    def get_all_policies(self) -> List[Dict[str, Any]]:
        """获取所有政策"""
        if self.use_mysql and self.connection:
            try:
                cursor = self.connection.cursor(dictionary=True)
                cursor.execute("SELECT * FROM policies ORDER BY updated_at DESC")
                results = cursor.fetchall()
                cursor.close()
                return results
            except Error as e:
                print(f"❌ 获取政策失败: {e}")
                return []
        else:
            return list(self.memory_storage['policies'].values())
    
    def close(self):
        """关闭数据库连接"""
        if self.connection and self.connection.is_connected():
            self.connection.close()
            print("✅ 数据库连接已关闭")

