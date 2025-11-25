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


def get_god_rankings(url=None):
    """
    获取主神排名数据（公共服务函数）
    
    Args:
        url: 排行榜页面 URL（可选）
    
    Returns:
        dict: 包含三个势力的排名数据
    """
    from app.utils.web_scraper import get_rankings_by_scraper
    
    # 使用爬虫获取数据
    ranking_data = get_rankings_by_scraper(url=url, category="虎威主神排行榜")
    
    # 检查是否有错误
    if "error" in ranking_data:
        logger.error(f"获取主神排名失败: {ranking_data['error']}")
        return {
            "success": False,
            "message": ranking_data["error"],
            "data": {
                "update_time": ranking_data.get("update_time"),
                "brahma_players": [],
                "vishnu_players": [],
                "shiva_players": []
            }
        }
    
    # 返回成功数据
    return {
        "success": True,
        "message": "获取主神排名成功",
        "data": {
            "update_time": ranking_data.get("update_time"),
            "brahma_players": ranking_data.get("brahma_players", []),
            "vishnu_players": ranking_data.get("vishnu_players", []),
            "shiva_players": ranking_data.get("shiva_players", [])
        }
    }


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
    
    # 查询击杀明细
    kills_details_sql = """
    SELECT 
        v.id AS victim_id,
        v.name AS victim_name,
        v.job AS victim_job,
        v.god AS victim_god,
        COUNT(*) AS kill_count
    FROM 
        battle_record br
    JOIN 
        person v ON br.lost = v.name
    WHERE 
        br.win = :player_name
        AND br.deleted_at IS NULL
        {date_condition}
    GROUP BY 
        v.id, v.name, v.job, v.god
    ORDER BY 
        kill_count DESC
    LIMIT 50
    """.format(date_condition=date_condition)
    
    if not date_condition and (start_datetime and end_datetime):
        old_condition = """
        AND (:start_datetime IS NULL OR br.publish_at >= :start_datetime)
        AND (:end_datetime IS NULL OR br.publish_at <= :end_datetime)
        """
        kills_details_sql = kills_details_sql.replace("{date_condition}", old_condition)
        kills_rows = db.session.execute(text(kills_details_sql), {"player_name": player_name, "start_datetime": start_datetime, "end_datetime": end_datetime}).fetchall()
    else:
        kills_rows = db.session.execute(text(kills_details_sql), {"player_name": player_name}).fetchall()
    
    kills_details = [
        {
            'id': row.victim_id,
            'name': row.victim_name,
            'job': row.victim_job,
            'god': row.victim_god,
            'count': int(row.kill_count or 0)
        }
        for row in kills_rows
    ]
    
    # 查询被杀明细
    deaths_details_sql = """
    SELECT 
        k.id AS killer_id,
        k.name AS killer_name,
        k.job AS killer_job,
        k.god AS killer_god,
        COUNT(*) AS death_count
    FROM 
        battle_record br
    JOIN 
        person k ON br.win = k.name
    WHERE 
        br.lost = :player_name
        AND br.deleted_at IS NULL
        {date_condition}
    GROUP BY 
        k.id, k.name, k.job, k.god
    ORDER BY 
        death_count DESC
    LIMIT 50
    """.format(date_condition=date_condition)
    
    if not date_condition and (start_datetime and end_datetime):
        old_condition = """
        AND (:start_datetime IS NULL OR br.publish_at >= :start_datetime)
        AND (:end_datetime IS NULL OR br.publish_at <= :end_datetime)
        """
        deaths_details_sql = deaths_details_sql.replace("{date_condition}", old_condition)
        deaths_rows = db.session.execute(text(deaths_details_sql), {"player_name": player_name, "start_datetime": start_datetime, "end_datetime": end_datetime}).fetchall()
    else:
        deaths_rows = db.session.execute(text(deaths_details_sql), {"player_name": player_name}).fetchall()
    
    deaths_details = [
        {
            'id': row.killer_id,
            'name': row.killer_name,
            'job': row.killer_job,
            'god': row.killer_god,
            'count': int(row.death_count or 0)
        }
        for row in deaths_rows
    ]
    
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
        ],
        'kills_details': kills_details,
        'deaths_details': deaths_details
    }
    
    logger.debug(f"获取玩家 {player_name} 详情成功")
    return player_details


