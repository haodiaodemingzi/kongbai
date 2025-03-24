import logging
import os
import sys
from logging.handlers import RotatingFileHandler
from datetime import datetime
from app.config import Config

# 确保日志目录存在
os.makedirs(os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'logs'), exist_ok=True)

# 创建日志格式
formatter = logging.Formatter(
    '[%(asctime)s] [%(levelname)s] [%(module)s:%(funcName)s:%(lineno)d] - %(message)s'
)

# 创建控制台处理器
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setFormatter(formatter)
console_handler.setLevel(logging.DEBUG)

# 创建文件处理器
log_file = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 
    'logs', 
    f'app_{datetime.now().strftime("%Y%m%d")}.log'
)
file_handler = RotatingFileHandler(
    log_file, 
    maxBytes=10485760,  # 10MB
    backupCount=10
)
file_handler.setFormatter(formatter)
file_handler.setLevel(logging.INFO)

# 创建日志对象
logger = logging.getLogger('battle_stats')
logger.setLevel(logging.DEBUG)
logger.addHandler(console_handler)
logger.addHandler(file_handler)

def get_logger():
    """获取日志对象"""
    return logger 