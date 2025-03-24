from functools import wraps
from flask import session, redirect, url_for, flash, request

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('user_id'):
            flash('请先登录', 'warning')
            # 保存当前URL，登录后跳回
            session['next_url'] = request.url
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function 