from app import db
from datetime import datetime

class Person(db.Model):
    __tablename__ = 'person'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)  # 玩家名称
    god = db.Column(db.String(20), nullable=False)  # 所属势力: 梵天, 比湿奴, 湿婆
    union_name = db.Column(db.String(100))  # 所属联盟
    job = db.Column(db.String(50))  # 职业
    level = db.Column(db.String(50))  # 级别
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)
    deleted_at = db.Column(db.DateTime)
    create_by = db.Column(db.Integer)
    update_by = db.Column(db.Integer)
    
    battle_records = db.relationship('BattleRecord', backref='person', lazy=True)
    
    def __repr__(self):
        return f'<Person {self.name}>'


class BattleRecord(db.Model):
    __tablename__ = 'battle_record'
    
    id = db.Column(db.Integer, primary_key=True)
    win = db.Column(db.String(100), default='0')  # 被击杀者名称，0表示无击杀
    lost = db.Column(db.String(100), default='0')  # 击杀者名称，0表示未被击杀
    position = db.Column(db.String(100))  # 位置坐标，格式: "X,Y"
    remark = db.Column(db.Integer, default=0)  # 备注字段，用于存储祝福次数
    publish_at = db.Column(db.DateTime)  # 战斗时间
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)
    deleted_at = db.Column(db.DateTime)
    create_by = db.Column(db.Integer, db.ForeignKey('person.id'))  # 关联到person表
    update_by = db.Column(db.Integer)
    
    def __repr__(self):
        return f'<BattleRecord {self.id}>'
    
    @property
    def kills(self):
        """击杀数/胜利次数"""
        return 1 if self.win != '0' else 0
        
    @property
    def deaths(self):
        """死亡数/失败次数"""
        return 1 if self.lost != '0' else 0
    
    @property
    def blessings(self):
        """祝福次数"""
        return self.remark
    
    @property
    def score(self):
        """计算得分：击杀10分，祝福5分"""
        return self.kills * 10 + int(self.remark) * 5
    
    @property
    def kd_ratio(self):
        """计算K/D比率"""
        if self.deaths > 0:
            return round(self.kills / self.deaths, 2)
        return self.kills  # 如果没有死亡，则返回击杀数 