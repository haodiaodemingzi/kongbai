from app.models.player import Person, BattleRecord
from app import db
from sqlalchemy import func, desc, and_, text
from datetime import datetime
import json
from app.utils.logger import get_logger

logger = get_logger()

def get_faction_stats():
    """获取各个势力的统计数据"""
    logger.info("获取势力统计数据")
    
    # 查询所有势力
    factions = ['梵天', '比湿奴', '湿婆']
    results = []
    
    # 获取死亡榜前三
    top_deaths_sql = """
    WITH player_deaths AS (
        SELECT 
            p.id AS player_id,
            p.name AS player_name,
            p.god AS player_faction,
            COUNT(DISTINCT br.id) as deaths
        FROM 
            person p
        JOIN 
            battle_record br ON br.lost = p.name
        GROUP BY 
            p.id, p.name, p.god
        HAVING 
            COUNT(DISTINCT br.id) > 0
    )
    SELECT 
        player_id,
        player_name,
        player_faction,
        deaths
    FROM 
        player_deaths
    ORDER BY 
        deaths DESC
    LIMIT 5
    """
    
    top_deaths = []
    try:
        death_results = db.session.execute(text(top_deaths_sql))
        top_deaths = [
            {
                'name': row.player_name,
                'faction': row.player_faction,
                'deaths': row.deaths
            }
            for row in death_results
        ]
        logger.debug(f"获取到死亡榜前三: {top_deaths}")
    except Exception as e:
        logger.error(f"获取死亡榜前三时出错: {str(e)}", exc_info=True)
    
    for faction in factions:
        logger.debug(f"获取 {faction} 势力的统计数据")
        
        try:
            # 使用SQL查询获取阵营汇总数据
            faction_sql = """
            WITH faction_stats AS (
                SELECT 
                    p.god AS faction,
                    -- 统计击杀次数(通过win字段关联)
                    COUNT(DISTINCT CASE WHEN br.win = p.name THEN br.id END) as total_kills,
                    -- 统计死亡次数(通过lost字段关联)
                    COUNT(DISTINCT CASE WHEN br.lost = p.name THEN br.id END) as total_deaths,
                    -- 统计祝福次数(只有win的玩家才会有祝福)
                    SUM(CASE WHEN br.win = p.name THEN COALESCE(br.remark, 0) ELSE 0 END) as total_blessings,
                    COUNT(DISTINCT p.id) AS player_count
                FROM 
                    person p
                LEFT JOIN 
                    battle_record br ON br.win = p.name OR br.lost = p.name
                WHERE 
                    p.god = :faction
                GROUP BY 
                    p.god
            )
            SELECT 
                faction,
                total_kills,
                total_deaths,
                total_blessings,
                (total_kills * 3 + total_blessings - total_deaths) AS total_score,
                CASE WHEN total_deaths > 0 
                     THEN ROUND(CAST(total_kills AS FLOAT) / total_deaths, 2) 
                     ELSE total_kills END AS kd_ratio,
                player_count
            FROM 
                faction_stats
            """
            
            faction_data = db.session.execute(text(faction_sql), {"faction": faction}).first()
            
            # 获取该势力击杀数最高的玩家
            top_killer_sql = """
            SELECT 
                p.id AS player_id,
                p.name AS player_name,
                COUNT(DISTINCT CASE WHEN br.win = p.name THEN br.id END) AS kills
            FROM 
                person p
            LEFT JOIN 
                battle_record br ON br.win = p.name OR br.lost = p.name
            WHERE 
                p.god = :faction
            GROUP BY 
                p.id, p.name
            HAVING 
                COUNT(DISTINCT CASE WHEN br.win = p.name THEN br.id END) > 0 
                OR COUNT(DISTINCT CASE WHEN br.lost = p.name THEN br.id END) > 0
            ORDER BY 
                kills DESC
            LIMIT 1
            """
            
            top_killer = db.session.execute(text(top_killer_sql), {"faction": faction}).first()
            
            # 获取该势力得分最高的玩家
            top_scorer_sql = """
            WITH player_scores AS (
                SELECT 
                    p.id AS player_id,
                    p.name AS player_name,
                    COUNT(DISTINCT CASE WHEN br.win = p.name THEN br.id END) as kills,
                    COUNT(DISTINCT CASE WHEN br.lost = p.name THEN br.id END) as deaths,
                    SUM(CASE WHEN br.win = p.name THEN COALESCE(br.remark, 0) ELSE 0 END) as blessings
                FROM 
                    person p
                LEFT JOIN 
                    battle_record br ON br.win = p.name OR br.lost = p.name
                WHERE 
                    p.god = :faction
                GROUP BY 
                    p.id, p.name
                HAVING 
                    COUNT(DISTINCT CASE WHEN br.win = p.name THEN br.id END) > 0 
                    OR COUNT(DISTINCT CASE WHEN br.lost = p.name THEN br.id END) > 0
            )
            SELECT 
                player_id,
                player_name,
                (kills * 3 + blessings - deaths) AS score
            FROM 
                player_scores
            ORDER BY 
                score DESC
            LIMIT 1
            """
            
            top_scorer = db.session.execute(text(top_scorer_sql), {"faction": faction}).first()
            
            # 如果没有数据则提供默认值
            if not faction_data:
                stats = {
                    'total_kills': 0,
                    'total_deaths': 0,
                    'total_blessings': 0,
                    'total_score': 0,
                    'kd_ratio': 0,
                    'player_count': 0,
                    'top_killer': {'name': 'N/A', 'kills': 0},
                    'top_scorer': {'name': 'N/A', 'score': 0}
                }
            else:
                stats = {
                    'total_kills': faction_data.total_kills or 0,
                    'total_deaths': faction_data.total_deaths or 0,
                    'total_blessings': faction_data.total_blessings or 0,
                    'total_score': faction_data.total_score or 0,
                    'kd_ratio': faction_data.kd_ratio or 0,
                    'player_count': faction_data.player_count or 0,
                    'top_killer': {
                        'name': top_killer.player_name if top_killer else 'N/A', 
                        'kills': top_killer.kills if top_killer else 0
                    },
                    'top_scorer': {
                        'name': top_scorer.player_name if top_scorer else 'N/A', 
                        'score': top_scorer.score if top_scorer else 0
                    }
                }
            
            results.append((faction, stats))
            logger.debug(f"{faction} 势力统计: 击杀 {stats['total_kills']}, 死亡 {stats['total_deaths']}, 得分 {stats['total_score']}")
            
        except Exception as e:
            logger.error(f"获取 {faction} 势力统计数据时出错: {str(e)}", exc_info=True)
            # 添加空统计数据
            stats = {
                'total_kills': 0,
                'total_deaths': 0,
                'total_blessings': 0,
                'total_score': 0,
                'kd_ratio': 0,
                'player_count': 0,
                'top_killer': {'name': 'N/A', 'kills': 0},
                'top_scorer': {'name': 'N/A', 'score': 0}
            }
            results.append((faction, stats))
    
    logger.info(f"返回 {len(results)} 个势力的统计数据")
    return results, top_deaths


