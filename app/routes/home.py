#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
主页路由
"""

from flask import Blueprint, render_template, current_app, request, flash, redirect, url_for
from app.routes.battle import get_faction_statistics
from app.services.data_service import get_faction_stats
from app.utils.logger import get_logger
from app.utils.auth import login_required

logger = get_logger()

home_bp = Blueprint('home', __name__)

@home_bp.route('/')
@login_required
def index():
    """首页仪表盘"""
    try:
        # 获取日期范围参数
        date_range = request.args.get('date_range', 'all')
        
        # 获取势力统计数据
        faction_stats, top_deaths = get_faction_stats(date_range)
        
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
        
        # 获取击杀榜前三
        top_killers = []
        for faction, stats in faction_stats:
            if stats['top_killer']['name']:
                top_killers.append({
                    'name': stats['top_killer']['name'],
                    'faction': faction,
                    'kills': stats['top_killer']['kills']
                })
        top_killers.sort(key=lambda x: (-x['kills']))
        top_killers = top_killers[:3]
        
        # 获取得分榜前三
        top_scorers = []
        for faction, stats in faction_stats:
            if stats['top_scorer']['name']:
                top_scorers.append({
                    'name': stats['top_scorer']['name'],
                    'faction': faction,
                    'score': stats['top_scorer']['score']
                })
        top_scorers.sort(key=lambda x: (-x['score']))
        top_scorers = top_scorers[:3]

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
                            faction_player_counts_values=faction_player_counts_values)
                            
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
                            faction_player_counts_values=[]) 