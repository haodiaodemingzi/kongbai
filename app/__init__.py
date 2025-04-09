import os
import logging
from flask import Flask, request, g, redirect, url_for, render_template
from app.config import Config
from app.extensions import db
from app.utils.logger import get_logger
import time
from sqlalchemy import text

logger = get_logger()

def create_app(config_class=Config):
    """创建并配置Flask应用程序"""
    logger.info("开始创建Flask应用程序")
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # 设置session密钥
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY') or 'dev-key-123'
    
    logger.info(f"应用程序配置已加载，SECRET_KEY: {app.config['SECRET_KEY'][:3]}******")
    
    # 注册自定义过滤器
    from app.utils.filters import chart_data
    app.jinja_env.filters['chart_data'] = chart_data
    
    # 启用更详细的日志
    if app.debug:
        app.logger.setLevel(logging.DEBUG)
        logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)
    
    # 配置数据库连接
    if app.debug:
        # 开发模式使用固定数据库
        app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://cheetah:cheetah@192.168.123.144:3306/oneapi?charset=utf8mb4'
        logger.info("开发模式：使用192.168.123.144数据库")
    else:
        # 生产模式优先使用环境变量中的数据库配置
        if 'SQLALCHEMY_DATABASE_URI' in os.environ:
            app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('SQLALCHEMY_DATABASE_URI')
            logger.info("生产模式：使用环境变量中的数据库配置")
        elif 'DATABASE_URL' in os.environ:
            app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
            logger.info("生产模式：使用DATABASE_URL环境变量")
        else:
            # 如果环境变量中没有配置，使用默认配置
            app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://admin:admin123@db:3306/oneapi?charset=utf8mb4'
            logger.info("生产模式：使用默认数据库配置")
    
    logger.info(f"数据库连接URI: {app.config['SQLALCHEMY_DATABASE_URI'][:15]}...")
    
    # 初始化数据库
    db.init_app(app)
    logger.info("数据库扩展已初始化")
    
    # 注册蓝图
    from app.routes.battle import battle_bp
    from app.routes.home import home_bp
    from app.routes.auth import auth_bp, login_required
    from app.routes.person import bp as person_bp
    from app.routes.reward import bp as reward_bp
    from app.routes.player_group import bp as player_group_bp
    
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(battle_bp, url_prefix='/battle')
    app.register_blueprint(home_bp)
    app.register_blueprint(person_bp)
    app.register_blueprint(reward_bp)
    app.register_blueprint(player_group_bp)
    logger.info("蓝图已注册: /auth, /battle, /, /person, /reward, /player_group")
    
    # 为需要登录的蓝图添加保护
    for blueprint in [home_bp, battle_bp, player_group_bp]:
        for view_func in blueprint.view_functions.values():
            view_func.decorated = login_required(view_func)
    
    # 检查数据库连接而不创建表
    with app.app_context():
        try:
            logger.info("检查数据库连接...")
            # 执行简单查询以测试连接
            db.session.execute(text('SELECT 1'))
            db.session.commit()
            logger.info("数据库连接正常")
        except Exception as e:
            logger.error(f"数据库连接失败: {str(e)}", exc_info=True)
    
    # 请求前中间件
    @app.before_request
    def before_request():
        request.start_time = time.time()
        g.start_time = request.start_time
        logger.debug(f"收到{request.method}请求: {request.url}")
        
        # 记录请求参数，但排除敏感信息和大型数据
        if request.args:
            safe_args = {k: v if len(v) < 100 else f"{v[:97]}..." for k, v in request.args.to_dict().items()}
            logger.debug(f"请求参数: {safe_args}")
            
        # 记录JSON数据，但排除敏感信息和大型数据
        if request.is_json and request.json:
            log_json = {}
            for k, v in request.json.items():
                if isinstance(v, str) and len(v) > 100:
                    log_json[k] = f"{v[:97]}..."
                else:
                    log_json[k] = v
            logger.debug(f"请求JSON数据: {log_json}")
    
    # 请求后中间件
    @app.after_request
    def after_request(response):
        # 计算请求处理时间
        if hasattr(request, 'start_time'):
            process_time = time.time() - request.start_time
            process_ms = round(process_time * 1000)
            
            # 根据处理时间记录不同级别的日志
            if process_ms > 1000:  # 超过1秒
                logger.warning(f"请求处理缓慢: {request.path}, 状态码: {response.status_code}, 处理时间: {process_ms}ms")
            else:
                logger.debug(f"请求完成: {request.path}, 状态码: {response.status_code}, 处理时间: {process_ms}ms")
            
            # 添加处理时间到响应头
            response.headers['X-Process-Time'] = str(process_ms)
        return response
    
    # 错误处理
    @app.errorhandler(404)
    def page_not_found(e):
        logger.warning(f"404 错误: {request.path}, 来源: {request.referrer}")
        return render_template('404.html'), 404
    
    @app.errorhandler(500)
    def internal_server_error(e):
        logger.error(f"500 错误: {request.path}, 错误: {str(e)}", exc_info=True)
        return render_template('500.html'), 500
    
    # 记录其他未处理的异常
    @app.errorhandler(Exception)
    def handle_exception(e):
        logger.critical(f"未处理的异常: {str(e)}", exc_info=True)
        return render_template('500.html'), 500
    
    logger.info(f"应用程序已启动，环境: {app.config.get('ENV', 'production')}, 调试模式: {app.debug}")
    logger.info(f"应用程序配置: UPLOAD_FOLDER={app.config.get('UPLOAD_FOLDER')}, MAX_CONTENT_LENGTH={app.config.get('MAX_CONTENT_LENGTH', '未设置')}")
    return app
