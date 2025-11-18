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


def get_player_details(player_name, time_range='week', start_datetime=None, end_datetime=None):
    """
    获取玩家详细信息（公共服务函数）
    
    Args:
        player_name: 玩家名称
        time_range: 时间范围 (today, yesterday, week, month, three_months, all)
        start_datetime: 自定义开始时间
        end_datetime: 自定义结束时间
    
    Returns:
        dict: 玩家详细信息，包括基本信息、战绩统计、近期战斗记录
    """
    from app.models.player import Person
    from datetime import datetime, timedelta
    
    # 查找玩家
    player = Person.query.filter_by(name=player_name, deleted_at=None).first()
    if not player:
        logger.warning(f"找不到玩家: {player_name}")
        return None
    
    # 确定时间筛选条件
    date_condition = ""
    if start_datetime and end_datetime:
        date_condition = f"AND br.publish_at BETWEEN '{start_datetime}' AND '{end_datetime}'"
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
    
    # 获取战绩汇总数据
    sql = """
    WITH player_battle_stats AS (
        SELECT 
            p.id AS player_id,
            p.name AS player_name,
            p.job AS player_job,
            p.god AS player_god,
            COUNT(DISTINCT CASE WHEN br.win = p.name THEN br.id END) as kills,
            COUNT(DISTINCT CASE WHEN br.lost = p.name THEN br.id END) as deaths,
            SUM(CASE WHEN br.win = p.name THEN COALESCE(br.remark, 0) ELSE 0 END) as blessings,
            MAX(br.position) as last_position,
            MAX(br.publish_at) as last_battle_time
        FROM 
            person p
        LEFT JOIN 
            battle_record br ON (br.win = p.name OR br.lost = p.name) AND br.deleted_at IS NULL
        WHERE 
            p.name = :player_name
            AND p.deleted_at IS NULL
            {date_condition}
        GROUP BY 
            p.id, p.name, p.job, p.god
    )
    SELECT 
        player_id,
        player_name,
        player_job,
        player_god,
        kills,
        deaths,
        blessings,
        CASE WHEN deaths > 0 
             THEN ROUND(CAST(kills AS FLOAT) / deaths, 2) 
             ELSE kills END as kd_ratio,
        (kills * 3 + blessings - deaths) as score,
        last_position,
        last_battle_time
    FROM 
        player_battle_stats
    """.format(date_condition=date_condition)
    
    result = db.session.execute(text(sql), {"player_name": player_name}).first()
    
    # 如果没有战绩记录，返回基本信息
    if not result or result.kills == 0:
        logger.debug(f"玩家 {player_name} 没有战绩记录")
        return {
            'id': player.id,
            'name': player.name,
            'faction': player.god,
            'job': player.job,
            'kills': 0,
            'deaths': 0,
            'kd_ratio': 0.0,
            'score': 0,
            'blessings': 0,
            'last_battle_time': None,
            'last_position': '0,0',
            'recent_battles': []
        }
    
    # 获取近期战斗记录
    recent_battles_sql = """
    SELECT 
        br.id,
        CASE 
            WHEN br.win = :player_name THEN br.lost
            ELSE br.win
        END as opponent_name,
        CASE 
            WHEN br.win = :player_name THEN 'win'
            ELSE 'lost'
        END as battle_result,
        br.remark as blessings,
        br.position,
        br.publish_at
    FROM 
        battle_record br 
    WHERE 
        (br.win = :player_name OR br.lost = :player_name)
        AND br.deleted_at IS NULL
        {date_condition}
    ORDER BY 
        br.publish_at DESC 
    LIMIT 50
    """.format(date_condition=date_condition)
    
    recent_battles = db.session.execute(text(recent_battles_sql), {"player_name": player_name}).fetchall()
    
    # 构建返回数据
    player_details = {
        'id': result.player_id,
        'name': result.player_name,
        'faction': result.player_god,
        'job': result.player_job,
        'kills': int(result.kills),
        'deaths': int(result.deaths),
        'kd_ratio': float(result.kd_ratio),
        'score': int(result.score),
        'blessings': int(result.blessings),
        'last_battle_time': result.last_battle_time.strftime('%Y-%m-%d %H:%M:%S') if result.last_battle_time else None,
        'last_position': result.last_position or '0,0',
        'recent_battles': [
            {
                'id': battle.id,
                'opponent_name': battle.opponent_name,
                'battle_result': battle.battle_result,
                'blessings': int(battle.blessings) if battle.blessings else 0,
                'position': battle.position,
                'publish_at': battle.publish_at.strftime('%Y-%m-%d %H:%M:%S') if battle.publish_at else None
            }
            for battle in recent_battles
        ]
    }
    
    logger.debug(f"获取玩家 {player_name} 详情成功")
    return player_details
