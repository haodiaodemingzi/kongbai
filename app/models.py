from app.extensions import db
from datetime import datetime

class Person(db.Model):
    """人员清单"""
    __tablename__ = 'person'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True, comment='id')
    name = db.Column(db.String(128), unique=True, nullable=True, comment='游戏id')
    god = db.Column(db.String(30), nullable=True, comment='主神: 比湿奴 湿婆 梵天')
    union_name = db.Column(db.String(100), nullable=True, comment='战盟')
    job = db.Column(db.String(100), nullable=True, comment='职业')
    level = db.Column(db.String(20), nullable=True, comment='主神等级')
    created_at = db.Column(db.TIMESTAMP, nullable=True, default=datetime.now)
    updated_at = db.Column(db.TIMESTAMP, nullable=True, default=datetime.now, onupdate=datetime.now)
    deleted_at = db.Column(db.TIMESTAMP, nullable=True)
    create_by = db.Column(db.Integer, nullable=True)
    update_by = db.Column(db.Integer, nullable=True)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'god': self.god,
            'union_name': self.union_name,
            'job': self.job,
            'level': self.level,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else None,
            'updated_at': self.updated_at.strftime('%Y-%m-%d %H:%M:%S') if self.updated_at else None
        }

class BattleRecord(db.Model):
    """战斗记录表"""
    __tablename__ = 'battle_record'
    
    id = db.Column(db.Integer, primary_key=True)
    winner_id = db.Column(db.Integer, db.ForeignKey('person.id'), nullable=False)
    loser_id = db.Column(db.Integer, db.ForeignKey('person.id'), nullable=False)
    battle_time = db.Column(db.DateTime, nullable=False, default=datetime.now)
    created_at = db.Column(db.DateTime, default=datetime.now)
    
    # 关联关系
    winner = db.relationship('Person', foreign_keys=[winner_id], backref='wins')
    loser = db.relationship('Person', foreign_keys=[loser_id], backref='losses') 