#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
创建示例数据
生成示例players数据并保存到SQLite数据库
"""

import os
import sys
import sqlite3
import logging
import csv
from datetime import datetime

# 配置日志 - 直接输出到控制台，不使用处理器
logging.basicConfig(
    level=logging.DEBUG,
    format='[%(asctime)s] [%(levelname)s] [%(name)s] - %(message)s',
)
logger = logging.getLogger("create_sample_data")

# 强制打印 - 确保日志直接显示
def log_print(message, level="INFO"):
    print(f"[{level}] {message}")
    if level == "INFO":
        logger.info(message)
    elif level == "ERROR":
        logger.error(message)
    elif level == "DEBUG":
        logger.debug(message)
    elif level == "WARNING":
        logger.warning(message)

# SQLite数据库路径
SQLITE_DB_PATH = os.path.abspath("app.db")
log_print(f"数据库路径: {SQLITE_DB_PATH}")

# 示例玩家数据
SAMPLE_PLAYERS = [
    {"id": 1, "name": "战神", "job": "战士", "god": "梵天", "status": 1},
    {"id": 2, "name": "破敌", "job": "战士", "god": "梵天", "status": 1},
    {"id": 3, "name": "银箭", "job": "猎人", "god": "梵天", "status": 1},
    {"id": 4, "name": "风刃", "job": "刺客", "god": "梵天", "status": 1},
    {"id": 5, "name": "圣光", "job": "牧师", "god": "梵天", "status": 1},
    {"id": 6, "name": "烈焰", "job": "法师", "god": "比湿奴", "status": 1},
    {"id": 7, "name": "冰霜", "job": "法师", "god": "比湿奴", "status": 1},
    {"id": 8, "name": "暗影", "job": "术士", "god": "比湿奴", "status": 1},
    {"id": 9, "name": "天罚", "job": "牧师", "god": "比湿奴", "status": 1},
    {"id": 10, "name": "猎风", "job": "猎人", "god": "比湿奴", "status": 1},
    {"id": 11, "name": "灭世", "job": "战士", "god": "湿婆", "status": 1},
    {"id": 12, "name": "黑暗", "job": "术士", "god": "湿婆", "status": 1},
    {"id": 13, "name": "毒牙", "job": "刺客", "god": "湿婆", "status": 1},
    {"id": 14, "name": "狂风", "job": "萨满", "god": "湿婆", "status": 1},
    {"id": 15, "name": "雷电", "job": "萨满", "god": "湿婆", "status": 1},
]

def initialize_sqlite_db():
    """初始化SQLite数据库，创建表结构"""
    log_print("初始化SQLite数据库...")
    
    # 检查文件是否存在，如果存在则删除
    if os.path.exists(SQLITE_DB_PATH):
        os.remove(SQLITE_DB_PATH)
        log_print(f"已删除现有数据库文件: {SQLITE_DB_PATH}")
    
    try:
        conn = sqlite3.connect(SQLITE_DB_PATH)
        cursor = conn.cursor()
        
        log_print("检查数据库文件是否正确创建")
        cursor.execute("PRAGMA integrity_check")
        integrity_result = cursor.fetchone()
        log_print(f"数据库完整性检查结果: {integrity_result}")
        
        # 创建person表
        log_print("创建person表...")
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
        log_print("创建battle_record表...")
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
        log_print("创建battle_detail表...")
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
        log_print("创建blessing表...")
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
        
        # 检查表是否创建成功
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        log_print(f"创建的表: {tables}")
        
        # 插入示例玩家数据
        log_print("插入示例玩家数据...")
        for player in SAMPLE_PLAYERS:
            cursor.execute('''
            INSERT INTO person (id, name, job, god, status)
            VALUES (?, ?, ?, ?, ?)
            ''', (
                player["id"],
                player["name"],
                player["job"],
                player["god"],
                player["status"]
            ))
        
        conn.commit()
        
        # 验证数据是否插入成功
        cursor.execute("SELECT COUNT(*) FROM person")
        count = cursor.fetchone()[0]
        log_print(f"person表中有 {count} 条记录")
        
        # 检查一些示例数据
        cursor.execute("SELECT id, name, job, god FROM person LIMIT 3")
        samples = cursor.fetchall()
        for sample in samples:
            log_print(f"样本数据: {sample}")
        
        conn.close()
        log_print(f"SQLite数据库初始化完成: {SQLITE_DB_PATH}")
        log_print(f"已插入 {len(SAMPLE_PLAYERS)} 条示例玩家数据")
        
        # 验证文件存在
        if os.path.exists(SQLITE_DB_PATH):
            file_size = os.path.getsize(SQLITE_DB_PATH)
            log_print(f"数据库文件大小: {file_size} 字节")
        else:
            log_print("警告：数据库文件未创建！", "WARNING")
        
        return True
    except Exception as e:
        log_print(f"初始化SQLite数据库时出错: {str(e)}", "ERROR")
        return False

def export_to_csv():
    """将示例数据导出到CSV文件，方便进一步导入"""
    csv_file = "person_data.csv"
    log_print(f"导出示例数据到CSV文件: {csv_file}")
    
    try:
        with open(csv_file, 'w', newline='', encoding='utf-8') as f:
            fieldnames = ["id", "name", "job", "god", "status", "create_at", "update_at"]
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            
            writer.writeheader()
            current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            for player in SAMPLE_PLAYERS:
                row = player.copy()
                row["create_at"] = current_time
                row["update_at"] = current_time
                writer.writerow(row)
        
        # 验证CSV文件是否创建成功
        if os.path.exists(csv_file):
            file_size = os.path.getsize(csv_file)
            log_print(f"CSV文件大小: {file_size} 字节")
            
            # 读取前几行进行验证
            with open(csv_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()[:3]
                log_print(f"CSV文件前几行: {lines}")
        else:
            log_print("警告：CSV文件未创建！", "WARNING")
        
        log_print(f"示例数据已导出到: {csv_file}")
        return True
    except Exception as e:
        log_print(f"导出CSV数据时出错: {str(e)}", "ERROR")
        return False

def main():
    """主函数"""
    log_print("========== 开始创建示例数据 ==========")
    log_print(f"当前工作目录: {os.getcwd()}")
    
    try:
        # 初始化SQLite数据库并插入示例数据
        db_success = initialize_sqlite_db()
        if not db_success:
            return 1
        
        # 导出到CSV文件
        csv_success = export_to_csv()
        if not csv_success:
            return 1
        
        log_print("========== 示例数据创建完成 ==========")
        return 0
    except Exception as e:
        log_print(f"创建示例数据时出错: {str(e)}", "ERROR")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code) 