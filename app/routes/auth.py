from flask import Blueprint, render_template, request, redirect, url_for, session, flash, make_response
from functools import wraps
from PIL import Image, ImageDraw, ImageFont
import random
import string
import io
import os

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
            return redirect(url_for('home.index'))
            # 验证验证码
            if captcha == session.get('captcha', ''):
                session['user_id'] = username
                session.pop('captcha', None)  # 清除验证码
                return redirect(url_for('home.index'))
            else:
                flash('验证码错误', 'danger')
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
