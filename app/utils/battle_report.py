#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
战斗报告生成工具，用于从battle_record和person表生成战斗报告
"""

import csv
import logging
import os
from datetime import datetime
from app.extensions import db
from app.utils.logger import get_logger
from sqlalchemy import text

logger = get_logger()

def generate_battle_report(output_dir="reports", start_date=None, end_date=None):
    """
    生成战斗报告，包括CSV文件和HTML报告
    
    参数:
        output_dir: 输出目录
        start_date: 开始日期 (datetime对象或None，如果为None则使用数据库中最早的记录时间)
        end_date: 结束日期 (datetime对象或None，如果为None则使用数据库中最晚的记录时间)
        
    返回:
        (csv_filename, report_data, god_stats, stats_summary): 包含CSV文件路径、报告数据、阵营统计和总体统计的元组
    """
    logger.info("开始生成战斗报告")
    start_time = datetime.now()
    
    try:
        # 创建输出目录（如果不存在）
        os.makedirs(output_dir, exist_ok=True)
        
        # 如果未指定日期，则获取数据库中最早和最晚的记录时间
        if start_date is None or end_date is None:
            from sqlalchemy import func
            from app.models.battle_record import BattleRecord
            
            min_max_dates = db.session.query(
                func.min(BattleRecord.publish_at),
                func.max(BattleRecord.publish_at)
            ).first()
            
            if min_max_dates:
                db_min_date, db_max_date = min_max_dates
                if start_date is None and db_min_date:
                    start_date = db_min_date.date()
                    logger.info(f"未指定开始日期，使用数据库中最早的记录时间: {start_date}")
                    
                if end_date is None and db_max_date:
                    end_date = db_max_date.date()
                    logger.info(f"未指定结束日期，使用数据库中最晚的记录时间: {end_date}")
        
        # 如果仍为None，则使用默认值
        if start_date is None:
            start_date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0).date()
        if end_date is None:
            end_date = datetime.now().replace(hour=23, minute=59, second=59, microsecond=999999).date()
            
        # 确保开始日期不晚于结束日期
        if start_date > end_date:
            start_date, end_date = end_date, start_date
            
        # 构建日期范围的描述
        if start_date == end_date:
            date_range_desc = f"{start_date} 的战斗数据"
        else:
            date_range_desc = f"{start_date} 至 {end_date} 的战斗数据"
        
        logger.info(f"生成报告的日期范围: {date_range_desc}")
        
        # 生成文件名
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        csv_filename = os.path.join(output_dir, f"battle_report_{start_date.strftime('%Y%m%d')}_{end_date.strftime('%Y%m%d')}_{timestamp}.csv")
        
        # 构建SQL查询，包含日期范围过滤
        date_filter = ""
        
        if start_date:
            date_filter += f" AND br.publish_at >= '{start_date.strftime('%Y-%m-%d %H:%M:%S')}'"
            
        if end_date:
            date_filter += f" AND br.publish_at <= '{end_date.strftime('%Y-%m-%d %H:%M:%S')}'"
        
        # 执行SQL查询获取战斗报告数据
        report_sql = f"""
        SELECT 
            p.id AS player_id,
            p.name AS player_name,
            p.job AS player_job,
            p.god AS player_god,
            COUNT(CASE WHEN br.win != '0' THEN 1 END) AS kills,
            COUNT(CASE WHEN br.lost != '0' THEN 1 END) AS deaths,
            SUM(COALESCE(br.remark, 0)) AS blessings,
            CASE WHEN COUNT(CASE WHEN br.lost != '0' THEN 1 END) > 0 
                 THEN ROUND(COUNT(CASE WHEN br.win != '0' THEN 1 END) * 1.0 / COUNT(CASE WHEN br.lost != '0' THEN 1 END), 2) 
                 ELSE COUNT(CASE WHEN br.win != '0' THEN 1 END) END AS kd_ratio,
            (COUNT(CASE WHEN br.win != '0' THEN 1 END) * 3 + SUM(COALESCE(br.remark, 0)) - COUNT(CASE WHEN br.lost != '0' THEN 1 END)) AS score,
            MAX(COALESCE(br.position, '0,0')) AS last_position,
            MAX(br.publish_at) AS last_battle_time,
            MAX(p.updated_at) AS last_updated
        FROM 
            person p
        LEFT JOIN 
            battle_record br ON p.id = br.create_by
        WHERE
            p.deleted_at IS NULL{date_filter}
        GROUP BY
            p.id, p.name, p.job, p.god
        ORDER BY 
            score DESC, kills DESC, deaths ASC;
        """
        
        # 使用SQLAlchemy执行原始SQL
        result = db.session.execute(text(report_sql))
        
        # 获取列名
        columns = result.keys()
        
        # 提取数据
        rows = result.fetchall()
        
        # 将行结果转换为字典列表，以便于模板访问
        report_data = []
        for row in rows:
            player_data = {}
            for idx, column in enumerate(columns):
                # 获取列的值，并处理可能的None值
                value = row[idx]
                player_data[column] = value
                
                # 确保数值字段为数值类型
                if column in ('kills', 'deaths', 'blessings', 'score', 'kd_ratio'):
                    try:
                        if value is not None:
                            # 尝试转换为浮点数
                            value = float(value)
                            # 如果是整数则转为整数类型
                            if value.is_integer():
                                value = int(value)
                            player_data[column] = value
                        else:
                            # 如果是None则设为0
                            player_data[column] = 0
                    except (ValueError, TypeError, AttributeError):
                        # 如果转换失败，设置为默认值0
                        player_data[column] = 0
                        logger.warning(f"字段 {column} 的值 '{value}' 无法转换为数值，设置为0")
            
            # 特殊处理：确保player_god字段有值
            if player_data.get('player_god') is None or player_data.get('player_god') == '':
                player_data['player_god'] = '未知'
                
            report_data.append(player_data)
        
        logger.info(f"查询到 {len(report_data)} 名玩家的战斗数据.{date_range_desc}")
        
        # 将结果写入CSV文件
        with open(csv_filename, 'w', newline='', encoding='utf-8') as csvfile:
            csv_writer = csv.writer(csvfile)
            
            # 写入CSV头部
            csv_writer.writerow(columns)
            
            # 写入数据行
            for row in rows:
                csv_writer.writerow(row)
        
        logger.info(f"战斗报告已保存为CSV文件: {csv_filename}")
        
        # 确保包含player_id字段
        for p in report_data:
            # 确保包含player_id字段
            if 'player_id' not in p:
                if 'id' in p:
                    p['player_id'] = p['id']

        # 创建击杀排行榜
        kills_leaders = sorted(report_data, key=lambda x: float(x.get('kills', 0) or 0), reverse=True)[:10]
        for player in kills_leaders:
            # 确保所有需要的字段都存在
            if 'player_id' not in player and 'id' in player:
                player['player_id'] = player['id']
        
        # 创建K/D比排行榜
        valid_kd = [p for p in report_data if float(p.get('deaths', 0) or 0) > 0]
        kd_leaders = sorted(valid_kd, key=lambda x: float(x.get('kd_ratio', 0) or 0), reverse=True)[:10]
        for player in kd_leaders:
            if 'player_id' not in player and 'id' in player:
                player['player_id'] = player['id']
        
        # 创建总分排行榜
        score_leaders = sorted(report_data, key=lambda x: float(x.get('score', 0) or 0), reverse=True)[:10]
        for player in score_leaders:
            if 'player_id' not in player and 'id' in player:
                player['player_id'] = player['id']
        
        # 阵营统计
        god_groups = {}
        for player in report_data:
            # 确保god字段有值
            god = player.get('player_god', '未知')
            if god is None or god == '':
                god = '未知'
                
            if god not in god_groups:
                god_groups[god] = []
            god_groups[god].append(player)
        
        # 计算每个阵营的总击杀、总死亡和总得分
        god_stats = {}
        for god, players in god_groups.items():
            try:
                # 使用安全的方式计算总和
                total_kills = sum(float(p.get('kills', 0) or 0) for p in players)
                total_deaths = sum(float(p.get('deaths', 0) or 0) for p in players)
                total_score = sum(float(p.get('score', 0) or 0) for p in players)
                player_count = len(players)
                
                # 格式化为整数或小数
                total_kills_formatted = int(total_kills) if total_kills.is_integer() else round(total_kills, 1)
                total_deaths_formatted = int(total_deaths) if total_deaths.is_integer() else round(total_deaths, 1)
                total_score_formatted = int(total_score) if total_score.is_integer() else round(total_score, 1)
                
                # 计算平均分
                avg_score = 0
                if player_count > 0:
                    avg_score = round(total_score / player_count, 1)
                
                god_stats[god] = {
                    'name': god,
                    'total_kills': total_kills_formatted,
                    'total_deaths': total_deaths_formatted,
                    'total_score': total_score_formatted,
                    'player_count': player_count,
                    'avg_score': avg_score
                }
            except Exception as e:
                logger.error(f"计算阵营 {god} 统计数据时出错: {str(e)}")
                # 提供一个默认值，避免模板渲染错误
                god_stats[god] = {
                    'name': god,
                    'total_kills': 0,
                    'total_deaths': 0,
                    'total_score': 0,
                    'player_count': len(players),
                    'avg_score': 0
                }
                
        # 记录一些统计数据
        total_players = len(report_data)
        
        # 安全地计算总和，处理可能的None值和类型转换错误
        try:
            total_kills = sum(float(p.get('kills', 0) or 0) for p in report_data)
            total_deaths = sum(float(p.get('deaths', 0) or 0) for p in report_data)
            total_blessings = sum(float(p.get('blessings', 0) or 0) for p in report_data)
            
            # 计算平均值
            avg_kills = 0
            avg_deaths = 0
            if total_players > 0:
                avg_kills = round(total_kills / total_players, 1)
                avg_deaths = round(total_deaths / total_players, 1)
                
            # 格式化为整数(如可能)
            total_kills = int(total_kills) if total_kills.is_integer() else round(total_kills, 1)
            total_deaths = int(total_deaths) if total_deaths.is_integer() else round(total_deaths, 1)
            total_blessings = int(total_blessings) if total_blessings.is_integer() else round(total_blessings, 1)
        except Exception as e:
            logger.error(f"计算总体统计数据时出错: {str(e)}")
            # 提供默认值
            total_kills = 0
            total_deaths = 0
            total_blessings = 0
            avg_kills = 0
            avg_deaths = 0
            
        stats_summary = {
            'total_players': total_players,
            'total_kills': total_kills,
            'total_deaths': total_deaths,
            'total_blessings': total_blessings,
            'avg_kills': avg_kills,
            'avg_deaths': avg_deaths,
            'date_range': date_range_desc,
            'date_generated': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        # 计算处理时间
        end_time = datetime.now()
        process_time = (end_time - start_time).total_seconds()
        logger.info(f"战斗报告生成完成，处理时间: {process_time:.2f} 秒")
        
        return csv_filename, report_data, god_stats, stats_summary

    except Exception as e:
        logger.error(f"生成战斗报告时发生错误: {str(e)}", exc_info=True)
        # 在出错的情况下，确保返回了所有需要的数据结构，即使是空的
        return None, [], {}, {
            'total_players': 0,
            'total_kills': 0, 
            'total_deaths': 0,
            'total_blessings': 0,
            'avg_kills': 0,
            'avg_deaths': 0,
            'date_range': '数据加载出错',
            'date_generated': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

def export_battle_sql(start_date=None, end_date=None):
    """
    导出生成战斗报告的SQL查询
    
    参数:
        start_date: 开始日期 (datetime对象或None，如果为None则使用数据库中最早的记录时间)
        end_date: 结束日期 (datetime对象或None，如果为None则使用数据库中最晚的记录时间)
        
    返回:
        SQL查询字符串
    """
    logger.info("导出战斗报告SQL查询")
    
    # 如果未指定日期，则获取数据库中最早和最晚的记录时间
    if start_date is None or end_date is None:
        from sqlalchemy import func
        from app.models.battle_record import BattleRecord
        
        min_max_dates = db.session.query(
            func.min(BattleRecord.publish_at),
            func.max(BattleRecord.publish_at)
        ).first()
        
        if min_max_dates:
            db_min_date, db_max_date = min_max_dates
            if start_date is None and db_min_date:
                start_date = db_min_date.date()
                
            if end_date is None and db_max_date:
                end_date = db_max_date.date()
    
    # 如果仍为None，则使用默认值
    if start_date is None:
        start_date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0).date()
    if end_date is None:
        end_date = datetime.now().replace(hour=23, minute=59, second=59, microsecond=999999).date()
        
    # 确保开始日期不晚于结束日期
    if start_date > end_date:
        start_date, end_date = end_date, start_date
    
    # 构建日期过滤条件
    date_filter = ""
    
    if start_date:
        date_filter += f" AND br.publish_at >= '{start_date.strftime('%Y-%m-%d %H:%M:%S')}'"
    if end_date:
        date_filter += f" AND br.publish_at <= '{end_date.strftime('%Y-%m-%d %H:%M:%S')}'"
    
    # 构建SQL查询
    report_sql = f"""
    SELECT 
        p.id AS player_id,
        p.name AS player_name,
        p.job AS player_job,
        p.god AS player_god,
        COUNT(CASE WHEN br.win != '0' THEN 1 END) AS kills,
        COUNT(CASE WHEN br.lost != '0' THEN 1 END) AS deaths,
        SUM(COALESCE(br.remark, 0)) AS blessings,
        CASE WHEN COUNT(CASE WHEN br.lost != '0' THEN 1 END) > 0 
             THEN ROUND(COUNT(CASE WHEN br.win != '0' THEN 1 END) * 1.0 / COUNT(CASE WHEN br.lost != '0' THEN 1 END), 2) 
             ELSE COUNT(CASE WHEN br.win != '0' THEN 1 END) END AS kd_ratio,
        (COUNT(CASE WHEN br.win != '0' THEN 1 END) * 3 + SUM(COALESCE(br.remark, 0)) - COUNT(CASE WHEN br.lost != '0' THEN 1 END)) AS score,
        MAX(COALESCE(br.position, '0,0')) AS last_position,
        MAX(br.publish_at) AS last_battle_time,
        MAX(p.updated_at) AS last_updated
    FROM 
        person p
    LEFT JOIN 
        battle_record br ON p.id = br.create_by
    WHERE
        p.deleted_at IS NULL{date_filter}
    GROUP BY
        p.id, p.name, p.job, p.god
    ORDER BY 
        score DESC, kills DESC, deaths ASC;
    """
    
    # 记录完整的SQL
    logger.info(f"生成的SQL查询: {report_sql}")
    
    # 返回SQL查询字符串
    return report_sql 