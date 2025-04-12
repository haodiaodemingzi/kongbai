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
        death_date_condition = base_date_condition.replace('publish_at', 'br.publish_at') if base_date_condition else ''

        # 获取死亡榜前三
        death_query = text(f"""
            SELECT 
                p.name,
                p.god as faction,
                COUNT(*) as deaths
            FROM battle_record br
            JOIN person p ON br.lost = p.name
            WHERE 1=1 {death_date_condition}
            GROUP BY p.name, p.god
            ORDER BY deaths DESC
            LIMIT 3 
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
        logger.debug(f"获取到死亡榜前三: {top_deaths}")

        faction_stats = []
        factions = ['梵天', '比湿奴', '湿婆']
        
        for faction in factions:
            logger.debug(f"获取 {faction} 势力的统计数据")
            
            # 为子查询动态生成带别名的日期条件
            date_cond_br2 = base_date_condition.replace('publish_at', 'br2.publish_at') if base_date_condition else ''
            date_cond_br3 = base_date_condition.replace('publish_at', 'br3.publish_at') if base_date_condition else ''
            date_cond_br4 = base_date_condition.replace('publish_at', 'br4.publish_at') if base_date_condition else '' # For blessings count
            date_cond_exists = base_date_condition.replace('publish_at', 'br_exists.publish_at') if base_date_condition else '' # For EXISTS clause
            
            # 基础统计查询 - 再次修正版
            stats_query = text(f"""
                WITH player_stats AS (
                    SELECT 
                        p.id,
                        p.name,
                        p.god as faction,
                        (
                            SELECT COUNT(*) 
                            FROM battle_record br2 
                            WHERE br2.win = p.name
                            {date_cond_br2}
                        ) as kills,
                        (
                            SELECT COUNT(*) 
                            FROM battle_record br3 
                            WHERE br3.lost = p.name
                            {date_cond_br3}
                        ) as deaths,
                        (
                            -- Count remarks = '1'
                            SELECT COALESCE(SUM(CASE WHEN br4.remark = '1' THEN 1 ELSE 0 END), 0)
                            FROM battle_record br4
                            WHERE br4.win = p.name
                            {date_cond_br4}
                        ) as blessings,
                        (
                            -- Score calculation: kills * 3 + blessings - deaths
                            (
                                SELECT COUNT(*) 
                                FROM battle_record br2 
                                WHERE br2.win = p.name
                                {date_cond_br2}
                            ) * 3 + 
                            (
                                SELECT COALESCE(SUM(CASE WHEN br4.remark = '1' THEN 1 ELSE 0 END), 0)
                                FROM battle_record br4
                                WHERE br4.win = p.name
                                {date_cond_br4}
                            ) - 
                            (
                                SELECT COUNT(*) 
                                FROM battle_record br3 
                                WHERE br3.lost = p.name
                                {date_cond_br3}
                            )
                        ) as score
                    FROM person p
                    WHERE p.god = :faction
                      AND p.deleted_at IS NULL
                      -- Correctly apply date condition within EXISTS
                      AND EXISTS (
                          SELECT 1 
                          FROM battle_record br_exists 
                          WHERE (br_exists.win = p.name OR br_exists.lost = p.name)
                          {date_cond_exists} -- Apply date condition on br_exists here
                      )
                )
                SELECT 
                    -- Count distinct players included in player_stats CTE
                    COUNT(DISTINCT ps.id) as player_count, 
                    COALESCE(SUM(ps.kills), 0) as total_kills,
                    COALESCE(SUM(ps.deaths), 0) as total_deaths,
                    COALESCE(SUM(ps.blessings), 0) as total_blessings,
                    (
                        SELECT ps_sub.name 
                        FROM player_stats ps_sub
                        WHERE ps_sub.kills > 0 -- Ensure killer has kills
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
        return faction_stats, top_deaths
        
    except Exception as e:
        logger.error(f"获取势力统计数据时出错: {str(e)}", exc_info=True)
        return [], []

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