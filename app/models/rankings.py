from app import db
from datetime import datetime
import json

class Rankings(db.Model):
    """排行榜数据表"""
    __tablename__ = 'rankings'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    update_time = db.Column(db.String(255))  # 更新时间
    category = db.Column(db.String(255))  # 排行榜类别
    players = db.Column(db.Text)  # 玩家排名数据，存储为JSON格式的字符串
    
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)
    
    def __repr__(self):
        return f'<Rankings {self.id}: {self.category}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'update_time': self.update_time,
            'category': self.category,
            'players': json.loads(self.players) if self.players else [],
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else None,
            'updated_at': self.updated_at.strftime('%Y-%m-%d %H:%M:%S') if self.updated_at else None
        }
    
    @classmethod
    def get_by_category(cls, category):
        """根据类别获取最新的排行榜数据"""
        return cls.query.filter_by(category=category).order_by(cls.updated_at.desc()).first()
    
    @classmethod
    def create_or_update(cls, category, players_data, update_time=None):
        """创建或更新排行榜数据"""
        if not update_time:
            update_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
        # 将玩家数据转换为JSON字符串
        players_json = json.dumps(players_data, ensure_ascii=False)
        
        # 创建新记录
        ranking = cls(
            update_time=update_time,
            category=category,
            players=players_json
        )
        
        db.session.add(ranking)
        db.session.commit()
        
        return ranking 