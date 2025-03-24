import os
from flask import Flask, render_template, redirect, url_for
from app.config import Config
from app.routes.battle import battle_bp
from app.extensions import db

def create_app(config_class=Config):
    """创建Flask应用实例"""
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # 初始化扩展
    db.init_app(app)
    
    # 注册蓝图
    app.register_blueprint(battle_bp, url_prefix='/battle')
    
    # 创建上传目录
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    
    @app.route('/')
    def index():
        """主页重定向到排名页"""
        return redirect(url_for('battle.rankings'))
    
    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('404.html'), 404
    
    @app.errorhandler(500)
    def internal_server_error(e):
        return render_template('500.html'), 500
    
    return app 