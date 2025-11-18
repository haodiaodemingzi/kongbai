#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""API 战斗数据路由 - 专门用于移动端 API 接口"""

from flask import Blueprint, request, jsonify
from app.utils.jwt_auth import token_required
from app.utils.logger import get_logger
from app.extensions import db
from app.models import Person
from app.config import Config
from datetime import datetime, timedelta
from dateutil import parser
import os
from werkzeug.utils import secure_filename

logger = get_logger()

# 创建 API 战斗数据蓝图
api_battle_bp = Blueprint('api_battle', __name__)

# 导入服务层函数
from app.services.battle_service import (
    get_player_rankings as get_rankings_service,
    get_player_details as get_player_details_service,
    get_god_rankings as get_god_rankings_service
)

# 导入必要的函数（从 battle.py）
from app.routes.battle import (
    parse_text_file,
    save_battle_log_to_db,
    allowed_file,
    get_faction_statistics
)


@api_battle_bp.route('/rankings', methods=['GET'])
@token_required
def api_get_rankings():
    """API 获取玩家排名列表"""
    try:
        # 获取筛选参数
        faction = request.args.get('faction')
        job = request.args.get('job')
        time_range = request.args.get('time_range', 'today')
        start_datetime = request.args.get('start_datetime')
        end_datetime = request.args.get('end_datetime')
        
        # 处理势力筛选
        if faction == 'all' or faction == '':
            query_faction = None
        elif faction is None:
            query_faction = None  # API 默认不筛选势力
        else:
            query_faction = faction
        
        # 处理职业筛选
        if job == 'all' or job == '' or job is None:
            query_job = None
        else:
            query_job = job
        
        # 使用服务层获取排名数据
        player_rankings = get_rankings_service(
            faction=query_faction,
            job=query_job,
            time_range=time_range,
            start_datetime=start_datetime,
            end_datetime=end_datetime
        )
        
        # 添加排名序号
        rankings = []
        for idx, player in enumerate(player_rankings, start=1):
            rankings.append({
                'rank': idx,
                **player  # 展开玩家数据
            })
        
        logger.info(f"API 获取排名成功，返回 {len(rankings)} 条记录")
        return jsonify({
            'status': 'success',
            'message': '获取排名成功',
            'data': {
                'rankings': rankings,
                'filters': {
                    'faction': query_faction,
                    'job': query_job,
                    'time_range': time_range
                }
            }
        }), 200
        
    except Exception as e:
        logger.error(f"API 获取排名时出错: {str(e)}", exc_info=True)
        return jsonify({
            'status': 'error',
            'message': f'获取排名失败: {str(e)}'
        }), 500


@api_battle_bp.route('/player/<string:player_name>', methods=['GET'])
@token_required
def api_get_player_details(player_name):
    """API 获取玩家详细信息"""
    try:
        # 获取时间参数
        time_range = request.args.get('time_range', 'week')
        start_datetime = request.args.get('start_datetime')
        end_datetime = request.args.get('end_datetime')
        
        # 使用服务层获取玩家详情
        player_details = get_player_details_service(
            player_name=player_name,
            time_range=time_range,
            start_datetime=start_datetime,
            end_datetime=end_datetime
        )
        
        if not player_details:
            return jsonify({
                'status': 'error',
                'message': f'未找到玩家: {player_name}'
            }), 404
        
        logger.info(f"API 获取玩家 {player_name} 详情成功")
        return jsonify({
            'status': 'success',
            'message': '获取玩家详情成功',
            'data': player_details
        }), 200
        
    except Exception as e:
        logger.error(f"API 获取玩家详情时出错: {str(e)}", exc_info=True)
        return jsonify({
            'status': 'error',
            'message': f'获取玩家详情失败: {str(e)}'
        }), 500


@api_battle_bp.route('/upload', methods=['POST'])
@token_required
def api_upload_battle_log():
    """API 上传战斗日志"""
    try:
        # 检查是否有文件
        if 'file' not in request.files:
            return jsonify({
                'status': 'error',
                'message': '没有上传文件'
            }), 400
        
        file = request.files['file']
        
        if file.filename == '':
            return jsonify({
                'status': 'error',
                'message': '文件名为空'
            }), 400
        
        if not allowed_file(file.filename):
            return jsonify({
                'status': 'error',
                'message': '只支持 .txt 文件'
            }), 400
        
        # 保存文件
        filename = secure_filename(file.filename)
        file_path = os.path.join(Config.UPLOAD_FOLDER, filename)
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        
        file.save(file_path)
        logger.info(f"API 文件已保存: {file_path}")
        
        # 解析文件
        success, message, battle_details, blessings = parse_text_file(file_path)
        
        if not success:
            return jsonify({
                'status': 'error',
                'message': f'文件解析失败: {message}'
            }), 400
        
        # 保存到数据库
        save_success, save_message = save_battle_log_to_db(battle_details, blessings)
        
        if save_success:
            logger.info(f"API 上传成功: {save_message}")
            return jsonify({
                'status': 'success',
                'message': f'{message}，{save_message}',
                'data': {
                    'battle_count': len(battle_details),
                    'blessing_count': len(blessings)
                }
            }), 200
        else:
            return jsonify({
                'status': 'error',
                'message': f'保存失败: {save_message}'
            }), 500
            
    except Exception as e:
        logger.error(f"API 上传文件时出错: {str(e)}", exc_info=True)
        return jsonify({
            'status': 'error',
            'message': f'上传失败: {str(e)}'
        }), 500


@api_battle_bp.route('/faction_stats', methods=['GET'])
@token_required
def api_get_faction_stats():
    """API 获取势力统计数据"""
    try:
        date_range = request.args.get('date_range', 'week')
        
        # 获取势力统计
        faction_stats = get_faction_statistics()
        
        logger.info(f"API 获取势力统计成功")
        return jsonify({
            'status': 'success',
            'message': '获取势力统计成功',
            'data': {
                'faction_stats': faction_stats,
                'date_range': date_range
            }
        }), 200
        
    except Exception as e:
        logger.error(f"API 获取势力统计时出错: {str(e)}", exc_info=True)
        return jsonify({
            'status': 'error',
            'message': f'获取势力统计失败: {str(e)}'
        }), 500


@api_battle_bp.route('/god_rankings', methods=['GET'])
@token_required
def api_get_god_rankings():
    """API 获取主神排名数据"""
    try:
        # 获取 URL 参数（可选）
        url = request.args.get('url')
        
        # 使用服务层获取主神排名
        result = get_god_rankings_service(url=url)
        
        if result['success']:
            logger.info("API 获取主神排名成功")
            return jsonify({
                'status': 'success',
                'message': result['message'],
                'data': result['data']
            }), 200
        else:
            logger.warning(f"API 获取主神排名失败: {result['message']}")
            return jsonify({
                'status': 'error',
                'message': result['message'],
                'data': result['data']
            }), 200  # 即使失败也返回 200，但数据为空
        
    except Exception as e:
        logger.error(f"API 获取主神排名时出错: {str(e)}", exc_info=True)
        return jsonify({
            'status': 'error',
            'message': f'获取主神排名失败: {str(e)}'
        }), 500
