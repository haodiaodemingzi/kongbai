from flask import Blueprint, render_template, redirect, url_for
from app.utils.data_service import get_faction_stats, generate_charts

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    """战绩系统首页"""
    # 获取势力统计数据
    faction_stats = get_faction_stats()
    
    # 生成图表
    charts = generate_charts()
    
    return render_template('index.html', 
                           faction_stats=faction_stats,
                           charts=charts) 