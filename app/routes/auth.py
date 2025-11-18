from flask import Blueprint, render_template, request, redirect, url_for, session, flash, make_response, jsonify
from functools import wraps
from PIL import Image, ImageDraw, ImageFont
import random
import string
import io
import os
from app.utils.jwt_auth import generate_token, token_required
from app.utils.logger import get_logger

logger = get_logger()

auth_bp = Blueprint('auth', __name__)

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function

def generate_captcha():
    # 生成随机验证码
    chars = string.ascii_letters + string.digits
    code = ''.join(random.choices(chars, k=4))
    
    # 创建图片
    width = 120
    height = 38
    image = Image.new('RGB', (width, height), color='white')
    draw = ImageDraw.Draw(image)
    
    # 使用系统默认字体
    try:
        font = ImageFont.truetype('arial.ttf', 28)
    except:
        font = ImageFont.load_default()
    
    # 绘制文字
    for i, char in enumerate(code):
        x = 20 + i * 20
        y = random.randint(2, 8)
        draw.text((x, y), char, font=font, fill='black')
    
    # 添加干扰线
    for _ in range(5):
        x1 = random.randint(0, width)
        y1 = random.randint(0, height)
        x2 = random.randint(0, width)
        y2 = random.randint(0, height)
        draw.line([(x1, y1), (x2, y2)], fill='gray')
    
    # 添加噪点
    for _ in range(30):
        x = random.randint(0, width)
        y = random.randint(0, height)
        draw.point((x, y), fill='black')
    
    # 保存验证码到session
    session['captcha'] = code.lower()
    
    # 将图片转换为bytes
    img_io = io.BytesIO()
    image.save(img_io, 'PNG')
    img_io.seek(0)
    
    return img_io

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        captcha = request.form.get('captcha', '').lower()
        
        # 验证用户名和密码
        if username == 'admin' and password == 'admin123':
            session['user_id'] = username
            session.pop('captcha', None)  # 清除验证码
            return redirect(url_for('battle.gods_ranking'))
            # 验证验证码
            '''
            if captcha == session.get('captcha', ''):
                session['user_id'] = username
                session.pop('captcha', None)  # 清除验证码
                return redirect(url_for('home.index'))
            else:
                flash('验证码错误', 'danger')
            '''
        else:
            flash('用户名或密码错误', 'danger')
        
    return render_template('auth/login.html')

@auth_bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('auth.login'))

@auth_bp.route('/captcha')
def get_captcha():
    img_io = generate_captcha()
    response = make_response(img_io.getvalue())
    response.headers['Content-Type'] = 'image/png'
    return response

# ==================== API 接口 ====================

@auth_bp.route('/api/login', methods=['POST'])
def api_login():
    """API 登录接口，返回 JWT token"""
    try:
        # 获取 JSON 数据
        data = request.get_json()
        if not data:
            return jsonify({
                'status': 'error',
                'message': '请求数据格式错误'
            }), 400
        
        username = data.get('username')
        password = data.get('password')
        
        # 验证必填字段
        if not username or not password:
            return jsonify({
                'status': 'error',
                'message': '用户名和密码不能为空'
            }), 400
        
        # 验证用户名和密码
        if username == 'admin' and password == 'admin123':
            # 生成 token
            token = generate_token(username, username)
            
            if token:
                logger.info(f"用户 {username} API 登录成功")
                return jsonify({
                    'status': 'success',
                    'message': '登录成功',
                    'data': {
                        'token': token,
                        'user': {
                            'user_id': username,
                            'username': username
                        }
                    }
                }), 200
            else:
                logger.error(f"为用户 {username} 生成 token 失败")
                return jsonify({
                    'status': 'error',
                    'message': '生成认证令牌失败'
                }), 500
        else:
            logger.warning(f"用户 {username} API 登录失败：用户名或密码错误")
            return jsonify({
                'status': 'error',
                'message': '用户名或密码错误'
            }), 401
            
    except Exception as e:
        logger.error(f"API 登录时出错: {str(e)}", exc_info=True)
        return jsonify({
            'status': 'error',
            'message': f'登录失败: {str(e)}'
        }), 500

@auth_bp.route('/api/logout', methods=['POST'])
@token_required
def api_logout():
    """API 登出接口"""
    try:
        username = request.current_user.get('username')
        logger.info(f"用户 {username} API 登出")
        
        return jsonify({
            'status': 'success',
            'message': '登出成功'
        }), 200
        
    except Exception as e:
        logger.error(f"API 登出时出错: {str(e)}", exc_info=True)
        return jsonify({
            'status': 'error',
            'message': f'登出失败: {str(e)}'
        }), 500

@auth_bp.route('/api/verify', methods=['GET'])
@token_required
def api_verify():
    """验证 token 是否有效"""
    try:
        return jsonify({
            'status': 'success',
            'message': 'Token 有效',
            'data': {
                'user': request.current_user
            }
        }), 200
        
    except Exception as e:
        logger.error(f"验证 token 时出错: {str(e)}", exc_info=True)
        return jsonify({
            'status': 'error',
            'message': f'验证失败: {str(e)}'
        }), 500 