def get_player_rankings(faction=None, limit=30):
    """获取玩家排名，可按势力筛选"""
    logger.info(f"获取玩家排名，势力筛选：{faction}, 限制数量：{limit}")
    
    try:
        # 使用SQLAlchemy的text函数执行原生SQL查询
        from sqlalchemy import text
        
        # 构建基础SQL查询
        sql = """
        WITH player_stats AS (
            SELECT 
                p.id AS player_id,
                p.name AS player_name,
                p.job AS player_job,
                p.god AS player_god,
                -- 统计击杀次数(通过win字段关联)
                COUNT(DISTINCT CASE WHEN br.win = p.name THEN br.id END) as kills,
                -- 统计死亡次数(通过lost字段关联)
                COUNT(DISTINCT CASE WHEN br.lost = p.name THEN br.id END) as deaths,
                -- 统计祝福次数(只有win的玩家才会有祝福)
                SUM(CASE WHEN br.win = p.name THEN COALESCE(br.remark, 0) ELSE 0 END) as blessings,
                -- 获取最后战斗位置和时间
                MAX(br.position) as last_position,
                MAX(br.publish_at) as last_battle_time,
                MAX(p.updated_at) as last_updated
            FROM 
                person p
            LEFT JOIN 
                battle_record br ON br.win = p.name OR br.lost = p.name
            WHERE 
                p.deleted_at IS NULL
        """
        
        # 添加势力筛选条件（如果提供）
        if faction:
            sql += f" AND p.god = '{faction}'"
            logger.debug(f"按势力 {faction} 筛选玩家")
        
        # 完成分组
        sql += """
            GROUP BY 
                p.id, p.name, p.job, p.god
            HAVING 
                COUNT(DISTINCT CASE WHEN br.win = p.name THEN br.id END) > 0 
                OR COUNT(DISTINCT CASE WHEN br.lost = p.name THEN br.id END) > 0
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
            last_battle_time,
            last_updated
        FROM 
            player_stats
        ORDER BY 
            score DESC, kills DESC, deaths ASC
        """
        
        # 添加限制条件
        if limit:
            sql += f" LIMIT {limit}"
        
        # 执行查询
        result = db.session.execute(text(sql))
        
        # 处理结果
        player_data = []
        for row in result:
            # 将查询结果转换为字典
            player = {
                'id': row.player_id,
                'name': row.player_name,
                'god': row.player_god,
                'job': row.player_job,
                'kills': row.kills,
                'deaths': row.deaths,
                'kd_ratio': row.kd_ratio,
                'score': row.score,
                'blessings': row.blessings
            }
            player_data.append(player)
        
        logger.info(f"返回 {len(player_data)} 名玩家的排名数据")
        return player_data
        
    except Exception as e:
        logger.error(f"获取玩家排名时出错: {str(e)}", exc_info=True)
        return []


