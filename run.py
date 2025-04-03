#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import logging
import sys
from dotenv import load_dotenv
from app import create_app
from app.utils.logger import get_logger
from decimal import Decimal


# 加载环境变量
load_dotenv()

# 获取日志对象
logger = get_logger()

# 添加额外的控制台处理器以确保Flask日志也输出到控制台
logging.basicConfig(
    level=logging.DEBUG,
    format='[%(asctime)s] [%(levelname)s] [%(name)s] [%(module)s:%(lineno)d] - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
# 设置Werkzeug日志级别
werkzeug_logger = logging.getLogger('werkzeug')
werkzeug_logger.setLevel(logging.DEBUG)
# 配置自定义编码器
from flask.json import JSONEncoder

class DecimalJSONEncoder(JSONEncoder):
    def default(self, o):
        if isinstance(o, Decimal):
            return float(o)  # 或 str(o)
        return super().default(o)


# 创建应用
app = create_app()
app.json_encoder = DecimalJSONEncoder

if __name__ == '__main__':
    # 设置日志级别
    log_level = os.environ.get('LOG_LEVEL', 'DEBUG').upper()
    logging.getLogger().setLevel(getattr(logging, log_level))
    
    # 打印启动信息
    logger.info("=" * 80)
    logger.info(" 战绩统计系统 - 启动中 ".center(80, "="))
    logger.info("=" * 80)
    logger.info(f"日志级别: {log_level}")
    logger.info(f"运行环境: {os.environ.get('FLASK_ENV', 'production')}")
    logger.info(f"调试模式: {'开启' if app.debug else '关闭'}")
    logger.info(f"数据库连接: {app.config.get('SQLALCHEMY_DATABASE_URI', '未配置').split('@')[-1]}")
    logger.info(f"上传目录: {app.config.get('UPLOAD_FOLDER', '未配置')}")
    logger.info("=" * 80)
    
    # 启动应用
    host = os.environ.get('FLASK_HOST', '0.0.0.0')
    port = int(os.environ.get('FLASK_PORT', 5000))
    
    logger.info(f"应用程序即将启动，监听地址: {host}:{port}")
    # 启用一系列调试选项
    app.run(
        host=host, 
        port=port, 
        debug=True,
        use_debugger=True,
        use_reloader=True,
        threaded=True
    ) 
