#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
主页路由
"""

from flask import Blueprint, render_template, current_app, request, flash, redirect, url_for
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
        
        # 准备图表数据
        chart_data = {
            'factions': [],
            'kills': [],
            'deaths': [],
            'blessings': []
        }
        
        for faction, stats in faction_stats:
            chart_data['factions'].append(faction)
            chart_data['kills'].append(stats['total_kills'])
            chart_data['deaths'].append(stats['total_deaths'])
            chart_data['blessings'].append(stats['total_blessings'])
            
        # 获取总击杀数和死亡数
        total_kills = sum(chart_data['kills'])
        total_deaths = sum(chart_data['deaths'])
        total_blessings = sum(chart_data['blessings'])
        
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
                            date_range=date_range)
                            
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
                            date_range='all') 