def get_battle_details_by_player(person_id):
    """获取指定玩家的战斗明细"""
    logger.info(f"获取玩家ID {person_id} 的战斗明细")
    
    try:
        # 获取玩家基本信息
        player = Person.query.filter_by(id=person_id).first()
        if not player:
            logger.warning(f"找不到ID为 {person_id} 的玩家")
            return None
        
        logger.debug(f"找到玩家: {player.name}, 势力: {player.god}, 职业: {player.job}")
        
        # 使用SQL查询获取战绩汇总数据
        sql = """
        WITH player_battle_stats AS (
            SELECT 
                p.id AS player_id,
                p.name AS player_name,
                p.job AS player_job,
                p.god AS player_god,
                -- 统计击杀次数(通过win字段关联)
                COUNT(DISTINCT CASE WHEN br.win = p.name THEN br.id END) as kills,
                -- 统计死亡次数(通过lost字段关联)
                COUNT(DISTINCT CASE WHEN br.lost = p.name THEN br.id END) as deaths,
                -- 统计祝福次数(只有win的玩家才会有祝福)
                SUM(CASE WHEN br.win = p.name THEN COALESCE(br.remark, 0) ELSE 0 END) as blessings,
                -- 获取最后战斗位置和时间
                MAX(br.position) as last_position,
                MAX(br.publish_at) as last_battle_time,
                MAX(p.updated_at) as last_updated
            FROM 
                person p
            LEFT JOIN 
                battle_record br ON br.win = p.name OR br.lost = p.name
            WHERE 
                p.id = :person_id
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
            last_battle_time,
            last_updated
        FROM 
            player_battle_stats
        """
        
        result = db.session.execute(text(sql), {"person_id": person_id}).first()
        
        # 如果没有战绩记录，返回基本信息
        if not result:
            logger.debug(f"玩家 {player.name} 没有战绩记录，返回基本信息")
            return {
                'id': player.id,
                'name': player.name,
                'god': player.god,
                'job': player.job,
                'kills': 0,
                'deaths': 0,
                'kd_ratio': 0,
                'score': 0,
                'blessings': 0,
                'last_battle_time': None,
                'last_position': '0,0'
            }
        
        # 创建包含详细信息的字典
        player_details = {
            'id': result.player_id,
            'name': result.player_name,
            'god': result.player_god,
            'job': result.player_job,
            'kills': result.kills,
            'deaths': result.deaths,
            'kd_ratio': result.kd_ratio,
            'score': result.score,
            'blessings': result.blessings,
            'last_battle_time': result.last_battle_time,
            'last_position': result.last_position
        }
        
        # 获取近期战斗记录
        recent_battles_sql = """
        SELECT 
            br.id,
            CASE 
                WHEN br.win = :player_name THEN br.lost  -- 如果是胜利者，显示被击杀者
                ELSE br.win  -- 如果是失败者，显示击杀者
            END as opponent_name,
            CASE 
                WHEN br.win = :player_name THEN 'win'  -- 玩家是胜利者
                ELSE 'lost'  -- 玩家是失败者
            END as battle_result,
            br.remark as blessings,
            br.position,
            br.publish_at
        FROM 
            battle_record br 
        WHERE 
            br.win = :player_name OR br.lost = :player_name
        ORDER BY 
            br.publish_at DESC 
        LIMIT 50
        """
        
        recent_battles = db.session.execute(text(recent_battles_sql), {"player_name": player.name}).fetchall()
        
        # 添加近期战斗记录
        player_details['recent_battles'] = [{
            'id': battle.id,
            'opponent_name': battle.opponent_name,
            'battle_result': battle.battle_result,
            'blessings': battle.blessings,
            'position': battle.position,
            'time': battle.publish_at.strftime('%Y-%m-%d %H:%M:%S') if battle.publish_at else None
        } for battle in recent_battles]
        
        # 获取玩家击杀其他玩家的次数
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
            person v ON br.lost = v.name  -- 被击杀者关联
        WHERE 
            br.win = :player_name  -- 当前玩家是胜利者(击杀者)
        GROUP BY 
            v.id, v.name, v.job, v.god
        ORDER BY 
            kill_count DESC
        LIMIT 20
        """
        
        kills_details = db.session.execute(text(kills_details_sql), {"player_name": player.name}).fetchall()
        
        # 添加击杀详情
        player_details['kills_details'] = [{
            'id': kill.victim_id,
            'name': kill.victim_name,
            'job': kill.victim_job,
            'god': kill.victim_god,
            'count': kill.kill_count
        } for kill in kills_details]
        
        # 获取被其他玩家击杀的次数
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
            person k ON br.win = k.name  -- 击杀者关联
        WHERE 
            br.lost = :player_name  -- 当前玩家是失败者(被击杀者)
        GROUP BY 
            k.id, k.name, k.job, k.god
        ORDER BY 
            death_count DESC
        LIMIT 20
        """
        
        deaths_details = db.session.execute(text(deaths_details_sql), {"player_name": player.name}).fetchall()
        
        # 添加死亡详情
        player_details['deaths_details'] = [{
            'id': death.killer_id,
            'name': death.killer_name,
            'job': death.killer_job,
            'god': death.killer_god,
            'count': death.death_count
        } for death in deaths_details]
        
        logger.info(f"返回玩家 {player.name} 的战斗明细")
        return player_details
        
    except Exception as e:
        logger.error(f"获取玩家战斗明细时出错: {str(e)}", exc_info=True)
        return None


