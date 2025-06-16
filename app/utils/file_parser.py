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
import io

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
    """解析文本文件，先尝试chardet检测编码，然后尝试解码。"""
    logger.info(f"尝试解析文件: {file_path}")
    content = None
    encoding_used = None
    detected_encoding = None
    detected_confidence = 0
    # 预设编码列表，作为 chardet 检测失败或结果不可信时的后备
    fallback_encodings = ['gbk', 'gb2312', 'utf-8']

    # --- 1. 使用 chardet 检测编码 --- 
    try:
        # 读取文件开头一部分用于检测 (例如 32KB)
        # 使用 io.open 更灵活，可以处理二进制
        with io.open(file_path, "rb") as f:
            raw_data = f.read(32 * 1024) # Read first 32KB
            if not raw_data:
                 logger.warning(f"文件为空: {file_path}")
                 return False, "文件为空", [], []
                 
            detection = chardet.detect(raw_data)
            detected_encoding = detection.get('encoding')
            detected_confidence = detection.get('confidence', 0)
            logger.info(f"Chardet 检测结果: encoding='{detected_encoding}', confidence={detected_confidence:.2f}")

    except FileNotFoundError:
        logger.error(f"文件不存在: {file_path}")
        return False, "文件不存在", [], []
    except Exception as e:
        logger.error(f"读取文件进行编码检测时出错: {e}", exc_info=True)
        # 检测失败，我们将直接使用 fallback 列表
        detected_encoding = None 

    # --- 2. 确定尝试解码的顺序 --- 
    encodings_to_try = []
    # 如果 chardet 检测到结果且置信度较高 (例如 > 0.9)，优先尝试它
    # 特别关注中文相关的编码
    if detected_encoding and detected_confidence > 0.9:
        # 标准化常见的中文编码名称
        normalized_encoding = detected_encoding.lower()
        if normalized_encoding in ['gb2312', 'gbk', 'gb18030']:
           # 如果是GB系列，将GBK放在首位尝试（兼容性好），然后是检测到的，再是GB2312
           encodings_to_try.extend(['gbk', normalized_encoding, 'gb2312'])
        elif normalized_encoding == 'utf-8':
            encodings_to_try.append('utf-8')
        else:
           # 对于其他高置信度的编码，也加入尝试列表
            encodings_to_try.append(detected_encoding) 
            
    # 添加后备编码（确保不重复）
    for enc in fallback_encodings:
        if enc not in encodings_to_try:
            encodings_to_try.append(enc)
            
    logger.info(f"最终尝试解码顺序: {encodings_to_try}")

    # --- 3. 依次尝试解码 --- 
    for encoding in encodings_to_try:
        try:
            # 对非 UTF-8 编码使用 errors='replace' 策略
            errors_policy = 'replace' if encoding != 'utf-8' else 'strict'
            with codecs.open(file_path, 'r', encoding=encoding, errors=errors_policy) as file:
                content = file.read()
            
            encoding_used = encoding
            logger.info(f"成功使用 {encoding} 编码读取文件 (errors='{errors_policy}')")
            
            # 检查是否有替换字符 (表明原始数据可能有问题)
            if errors_policy == 'replace' and '\ufffd' in content:
                 logger.warning(f"文件在使用 {encoding} (errors='replace') 读取时检测到替换字符 ('\uFFFD')，原始文件可能包含无法解码的字节。")
            
            break # 成功读取，跳出循环
            
        except UnicodeDecodeError:
            logger.warning(f"使用 {encoding} 编码 (errors='{errors_policy}') 打开文件时发生 UnicodeDecodeError，尝试下一种编码...")
        except LookupError: # 处理 Python 不支持的编码名称
            logger.warning(f"Python 不支持编码 '{encoding}'，跳过尝试...")
        except Exception as e:
            logger.error(f"尝试使用 {encoding} 编码 (errors='{errors_policy}') 读取时发生一般错误: {e}", exc_info=True)
            # 对于其他读取错误，继续尝试下一种编码
            
    # --- 4. 处理解码结果 --- 
    if content is None:
        logger.error(f"无法使用尝试的所有编码 ({', '.join(encodings_to_try)}) 读取文件: {file_path}")
        # 最终错误消息可以结合 chardet 的原始检测结果
        error_msg = f"无法识别或解码文件编码。尝试列表: {encodings_to_try}。"
        if detected_encoding:
             error_msg += f" (Chardet 最初检测为: {detected_encoding}, 置信度: {detected_confidence:.2f})"
        return False, error_msg, [], []

    # --- 5. 如果成功读取文件内容，则继续执行后续逻辑 --- 
    try:
        # 打印前几行用于调试
        lines = content.split('\n')
        first_lines = lines[:5]
        logger.debug(f"文件前{len(first_lines)}行内容 (使用 {encoding_used} 编码):")
        for i, line in enumerate(first_lines):
            logger.debug(f"行 {i+1}: {line.strip()}")
        
        logger.info(f"成功读取文件 (使用 {encoding_used} 编码)，共 {len(lines)} 行")
        
        # 解析战斗日志
        battle_details, blessings = parse_battle_log(content)
        logger.info(f"解析完成: {len(battle_details)} 条击杀, {len(blessings)} 条祝福")
        
        # 检查数据库连接
        try:
            # 检查数据库连接是否正常
            test_query = Person.query.limit(1).all()
            logger.debug(f"数据库连接测试: 成功读取 {len(test_query)} 条记录")
        except Exception as e:
            logger.error(f"数据库连接测试失败: {str(e)}", exc_info=True)
            # 返回解析结果，但说明数据库连接失败
            return True, f"文件解析成功（{len(battle_details)}条击杀，{len(blessings)}条祝福），但数据库连接失败: {str(e)}", battle_details, blessings
        
        # 返回解析结果
        return True, f"成功解析 {len(battle_details)} 条击杀记录和 {len(blessings)} 条祝福记录 (使用 {encoding_used} 编码)", battle_details, blessings
        
    except Exception as e:
        logger.error(f"处理文件内容时出错 (编码: {encoding_used}): {str(e)}", exc_info=True)
        return False, f"处理文件内容时出错: {str(e)}", [], []


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
        start_time = datetime.now() # Record start time
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
                # existing_players[person.name] = person.id # Original line
                # Use stripped name from DB as key to ensure exact match with stripped name from log
                cleaned_db_name = person.name.strip() if person.name else ''
                if cleaned_db_name: # Avoid adding empty keys if name is null/empty after stripping
                    existing_players[cleaned_db_name] = person.id
            
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
            blessing_success_count = 0 # Initialize blessing counter
            battle_error_count = 0
            battle_missing_player_count = 0
            battle_skip_count = 0
            
            # 首先处理所有战斗记录
            battle_records_for_blessing = {}  # 创建一个字典保存战斗记录，以便祝福处理时查找
            
            # 收集所有时间戳，用于检查记录是否已存在
            timestamps = {detail['timestamp'] for detail in battle_details}
            
            # 逐条处理击杀记录
            for idx, detail in enumerate(battle_details):
                killer_name_from_log = detail['killer_name']
                victim_name_from_log = detail['victim_name']
                
                killer_id = existing_players.get(killer_name_from_log)
                victim_id = existing_players.get(victim_name_from_log)
                
                # 只有当击杀者和受害者都在数据库中存在时才记录战斗详情
                if killer_id and victim_id:
                    try:
                        # 检查是否已存在相同的战斗记录
                        exists = BattleRecord.query.filter_by(
                            win=detail['killer_name'],
                            lost=detail['victim_name'],
                            publish_at=detail['timestamp']
                        ).first()
                        
                        if not exists:
                            # 创建战斗记录 - 只在记录不存在时创建
                            battle_record = BattleRecord(
                                win=detail['killer_name'],  # 胜利者(击杀者)名称
                                lost=detail['victim_name'],  # 失败者(被击杀者)名称
                                position=f"{detail['x_coord']},{detail['y_coord']}",
                                remark=0,  # 祝福数初始为0，后续处理祝福时更新
                                publish_at=detail['timestamp'],
                                create_by=detail['killer_name']  # 记录创建者为击杀者
                            )
                            db.session.add(battle_record)
                            
                            # 保存到字典中以便后续查找
                            date_str = detail['timestamp'].date().strftime('%Y-%m-%d')
                            key = (detail['killer_name'], date_str)
                            if key not in battle_records_for_blessing:
                                battle_records_for_blessing[key] = []
                            battle_records_for_blessing[key].append(battle_record)
                            
                            # 每100条提交一次
                            if (idx + 1) % 100 == 0 or idx == len(battle_details) - 1:
                                db.session.commit()
                                logger.debug(f"已处理 {idx+1}/{len(battle_details)} 条战斗记录")
                            
                            battle_success_count += 1
                            
                        else:
                            # 记录已存在，也保存到字典中以便更新祝福
                            date_str = detail['timestamp'].date().strftime('%Y-%m-%d')
                            key = (detail['killer_name'], date_str)
                            if key not in battle_records_for_blessing:
                                battle_records_for_blessing[key] = []
                            battle_records_for_blessing[key].append(exists)
                            
                            battle_skip_count += 1
                            if battle_skip_count <= 10:
                                logger.debug(f"跳过已存在的重复战斗记录: Win='{detail['killer_name']}', Lost='{detail['victim_name']}', Time='{detail['timestamp']}'")
                            continue
                        
                    except Exception as e:
                        battle_error_count += 1
                        logger.error(f"处理战斗记录时出错: {str(e)}, 详情: {detail}", exc_info=True)
                        db.session.rollback()
                
            # 中间提交一次
            try:
                db.session.commit()
                logger.info(f"战斗记录处理完成：成功插入 {battle_success_count} 条新记录，跳过 {battle_skip_count} 条重复记录。")
            except Exception as e:
                db.session.rollback()
                logger.error(f"提交战斗记录时出错: {str(e)}", exc_info=True)
                return False, f"提交战斗记录时出错: {str(e)}"
            
            # 处理祝福记录
            logger.info(f"开始处理 {len(blessings)} 条祝福记录")
            blessing_success_count = 0
            blessing_error_count = 0
            blessing_missing_player_count = 0
            
            for idx, blessing in enumerate(blessings):
                player_name = blessing['player_name']
                blessing_date = blessing['timestamp'].date()
                
                # 将日期对象格式化为字符串作为键
                date_str = blessing_date.strftime('%Y-%m-%d')
                
                # 查找该玩家当天的战斗记录
                key = (player_name, date_str)
                if key in battle_records_for_blessing and battle_records_for_blessing[key]:
                    # 遍历当天该玩家的所有战斗记录，找到时间戳匹配的记录
                    found_matching_record = False
                    for battle_record in battle_records_for_blessing[key]:
                        # 检查时间戳是否匹配
                        if battle_record.publish_at == blessing['timestamp']:
                            try:
                                # 更新祝福标记 - 设置为1
                                battle_record.remark = 1
                                blessing_success_count += 1
                                if blessing_success_count <= 10:
                                    logger.debug(f"更新战斗记录祝福标记: 玩家='{player_name}', 祝福='{blessing['blessing_name']}', 时间='{blessing['timestamp']}', 祝福值设置为1")
                                found_matching_record = True
                                break  # 找到匹配记录后跳出循环
                            except Exception as e:
                                blessing_error_count += 1
                                logger.error(f"更新祝福记录时出错: {str(e)}, 详情: {blessing}", exc_info=True)
                    
                    # 如果没有找到时间戳完全匹配的记录，记录警告信息
                    if not found_matching_record:
                        logger.warning(f"玩家 {player_name} 的祝福记录 (时间: {blessing['timestamp']}) 没有找到完全匹配的战斗记录")
                else:
                    # 没有找到当天的战斗记录
                    blessing_missing_player_count += 1
                    if blessing_missing_player_count <= 5:
                        logger.warning(f"玩家 {player_name} 的祝福记录没有找到匹配的战斗记录，日期: {date_str}")
                
                # 每50条提交一次
                if (idx + 1) % 50 == 0 or idx == len(blessings) - 1:
                    try:
                        db.session.commit()
                        logger.debug(f"已处理 {idx+1}/{len(blessings)} 条祝福记录")
                    except Exception as e:
                        db.session.rollback()
                        logger.error(f"提交祝福记录更新时出错: {str(e)}", exc_info=True)
            
            # Final commit after processing all records
            try:
                db.session.commit()
                logger.info(f"祝福记录处理完成：成功更新 {blessing_success_count} 条记录，找不到匹配的战斗记录 {blessing_missing_player_count} 条。")
            except Exception as e:
                db.session.rollback()
                logger.error(f"提交祝福记录时出错: {str(e)}", exc_info=True)
                return False, f"提交祝福记录时出错: {str(e)}"
            
            # 生成战绩报告SQL (remains the same)
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
            return True, f"处理完成：{battle_success_count} 条战斗记录，{blessing_success_count} 条祝福记录成功更新。"
            
        except Exception as e:
            # 发生错误时回滚事务
            db.session.rollback()
            logger.error(f"保存战斗日志到数据库时发生错误: {str(e)}", exc_info=True)
            return False, f"保存战斗日志时出错: {str(e)}"
        
    except Exception as e:
        logger.error(f"保存战斗日志到数据库时发生错误: {str(e)}", exc_info=True)
        return False, f"保存战斗日志时出错: {str(e)}" 