def get_gods_stats(start_datetime=None, end_datetime=None, show_grouped=False):
    """
    获取三神统计数据（公共服务函数）
    
    Args:
        start_datetime: 开始时间
        end_datetime: 结束时间
        show_grouped: 是否按玩家分组显示
    
    Returns:
        dict: 三神统计数据，包含每个神的击杀、死亡、爆灯数据和玩家列表
    """
    gods = ['梵天', '比湿奴', '湿婆']
    stats = {}
    
    try:
        for god in gods:
            # 构建日期条件
            date_condition = ""
            query_params = {'god': god}
            
            if start_datetime:
                date_condition += " AND publish_at >= :start_datetime"
                query_params['start_datetime'] = start_datetime
            if end_datetime:
                date_condition += " AND publish_at <= :end_datetime"
                query_params['end_datetime'] = end_datetime
            
            # 根据是否需要按玩家分组进行统计选择不同的查询
            if show_grouped:
                # 使用玩家分组的查询
                query = text(f"""
                    WITH filtered_battle_records AS (
                        SELECT win, lost, remark
                        FROM battle_record
                        WHERE deleted_at IS NULL
                          {date_condition}
                    ),
                    win_stats AS (
                        SELECT 
                            win as player_name,
                            COUNT(*) as kills,
                            SUM(COALESCE(remark, 0)) as bless
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
                    player_battle_stats AS (
                        SELECT
                            p.id,
                            p.name,
                            COALESCE(ws.kills, 0) as kills,
                            COALESCE(ls.deaths, 0) as deaths,
                            COALESCE(ws.bless, 0) as bless
                        FROM person p
                        LEFT JOIN win_stats ws ON p.name = ws.player_name
                        LEFT JOIN lost_stats ls ON p.name = ls.player_name
                        WHERE p.god = :god
                          AND p.deleted_at IS NULL
                          AND (COALESCE(ws.kills, 0) > 0 
                               OR COALESCE(ls.deaths, 0) > 0 
                               OR COALESCE(ws.bless, 0) > 0)
                    ),
                    player_distinct AS (
                        SELECT
                            p.id,
                            p.name AS original_player_name,
                            p.god,
                            COALESCE(p.player_group_id, p.id) AS group_key,
                            COALESCE(pg.group_name, p.name) AS player_name,
                            CASE
                                WHEN p.player_group_id IS NOT NULL AND EXISTS (
                                    SELECT 1 FROM person p2
                                    WHERE p2.player_group_id = p.player_group_id
                                    AND p2.id != p.id
                                    AND p2.deleted_at IS NULL
                                ) THEN 1
                                ELSE 0
                            END AS is_group
                        FROM
                            person p
                        LEFT JOIN
                            player_group pg ON p.player_group_id = pg.id
                        WHERE
                            p.god = :god
                            AND p.deleted_at IS NULL
                    )
                    SELECT
                        pd.player_name AS name,
                        p.job AS job,
                        MAX(pd.is_group) AS is_group,
                        SUM(COALESCE(pbs.kills, 0)) AS kills,
                        SUM(COALESCE(pbs.deaths, 0)) AS deaths,
                        SUM(COALESCE(pbs.bless, 0)) AS bless
                    FROM
                        player_distinct pd
                    LEFT JOIN
                        player_battle_stats pbs ON pd.id = pbs.id
                    LEFT JOIN
                        person p ON pd.id = p.id
                    GROUP BY
                        pd.group_key, pd.player_name, p.job
                    HAVING
                        SUM(COALESCE(pbs.kills, 0)) > 0 OR SUM(COALESCE(pbs.deaths, 0)) > 0 OR SUM(COALESCE(pbs.bless, 0)) > 0
                    ORDER BY
                        kills DESC, deaths ASC, bless DESC
                """)
            else:
                # 原始查询（不考虑玩家分组）
                query = text(f"""
                    WITH filtered_battle_records AS (
                        SELECT win, lost, remark
                        FROM battle_record
                        WHERE deleted_at IS NULL
                          {date_condition}
                    ),
                    win_stats AS (
                        SELECT 
                            win as player_name,
                            COUNT(*) as kills,
                            SUM(COALESCE(remark, 0)) as bless
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
                            p.name AS name,
                            p.job AS job,
                            COALESCE(ws.kills, 0) as kills,
                            COALESCE(ls.deaths, 0) as deaths,
                            COALESCE(ws.bless, 0) as bless
                        FROM person p
                        LEFT JOIN win_stats ws ON p.name = ws.player_name
                        LEFT JOIN lost_stats ls ON p.name = ls.player_name
                        WHERE p.god = :god
                          AND p.deleted_at IS NULL
                          AND (COALESCE(ws.kills, 0) > 0 
                               OR COALESCE(ls.deaths, 0) > 0 
                               OR COALESCE(ws.bless, 0) > 0)
                    )
                    SELECT 
                        name,
                        job,
                        kills,
                        deaths,
                        bless
                    FROM player_stats
                    ORDER BY kills DESC, deaths ASC, bless DESC
                """)
            
            # 获取玩家数据
            player_stats = []
            total_kills = 0
            total_deaths = 0
            total_bless = 0
            
            for row in db.session.execute(query, query_params):
                player_data = {
                    'name': row.name,
                    'job': row.job if hasattr(row, 'job') and row.job else '未知',
                    'kills': int(row.kills or 0),
                    'deaths': int(row.deaths or 0),
                    'bless': int(row.bless or 0)
                }
                
                # 如果是分组查询，添加is_group字段
                if show_grouped:
                    player_data['is_group'] = bool(row.is_group) if hasattr(row, 'is_group') else False
                    
                player_stats.append(player_data)
                total_kills += int(row.kills or 0)
                total_deaths += int(row.deaths or 0)
                total_bless += int(row.bless or 0)
            
            stats[god] = {
                'kills': total_kills,
                'deaths': total_deaths,
                'bless': total_bless,
                'players': player_stats,
                'player_count': len(player_stats)
            }
        
        logger.info(f"获取三神统计成功")
        return stats
        
    except Exception as e:
        logger.error(f"获取三神统计时出错: {str(e)}", exc_info=True)
        raise


