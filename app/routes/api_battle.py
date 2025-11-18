#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""API 战斗数据路由 - 专门用于移动端 API 接口"""

from flask import Blueprint, request, jsonify
from app.utils.jwt_auth import token_required
from app.utils.logger import get_logger
from app.extensions import db
from app.models import Person
from app.config import Config
from sqlalchemy import text
from datetime import datetime, timedelta
from dateutil import parser
import os
from werkzeug.utils import secure_filename

logger = get_logger()

# 创建 API 战斗数据蓝图
api_battle_bp = Blueprint('api_battle', __name__)

# 导入必要的函数（从 battle.py）
from app.routes.battle import (
    get_battle_details_by_player,
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
            query_faction = '比湿奴'  # 默认
        else:
            query_faction = faction
        
        # 处理职业筛选
        if job == 'all' or job == '' or job is None:
            query_job = None
        else:
            query_job = job
        
        # 确定时间筛选条件
        date_condition = ""
        if start_datetime and end_datetime:
            date_condition = f"AND publish_at BETWEEN '{start_datetime}' AND '{end_datetime}'"
        elif time_range == 'today':
            date_condition = "AND DATE(publish_at) = CURDATE()"
        elif time_range == 'yesterday':
            date_condition = "AND DATE(publish_at) = DATE_SUB(CURDATE(), INTERVAL 1 DAY)"
        elif time_range == 'week':
            date_condition = "AND publish_at >= DATE_SUB(CURDATE(), INTERVAL 7 DAY)"
        elif time_range == 'month':
            date_condition = "AND publish_at >= DATE_SUB(CURDATE(), INTERVAL 30 DAY)"
        elif time_range == 'three_months':
            date_condition = "AND publish_at >= DATE_SUB(CURDATE(), INTERVAL 90 DAY)"
        elif time_range == 'all':
            date_condition = "AND publish_at >= DATE_SUB(CURDATE(), INTERVAL 365 DAY)"
        
        # 构建查询
        query_text = """
            WITH filtered_battle_records AS (
                SELECT win, lost, remark
                FROM battle_record
                WHERE deleted_at IS NULL
                  {filtered_date_condition}
            ),
            win_stats AS (
                SELECT 
                    win as player_name,
                    COUNT(*) as kills,
                    SUM(COALESCE(remark, 0)) as blessings
                FROM filtered_battle_records
                WHERE win IS NOT NULL
                GROUP BY win
            ),
            lost_stats AS (
                SELECT 
                    lost as player_name,
                    COUNT(*) as deaths
                FROM filtered_battle_records
                WHERE lost IS NOT NULL
                GROUP BY lost
            ),
            player_stats AS (
                SELECT 
                    p.id,
                    p.name,
                    p.faction,
                    p.job,
                    COALESCE(w.kills, 0) as kills,
                    COALESCE(l.deaths, 0) as deaths,
                    COALESCE(w.blessings, 0) as blessings,
                    (COALESCE(w.kills, 0) * 3 + COALESCE(w.blessings, 0) - COALESCE(l.deaths, 0)) as score
                FROM person p
                LEFT JOIN win_stats w ON p.name = w.player_name
                LEFT JOIN lost_stats l ON p.name = l.player_name
                WHERE p.deleted_at IS NULL
                  {faction_condition}
                  {job_condition}
            )
            SELECT 
                id, name, faction, job, kills, deaths, blessings, score
            FROM player_stats
            WHERE kills > 0 OR deaths > 0
            ORDER BY score DESC, kills DESC
        """.format(
            filtered_date_condition=date_condition,
            faction_condition=f"AND p.faction = '{query_faction}'" if query_faction else "",
            job_condition=f"AND p.job = '{query_job}'" if query_job else ""
        )
        
        # 执行查询
        result = db.session.execute(text(query_text))
        rankings = []
        
        for idx, row in enumerate(result, start=1):
            rankings.append({
                'rank': idx,
                'id': row.id,
                'name': row.name,
                'faction': row.faction,
                'job': row.job,
                'kills': int(row.kills),
                'deaths': int(row.deaths),
                'blessings': int(row.blessings),
                'score': int(row.score)
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
        time_range = request.args.get('time_range')
        start_date = request.args.get('start_datetime')
        end_date = request.args.get('end_datetime')
        
        # 构建日期条件
        date_condition = ""
        if start_date and end_date:
            try:
                start_datetime = parser.parse(start_date)
                end_datetime = parser.parse(end_date)
                date_condition = f"AND br.publish_at BETWEEN '{start_datetime:%Y-%m-%d %H:%M:%S}' AND '{end_datetime:%Y-%m-%d %H:%M:%S}'"
            except (ValueError, TypeError) as e:
                logger.error(f"日期解析错误: {str(e)}")
        elif time_range:
            now = datetime.now()
            if time_range == 'today':
                date_condition = f"AND DATE(br.publish_at) = '{now:%Y-%m-%d}'"
            elif time_range == 'yesterday':
                yesterday = now - timedelta(days=1)
                date_condition = f"AND DATE(br.publish_at) = '{yesterday:%Y-%m-%d}'"
            elif time_range == 'week':
                week_ago = now - timedelta(days=7)
                date_condition = f"AND br.publish_at >= '{week_ago:%Y-%m-%d}'"
            elif time_range == 'month':
                month_ago = now - timedelta(days=30)
                date_condition = f"AND br.publish_at >= '{month_ago:%Y-%m-%d}'"
            elif time_range == 'three_months':
                three_months_ago = now - timedelta(days=90)
                date_condition = f"AND br.publish_at >= '{three_months_ago:%Y-%m-%d}'"
        
        # 查找玩家
        player = Person.query.filter_by(name=player_name, deleted_at=None).first()
        if not player:
            return jsonify({
                'status': 'error',
                'message': f'未找到玩家: {player_name}'
            }), 404
        
        # 获取玩家战斗明细
        player_details = get_battle_details_by_player(player.id, date_condition=date_condition)
        
        if not player_details:
            return jsonify({
                'status': 'error',
                'message': '未找到该玩家的详细信息'
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
