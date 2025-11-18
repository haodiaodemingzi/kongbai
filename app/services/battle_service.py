#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
战斗数据服务层
"""

from app.extensions import db
from sqlalchemy import text
from app.utils.logger import get_logger

logger = get_logger()


def get_player_rankings(faction=None, job=None, time_range='today', start_datetime=None, end_datetime=None):
    """
    获取玩家排名数据（公共服务函数）
    
    Args:
        faction: 势力筛选（None 表示全部）
        job: 职业筛选（None 表示全部）
        time_range: 时间范围 (today, yesterday, week, month, three_months, all)
        start_datetime: 自定义开始时间
        end_datetime: 自定义结束时间
    
    Returns:
        list: 排名数据列表，每个元素包含 id, name, job, faction, kills, deaths, blessings, kd_ratio, score
    """
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
    
    # 构建查询 - 优化版：先过滤 battle_record 并聚合，充分利用索引
    query_text = """
        WITH filtered_battle_records AS (
            -- 1. 先过滤 battle_record 表（利用 deleted_at 和 publish_at 索引）
            SELECT win, lost, remark
            FROM battle_record
            WHERE deleted_at IS NULL
              {filtered_date_condition}
        ),
        win_stats AS (
            -- 2. 统计每个玩家的击杀和祝福（利用 win 索引）
            SELECT 
                win as player_name,
                COUNT(*) as kills,
                SUM(COALESCE(remark, 0)) as blessings
            FROM filtered_battle_records
            WHERE win IS NOT NULL
            GROUP BY win
        ),
        lost_stats AS (
            -- 3. 统计每个玩家的死亡（利用 lost 索引）
            SELECT 
                lost as player_name,
                COUNT(*) as deaths
            FROM filtered_battle_records
            WHERE lost IS NOT NULL
            GROUP BY lost
        ),
        player_stats AS (
            -- 4. 将统计数据与玩家表 JOIN（使用等值 JOIN，可以走索引）
            SELECT 
                p.id,
                p.name,
                p.job,
                p.god as faction,
                COALESCE(ws.kills, 0) as kills,
                COALESCE(ls.deaths, 0) as deaths,
                COALESCE(ws.blessings, 0) as blessings,
                CASE 
                    WHEN COALESCE(ls.deaths, 0) > 0 
                    THEN ROUND(COALESCE(ws.kills, 0) * 1.0 / COALESCE(ls.deaths, 0), 2)
                    ELSE COALESCE(ws.kills, 0)
                END as kd_ratio
            FROM person p
            LEFT JOIN win_stats ws ON p.name = ws.player_name
            LEFT JOIN lost_stats ls ON p.name = ls.player_name
            WHERE p.deleted_at IS NULL
                AND (:faction IS NULL OR p.god = :faction)
                AND (:job IS NULL OR p.job = :job)
                AND (COALESCE(ws.kills, 0) > 0 OR COALESCE(ls.deaths, 0) > 0)
        )
        SELECT 
            id,
            name,
            job,
            faction,
            kills,
            deaths,
            blessings,
            kd_ratio,
            (kills * 3 + blessings - deaths) as score
        FROM player_stats
        ORDER BY score DESC, kills DESC, deaths ASC
    """.format(filtered_date_condition=date_condition)
    
    query = text(query_text)
    
    # 执行查询
    result = db.session.execute(query, {
        'faction': faction,
        'job': job
    })
    
    # 转换结果为列表
    player_rankings = []
    for row in result:
        player_rankings.append({
            'id': row.id,
            'name': row.name,
            'job': row.job,
            'faction': row.faction,
            'kills': int(row.kills),
            'deaths': int(row.deaths),
            'blessings': int(row.blessings),
            'kd_ratio': float(row.kd_ratio),
            'score': int(row.score)
        })
    
    logger.debug(f"获取到 {len(player_rankings)} 名玩家排名数据")
    return player_rankings


def get_all_jobs():
    """
    获取所有职业列表
    
    Returns:
        list: 职业列表
    """
    jobs_query = text("""
        SELECT DISTINCT job 
        FROM person 
        WHERE job IS NOT NULL 
        AND deleted_at IS NULL 
        ORDER BY job
    """)
    
    jobs = [row[0] for row in db.session.execute(jobs_query)]
    logger.debug(f"获取到 {len(jobs)} 个职业分类")
    return jobs