def get_group_kill_details(group_name, direction='out', time_range='week', start_datetime=None, end_datetime=None, limit=100):
    """
    获取指定玩家分组的击杀/被杀明细汇总
    direction为out表示该分组击杀了哪些人, 为in表示该分组被哪些人击杀
    支持时间筛选
    """
    from datetime import datetime, timedelta
    
    # 构建时间条件
    date_condition = ""
    params = {'group_name': group_name}
    
    if start_datetime and end_datetime:
        date_condition = "AND br.publish_at BETWEEN :start_datetime AND :end_datetime"
        params['start_datetime'] = start_datetime
        params['end_datetime'] = end_datetime
    elif time_range:
        now = datetime.now()
        if time_range == 'today':
            date_condition = "AND DATE(br.publish_at) = CURDATE()"
        elif time_range == 'yesterday':
            date_condition = "AND DATE(br.publish_at) = DATE_SUB(CURDATE(), INTERVAL 1 DAY)"
        elif time_range == 'week':
            date_condition = "AND br.publish_at >= DATE_SUB(CURDATE(), INTERVAL 7 DAY)"
        elif time_range == 'month':
            date_condition = "AND br.publish_at >= DATE_SUB(CURDATE(), INTERVAL 30 DAY)"
        elif time_range == 'three_months':
            date_condition = "AND br.publish_at >= DATE_SUB(CURDATE(), INTERVAL 90 DAY)"
        elif time_range == 'all':
            date_condition = "AND br.publish_at >= DATE_SUB(CURDATE(), INTERVAL 365 DAY)"
    
    if direction == 'out':
        # 该分组击杀了哪些人
        sql = f"""
        SELECT 
            v.id AS target_id,
            v.name AS target_name,
            v.job AS target_job,
            v.god AS target_god,
            COUNT(*) AS cnt
        FROM battle_record br
        JOIN person k ON br.win = k.name
        JOIN person v ON br.lost = v.name
        JOIN player_group pg ON k.player_group_id = pg.id
        WHERE pg.group_name = :group_name
          AND br.deleted_at IS NULL
          {date_condition}
        GROUP BY v.id, v.name, v.job, v.god
        ORDER BY cnt DESC
        LIMIT {int(limit)}
        """
    else:
        # 该分组被哪些人击杀
        sql = f"""
        SELECT 
            k.id AS target_id,
            k.name AS target_name,
            k.job AS target_job,
            k.god AS target_god,
            COUNT(*) AS cnt
        FROM battle_record br
        JOIN person v ON br.lost = v.name
        JOIN person k ON br.win = k.name
        JOIN player_group pg ON v.player_group_id = pg.id
        WHERE pg.group_name = :group_name
          AND br.deleted_at IS NULL
          {date_condition}
        GROUP BY k.id, k.name, k.job, k.god
        ORDER BY cnt DESC
        LIMIT {int(limit)}
        """
    
    rows = db.session.execute(text(sql), params).fetchall()
    return [
        {
            'id': r.target_id,
            'name': r.target_name,
            'job': r.target_job,
            'god': r.target_god,
            'count': int(r.cnt or 0)
        }
        for r in rows
    ]


