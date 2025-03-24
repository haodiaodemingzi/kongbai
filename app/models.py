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