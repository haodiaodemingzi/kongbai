#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""API 认证路由 - 专门用于移动端 API 接口"""

from flask import Blueprint, request, jsonify
from app.utils.jwt_auth import generate_token, token_required
from app.utils.logger import get_logger

logger = get_logger()

# 创建 API 认证蓝图
api_auth_bp = Blueprint('api_auth', __name__)


@api_auth_bp.route('/login', methods=['POST'])
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


@api_auth_bp.route('/logout', methods=['POST'])
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


@api_auth_bp.route('/verify', methods=['GET'])
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


@api_auth_bp.route('/refresh', methods=['POST'])
@token_required
def api_refresh_token():
    """刷新 token"""
    try:
        # 从当前 token 中获取用户信息
        user_id = request.current_user.get('user_id')
        username = request.current_user.get('username')
        
        # 生成新的 token
        new_token = generate_token(user_id, username)
        
        if new_token:
            logger.info(f"用户 {username} 刷新 token 成功")
            return jsonify({
                'status': 'success',
                'message': 'Token 刷新成功',
                'data': {
                    'token': new_token,
                    'user': {
                        'user_id': user_id,
                        'username': username
                    }
                }
            }), 200
        else:
            logger.error(f"为用户 {username} 刷新 token 失败")
            return jsonify({
                'status': 'error',
                'message': '刷新令牌失败'
            }), 500
            
    except Exception as e:
        logger.error(f"刷新 token 时出错: {str(e)}", exc_info=True)
        return jsonify({
            'status': 'error',
            'message': f'刷新失败: {str(e)}'
        }), 500
