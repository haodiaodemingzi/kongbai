#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
API 仪表盘路由
"""

from flask import Blueprint, request, jsonify
from app.routes.battle import get_faction_statistics
from app.services.data_service import (
    get_faction_stats,
    get_daily_kills_by_player,
    get_daily_deaths_by_player,
    get_daily_scores_by_player
)
from app.utils.logger import get_logger
from app.utils.jwt_auth import token_required

logger = get_logger()

api_dashboard_bp = Blueprint('api_dashboard', __name__)


@api_dashboard_bp.route('/dashboard', methods=['GET'])
@token_required
def api_dashboard():
    """API 首页仪表盘数据接口"""
    try:
        # 获取日期范围参数
        date_range = request.args.get('date_range', 'week')
        if date_range == 'all':
            date_range = 'week'
        
        # 获取势力统计数据
        faction_stats, top_deaths, top_killers, top_scorers = get_faction_stats(date_range)
        
        # 获取势力人数统计
        faction_statistics = get_faction_statistics()
        
        # 准备图表数据
        chart_data = {
            'factions': [],
            'kills': [],
            'deaths': [],
            'blessings': []
        }
        
        # 为势力人数统计创建一个简单的字典
        faction_player_counts = {'梵天': 0, '比湿奴': 0, '湿婆': 0}
        
        for faction, stats in faction_stats:
            chart_data['factions'].append(faction)
            chart_data['kills'].append(stats['total_kills'])
            chart_data['deaths'].append(stats['total_deaths'])
            chart_data['blessings'].append(stats['total_blessings'])
            # 添加玩家数量
            faction_player_counts[faction] = stats.get('player_count', 0)
            
        # 获取总击杀数和死亡数
        total_kills = sum(chart_data['kills'])
        total_deaths = sum(chart_data['deaths'])
        total_blessings = sum(chart_data['blessings'])
        total_players = sum(faction_player_counts.values())
        
        # 获取每日击杀数据
        daily_kills_data = get_daily_kills_by_player(date_range, limit=5)
        # 获取每日死亡数据
        daily_deaths_data = get_daily_deaths_by_player(date_range, limit=5)
        # 获取每日得分数据
        daily_scores_data = get_daily_scores_by_player(date_range, limit=5)
        
        # 构建响应数据
        response_data = {
            'status': 'success',
            'message': '获取首页数据成功',
            'data': {
                'summary': {
                    'total_kills': total_kills,
                    'total_deaths': total_deaths,
                    'total_blessings': total_blessings,
                    'total_players': total_players
                },
                'faction_stats': {
                    'chart_data': chart_data,
                    'player_counts': faction_player_counts,
                    'statistics': faction_statistics
                },
                'top_rankings': {
                    'top_killers': top_killers,
                    'top_scorers': top_scorers,
                    'top_deaths': top_deaths
                },
                'daily_trends': {
                    'kills': daily_kills_data,
                    'deaths': daily_deaths_data,
                    'scores': daily_scores_data
                },
                'date_range': date_range
            }
        }
        
        logger.info(f"API 首页数据请求成功，日期范围: {date_range}")
        return jsonify(response_data), 200
                            
    except Exception as e:
        logger.error(f"API 获取首页数据时出错: {str(e)}", exc_info=True)
        return jsonify({
            'status': 'error',
            'message': f'获取首页数据失败: {str(e)}'
        }), 500
