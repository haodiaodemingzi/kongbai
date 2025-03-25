#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
文件解析工具，用于解析CSV和文本文件
"""

import re
import os
import codecs
from datetime import datetime
from app.models.player import Person, BattleRecord
from app import db
from app.utils.logger import get_logger
import chardet
from app.utils.transaction_helper import retry_on_deadlock

logger = get_logger()

def parse_csv_file(file_path):
    """解析CSV文件，返回清洗后的数据"""
    try:
        df = pd.read_csv(file_path)
        # 检查必要的列是否存在
        required_columns = ['玩家ID', '玩家名称', '所属联盟', '击杀数', '死亡数', '助攻数', '得分', '战斗时间']
        missing_columns = [col for col in required_columns if col not in df.columns]
        
        if missing_columns:
            return False, f"缺少必要的列：{', '.join(missing_columns)}", None
        
        # 数据类型转换和清洗
        df['击杀数'] = pd.to_numeric(df['击杀数'], errors='coerce').fillna(0).astype(int)
        df['死亡数'] = pd.to_numeric(df['死亡数'], errors='coerce').fillna(0).astype(int)
        df['助攻数'] = pd.to_numeric(df['助攻数'], errors='coerce').fillna(0).astype(int)
        df['得分'] = pd.to_numeric(df['得分'], errors='coerce').fillna(0).astype(int)
        
        # 检查数据有效性
        invalid_rows = []
        for index, row in df.iterrows():
            if pd.isna(row['玩家ID']) or pd.isna(row['玩家名称']) or pd.isna(row['所属联盟']):
                invalid_rows.append(index + 2)  # +2 因为有表头和索引从0开始
        
        if invalid_rows:
            return False, f"以下行的必要字段缺失：{', '.join(map(str, invalid_rows))}", None
            
        return True, "CSV文件解析成功", df
    except Exception as e:
        return False, f"解析CSV文件时出错：{str(e)}", None


def parse_text_file(file_path):
    """解析战斗日志文本文件"""
    logger.info(f"开始解析文件: {file_path}")
    
    # 检查文件是否存在
    if not os.path.exists(file_path):
        logger.error(f"文件不存在: {file_path}")
        return False, "文件不存在", [], []
    
    # 检查文件大小
    file_size = os.path.getsize(file_path)
    logger.info(f"文件大小: {file_size} 字节")
    if file_size == 0:
        logger.warning(f"文件为空: {file_path}")
        return False, "文件为空", [], []
    
    try:
        # 尝试读取文件内容 (GBK编码)
        with codecs.open(file_path, 'r', encoding='gbk') as file:
            try:
                content = file.read()
                
                # 打印前几行用于调试
                lines = content.split('\n')
                first_lines = lines[:5]
                logger.debug(f"文件前{len(first_lines)}行内容:")
                for i, line in enumerate(first_lines):
                    logger.debug(f"行 {i+1}: {line}")
                
                logger.info(f"成功读取文件，共 {len(lines)} 行")
                
                # 解析战斗日志
                battle_details, blessings = parse_battle_log(content)
                
                # 检查数据库连接
                try:
                    from app.models.player import Person
                    # 检查数据库连接是否正常
                    test_query = Person.query.limit(1).all()
                    logger.debug(f"数据库连接测试: 成功读取 {len(test_query)} 条记录")
                except Exception as e:
                    logger.error(f"数据库连接测试失败: {str(e)}", exc_info=True)
                    # 返回解析结果，但说明数据库连接失败
                    return True, f"文件解析成功（{len(battle_details)}条击杀记录，{len(blessings)}条祝福记录），但数据库连接失败: {str(e)}", battle_details, blessings
                
                # 返回解析结果
                return True, f"成功解析 {len(battle_details)} 条击杀记录和 {len(blessings)} 条祝福记录", battle_details, blessings
            except UnicodeDecodeError as e:
                logger.error(f"文件编码错误，尝试以GBK解码失败: {str(e)}")
                # 尝试检测编码
                try:
                    with open(file_path, 'rb') as binary_file:
                        raw_data = binary_file.read(1024)  # 读取前1024字节
                        possible_encoding = chardet.detect(raw_data)
                        logger.error(f"检测到可能的编码: {possible_encoding}")
                        return False, f"文件编码错误，可能的编码为{possible_encoding.get('encoding', 'unknown')}，请转换为GBK编码", [], []
                except Exception as detect_error:
                    logger.error(f"尝试检测编码时出错: {str(detect_error)}")
                return False, "文件编码错误，请确保使用GBK编码", [], []
    except Exception as e:
        logger.error(f"解析文件时出错: {str(e)}", exc_info=True)
        return False, f"解析文件时出错: {str(e)}", [], []


def parse_battle_log(log_content):
    """使用正则表达式解析战斗日志内容"""
    logger.info("开始解析日志内容")
    
    # 计算总行数
    lines = log_content.strip().split('\n')
    total_lines = len(lines)
    logger.info(f"日志共 {total_lines} 行")
    
    # 定义正则表达式
    # 击杀记录模式：[战况]玩家A 击杀 玩家B !坐标:X，Y (YYYYMMDD,HH:MM:SS)
    kill_pattern = r'\[战况\](.*?) 击杀 (.*?) !坐标:(\d+)，(\d+)  \((\d{8},\d{2}:\d{2}:\d{2})\)'
    
    # 祝福记录模式：[公告] 玩家A 得到了 XX祝福 的祝福! (YYYYMMDD,HH:MM:SS)
    blessing_pattern = r'\[公告\]  (.*?) 得到了 (.*?) 的祝福! \((\d{8},\d{2}:\d{2}:\d{2})\)'
    
    battle_details = []
    blessings = []
    
    # 逐行处理，打印调试信息
    for i, line in enumerate(lines):
        if i % 1000 == 0 and i > 0:
            logger.debug(f"已处理 {i}/{total_lines} 行")
            
        # 尝试匹配击杀记录
        kill_match = re.search(kill_pattern, line)
        if kill_match:
            killer_name = kill_match.group(1).strip()
            victim_name = kill_match.group(2).strip()
            x_coord = int(kill_match.group(3))
            y_coord = int(kill_match.group(4))
            timestamp_str = kill_match.group(5)
            
            try:
                # 解析时间戳 YYYYMMDD,HH:MM:SS
                date_part, time_part = timestamp_str.split(',')
                year = int(date_part[0:4])
                month = int(date_part[4:6])
                day = int(date_part[6:8])
                
                hour, minute, second = map(int, time_part.split(':'))
                timestamp = datetime(year, month, day, hour, minute, second)
                
                battle_details.append({
                    'killer_name': killer_name,
                    'victim_name': victim_name,
                    'x_coord': x_coord,
                    'y_coord': y_coord,
                    'timestamp': timestamp
                })
                continue
            except (ValueError, IndexError) as e:
                logger.error(f"解析时间戳时出错，行 {i+1}: {timestamp_str}，错误: {str(e)}")
        
        # 尝试匹配祝福记录
        blessing_match = re.search(blessing_pattern, line)
        if blessing_match:
            player_name = blessing_match.group(1).strip()
            blessing_name = blessing_match.group(2).strip()
            timestamp_str = blessing_match.group(3)
            
            try:
                # 解析时间戳 YYYYMMDD,HH:MM:SS
                date_part, time_part = timestamp_str.split(',')
                year = int(date_part[0:4])
                month = int(date_part[4:6])
                day = int(date_part[6:8])
                
                hour, minute, second = map(int, time_part.split(':'))
                timestamp = datetime(year, month, day, hour, minute, second)
                
                blessings.append({
                    'player_name': player_name,
                    'blessing_name': blessing_name,
                    'timestamp': timestamp
                })
                continue
            except (ValueError, IndexError) as e:
                logger.error(f"解析时间戳时出错，行 {i+1}: {timestamp_str}，错误: {str(e)}")
    
    # 记录解析结果
    logger.info(f"解析完成，共找到 {len(battle_details)} 条击杀记录和 {len(blessings)} 条祝福记录")
    
    # 示例显示部分解析结果
    if battle_details:
        logger.debug(f"击杀记录示例: {battle_details[0]}")
    if blessings:
        logger.debug(f"祝福记录示例: {blessings[0]}")
    
    return battle_details, blessings


def save_battle_log_to_db(battle_details, blessings):
    """将解析的战斗日志和祝福数据保存到数据库"""
    logger.info(f"开始保存战斗日志到数据库: {len(battle_details)}条击杀记录, {len(blessings)}条祝福记录")
    
    try:
        # 清空历史战斗记录
        logger.info("清空历史战斗记录...")
        BattleRecord.query.delete()
        db.session.commit()
        logger.info("历史战斗记录已清空")
        
        # 开始处理新的战斗记录
        logger.info("开始处理战斗日志到数据库")
        start_time = datetime.now()

        # 获取所有玩家名称
        all_player_names = set()
        for detail in battle_details:
            all_player_names.add(detail['killer_name'])
            all_player_names.add(detail['victim_name'])
        
        for blessing in blessings:
            all_player_names.add(blessing['player_name'])
        
        logger.info(f"战斗日志中共涉及 {len(all_player_names)} 名玩家")
        
        # 查询现有玩家信息
        existing_players = {}
        # 查询现在已经存在的人员信息
        try:
            persons = Person.query.all()
            logger.info(f"数据库中查询到 {len(persons)} 名玩家记录")
            
            for person in persons:
                existing_players[person.name] = person.id
            
            # 检查有多少玩家在数据库中能找到
            found_players = set(existing_players.keys()).intersection(all_player_names)
            missing_players = all_player_names - set(existing_players.keys())
            
            logger.info(f"战斗日志中的玩家在数据库中找到 {len(found_players)}/{len(all_player_names)} 个，缺少 {len(missing_players)} 个")
            if missing_players and len(missing_players) <= 10:
                logger.warning(f"以下玩家在数据库中不存在: {', '.join(list(missing_players))}")
            elif missing_players:
                logger.warning(f"大量玩家在数据库中不存在，缺少 {len(missing_players)} 个玩家记录")
        except Exception as e:
            logger.error(f"查询玩家信息时出错: {str(e)}", exc_info=True)
            return False, f"查询玩家信息时出错: {str(e)}"
        
        try:
            # 开始逐条处理数据
            logger.debug(f"开始处理 {len(battle_details)} 条击杀记录")
            
            battle_success_count = 0
            battle_error_count = 0
            battle_missing_player_count = 0
            battle_skip_count = 0
            
            # 收集所有时间戳，用于检查记录是否已存在
            timestamps = {detail['timestamp'] for detail in battle_details}
            existing_records = BattleRecord.query.filter(BattleRecord.publish_at.in_(timestamps)).all()
            existing_timestamps = {record.publish_at for record in existing_records}
            
            logger.info(f"检查到 {len(existing_timestamps)} 条已存在的战斗记录时间戳")
            
            # 逐条处理击杀记录
            for idx, detail in enumerate(battle_details):
                # 检查该时间戳的记录是否已存在
                if detail['timestamp'] in existing_timestamps:
                    battle_skip_count += 1
                    if battle_skip_count <= 5:  # 只记录前几条跳过的记录
                        logger.debug(f"跳过已存在的战斗记录: {detail['killer_name']} 击杀 {detail['victim_name']} 在 {detail['timestamp']}")
                    continue
                    
                killer_id = existing_players.get(detail['killer_name'])
                victim_id = existing_players.get(detail['victim_name'])
                
                # 只有当击杀者和受害者都在数据库中存在时才记录战斗详情
                if killer_id and victim_id:
                    try:
                        # 创建战斗记录 - 只存储一次
                        battle_record = BattleRecord(
                            win=detail['killer_name'],  # 胜利者(击杀者)名称
                            lost=detail['victim_name'],  # 失败者(被击杀者)名称
                            position=f"{detail['x_coord']},{detail['y_coord']}",
                            remark=0,  # 祝福数初始为0
                            publish_at=detail['timestamp'],
                            create_by=killer_id  # 记录创建者为击杀者
                        )
                        db.session.add(battle_record)
                        
                        # 每100条提交一次
                        if (idx + 1) % 100 == 0 or idx == len(battle_details) - 1:
                            db.session.commit()
                            logger.debug(f"已处理 {idx+1}/{len(battle_details)} 条战斗记录")
                        
                        battle_success_count += 1
                        
                    except Exception as e:
                        battle_error_count += 1
                        logger.error(f"处理战斗记录时出错: {str(e)}, 详情: {detail}", exc_info=True)
                        db.session.rollback()
                else:
                    battle_missing_player_count += 1
                    if battle_missing_player_count <= 5:  # 只记录前几条错误详情
                        if not killer_id:
                            logger.warning(f"击杀者 {detail['killer_name']} 在数据库中不存在")
                        if not victim_id:
                            logger.warning(f"受害者 {detail['victim_name']} 在数据库中不存在")
            
            # 确保所有战斗记录已提交
            db.session.commit()
            logger.info(f"战斗记录处理完成：成功 {battle_success_count}，错误 {battle_error_count}，缺少玩家 {battle_missing_player_count}，跳过 {battle_skip_count}")
            
            # 处理祝福记录
            blessing_success_count = 0
            blessing_error_count = 0
            blessing_missing_player_count = 0
            blessing_skip_count = 0
            
            # 收集所有祝福时间戳
            blessing_timestamps = {blessing['timestamp'] for blessing in blessings}
            existing_blessing_records = BattleRecord.query.filter(
                BattleRecord.publish_at.in_(blessing_timestamps),
                BattleRecord.remark > 0
            ).all()
            existing_blessing_timestamps = {record.publish_at for record in existing_blessing_records}
            
            logger.info(f"检查到 {len(existing_blessing_timestamps)} 条已存在的祝福记录时间戳")
            
            # 处理祝福记录
            player_blessings = {}
            for blessing_data in blessings:
                # 检查祝福记录是否已存在
                if blessing_data['timestamp'] in existing_blessing_timestamps:
                    blessing_skip_count += 1
                    if blessing_skip_count <= 5:
                        logger.debug(f"跳过已存在的祝福记录: {blessing_data['player_name']} 在 {blessing_data['timestamp']}")
                    continue
                    
                player_id = existing_players.get(blessing_data['player_name'])
                if player_id:
                    if player_id not in player_blessings:
                        player_blessings[player_id] = {
                            'count': 1,
                            'timestamp': blessing_data['timestamp']
                        }
                    else:
                        player_blessings[player_id]['count'] += 1
                        if blessing_data['timestamp'] > player_blessings[player_id]['timestamp']:
                            player_blessings[player_id]['timestamp'] = blessing_data['timestamp']
                else:
                    blessing_missing_player_count += 1
                    if blessing_missing_player_count <= 5:
                        logger.warning(f"祝福接收者 {blessing_data['player_name']} 在数据库中不存在")
            
            # 保存祝福记录
            logger.debug(f"开始处理 {len(player_blessings)} 名玩家的祝福记录")
            
            # 根据玩家ID查询已有战绩记录，如果有则更新，没有则创建
            for player_id, blessing_info in player_blessings.items():
                try:
                    # 查询该玩家是否已有战绩记录（击杀记录中创建的）
                    player_record = BattleRecord.query.filter_by(create_by=player_id).first()
                    
                    if player_record:
                        # 更新现有记录的祝福次数
                        player_record.remark = blessing_info['count']
                        if blessing_info['timestamp'] > player_record.publish_at:
                            player_record.publish_at = blessing_info['timestamp']
                        player_record = BattleRecord(
                            remark=blessing_info['count'],
                            publish_at=blessing_info['timestamp'],
                            create_by=player_id
                        )
                        db.session.add(player_record)
                    
                    blessing_success_count += 1
                    
                except Exception as e:
                    blessing_error_count += 1
                    logger.error(f"处理玩家ID {player_id} 的祝福记录时出错: {str(e)}", exc_info=True)
            
            # 提交所有祝福记录
            try:
                db.session.commit()
                logger.info(f"祝福记录处理完成：成功 {blessing_success_count}，错误 {blessing_error_count}，缺少玩家 {blessing_missing_player_count}")
                
                # 生成战绩报告SQL - 使用关联查询统计击杀和死亡次数
                battle_report_sql = """
                WITH player_stats AS (
                    SELECT 
                        p.id,
                        p.name,
                        p.job,
                        p.god,
                        -- 统计击杀次数(通过win字段关联)
                        COUNT(DISTINCT CASE WHEN br.win = p.name THEN br.id END) as kills,
                        -- 统计死亡次数(通过lost字段关联)
                        COUNT(DISTINCT CASE WHEN br.lost = p.name THEN br.id END) as deaths,
                        -- 统计祝福次数(只有win的玩家才会有祝福)
                        SUM(CASE WHEN br.win = p.name THEN COALESCE(br.remark, 0) ELSE 0 END) as blessings,
                        -- 获取最后战斗位置和时间
                        MAX(br.position) as last_position,
                        MAX(br.publish_at) as last_battle_time
                    FROM 
                        person p
                    LEFT JOIN 
                        battle_record br ON br.win = p.name OR br.lost = p.name
                    WHERE 1=1
                    GROUP BY 
                        p.id, p.name, p.job, p.god
                )
                SELECT 
                    id as player_id,
                    name as player_name,
                    job as player_job,
                    god as player_god,
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
                    player_stats
                ORDER BY 
                    score DESC, kills DESC, deaths ASC;
                """
                
                logger.info("生成战绩报告SQL:")
                logger.info(battle_report_sql)
                
                # 计算总体处理时间
                end_time = datetime.now()
                process_time = (end_time - start_time).total_seconds()
                
                logger.info(f"战斗日志保存完成，总处理时间: {process_time:.2f} 秒")
                
                # 返回处理结果
                return True, f"处理完成：{battle_success_count} 条战斗记录，{blessing_success_count} 条祝福记录"
                
            except Exception as e:
                # 发生错误时回滚事务
                db.session.rollback()
                logger.error(f"保存祝福记录到数据库时发生错误: {str(e)}", exc_info=True)
                return False, f"保存祝福记录时出错: {str(e)}"
            
        except Exception as e:
            # 发生错误时回滚事务
            db.session.rollback()
            logger.error(f"保存战斗日志到数据库时发生错误: {str(e)}", exc_info=True)
            return False, f"保存战斗日志时出错: {str(e)}"
        
    except Exception as e:
        logger.error(f"保存战斗日志到数据库时发生错误: {str(e)}", exc_info=True)
        return False, f"保存战斗日志时出错: {str(e)}" 