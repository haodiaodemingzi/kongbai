import os
from dotenv import load_dotenv
from datetime import timedelta
import logging

# 加载环境变量
load_dotenv()

basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    """应用配置类"""
    # 密钥配置
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'your_secret_key_here'
    
    # 数据库配置
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://cheetah:cheetah@192.168.123.144/oneapi?charset=utf8mb4'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = False  # 设为True可以查看SQL语句
    
    # 上传文件配置
    UPLOAD_FOLDER = os.path.join(os.path.dirname(basedir), 'uploads')
    ALLOWED_EXTENSIONS = {'txt', 'log', 'csv'}
    MAX_CONTENT_LENGTH = 10 * 1024 * 1024  # 限制上传文件大小为 10MB
    
    # 调试配置
    DEBUG = os.environ.get('FLASK_ENV') == 'development'
    
    # 日志配置
    LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO')
    
    # 会话配置
    PERMANENT_SESSION_LIFETIME = timedelta(days=7)
    
    # 图表配置
    CHART_FOLDER = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'app/static/charts')

    @staticmethod
    def init_app(app):
        # 配置日志
        logging.basicConfig(
            level=logging.DEBUG,
            format='[%(asctime)s] [%(name)s] [%(levelname)s] %(message)s',
            handlers=[
                logging.FileHandler(os.path.join(os.path.dirname(basedir), 'logs', 'app.log')),
                logging.StreamHandler()
            ]
        )
        
        # 创建上传目录
        os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