def get_faction_kill_details(faction, direction='out', time_range='week', start_datetime=None, end_datetime=None, limit=100):
    """
    获取指定势力的击杀明细
    direction为out表示该势力击杀了哪些人, 为in表示该势力被哪些人击杀
    支持时间筛选
    """
    # 构建时间条件
    date_condition = ""
    if start_datetime and end_datetime:
        date_condition = "AND br.publish_at BETWEEN :start_datetime AND :end_datetime"
    elif time_range:
        from datetime import datetime, timedelta
        now = datetime.now()
        if time_range == 'today':
            date_condition = "AND DATE(br.publish_at) = CURDATE()"
        elif time_range == 'yesterday':
            date_condition = "AND DATE(br.publish_at) = DATE_SUB(CURDATE(), INTERVAL 1 DAY)"
        elif time_range == 'week':
            date_condition = "AND br.publish_at >= DATE_SUB(CURDATE(), INTERVAL 7 DAY)"
        elif time_range == 'month':
            date_condition = "AND br.publish_at >= DATE_SUB(CURDATE(), INTERVAL 30 DAY)"
        elif time_range == 'three_months':
            date_condition = "AND br.publish_at >= DATE_SUB(CURDATE(), INTERVAL 90 DAY)"
        elif time_range == 'all':
            date_condition = "AND br.publish_at >= DATE_SUB(CURDATE(), INTERVAL 365 DAY)"
    
    params = {'faction': faction}
    if start_datetime and end_datetime:
        params['start_datetime'] = start_datetime
        params['end_datetime'] = end_datetime
    
    if direction == 'out':
        # 该势力击杀了哪些人
        sql = f"""
        SELECT 
            v.id AS target_id,
            v.name AS target_name,
            v.job AS target_job,
            v.god AS target_god,
            COUNT(*) AS cnt
        FROM battle_record br
        JOIN person k ON br.win = k.name
        JOIN person v ON br.lost = v.name
        WHERE k.god = :faction
          AND br.deleted_at IS NULL
          {date_condition}
        GROUP BY v.id, v.name, v.job, v.god
        ORDER BY cnt DESC
        LIMIT {int(limit)}
        """
    else:
        # 该势力被哪些人击杀
        sql = f"""
        SELECT 
            k.id AS target_id,
            k.name AS target_name,
            k.job AS target_job,
            k.god AS target_god,
            COUNT(*) AS cnt
        FROM battle_record br
        JOIN person v ON br.lost = v.name
        JOIN person k ON br.win = k.name
        WHERE v.god = :faction
          AND br.deleted_at IS NULL
          {date_condition}
        GROUP BY k.id, k.name, k.job, k.god
        ORDER BY cnt DESC
        LIMIT {int(limit)}
        """
    
    rows = db.session.execute(text(sql), params).fetchall()
    return [
        {
            'id': r.target_id,
            'name': r.target_name,
            'job': r.target_job,
            'god': r.target_god,
            'count': int(r.cnt or 0)
        }
        for r in rows
    ]
