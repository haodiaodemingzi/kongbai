#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
主页路由
"""

from flask import Blueprint, render_template, current_app, request, flash, redirect, url_for, jsonify
from app.routes.battle import get_faction_statistics
from app.services.data_service import get_faction_stats, get_daily_kills_by_player, get_daily_deaths_by_player, get_daily_scores_by_player
from app.utils.logger import get_logger
from app.utils.auth import login_required
from app.utils.jwt_auth import token_required

logger = get_logger()

home_bp = Blueprint('home', __name__)

@home_bp.route('/')
@login_required
def index():
    """首页仪表盘"""
    try:
        # 获取日期范围参数
        date_range = request.args.get('date_range', 'week')
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        if date_range == 'all':
            date_range = 'week'
        
        # 获取势力统计数据
        if date_range == 'custom' and start_date and end_date:
            faction_stats, top_deaths, top_killers, top_scorers = get_faction_stats(date_range, start_date, end_date)
        else:
            faction_stats, top_deaths, top_killers, top_scorers = get_faction_stats(date_range)
        
        # 获取势力人数统计
        faction_statistics = get_faction_statistics()
        
        # 准备饼图数据
        faction_player_names = []
        faction_player_counts_values = []
        
        for stat in faction_statistics:
            faction_player_names.append(stat['faction'])
            faction_player_counts_values.append(stat['player_count'])
        
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
        
        # 转换为字典格式以便模板中使用
        faction_names = chart_data['factions']
        faction_kills = chart_data['kills']
        faction_deaths = chart_data['deaths']
        faction_blessings = chart_data['blessings']
        
        # 创建击杀数字典用于饼图
        faction_kills_dict = {faction: kills for faction, kills in zip(faction_names, faction_kills)}
        
        # 颜色映射
        faction_colors = {
            '梵天': '#ff4d4d',
            '比湿奴': '#4d94ff',
            '湿婆': '#9966ff'
        }
        
        # 不再需要从各个势力收集top_killers和top_scorers
        
        # 获取每日击杀数据
        if date_range == 'custom' and start_date and end_date:
            daily_kills_data = get_daily_kills_by_player(date_range, limit=5, start_date=start_date, end_date=end_date)
            # 获取每日死亡数据
            daily_deaths_data = get_daily_deaths_by_player(date_range, limit=5, start_date=start_date, end_date=end_date)
            # 获取每日得分数据
            daily_scores_data = get_daily_scores_by_player(date_range, limit=5, start_date=start_date, end_date=end_date)
        else:
            daily_kills_data = get_daily_kills_by_player(date_range, limit=5)
            # 获取每日死亡数据
            daily_deaths_data = get_daily_deaths_by_player(date_range, limit=5)
            # 获取每日得分数据
            daily_scores_data = get_daily_scores_by_player(date_range, limit=5)

        return render_template('home/index.html',
                            chart_data=chart_data,
                            total_kills=total_kills,
                            total_deaths=total_deaths,
                            total_blessings=total_blessings,
                            top_killers=top_killers,
                            top_scorers=top_scorers,
                            top_deaths=top_deaths,
                            date_range=date_range,
                            total_players=total_players,
                            faction_player_counts=faction_player_counts,
                            faction_statistics=faction_statistics,
                            faction_player_names=faction_player_names,
                            faction_player_counts_values=faction_player_counts_values,
                            daily_kills_data=daily_kills_data,
                            daily_deaths_data=daily_deaths_data,
                            daily_scores_data=daily_scores_data)
                            
    except Exception as e:
        logger.error(f"生成首页仪表盘时出错: {str(e)}", exc_info=True)
        return render_template('home/index.html',
                            chart_data={'factions': [], 'kills': [], 'deaths': [], 'blessings': []},
                            total_kills=0,
                            total_deaths=0,
                            total_blessings=0,
                            top_killers=[],
                            top_scorers=[],
                            top_deaths=[],
                            date_range='all',
                            total_players=0,
                            faction_player_counts={'梵天': 0, '比湿奴': 0, '湿婆': 0},
                            faction_statistics=[],
                            faction_player_names=[],
                            faction_player_counts_values=[],
                            daily_kills_data={'dates': [], 'players': []},
                            daily_deaths_data={'dates': [], 'players': []},
                            daily_scores_data={'dates': [], 'players': []})

# ==================== API 接口 ====================

@home_bp.route('/api/dashboard', methods=['GET'])
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