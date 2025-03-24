#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
MySQL到SQLite的数据迁移脚本
将MySQL中的Person表数据导入到SQLite数据库
"""

import os
import sys
import sqlite3
import logging
import csv
from dotenv import load_dotenv
from datetime import datetime

# 配置日志
logging.basicConfig(
    level=logging.DEBUG,
    format='[%(asctime)s] [%(levelname)s] [%(name)s] - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger("mysql_to_sqlite")

# 加载环境变量
load_dotenv()

# SQLite数据库路径
SQLITE_DB_PATH = os.path.abspath("app.db")

def initialize_sqlite_db():
    """初始化SQLite数据库，创建表结构"""
    logger.info("初始化SQLite数据库...")
    conn = sqlite3.connect(SQLITE_DB_PATH)
    cursor = conn.cursor()
    
    # 删除现有表（如果存在）
    cursor.execute("DROP TABLE IF EXISTS battle_record")
    cursor.execute("DROP TABLE IF EXISTS battle_detail")
    cursor.execute("DROP TABLE IF EXISTS blessing")
    cursor.execute("DROP TABLE IF EXISTS person")
    
    # 创建person表
    logger.info("创建person表...")
    cursor.execute('''
    CREATE TABLE person (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        job TEXT,
        god TEXT,
        status INTEGER DEFAULT 1,
        create_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        update_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    # 创建battle_record表
    logger.info("创建battle_record表...")
    cursor.execute('''
    CREATE TABLE battle_record (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        create_by INTEGER NOT NULL,
        win INTEGER DEFAULT 0,
        lost INTEGER DEFAULT 0,
        remark INTEGER DEFAULT 0,
        score INTEGER DEFAULT 0,
        kd_ratio REAL DEFAULT 0.0,
        position TEXT,
        publish_at TIMESTAMP,
        create_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        update_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (create_by) REFERENCES person (id)
    )
    ''')
    
    # 创建battle_detail表
    logger.info("创建battle_detail表...")
    cursor.execute('''
    CREATE TABLE battle_detail (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        killer_id INTEGER,
        victim_id INTEGER,
        position TEXT,
        publish_at TIMESTAMP,
        create_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (killer_id) REFERENCES person (id),
        FOREIGN KEY (victim_id) REFERENCES person (id)
    )
    ''')
    
    # 创建blessing表
    logger.info("创建blessing表...")
    cursor.execute('''
    CREATE TABLE blessing (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        person_id INTEGER,
        blessing_name TEXT,
        publish_at TIMESTAMP,
        create_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (person_id) REFERENCES person (id)
    )
    ''')
    
    conn.commit()
    conn.close()
    logger.info(f"SQLite数据库初始化完成: {SQLITE_DB_PATH}")

def import_from_csv(csv_file):
    """从CSV文件导入数据到SQLite"""
    logger.info(f"从CSV文件导入数据: {csv_file}")
    
    if not os.path.exists(csv_file):
        logger.error(f"CSV文件不存在: {csv_file}")
        return False
    
    conn = sqlite3.connect(SQLITE_DB_PATH)
    cursor = conn.cursor()
    
    try:
        with open(csv_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                # 插入person表数据
                cursor.execute('''
                INSERT INTO person (name, job, god, status)
                VALUES (?, ?, ?, ?)
                ''', (
                    row.get('name', ''),
                    row.get('job', ''),
                    row.get('god', ''),
                    int(row.get('status', 1))
                ))
        
        conn.commit()
        
        # 获取导入的记录数量
        cursor.execute("SELECT COUNT(*) FROM person")
        count = cursor.fetchone()[0]
        logger.info(f"成功导入 {count} 条person记录")
        
        return True
    except Exception as e:
        logger.error(f"导入数据时出错: {str(e)}")
        conn.rollback()
        return False
    finally:
        conn.close()

def main():
    """主函数"""
    try:
        # 初始化SQLite数据库
        initialize_sqlite_db()
        
        # 检查命令行参数，确定CSV文件路径
        if len(sys.argv) > 1:
            csv_file = sys.argv[1]
        else:
            csv_file = "person_data.csv"
            
        # 导入数据
        success = import_from_csv(csv_file)
        
        if success:
            logger.info("数据迁移完成")
            return 0
        else:
            logger.error("数据迁移失败")
            return 1
            
    except Exception as e:
        logger.error(f"迁移过程中发生错误: {str(e)}")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 