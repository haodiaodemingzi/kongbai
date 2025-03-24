#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
使用SQLAlchemy直接初始化SQLite数据库
创建数据库并导入示例数据
"""

import os
import sys
import logging
from datetime import datetime
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

# 配置日志
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# 创建一个简单的Flask应用
app = Flask(__name__)

# 直接设置数据库路径和URI
DB_PATH = os.path.abspath("app.db")
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_PATH}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = True  # 显示SQL语句

# 初始化SQLAlchemy
db = SQLAlchemy(app)

# 打印函数 - 强制输出到控制台
def log_print(message):
    print(f"[INFO] {message}")
    logger.info(message)

# 定义数据模型
class Person(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    job = db.Column(db.String(50))
    god = db.Column(db.String(50))
    status = db.Column(db.Integer, default=1)
    create_at = db.Column(db.DateTime, default=datetime.now)
    update_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)
    
    def __repr__(self):
        return f'<Person {self.name}>'

class BattleRecord(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    create_by = db.Column(db.Integer, db.ForeignKey('person.id'), nullable=False)
    win = db.Column(db.Integer, default=0)
    lost = db.Column(db.Integer, default=0)
    remark = db.Column(db.Integer, default=0)
    score = db.Column(db.Integer, default=0)
    kd_ratio = db.Column(db.Float, default=0.0)
    position = db.Column(db.String(50))
    publish_at = db.Column(db.DateTime)
    create_at = db.Column(db.DateTime, default=datetime.now)
    update_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)

class BattleDetail(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    killer_id = db.Column(db.Integer, db.ForeignKey('person.id'))
    victim_id = db.Column(db.Integer, db.ForeignKey('person.id'))
    position = db.Column(db.String(50))
    publish_at = db.Column(db.DateTime)
    create_at = db.Column(db.DateTime, default=datetime.now)

class Blessing(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    person_id = db.Column(db.Integer, db.ForeignKey('person.id'))
    blessing_name = db.Column(db.String(100))
    publish_at = db.Column(db.DateTime)
    create_at = db.Column(db.DateTime, default=datetime.now)

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

def init_db():
    """初始化数据库并导入示例数据"""
    # 删除现有数据库文件
    if os.path.exists(DB_PATH):
        try:
            os.remove(DB_PATH)
            log_print(f"已删除旧数据库文件：{DB_PATH}")
        except Exception as e:
            log_print(f"删除数据库文件时出错：{str(e)}")
            return False
    
    # 使用SQLAlchemy创建所有表
    try:
        with app.app_context():
            log_print("创建数据库表...")
            db.create_all()
            log_print("数据库表创建成功")
            
            # 导入示例玩家数据
            log_print("开始导入示例玩家数据...")
            for player_data in SAMPLE_PLAYERS:
                player = Person(
                    id=player_data["id"],
                    name=player_data["name"],
                    job=player_data["job"],
                    god=player_data["god"],
                    status=player_data["status"]
                )
                db.session.add(player)
            
            # 提交事务
            db.session.commit()
            log_print(f"导入了 {len(SAMPLE_PLAYERS)} 名玩家数据")
            
            # 验证数据
            players = Person.query.all()
            log_print(f"查询到 {len(players)} 名玩家")
            for i, player in enumerate(players):
                if i < 3:  # 只显示前3个
                    log_print(f"玩家 {i+1}: {player.name}, {player.job}, {player.god}")
            
            # 检查文件大小
            file_size = os.path.getsize(DB_PATH)
            log_print(f"数据库文件大小: {file_size} 字节")
            
            return True
    except Exception as e:
        log_print(f"初始化数据库时出错: {str(e)}")
        return False

if __name__ == "__main__":
    log_print("===== 开始使用SQLAlchemy初始化数据库 =====")
    log_print(f"当前工作目录: {os.getcwd()}")
    log_print(f"数据库路径: {DB_PATH}")
    
    success = init_db()
    
    if success:
        log_print("===== 数据库初始化成功 =====")
        sys.exit(0)
    else:
        log_print("===== 数据库初始化失败 =====")
        sys.exit(1) 