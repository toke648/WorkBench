import sqlite3
import json
from typing import List, Dict, Any, Optional
from datetime import datetime
import pandas as pd
# 改为绝对导入
from utils.logger import get_logger

logger = get_logger(__name__)

class KnowledgeBase:
    """智能知识库管理系统"""
    
    def __init__(self, db_path: str = "policy_knowledge.db"):
        self.db_path = db_path
        self._init_database()
    
    def _init_database(self):
        """初始化数据库"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 政策知识表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS policies (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                content TEXT NOT NULL,
                category TEXT,
                source TEXT,
                url TEXT,
                effective_date TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # 政策条款表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS policy_clauses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                policy_id INTEGER,
                clause_text TEXT,
                clause_type TEXT,
                keywords TEXT,
                FOREIGN KEY (policy_id) REFERENCES policies (id)
            )
        ''')
        
        # 爬虫数据表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS crawled_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                url TEXT UNIQUE,
                title TEXT,
                content TEXT,
                source_domain TEXT,
                crawl_date TEXT,
                processed BOOLEAN DEFAULT 0
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def add_policy(self, policy_data: Dict[str, Any]) -> int:
        """添加政策到知识库"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO policies (title, content, category, source, url, effective_date)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            policy_data['title'],
            policy_data['content'],
            policy_data.get('category', '通用'),
            policy_data.get('source', '未知'),
            policy_data.get('url', ''),
            policy_data.get('effective_date', '')
        ))
        
        policy_id = cursor.lastrowid
        
        # 提取条款
        if 'clauses' in policy_data:
            for clause in policy_data['clauses']:
                cursor.execute('''
                    INSERT INTO policy_clauses (policy_id, clause_text, clause_type, keywords)
                    VALUES (?, ?, ?, ?)
                ''', (
                    policy_id,
                    clause['text'],
                    clause.get('type', '条款'),
                    json.dumps(clause.get('keywords', []), ensure_ascii=False)
                ))
        
        conn.commit()
        conn.close()
        return policy_id
    
    def search_policies(self, query: str, category: str = None, limit: int = 10) -> List[Dict[str, Any]]:
        """搜索政策"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        sql = '''
            SELECT p.*, GROUP_CONCAT(pc.clause_text) as clause_texts
            FROM policies p
            LEFT JOIN policy_clauses pc ON p.id = pc.policy_id
            WHERE p.title LIKE ? OR p.content LIKE ? OR pc.clause_text LIKE ?
        '''
        params = [f'%{query}%', f'%{query}%', f'%{query}%']
        
        if category:
            sql += ' AND p.category = ?'
            params.append(category)
        
        sql += ' GROUP BY p.id ORDER BY p.updated_at DESC LIMIT ?'
        params.append(limit)
        
        cursor.execute(sql, params)
        results = [dict(row) for row in cursor.fetchall()]
        conn.close()
        
        return results
    
    def import_from_csv(self, file_path: str):
        """从CSV文件导入知识库"""
        try:
            df = pd.read_csv(file_path)
            for _, row in df.iterrows():
                policy_data = {
                    'title': row.get('title', ''),
                    'content': row.get('content', ''),
                    'category': row.get('category', '通用'),
                    'source': row.get('source', 'CSV导入'),
                    'url': row.get('url', ''),
                    'effective_date': row.get('effective_date', '')
                }
                self.add_policy(policy_data)
            
            logger.info(f"成功从CSV导入 {len(df)} 条政策数据")
        except Exception as e:
            logger.error(f"CSV导入失败: {str(e)}")
    
    def export_to_csv(self, file_path: str):
        """导出知识库到CSV"""
        conn = sqlite3.connect(self.db_path)
        df = pd.read_sql_query('SELECT * FROM policies', conn)
        df.to_csv(file_path, index=False, encoding='utf-8-sig')
        conn.close()