def export_data_to_json(faction=None):
    """导出数据为JSON字符串，替代Excel导出功能"""
    logger.info(f"导出数据为JSON，势力筛选：{faction}")
    
    try:
        # 使用SQLAlchemy的text函数执行原生SQL查询
        from sqlalchemy import text
        
        # 构建基础SQL查询
        sql = """
        WITH player_stats AS (
            SELECT 
                p.id AS player_id,
                p.name AS player_name,
                p.job AS player_job,
                p.god AS player_god,
                -- 统计击杀次数(通过win字段关联)
                COUNT(DISTINCT CASE WHEN br.win = p.name THEN br.id END) as kills,
                -- 统计死亡次数(通过lost字段关联)
                COUNT(DISTINCT CASE WHEN br.lost = p.name THEN br.id END) as deaths,
                -- 统计祝福次数(只有win的玩家才会有祝福)
                SUM(CASE WHEN br.win = p.name THEN COALESCE(br.remark, 0) ELSE 0 END) as blessings,
                -- 获取最后战斗位置和时间
                MAX(br.position) as last_position,
                MAX(br.publish_at) as last_battle_time,
                MAX(p.updated_at) as last_updated
            FROM 
                person p
            LEFT JOIN 
                battle_record br ON br.win = p.name OR br.lost = p.name
            WHERE 
                p.deleted_at IS NULL
        """
        
        # 添加势力筛选条件（如果提供）
        if faction:
            sql += f" AND p.god = '{faction}'"
            logger.debug(f"按势力 {faction} 筛选玩家")
        
        # 完成分组和计算
        sql += """
            GROUP BY 
                p.id, p.name, p.job, p.god
            HAVING 
                COUNT(DISTINCT CASE WHEN br.win = p.name THEN br.id END) > 0 
                OR COUNT(DISTINCT CASE WHEN br.lost = p.name THEN br.id END) > 0
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
            last_battle_time,
            last_updated
        FROM 
            player_stats
        ORDER BY 
            score DESC, kills DESC, deaths ASC
        """
        
        # 执行查询
        result = db.session.execute(text(sql))
        
        # 处理结果
        player_data = []
        for row in result:
            player_data.append({
                '玩家ID': row.player_id,
                '玩家名称': row.player_name,
                '所属势力': row.player_god,
                '职业': row.player_job,
                '击杀数': row.kills,
                '死亡数': row.deaths,
                'K/D比': row.kd_ratio,
                '祝福次数': row.blessings,
                '得分': row.score,
                '最后战斗时间': row.last_battle_time.strftime('%Y-%m-%d %H:%M:%S') if row.last_battle_time else None
            })
        
        logger.info(f"导出 {len(player_data)} 名玩家的数据")
        
        # 生成文件名
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"battle_data_{timestamp}.json"
        if faction:
            filename = f"battle_data_{faction}_{timestamp}.json"
        
        # 转换为JSON字符串
        json_data = json.dumps(player_data, ensure_ascii=False, indent=2)
        
        return json_data, filename
    except Exception as e:
        logger.error(f"导出数据时出错: {str(e)}", exc_info=True)
        return "{\"error\": \"导出数据时出错: " + str(e) + "\"}", "error.json"


