#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
初始化SQLite数据库
"""

from app import db, create_app
from app.models.player import Person, BattleRecord, BattleDetail, Blessing
import logging
import os

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] [%(levelname)s] [%(name)s] - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger("init_sqlite_db")

def init_db():
    """初始化数据库"""
    app = create_app()
    with app.app_context():
        logger.info("正在初始化数据库...")
        
        # 检查数据库文件是否存在
        db_path = app.config['SQLITE_DB_PATH']
        if os.path.exists(db_path):
            logger.info(f"数据库文件已存在: {db_path}，将重新创建")
        
        # 创建所有表
        db.drop_all()
        db.create_all()
        
        logger.info("数据库表已创建")
        
        # 检查是否有导入数据
        if os.path.exists('person_data.csv'):
            logger.info("检测到person_data.csv文件，将导入数据")
            import csv
            
            # 从CSV导入数据
            count = 0
            try:
                with open('person_data.csv', 'r', encoding='utf-8') as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        person = Person(
                            id=int(row.get('id')),
                            name=row.get('name', ''),
                            job=row.get('job', ''),
                            god=row.get('god', ''),
                            status=int(row.get('status', 1))
                        )
                        db.session.add(person)
                        count += 1
                        
                        if count % 100 == 0:
                            db.session.commit()
                            logger.info(f"已导入 {count} 条记录")
                
                db.session.commit()
                logger.info(f"成功从CSV导入 {count} 条person记录")
            except Exception as e:
                db.session.rollback()
                logger.error(f"导入数据时出错: {str(e)}")
        else:
            logger.warning("未找到person_data.csv文件，跳过数据导入")
            
        # 获取表信息
        tables = ['person', 'battle_record', 'battle_detail', 'blessing']
        for table in tables:
            try:
                result = db.session.execute(f"SELECT COUNT(*) FROM {table}")
                count = result.scalar()
                logger.info(f"表 {table} 记录数: {count}")
            except Exception as e:
                logger.error(f"检查表 {table} 时出错: {str(e)}")
        
        logger.info("数据库初始化完成")

if __name__ == '__main__':
    init_db() 