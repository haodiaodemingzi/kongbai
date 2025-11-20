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
from sqlalchemy import text
import os
from werkzeug.utils import secure_filename

logger = get_logger()

# 创建 API 战斗数据蓝图
api_battle_bp = Blueprint('api_battle', __name__)

# 导入服务层函数
from app.services.battle_service import (
    get_player_rankings as get_rankings_service,
    get_player_details as get_player_details_service,
    get_god_rankings as get_god_rankings_service,
    get_gods_stats as get_gods_stats_service
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


@api_battle_bp.route('/gods_stats', methods=['GET'])
@token_required
def api_get_gods_stats():
    """API 获取三神统计数据"""
    try:
        # 获取筛选参数
        start_datetime = request.args.get('start_datetime')
        end_datetime = request.args.get('end_datetime')
        show_grouped = request.args.get('show_grouped', 'false').lower() == 'true'
        
        # 使用服务层获取三神统计
        stats = get_gods_stats_service(
            start_datetime=start_datetime,
            end_datetime=end_datetime,
            show_grouped=show_grouped
        )
        
        logger.info(f"API 获取三神统计成功")
        return jsonify({
            'status': 'success',
            'message': '获取三神统计成功',
            'data': {
                'stats': stats,
                'filters': {
                    'start_datetime': start_datetime,
                    'end_datetime': end_datetime,
                    'show_grouped': show_grouped
                }
            }
        }), 200
        
    except Exception as e:
        logger.error(f"API 获取三神统计时出错: {str(e)}", exc_info=True)
        return jsonify({
            'status': 'error',
            'message': f'获取三神统计失败: {str(e)}'
        }), 500


@api_battle_bp.route('/group_details', methods=['GET'])
@token_required
def api_get_group_details():
    """API 获取玩家分组下所有游戏ID的详细战绩"""
    try:
        # 获取参数
        god = request.args.get('god')
        player_name = request.args.get('player_name')
        start_datetime_str = request.args.get('start_datetime')
        end_datetime_str = request.args.get('end_datetime')
        
        # 验证必要参数
        if not player_name:
            return jsonify({
                'status': 'error',
                'message': '缺少必要参数: player_name'
            }), 400
            
        # 解析日期时间
        start_datetime = None
        end_datetime = None
        
        if start_datetime_str:
            try:
                start_datetime = datetime.strptime(start_datetime_str, '%Y-%m-%dT%H:%M')
            except ValueError:
                return jsonify({
                    'status': 'error',
                    'message': '开始时间格式不正确'
                }), 400
                
        if end_datetime_str:
            try:
                end_datetime = datetime.strptime(end_datetime_str, '%Y-%m-%dT%H:%M')
                end_datetime = end_datetime.replace(second=59)
            except ValueError:
                return jsonify({
                    'status': 'error',
                    'message': '结束时间格式不正确'
                }), 400
        
        # 构建日期条件
        date_condition = ""
        query_params = {
            'god': god,
            'player_name': player_name
        }
        
        if start_datetime:
            date_condition += " AND br.publish_at >= :start_datetime"
            query_params['start_datetime'] = start_datetime
        if end_datetime:
            date_condition += " AND br.publish_at <= :end_datetime"
            query_params['end_datetime'] = end_datetime
        
        # 首先查询分组信息
        group_query = text("""
            SELECT 
                pg.id as group_id,
                pg.group_name,
                pg.description
            FROM 
                player_group pg 
            WHERE 
                pg.group_name = :player_name
            LIMIT 1
        """)
        
        group_result = db.session.execute(group_query, query_params).fetchone()
        
        if not group_result:
            return jsonify({
                'status': 'error',
                'message': '找不到指定的玩家分组'
            }), 404
            
        # 获取分组ID
        group_id = group_result.group_id
        
        # 查询该分组下所有玩家的战绩
        members_query = text(f"""
            SELECT 
                p.id,
                p.name,
                p.god,
                COUNT(DISTINCT CASE WHEN br.win = p.name THEN br.id END) AS kills,
                COUNT(DISTINCT CASE WHEN br.lost = p.name THEN br.id END) AS deaths,
                SUM(CASE WHEN br.win = p.name THEN COALESCE(br.remark, 0) ELSE 0 END) AS bless
            FROM 
                person p
            LEFT JOIN 
                battle_record br ON p.name IN (br.win, br.lost)
            WHERE 
                p.deleted_at IS NULL
                AND p.player_group_id = :group_id
                {'' if god is None else 'AND p.god = :god'}
                {date_condition}
            GROUP BY 
                p.id, p.name, p.god
            HAVING 
                kills > 0 OR deaths > 0
            ORDER BY 
                kills DESC, deaths ASC
        """)
        
        # 添加分组ID参数
        query_params['group_id'] = group_id
        
        # 获取成员数据
        members = []
        for row in db.session.execute(members_query, query_params):
            members.append({
                'id': row.id,
                'name': row.name,
                'god': row.god,
                'kills': int(row.kills or 0),
                'deaths': int(row.deaths or 0),
                'bless': int(row.bless or 0)
            })
        
        logger.info(f"API 获取分组 {player_name} 详情成功，包含 {len(members)} 个成员")
        
        # 返回结果
        return jsonify({
            'status': 'success',
            'message': '获取分组详情成功',
            'data': {
                'group': {
                    'id': group_result.group_id,
                    'name': group_result.group_name,
                    'description': group_result.description
                },
                'members': members
            }
        }), 200
        
    except Exception as e:
        logger.error(f"API 获取分组详情出错: {str(e)}", exc_info=True)
        return jsonify({
            'status': 'error',
            'message': f'获取分组详情失败: {str(e)}'
        }), 500