def get_statistics(faction=None):
    """
    获取总统计数据，考虑到同一个玩家可能有多个ID的情况
    :param faction: 势力名称（可选）
    :return: 总玩家数, 总击杀数, 总死亡数, 总得分
    """
    logger.info(f"获取总统计数据，势力筛选：{faction}")
    
    try:
        # 构建查询，按玩家组统计
        sql = """
        WITH player_distinct AS (
            -- 获取所有有效的玩家ID，并关联其分组信息
            SELECT 
                p.id,
                p.name,
                p.god,
                -- 使用分组ID作为分组键，如果没有分组则使用玩家自身ID
                COALESCE(p.player_group_id, p.id) AS group_key
            FROM 
                person p
            WHERE 
                p.deleted_at IS NULL
                AND (:faction IS NULL OR p.god = :faction)
        ),
        unique_group_players AS (
            -- 按分组计算不重复的玩家数（每个分组只计算一次）
            SELECT 
                group_key,
                COUNT(DISTINCT id) AS player_count,
                -- 示例：可以在这里添加更多聚合字段
                MIN(god) AS faction
            FROM 
                player_distinct
            GROUP BY 
                group_key
        ),
        battle_stats AS (
            -- 计算战斗统计数据
            SELECT 
                pd.group_key,
                COUNT(DISTINCT CASE WHEN br.win = pd.name THEN br.id END) AS kills,
                COUNT(DISTINCT CASE WHEN br.lost = pd.name THEN br.id END) AS deaths
            FROM 
                player_distinct pd
            LEFT JOIN 
                battle_record br ON pd.name IN (br.win, br.lost)
            GROUP BY 
                pd.group_key
        )
        -- 最终汇总数据
        SELECT 
            -- 计算不重复的分组数量为实际玩家数
            COUNT(DISTINCT ugp.group_key) AS total_players,
            -- 汇总所有击杀数
            SUM(bs.kills) AS total_kills,
            -- 汇总所有死亡数
            SUM(bs.deaths) AS total_deaths
        FROM 
            unique_group_players ugp
        LEFT JOIN 
            battle_stats bs ON ugp.group_key = bs.group_key
        """
        
        # 添加势力筛选条件
        params = {}
        if faction:
            params['faction'] = faction
            
        # 执行查询
        result = db.session.execute(text(sql), params).fetchone()
        
        # 处理结果
        total_players = result.total_players or 0
        total_kills = result.total_kills or 0
        total_deaths = result.total_deaths or 0
        
        # 计算总得分
        total_score = (total_kills * 3) - total_deaths
        
        logger.debug(f"统计结果（考虑玩家分组）：总实际玩家数={total_players}, 总击杀数={total_kills}, 总死亡数={total_deaths}, 总得分={total_score}")
        
        return total_players, total_kills, total_deaths, total_score
        
    except Exception as e:
        logger.error(f"获取总统计数据时出错: {str(e)}", exc_info=True)
        return 0, 0, 0, 0 