#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
JWT Token 认证工具模块
用于移动端 API 访问的 token 认证
"""

import jwt
import datetime
from functools import wraps
from flask import request, jsonify, current_app
from app.utils.logger import get_logger

logger = get_logger()

# 默认密钥，应该从环境变量或配置中读取
SECRET_KEY = 'your-secret-key-change-in-production'
ALGORITHM = 'HS256'
TOKEN_EXPIRATION_HOURS = 720  # token 有效期 30 天

def generate_token(user_id, username):
    """
    生成 JWT token
    
    Args:
        user_id: 用户ID
        username: 用户名
        
    Returns:
        str: JWT token
    """
    try:
        # 设置过期时间
        expiration = datetime.datetime.utcnow() + datetime.timedelta(hours=TOKEN_EXPIRATION_HOURS)
        
        # 创建 payload
        payload = {
            'user_id': user_id,
            'username': username,
            'exp': expiration,
            'iat': datetime.datetime.utcnow()
        }
        
        # 生成 token
        token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
        
        logger.info(f"为用户 {username} 生成 token，有效期至 {expiration}")
        return token
        
    except Exception as e:
        logger.error(f"生成 token 失败: {str(e)}", exc_info=True)
        return None

def verify_token(token):
    """
    验证 JWT token
    
    Args:
        token: JWT token 字符串
        
    Returns:
        dict: 解码后的 payload，如果验证失败返回 None
    """
    try:
        # 解码并验证 token
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        logger.debug(f"Token 验证成功，用户: {payload.get('username')}")
        return payload
        
    except jwt.ExpiredSignatureError:
        logger.warning("Token 已过期")
        return None
    except jwt.InvalidTokenError as e:
        logger.warning(f"无效的 token: {str(e)}")
        return None
    except Exception as e:
        logger.error(f"验证 token 时出错: {str(e)}", exc_info=True)
        return None

def token_required(f):
    """
    装饰器：要求请求必须携带有效的 JWT token
    支持两种方式传递 token:
    1. Authorization header: Bearer <token>
    2. Query parameter: token=<token>
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = None
        
        # 从 Authorization header 获取 token
        auth_header = request.headers.get('Authorization')
        if auth_header and auth_header.startswith('Bearer '):
            token = auth_header.split(' ')[1]
        
        # 如果 header 中没有，尝试从 query parameter 获取
        if not token:
            token = request.args.get('token')
        
        # 如果还是没有，返回错误
        if not token:
            logger.warning(f"请求 {request.path} 缺少 token")
            return jsonify({
                'status': 'error',
                'message': '缺少认证 token，请先登录'
            }), 401
        
        # 验证 token
        payload = verify_token(token)
        if not payload:
            logger.warning(f"请求 {request.path} 的 token 无效或已过期")
            return jsonify({
                'status': 'error',
                'message': 'Token 无效或已过期，请重新登录'
            }), 401
        
        # 将用户信息添加到请求上下文
        request.current_user = {
            'user_id': payload.get('user_id'),
            'username': payload.get('username')
        }
        
        return f(*args, **kwargs)
    
    return decorated_function

def optional_token(f):
    """
    装饰器：token 是可选的，如果有 token 则验证，没有也可以访问
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = None
        
        # 从 Authorization header 获取 token
        auth_header = request.headers.get('Authorization')
        if auth_header and auth_header.startswith('Bearer '):
            token = auth_header.split(' ')[1]
        
        # 如果 header 中没有，尝试从 query parameter 获取
        if not token:
            token = request.args.get('token')
        
        # 如果有 token，验证它
        if token:
            payload = verify_token(token)
            if payload:
                request.current_user = {
                    'user_id': payload.get('user_id'),
                    'username': payload.get('username')
                }
            else:
                request.current_user = None
        else:
            request.current_user = None
        
        return f(*args, **kwargs)
    
    return decorated_function
