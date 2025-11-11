#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
数据服务模块
"""

from app import db
from sqlalchemy import text
from app.utils.logger import get_logger

logger = get_logger()

def get_faction_stats(date_range=None):
    """
    获取各个势力的统计数据
    
    Args:
        date_range: 日期范围，可选值：today, yesterday, week, month, three_months
    """
    try:
        # 构建日期筛选条件的 *基础部分* (不含别名)
        base_date_condition = ""
        if date_range:
            if date_range == 'today':
                base_date_condition = "AND DATE(publish_at) = CURDATE()"
            elif date_range == 'yesterday':
                base_date_condition = "AND DATE(publish_at) = DATE_SUB(CURDATE(), INTERVAL 1 DAY)"
            elif date_range == 'week':
                base_date_condition = "AND publish_at >= DATE_SUB(CURDATE(), INTERVAL 7 DAY)"
            elif date_range == 'month':
                base_date_condition = "AND publish_at >= DATE_SUB(CURDATE(), INTERVAL 1 MONTH)"
            elif date_range == 'three_months':
                base_date_condition = "AND publish_at >= DATE_SUB(CURDATE(), INTERVAL 3 MONTH)"

        # 在需要的地方动态替换别名
        br_date_condition = base_date_condition.replace('publish_at', 'br.publish_at') if base_date_condition else ''
        br_date_condition_with_deleted = f"{br_date_condition} AND br.deleted_at IS NULL" if br_date_condition else "AND br.deleted_at IS NULL"

        # 获取死亡榜前十 - 优化版：先过滤battle_record
        death_query = text(f"""
            SELECT 
                p.name,
                p.god as faction,
                COUNT(*) as deaths
            FROM battle_record br
            JOIN person p ON br.lost = p.name
            WHERE p.deleted_at IS NULL
              {br_date_condition_with_deleted}
            GROUP BY p.name, p.god
            ORDER BY deaths DESC
            LIMIT 10 
        """)
        death_result = db.session.execute(death_query)
        top_deaths = [
            {
                'name': row.name,
                'faction': row.faction,
                'deaths': row.deaths
            }
            for row in death_result
        ]
        logger.debug(f"获取到死亡榜前十: {top_deaths}")

        # 获取击杀榜前十（所有势力） - 优化版：先过滤battle_record
        killer_query = text(f"""
            SELECT 
                p.name,
                p.god as faction,
                COUNT(*) as kills
            FROM battle_record br
            JOIN person p ON br.win = p.name
            WHERE p.deleted_at IS NULL
              {br_date_condition_with_deleted}
            GROUP BY p.name, p.god
            ORDER BY kills DESC
            LIMIT 10
        """)
        killer_result = db.session.execute(killer_query)
        top_killers = [
            {
                'name': row.name,
                'faction': row.faction,
                'kills': row.kills
            }
            for row in killer_result
        ]
        logger.debug(f"获取到击杀榜前十: {top_killers}")

        # 获取得分榜前十（所有势力） - 优化版：分别统计win和lost，避免OR条件
        scorer_query = text(f"""
            WITH filtered_battle_records AS (
                SELECT win, lost, remark
                FROM battle_record
                WHERE deleted_at IS NULL
                  {base_date_condition}
            ),
            win_stats AS (
                SELECT 
                    win as player_name,
                    COUNT(*) as kills,
                    SUM(CASE WHEN remark = '1' THEN 1 ELSE 0 END) as blessings
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
            player_scores AS (
                SELECT 
                    p.name,
                    p.god as faction,
                    COALESCE(ws.kills, 0) * 3 + COALESCE(ws.blessings, 0) - COALESCE(ls.deaths, 0) as score
                FROM person p
                LEFT JOIN win_stats ws ON p.name = ws.player_name
                LEFT JOIN lost_stats ls ON p.name = ls.player_name
                WHERE p.deleted_at IS NULL
                  AND (COALESCE(ws.kills, 0) * 3 + COALESCE(ws.blessings, 0) - COALESCE(ls.deaths, 0) > 0)
            )
            SELECT 
                name,
                faction,
                score
            FROM player_scores
            ORDER BY score DESC
            LIMIT 10
        """)
        scorer_result = db.session.execute(scorer_query)
        top_scorers = [
            {
                'name': row.name,
                'faction': row.faction,
                'score': row.score
            }
            for row in scorer_result
        ]
        logger.debug(f"获取到得分榜前十: {top_scorers}")
        
        faction_stats = []
        factions = ['梵天', '比湿奴', '湿婆']
        
        for faction in factions:
            logger.debug(f"获取 {faction} 势力的统计数据")
            
            # 基础统计查询 - 优化版：先聚合再JOIN，避免多次子查询
            # 统一日期条件用于filtered_battle_records CTE
            filtered_date_condition = base_date_condition if base_date_condition else ""
            
            stats_query = text(f"""
                WITH filtered_battle_records AS (
                    -- 1. 先过滤battle_record表（利用索引）
                    SELECT win, lost, remark
                    FROM battle_record
                    WHERE deleted_at IS NULL
                      {filtered_date_condition}
                ),
                win_stats AS (
                    -- 2. 统计每个玩家的击杀和祝福（利用win索引）
                    SELECT 
                        win as player_name,
                        COUNT(*) as kills,
                        SUM(CASE WHEN remark = '1' THEN 1 ELSE 0 END) as blessings
                    FROM filtered_battle_records
                    WHERE win IS NOT NULL
                    GROUP BY win
                ),
                lost_stats AS (
                    -- 3. 统计每个玩家的死亡（利用lost索引）
                    SELECT 
                        lost as player_name,
                        COUNT(*) as deaths
                    FROM filtered_battle_records
                    WHERE lost IS NOT NULL
                    GROUP BY lost
                ),
                player_stats AS (
                    -- 4. 合并统计数据（只包含有战斗记录的玩家）
                    SELECT 
                        p.id,
                        p.name,
                        p.god as faction,
                        COALESCE(ws.kills, 0) as kills,
                        COALESCE(ls.deaths, 0) as deaths,
                        COALESCE(ws.blessings, 0) as blessings,
                        COALESCE(ws.kills, 0) * 3 + COALESCE(ws.blessings, 0) - COALESCE(ls.deaths, 0) as score
                    FROM person p
                    LEFT JOIN win_stats ws ON p.name = ws.player_name
                    LEFT JOIN lost_stats ls ON p.name = ls.player_name
                    WHERE p.god = :faction
                      AND p.deleted_at IS NULL
                      AND (COALESCE(ws.kills, 0) > 0 OR COALESCE(ls.deaths, 0) > 0 OR COALESCE(ws.blessings, 0) > 0)
                )
                SELECT 
                    COUNT(DISTINCT ps.id) as player_count, 
                    COALESCE(SUM(ps.kills), 0) as total_kills,
                    COALESCE(SUM(ps.deaths), 0) as total_deaths,
                    COALESCE(SUM(ps.blessings), 0) as total_blessings,
                    (
                        SELECT ps_sub.name 
                        FROM player_stats ps_sub
                        WHERE ps_sub.kills > 0
                        ORDER BY ps_sub.kills DESC, ps_sub.deaths ASC 
                        LIMIT 1
                    ) as top_killer_name,
                    (
                        SELECT ps_sub.kills 
                        FROM player_stats ps_sub
                        WHERE ps_sub.kills > 0
                        ORDER BY ps_sub.kills DESC, ps_sub.deaths ASC 
                        LIMIT 1
                    ) as top_killer_kills,
                    (
                        SELECT ps_sub.name 
                        FROM player_stats ps_sub 
                        ORDER BY ps_sub.score DESC, ps_sub.kills DESC, ps_sub.deaths ASC 
                        LIMIT 1
                    ) as top_scorer_name,
                    (
                        SELECT ps_sub.score 
                        FROM player_stats ps_sub 
                        ORDER BY ps_sub.score DESC, ps_sub.kills DESC, ps_sub.deaths ASC 
                        LIMIT 1
                    ) as top_scorer_score
                FROM player_stats ps
            """)
            
            # Remove date_range from params here as it's only used conceptually for the condition string
            result = db.session.execute(stats_query, {'faction': faction}).fetchone()
            
            # 构建统计数据字典
            stats = {
                'player_count': result.player_count,
                'total_kills': result.total_kills,
                'total_deaths': result.total_deaths,
                'total_blessings': result.total_blessings,
                'top_killer': {
                    'name': result.top_killer_name,
                    'kills': result.top_killer_kills
                },
                'top_scorer': {
                    'name': result.top_scorer_name,
                    'score': result.top_scorer_score
                }
            }
            
            logger.debug(f"{faction} 势力统计: 击杀 {stats['total_kills']}, 死亡 {stats['total_deaths']}, 得分 {stats['top_scorer']['score']}")
            
            faction_stats.append((faction, stats))
            
        logger.info(f"返回 {len(faction_stats)} 个势力的统计数据")
        return faction_stats, top_deaths, top_killers, top_scorers
        
    except Exception as e:
        logger.error(f"获取势力统计数据时出错: {str(e)}", exc_info=True)
        return [], [], [], []

def get_player_rankings(faction=None, time_range=None):
    """
    获取玩家排名数据
    
    Args:
        faction: 可选，指定势力名称进行筛选
        time_range: 可选，指定时间范围筛选（today, yesterday, week, month, three_months）
        
    Returns:
        list: 玩家排名数据列表
    """
    try:
        # 构建时间筛选条件
        date_condition = ""
        if time_range:
            if time_range == 'today':
                date_condition = "AND DATE(br.created_at) = CURDATE()"
            elif time_range == 'yesterday':
                date_condition = "AND DATE(br.created_at) = DATE_SUB(CURDATE(), INTERVAL 1 DAY)"
            elif time_range == 'week':
                date_condition = "AND br.created_at >= DATE_SUB(CURDATE(), INTERVAL 7 DAY)"
            elif time_range == 'month':
                date_condition = "AND br.created_at >= DATE_SUB(CURDATE(), INTERVAL 30 DAY)"
            elif time_range == 'three_months':
                date_condition = "AND br.created_at >= DATE_SUB(CURDATE(), INTERVAL 90 DAY)"

        # 构建基础查询
        query = text(f"""
            SELECT 
                p.id,
                p.name,
                p.god as faction,
                COALESCE(
                    (SELECT COUNT(*) FROM battle_record br 
                     WHERE br.win = p.name {date_condition}), 
                    0
                ) as kills,
                COALESCE(
                    (SELECT COUNT(*) FROM battle_record br 
                     WHERE br.lost = p.name {date_condition}),
                    0
                ) as deaths,
                COALESCE(
                    (SELECT COUNT(*) FROM battle_record br 
                     WHERE br.win = p.name AND br.remark > 0 {date_condition}),
                    0
                ) as blessings,
                COALESCE(
                    (SELECT COUNT(*) FROM battle_record br 
                     WHERE br.win = p.name {date_condition}) * 3 -
                    (SELECT COUNT(*) FROM battle_record br 
                     WHERE br.lost = p.name {date_condition}),
                    0
                ) as score
            FROM person p
            WHERE 1=1
            AND EXISTS (
                SELECT 1 FROM battle_record br 
                WHERE (br.win = p.name OR br.lost = p.name)
                {date_condition}
            )
        """)
        
        # 添加势力筛选条件
        if faction:
            query = text(query.text + " AND p.god = :faction")
            result = db.session.execute(query, {'faction': faction})
        else:
            result = db.session.execute(query)
            
        # 转换结果为列表
        players = []
        for row in result:
            # 只包含在指定时间范围内有战斗记录的玩家
            if row.kills > 0 or row.deaths > 0:
                player = {
                    'id': row.id,
                    'name': row.name,
                    'faction': row.faction,
                    'kills': row.kills,
                    'deaths': row.deaths,
                    'blessings': row.blessings,
                    'score': row.score,
                    'kd_ratio': round(row.kills / row.deaths, 2) if row.deaths > 0 else row.kills
                }
                players.append(player)
            
        # 按得分和击杀数排序
        players.sort(key=lambda x: (-x['score'], -x['kills'], x['deaths']))
        
        return players
    except Exception as e:
        logger.error(f"获取玩家排名数据时出错: {str(e)}", exc_info=True)
        return []

def get_battle_details_by_player(player_name):
    """
    获取指定玩家的战斗详情
    
    Args:
        player_name: 玩家名称
        
    Returns:
        dict: 玩家详细信息，包括基本信息和战斗记录
    """
    try:
        # 获取玩家基本信息
        player_query = text("""
            SELECT 
                p.id,
                p.name,
                p.god as faction,
                COALESCE(
                    (SELECT COUNT(*) FROM battle_record br WHERE br.win = p.name),
                    0
                ) as kills,
                COALESCE(
                    (SELECT COUNT(*) FROM battle_record br WHERE br.lost = p.name),
                    0
                ) as deaths,
                COALESCE(
                    (SELECT COUNT(*) FROM blessings b WHERE b.player_id = p.id),
                    0
                ) as blessings,
                COALESCE(
                    (SELECT COUNT(*) FROM battle_record br WHERE br.win = p.name) * 3 -
                    (SELECT COUNT(*) FROM battle_record br WHERE br.lost = p.name),
                    0
                ) as score
            FROM person p
            WHERE p.name = :player_name
        """)
        
        result = db.session.execute(player_query, {'player_name': player_name}).fetchone()
        
        if not result:
            return None
            
        player_info = {
            'id': result.id,
            'name': result.name,
            'faction': result.faction,
            'kills': result.kills,
            'deaths': result.deaths,
            'blessings': result.blessings,
            'score': result.score,
            'kd_ratio': round(result.kills / result.deaths, 2) if result.deaths > 0 else result.kills
        }
        
        # 获取击杀详情
        kills_query = text("""
            SELECT 
                br.lost as victim_name,
                p2.god as victim_faction,
                COUNT(*) as kill_count,
                MAX(br.publish_at) as last_kill_time
            FROM battle_record br
            JOIN person p2 ON br.lost = p2.name
            WHERE br.win = :player_name
            GROUP BY br.lost, p2.god
            ORDER BY kill_count DESC, last_kill_time DESC
        """)
        
        kills_result = db.session.execute(kills_query, {'player_name': player_name})
        
        kills_details = [
            {
                'victim_name': row.victim_name,
                'victim_faction': row.victim_faction,
                'kill_count': row.kill_count,
                'last_kill_time': row.last_kill_time
            }
            for row in kills_result
        ]
        
        # 获取死亡详情
        deaths_query = text("""
            SELECT 
                br.win as killer_name,
                p2.god as killer_faction,
                COUNT(*) as death_count,
                MAX(br.publish_at) as last_death_time
            FROM battle_record br
            JOIN person p2 ON br.win = p2.name
            WHERE br.lost = :player_name
            GROUP BY br.win, p2.god
            ORDER BY death_count DESC, last_death_time DESC
        """)
        
        deaths_result = db.session.execute(deaths_query, {'player_name': player_name})
        
        deaths_details = [
            {
                'killer_name': row.killer_name,
                'killer_faction': row.killer_faction,
                'death_count': row.death_count,
                'last_death_time': row.last_death_time
            }
            for row in deaths_result
        ]
        
        # 合并所有信息
        player_info['kills_details'] = kills_details
        player_info['deaths_details'] = deaths_details
        
        return player_info
        
    except Exception as e:
        logger.error(f"获取玩家 {player_name} 战斗详情时出错: {str(e)}", exc_info=True)
        return None

def export_data_to_json(faction=None):
    """
    导出数据为JSON格式
    
    Args:
        faction: 可选，指定势力名称进行筛选
        
    Returns:
        tuple: (json_string, filename)
    """
    try:
        # 获取玩家排名数据
        players = get_player_rankings(faction)
        
        # 转换为JSON字符串
        import json
        from datetime import datetime
        
        # 准备导出数据
        export_data = {
            'export_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'faction_filter': faction,
            'players': players
        }
        
        json_data = json.dumps(export_data, ensure_ascii=False, indent=2)
        
        # 生成文件名
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        faction_str = f"_{faction}" if faction else ""
        filename = f"battle_stats{faction_str}_{timestamp}.json"
        
        return json_data, filename
        
    except Exception as e:
        logger.error(f"导出数据时出错: {str(e)}", exc_info=True)
        return "{}", "error.json"

def get_daily_kills_by_player(date_range=None, limit=5):
    """
    获取每日击杀数据，按角色和日期分组（优化版：单次查询）
    
    Args:
        date_range: 日期范围，可选值：today, yesterday, week, month, three_months
        limit: 返回前N个击杀最多的玩家
    
    Returns:
        dict: {
            'dates': ['2025-01-01', '2025-01-02', ...],
            'players': [
                {
                    'name': '玩家名',
                    'faction': '势力',
                    'data': [10, 15, 20, ...]  # 每天的击杀数
                },
                ...
            ]
        }
    """
    try:
        # 构建日期筛选条件（基础部分，不含别名）
        base_date_condition = ""
        if date_range:
            if date_range == 'today':
                base_date_condition = "AND DATE(br.publish_at) = CURDATE()"
            elif date_range == 'yesterday':
                base_date_condition = "AND DATE(br.publish_at) = DATE_SUB(CURDATE(), INTERVAL 1 DAY)"
            elif date_range == 'week':
                base_date_condition = "AND br.publish_at >= DATE_SUB(CURDATE(), INTERVAL 7 DAY)"
            elif date_range == 'month':
                base_date_condition = "AND br.publish_at >= DATE_SUB(CURDATE(), INTERVAL 1 MONTH)"
            elif date_range == 'three_months':
                base_date_condition = "AND br.publish_at >= DATE_SUB(CURDATE(), INTERVAL 3 MONTH)"
        
        # 优化：使用单次查询获取所有数据
        query = text(f"""
            WITH filtered_records AS (
                SELECT 
                    br.win as player_name,
                    DATE(br.publish_at) as date,
                    p.god as faction
                FROM battle_record br
                JOIN person p ON br.win = p.name
                WHERE br.deleted_at IS NULL
                  AND p.deleted_at IS NULL
                  AND br.win IS NOT NULL
                  {base_date_condition}
            ),
            daily_stats AS (
                SELECT 
                    player_name,
                    faction,
                    date,
                    COUNT(*) as kills
                FROM filtered_records
                GROUP BY player_name, faction, date
            ),
            total_stats AS (
                SELECT 
                    player_name,
                    faction,
                    SUM(kills) as total_kills
                FROM daily_stats
                GROUP BY player_name, faction
            ),
            top_players AS (
                SELECT player_name, faction
                FROM total_stats
                ORDER BY total_kills DESC
                LIMIT :limit
            )
            SELECT 
                tp.player_name,
                tp.faction,
                ds.date,
                COALESCE(ds.kills, 0) as kills
            FROM top_players tp
            LEFT JOIN daily_stats ds ON tp.player_name = ds.player_name
            ORDER BY tp.player_name, ds.date ASC
        """)
        
        result = db.session.execute(query, {'limit': limit})
        
        # 处理结果
        players_dict = {}
        dates_set = set()
        
        for row in result:
            player_name = row.player_name
            if player_name not in players_dict:
                players_dict[player_name] = {
                    'name': player_name,
                    'faction': row.faction,
                    'daily_data': {}
                }
            if row.date:
                date_str = row.date.strftime('%Y-%m-%d')
                dates_set.add(date_str)
                players_dict[player_name]['daily_data'][date_str] = row.kills
        
        # 获取所有日期并排序
        dates = sorted(list(dates_set))
        
        if not dates:
            return {'dates': [], 'players': []}
        
        # 为每个玩家填充完整日期数组
        players_data = []
        for player_name, player_info in players_dict.items():
            data = [player_info['daily_data'].get(date, 0) for date in dates]
            players_data.append({
                'name': player_info['name'],
                'faction': player_info['faction'],
                'data': data
            })
        
        return {
            'dates': dates,
            'players': players_data
        }
        
    except Exception as e:
        logger.error(f"获取每日击杀数据时出错: {str(e)}", exc_info=True)
        return {'dates': [], 'players': []}

def get_daily_deaths_by_player(date_range=None, limit=5):
    """
    获取每日死亡数据，按角色和日期分组（优化版：单次查询）
    
    Args:
        date_range: 日期范围，可选值：today, yesterday, week, month, three_months
        limit: 返回前N个死亡最多的玩家
    
    Returns:
        dict: {
            'dates': ['2025-01-01', '2025-01-02', ...],
            'players': [
                {
                    'name': '玩家名',
                    'faction': '势力',
                    'data': [10, 15, 20, ...]  # 每天的死亡数
                },
                ...
            ]
        }
    """
    try:
        # 构建日期筛选条件（基础部分，不含别名）
        base_date_condition = ""
        if date_range:
            if date_range == 'today':
                base_date_condition = "AND DATE(br.publish_at) = CURDATE()"
            elif date_range == 'yesterday':
                base_date_condition = "AND DATE(br.publish_at) = DATE_SUB(CURDATE(), INTERVAL 1 DAY)"
            elif date_range == 'week':
                base_date_condition = "AND br.publish_at >= DATE_SUB(CURDATE(), INTERVAL 7 DAY)"
            elif date_range == 'month':
                base_date_condition = "AND br.publish_at >= DATE_SUB(CURDATE(), INTERVAL 1 MONTH)"
            elif date_range == 'three_months':
                base_date_condition = "AND br.publish_at >= DATE_SUB(CURDATE(), INTERVAL 3 MONTH)"
        
        # 优化：使用单次查询获取所有数据
        query = text(f"""
            WITH filtered_records AS (
                SELECT 
                    br.lost as player_name,
                    DATE(br.publish_at) as date,
                    p.god as faction
                FROM battle_record br
                JOIN person p ON br.lost = p.name
                WHERE br.deleted_at IS NULL
                  AND p.deleted_at IS NULL
                  AND br.lost IS NOT NULL
                  {base_date_condition}
            ),
            daily_stats AS (
                SELECT 
                    player_name,
                    faction,
                    date,
                    COUNT(*) as deaths
                FROM filtered_records
                GROUP BY player_name, faction, date
            ),
            total_stats AS (
                SELECT 
                    player_name,
                    faction,
                    SUM(deaths) as total_deaths
                FROM daily_stats
                GROUP BY player_name, faction
            ),
            top_players AS (
                SELECT player_name, faction
                FROM total_stats
                ORDER BY total_deaths DESC
                LIMIT :limit
            )
            SELECT 
                tp.player_name,
                tp.faction,
                ds.date,
                COALESCE(ds.deaths, 0) as deaths
            FROM top_players tp
            LEFT JOIN daily_stats ds ON tp.player_name = ds.player_name
            ORDER BY tp.player_name, ds.date ASC
        """)
        
        result = db.session.execute(query, {'limit': limit})
        
        # 处理结果
        players_dict = {}
        dates_set = set()
        
        for row in result:
            player_name = row.player_name
            if player_name not in players_dict:
                players_dict[player_name] = {
                    'name': player_name,
                    'faction': row.faction,
                    'daily_data': {}
                }
            if row.date:
                date_str = row.date.strftime('%Y-%m-%d')
                dates_set.add(date_str)
                players_dict[player_name]['daily_data'][date_str] = row.deaths
        
        # 获取所有日期并排序
        dates = sorted(list(dates_set))
        
        if not dates:
            return {'dates': [], 'players': []}
        
        # 为每个玩家填充完整日期数组
        players_data = []
        for player_name, player_info in players_dict.items():
            data = [player_info['daily_data'].get(date, 0) for date in dates]
            players_data.append({
                'name': player_info['name'],
                'faction': player_info['faction'],
                'data': data
            })
        
        return {
            'dates': dates,
            'players': players_data
        }
        
    except Exception as e:
        logger.error(f"获取每日死亡数据时出错: {str(e)}", exc_info=True)
        return {'dates': [], 'players': []}

def get_daily_scores_by_player(date_range=None, limit=5):
    """
    获取每日得分数据，按角色和日期分组（优化版：单次查询）
    
    Args:
        date_range: 日期范围，可选值：today, yesterday, week, month, three_months
        limit: 返回前N个得分最高的玩家
    
    Returns:
        dict: {
            'dates': ['2025-01-01', '2025-01-02', ...],
            'players': [
                {
                    'name': '玩家名',
                    'faction': '势力',
                    'data': [10, 15, 20, ...]  # 每天的得分
                },
                ...
            ]
        }
    """
    try:
        # 构建日期筛选条件（基础部分，不含别名）
        base_date_condition = ""
        if date_range:
            if date_range == 'today':
                base_date_condition = "AND DATE(br.publish_at) = CURDATE()"
            elif date_range == 'yesterday':
                base_date_condition = "AND DATE(br.publish_at) = DATE_SUB(CURDATE(), INTERVAL 1 DAY)"
            elif date_range == 'week':
                base_date_condition = "AND br.publish_at >= DATE_SUB(CURDATE(), INTERVAL 7 DAY)"
            elif date_range == 'month':
                base_date_condition = "AND br.publish_at >= DATE_SUB(CURDATE(), INTERVAL 1 MONTH)"
            elif date_range == 'three_months':
                base_date_condition = "AND br.publish_at >= DATE_SUB(CURDATE(), INTERVAL 3 MONTH)"
        
        # 优化：使用单次查询获取所有数据，避免循环查询和子查询
        query = text(f"""
            WITH filtered_records AS (
                SELECT 
                    br.win,
                    br.lost,
                    DATE(br.publish_at) as date
                FROM battle_record br
                WHERE br.deleted_at IS NULL
                  {base_date_condition}
            ),
            win_stats AS (
                SELECT 
                    win as player_name,
                    date,
                    COUNT(*) * 3 as score
                FROM filtered_records
                WHERE win IS NOT NULL
                GROUP BY win, date
            ),
            lost_stats AS (
                SELECT 
                    lost as player_name,
                    date,
                    COUNT(*) as score
                FROM filtered_records
                WHERE lost IS NOT NULL
                GROUP BY lost, date
            ),
            daily_scores AS (
                SELECT 
                    COALESCE(ws.player_name, ls.player_name) as player_name,
                    COALESCE(ws.date, ls.date) as date,
                    COALESCE(ws.score, 0) - COALESCE(ls.score, 0) as daily_score
                FROM win_stats ws
                FULL OUTER JOIN lost_stats ls ON ws.player_name = ls.player_name AND ws.date = ls.date
                UNION
                SELECT 
                    ls.player_name,
                    ls.date,
                    -ls.score as daily_score
                FROM lost_stats ls
                WHERE NOT EXISTS (
                    SELECT 1 FROM win_stats ws 
                    WHERE ws.player_name = ls.player_name AND ws.date = ls.date
                )
            ),
            player_totals AS (
                SELECT 
                    ds.player_name,
                    SUM(ds.daily_score) as total_score
                FROM daily_scores ds
                GROUP BY ds.player_name
            ),
            top_players AS (
                SELECT 
                    pt.player_name,
                    p.god as faction
                FROM player_totals pt
                JOIN person p ON pt.player_name = p.name
                WHERE pt.total_score > 0
                  AND p.deleted_at IS NULL
                ORDER BY pt.total_score DESC
                LIMIT :limit
            )
            SELECT 
                tp.player_name,
                tp.faction,
                ds.date,
                COALESCE(ds.daily_score, 0) as daily_score
            FROM top_players tp
            LEFT JOIN daily_scores ds ON tp.player_name = ds.player_name
            ORDER BY tp.player_name, ds.date ASC
        """)
        
        # MySQL/MariaDB不支持FULL OUTER JOIN，改用UNION方式
        query = text(f"""
            WITH filtered_records AS (
                SELECT 
                    br.win,
                    br.lost,
                    DATE(br.publish_at) as date
                FROM battle_record br
                WHERE br.deleted_at IS NULL
                  {base_date_condition}
            ),
            win_stats AS (
                SELECT 
                    win as player_name,
                    date,
                    COUNT(*) * 3 as score
                FROM filtered_records
                WHERE win IS NOT NULL
                GROUP BY win, date
            ),
            lost_stats AS (
                SELECT 
                    lost as player_name,
                    date,
                    COUNT(*) as score
                FROM filtered_records
                WHERE lost IS NOT NULL
                GROUP BY lost, date
            ),
            daily_scores AS (
                SELECT 
                    ws.player_name,
                    ws.date,
                    ws.score - COALESCE(ls.score, 0) as daily_score
                FROM win_stats ws
                LEFT JOIN lost_stats ls ON ws.player_name = ls.player_name AND ws.date = ls.date
                UNION
                SELECT 
                    ls.player_name,
                    ls.date,
                    -ls.score as daily_score
                FROM lost_stats ls
                WHERE NOT EXISTS (
                    SELECT 1 FROM win_stats ws 
                    WHERE ws.player_name = ls.player_name AND ws.date = ls.date
                )
            ),
            player_totals AS (
                SELECT 
                    ds.player_name,
                    SUM(ds.daily_score) as total_score
                FROM daily_scores ds
                GROUP BY ds.player_name
            ),
            top_players AS (
                SELECT 
                    pt.player_name,
                    p.god as faction
                FROM player_totals pt
                JOIN person p ON pt.player_name = p.name
                WHERE pt.total_score > 0
                  AND p.deleted_at IS NULL
                ORDER BY pt.total_score DESC
                LIMIT :limit
            )
            SELECT 
                tp.player_name,
                tp.faction,
                ds.date,
                COALESCE(ds.daily_score, 0) as daily_score
            FROM top_players tp
            LEFT JOIN daily_scores ds ON tp.player_name = ds.player_name
            ORDER BY tp.player_name, ds.date ASC
        """)
        
        result = db.session.execute(query, {'limit': limit})
        
        # 处理结果
        players_dict = {}
        dates_set = set()
        
        for row in result:
            player_name = row.player_name
            if player_name not in players_dict:
                players_dict[player_name] = {
                    'name': player_name,
                    'faction': row.faction,
                    'daily_data': {}
                }
            if row.date:
                date_str = row.date.strftime('%Y-%m-%d')
                dates_set.add(date_str)
                players_dict[player_name]['daily_data'][date_str] = row.daily_score
        
        # 获取所有日期并排序
        dates = sorted(list(dates_set))
        
        if not dates:
            return {'dates': [], 'players': []}
        
        # 为每个玩家填充完整日期数组
        players_data = []
        for player_name, player_info in players_dict.items():
            data = [player_info['daily_data'].get(date, 0) for date in dates]
            players_data.append({
                'name': player_info['name'],
                'faction': player_info['faction'],
                'data': data
            })
        
        return {
            'dates': dates,
            'players': players_data
        }
        
    except Exception as e:
        logger.error(f"获取每日得分数据时出错: {str(e)}", exc_info=True)
        return {'dates': [], 'players': []} 