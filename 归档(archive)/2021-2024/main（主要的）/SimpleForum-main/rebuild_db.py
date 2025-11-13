import os
from app import app, db, User

if os.path.exists('forum.db'):
    os.remove('forum.db')

with app.app_context():
    db.create_all()
    
    # 创建默认管理员账户
    admin = User(username='admin', is_admin=True)
    admin.set_password('admin123')
    db.session.add(admin)
    db.session.commit()
    
    print('数据库已成功重建，默认管理员账户已创建')
    print('管理员用户名：admin')
    print('管理员密码：admin123')
    print('数据库已成功重建')