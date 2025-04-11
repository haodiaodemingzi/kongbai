#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
战斗报告相关路由
"""

import os
from flask import Blueprint, render_template, request, redirect, url_for, flash, session, send_file, jsonify, Response, current_app
from werkzeug.utils import secure_filename
from app import db
from app.models.player import Person, BattleRecord
from app.utils.file_parser import parse_text_file, save_battle_log_to_db
from app.utils.data_service import get_player_rankings, get_battle_details_by_player, export_data_to_json, get_statistics
from app.config import Config
from app.utils.logger import get_logger
from app.utils.battle_report import generate_battle_report, export_battle_sql
from datetime import datetime, date
from sqlalchemy import text
from app.utils.auth import login_required

logger = get_logger()

battle_bp = Blueprint('battle', __name__)

# 确保上传目录存在
os.makedirs(Config.UPLOAD_FOLDER, exist_ok=True)
logger.info(f"确保上传目录存在: {Config.UPLOAD_FOLDER}")

def allowed_file(filename):
    """检查文件是否允许上传"""
    allowed_extensions = {'txt'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extensions


@battle_bp.route('/upload', methods=['GET', 'POST'])
@login_required
def upload_file():
    """上传并解析文件"""
    logger.info("访问文件上传页面")
    
    if request.method == 'POST':
        logger.info("收到文件上传请求")
        # 检查是否有文件
        if 'file' not in request.files:
            logger.warning("上传请求中没有文件部分")
            flash('没有选择文件', 'error')
            return redirect(request.url)
        
        file = request.files['file']
        
        # 检查文件名是否为空
        if file.filename == '':
            logger.warning("上传的文件名为空")
            flash('没有选择文件', 'error')
            return redirect(request.url)
        
        logger.info(f"收到上传文件: {file.filename}")
        
        if file and allowed_file(file.filename):
            # 保存文件
            filename = secure_filename(file.filename)
            file_path = os.path.join(Config.UPLOAD_FOLDER, filename)
            
            # 确保上传目录存在
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            logger.debug(f"确保上传目录存在: {os.path.dirname(file_path)}")
            
            try:
                file.save(file_path)
                logger.info(f"文件已保存到: {file_path}")
            except Exception as e:
                logger.error(f"保存文件时出错: {str(e)}", exc_info=True)
                flash('保存文件时出错: ' + str(e), 'error')
                return redirect(request.url)
            
            # 解析战斗日志文本
            logger.info(f"开始解析文件: {file_path}")
            success, message, battle_details, blessings = parse_text_file(file_path)
            
            # 如果解析成功但提示数据库连接问题，直接显示消息
            if success and "数据库连接失败" in message:
                logger.warning("解析成功但数据库连接失败")
                flash(message, 'warning')
                return redirect(url_for('battle.rankings'))
                
            if success:
                logger.info(f"文件解析成功: {message}")
                # 保存到数据库
                logger.info("开始将解析结果保存到数据库")
                try:
                    save_success, save_message = save_battle_log_to_db(battle_details, blessings)
                    if save_success:
                        logger.info(f"数据保存成功: {save_message}")
                        flash(f"{message}，{save_message}", 'success')
                    else:
                        logger.error(f"数据保存失败: {save_message}")
                        flash(save_message, 'error')
                except Exception as e:
                    logger.error(f"保存到数据库时发生异常: {str(e)}", exc_info=True)
                    error_message = str(e)
                    flash(f"文件解析成功，但保存到数据库时出错: {error_message}", 'error')
            else:
                logger.error(f"文件解析失败: {message}")
                flash(message, 'error')
            
            return redirect(url_for('battle.rankings'))
        else:
            logger.warning(f"不支持的文件类型: {file.filename}")
            flash('不支持的文件类型，请上传txt格式文件', 'error')
            return redirect(request.url)
    
    # GET请求显示上传表单
    logger.debug("显示上传文件表单页面")
    return render_template('upload.html')


@battle_bp.route('/rankings')
@login_required
def rankings():
    """玩家排名页面，考虑玩家分组情况"""
    logger.info("访问玩家排名页面")
    
    # 获取筛选参数
    faction = request.args.get('faction')
    job = request.args.get('job')  # 新增职业筛选参数
    if job == 'all' or job == '':
        job = None
    if faction == 'all' or faction == '':
        faction = None

    time_range = request.args.get('time_range', 'all')
    show_grouped = request.args.get('show_grouped', 'true') == 'true'  # 新增参数：是否按分组统计
    logger.debug(f"排名筛选参数: faction={faction}, job={job}, time_range={time_range}, show_grouped={show_grouped}")
    
    try:
        # 根据是否需要按分组统计选择不同的查询
        if show_grouped:
            # 按照玩家分组进行统计的查询
            query = text("""
                WITH player_distinct AS (
                    -- 获取所有有效的玩家ID，并关联其分组信息
                    SELECT 
                        p.id,
                        p.name,
                        p.job,
                        p.god as faction,
                        -- 使用分组ID作为分组键，如果没有分组则使用玩家自身ID
                        COALESCE(p.player_group_id, p.id) AS group_key,
                        -- 获取分组名称
                        COALESCE(pg.group_name, p.name) AS player_name
                    FROM 
                        person p
                    LEFT JOIN
                        player_group pg ON p.player_group_id = pg.id
                    WHERE 
                        p.deleted_at IS NULL
                        AND (:faction IS NULL OR p.god = :faction)
                        AND (:job IS NULL OR p.job = :job)
                ),
                group_battle_stats AS (
                    -- 按分组计算战斗数据
                    SELECT 
                        pd.group_key,
                        pd.player_name,
                        -- 统一使用第一个遇到的job和faction作为分组的job和faction
                        ANY_VALUE(pd.job) AS job,
                        ANY_VALUE(pd.faction) AS faction,
                        COUNT(DISTINCT CASE WHEN br.win = pd.name THEN br.id END) AS kills,
                        COUNT(DISTINCT CASE WHEN br.lost = pd.name THEN br.id END) AS deaths,
                        SUM(CASE WHEN br.win = pd.name THEN COALESCE(br.remark, 0) ELSE 0 END) AS blessings,
                        -- 计算K/D比率
                        CASE 
                            WHEN COUNT(DISTINCT CASE WHEN br.lost = pd.name THEN br.id END) > 0 
                            THEN ROUND(COUNT(DISTINCT CASE WHEN br.win = pd.name THEN br.id END) * 1.0 / 
                                 COUNT(DISTINCT CASE WHEN br.lost = pd.name THEN br.id END), 2)
                            ELSE COUNT(DISTINCT CASE WHEN br.win = pd.name THEN br.id END)
                        END AS kd_ratio
                    FROM 
                        player_distinct pd
                    LEFT JOIN 
                        battle_record br ON pd.name IN (br.win, br.lost)
                    GROUP BY 
                        pd.group_key, pd.player_name
                    HAVING 
                        kills > 0 OR deaths > 0
                )
                SELECT 
                    group_key AS id,
                    player_name AS name,
                    job,
                    faction,
                    kills,
                    deaths,
                    blessings,
                    kd_ratio,
                    (kills * 3 + blessings - deaths) AS score
                FROM 
                    group_battle_stats
                ORDER BY 
                    score DESC, kills DESC, deaths ASC
            """)
        else:
            # 原始查询（不考虑玩家分组）
            query = text("""
                WITH player_stats AS (
                    SELECT 
                        p.id,
                        p.name,
                        p.job,
                        p.god as faction,
                        COUNT(CASE WHEN br.win = p.name THEN 1 END) as kills,
                        COUNT(CASE WHEN br.lost = p.name THEN 1 END) as deaths,
                        SUM(CASE WHEN br.win = p.name THEN COALESCE(br.remark, 0) ELSE 0 END) as blessings,
                        CASE 
                            WHEN COUNT(CASE WHEN br.lost = p.name THEN 1 END) > 0 
                            THEN ROUND(COUNT(CASE WHEN br.win = p.name THEN 1 END) * 1.0 / 
                                 COUNT(CASE WHEN br.lost = p.name THEN 1 END), 2)
                            ELSE COUNT(CASE WHEN br.win = p.name THEN 1 END)
                        END as kd_ratio
                    FROM person p
                    LEFT JOIN battle_record br ON p.name IN (br.win, br.lost)
                    WHERE p.deleted_at IS NULL
                    AND (:faction IS NULL OR p.god = :faction)
                    AND (:job IS NULL OR p.job = :job)
                    GROUP BY p.id, p.name, p.job, p.god
                    HAVING kills > 0 OR deaths > 0
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
            """)
        
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
        
        # 获取所有职业列表（去重）
        jobs_query = text("""
            SELECT DISTINCT job 
            FROM person 
            WHERE job IS NOT NULL 
            AND deleted_at IS NULL 
            ORDER BY job
        """)
        
        jobs = [row[0] for row in db.session.execute(jobs_query)]
        logger.debug(f"获取到 {len(jobs)} 个职业分类")
        
        # 获取统计数据
        total_players, total_kills, total_deaths, total_score = get_statistics(faction=faction)
        
        return render_template('rankings.html', 
                              players=player_rankings, 
                              jobs=jobs,
                              selected_job=job,
                              selected_faction=faction,
                              show_grouped=show_grouped,
                              selected_time=time_range,
                              total_players=total_players,
                              total_kills=total_kills,
                              total_deaths=total_deaths,
                              total_score=total_score)
    except Exception as e:
        logger.error(f"玩家排名页面渲染出错: {str(e)}", exc_info=True)
        flash('获取排名数据时出错', 'error')
        return render_template('rankings.html', 
                             players=[], 
                             jobs=[],
                             selected_job=job,
                             selected_faction=faction,
                             show_grouped=show_grouped,
                             selected_time=time_range,
                             total_players=0,
                             total_kills=0,
                             total_deaths=0,
                             total_score=0)


@battle_bp.route('/player/<int:person_id>')
def player_details(person_id):
    """玩家详情页"""
    try:
        player_details = get_battle_details_by_player(person_id)
        if not player_details:
            flash('找不到该玩家', 'danger')
            return redirect(url_for('battle.rankings'))
        
        # 确保kills_details和deaths_details字段存在，如果没有则提供空列表
        if 'kills_details' not in player_details:
            player_details['kills_details'] = []
        if 'deaths_details' not in player_details:
            player_details['deaths_details'] = []
            
        return render_template('player_details.html', player=player_details)
    except Exception as e:
        logger.error(f"查看玩家 {person_id} 详情时出错: {str(e)}", exc_info=True)
        flash(f'加载玩家详情时出错: {str(e)}', 'danger')
        return redirect(url_for('battle.rankings'))


@battle_bp.route('/export')
def export_json():
    """导出JSON数据"""
    logger.info("访问数据导出页面")
    
    # 获取筛选参数
    faction = request.args.get('faction')
    logger.debug(f"导出数据筛选参数: faction={faction}")
    
    try:
        # 导出数据为JSON
        json_data, filename = export_data_to_json(faction=faction)
        logger.info(f"数据导出成功，文件名: {filename}")
        
        # 发送JSON文件
        return Response(
            json_data,
            mimetype='application/json',
            headers={'Content-Disposition': f'attachment; filename={filename}'}
        )
    except Exception as e:
        logger.error(f"导出数据时出错: {str(e)}", exc_info=True)
        return Response(
            "{\"error\": \"导出数据时出错\"}",
            mimetype='application/json',
            status=500
        )

@battle_bp.route('/report', methods=['GET'])
def report():
    try:
        # 获取日期参数
        start_date_str = request.args.get('start_date')
        end_date_str = request.args.get('end_date')
        
        # 设置默认日期为今天
        today = date.today()
        end_date = today
        start_date = today
        
        # 解析日期
        if start_date_str:
            try:
                start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
            except ValueError:
                flash('开始日期格式不正确，请使用YYYY-MM-DD格式', 'error')
                return redirect(url_for('battle.report'))
                
        if end_date_str:
            try:
                end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
            except ValueError:
                flash('结束日期格式不正确，请使用YYYY-MM-DD格式', 'error')
                return redirect(url_for('battle.report'))
        
        # 确保reports目录存在
        report_dir = os.path.join(current_app.root_path, 'static', 'reports')
        if not os.path.exists(report_dir):
            os.makedirs(report_dir)
            
        # 生成报告
        csv_filename, report_data, god_stats, stats_summary = generate_battle_report(
            output_dir=report_dir, 
            start_date=start_date,
            end_date=end_date
        )
        
        # 安全地创建排行榜
        try:
            # 击杀排行榜
            kills_leaders = sorted(
                [p for p in report_data if p.get('kills', 0) is not None], 
                key=lambda x: (-x.get('kills', 0), x.get('deaths', 0))
            )[:10]
            
            # 得分排行榜
            score_leaders = sorted(
                [p for p in report_data if p.get('score', 0) is not None],
                key=lambda x: (-x.get('score', 0), -x.get('kills', 0), x.get('deaths', 0))
            )[:10]
            
            # KD比排行榜
            kd_leaders = sorted(
                [p for p in report_data if p.get('kd_ratio', 0) is not None and p.get('kills', 0) >= 10],
                key=lambda x: (-x.get('kd_ratio', 0), -x.get('kills', 0))
            )[:10]
            
            # 祝福排行榜
            bless_leaders = sorted(
                [p for p in report_data if p.get('blessings', 0) is not None],
                key=lambda x: (-x.get('blessings', 0))
            )[:10]
            
            return render_template(
                'battle/report.html',
                start_date=start_date,
                end_date=end_date,
                kills_leaders=kills_leaders,
                score_leaders=score_leaders,
                kd_leaders=kd_leaders,
                bless_leaders=bless_leaders,
                god_stats=god_stats,
                stats_summary=stats_summary,
                csv_filename=csv_filename
            )
            
        except Exception as e:
            logger.error(f"生成报告时出错: {str(e)}")
            flash('生成报告时出错，请稍后重试', 'error')
            return redirect(url_for('home.index'))
    except Exception as e:
        flash(f'生成报告时出错: {str(e)}', 'error')
        logger.error(f"生成报告时出错: {str(e)}")
        return redirect(url_for('main.index'))

@battle_bp.route('/report/download', methods=['GET'])
def download_report():
    try:
        # 获取日期参数
        start_date_str = request.args.get('start_date')
        end_date_str = request.args.get('end_date')
        
        # 设置默认日期为今天
        today = date.today()
        end_date = today
        start_date = today
        
        # 解析日期
        if start_date_str:
            try:
                start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
            except ValueError:
                flash('开始日期格式不正确，请使用YYYY-MM-DD格式', 'error')
                return redirect(url_for('battle.report'))
                
        if end_date_str:
            try:
                end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
            except ValueError:
                flash('结束日期格式不正确，请使用YYYY-MM-DD格式', 'error')
                return redirect(url_for('battle.report'))

        # 确保reports目录存在
        report_dir = os.path.join(current_app.root_path, 'static', 'reports')
        if not os.path.exists(report_dir):
            os.makedirs(report_dir)
            
        # 生成CSV报告
        try:
            # 获取生成报告返回的结果
            csv_file, _, _, _ = generate_battle_report(
                output_dir=report_dir, 
                start_date=start_date,
                end_date=end_date
            )
            
            # 如果没有报告文件，通知用户
            if not csv_file or not os.path.exists(csv_file):
                flash('无法生成报告文件', 'error')
                return redirect(url_for('battle.report'))
                
            # 准备下载响应
            return send_file(
                csv_file, 
                as_attachment=True, 
                download_name=os.path.basename(csv_file),
                mimetype='text/csv'
            )
        except Exception as e:
            logger.error(f"生成CSV报告时出错: {str(e)}")
            flash(f'生成CSV报告时出错: {str(e)}', 'error')
            return redirect(url_for('battle.report'))
    except Exception as e:
        flash(f'下载报告时出错: {str(e)}', 'error')
        logger.error(f"下载报告时出错: {str(e)}")
        return redirect(url_for('battle.report'))

@battle_bp.route('/report/sql', methods=['GET'])
def report_sql():
    try:
        # 获取日期参数
        start_date_str = request.args.get('start_date')
        end_date_str = request.args.get('end_date')
        
        # 设置默认日期为今天
        today = date.today()
        end_date = today
        start_date = today
        
        # 解析日期
        if start_date_str:
            try:
                start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
            except ValueError:
                return jsonify({'error': '开始日期格式不正确，请使用YYYY-MM-DD格式'}), 400
                
        if end_date_str:
            try:
                end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
            except ValueError:
                return jsonify({'error': '结束日期格式不正确，请使用YYYY-MM-DD格式'}), 400
        
        # 生成SQL查询
        try:
            sql = export_battle_sql(start_date, end_date)
            return jsonify({'sql': sql})
        except Exception as e:
            logger.error(f"生成SQL查询时出错: {str(e)}")
            return jsonify({'error': f'生成SQL查询时出错: {str(e)}'}), 500
    except Exception as e:
        logger.error(f"返回SQL查询时出错: {str(e)}")
        return jsonify({'error': f'返回SQL查询时出错: {str(e)}'}), 500

@battle_bp.route('/api/battle_data', methods=['GET'])
def battle_data():
    try:
        # 获取日期参数
        start_date_str = request.args.get('start_date')
        end_date_str = request.args.get('end_date')
        
        # 设置默认日期为今天
        today = date.today()
        end_date = today
        start_date = today
        
        # 解析日期
        if start_date_str:
            try:
                start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
            except ValueError:
                return jsonify({'error': '开始日期格式不正确，请使用YYYY-MM-DD格式'}), 400
                
        if end_date_str:
            try:
                end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
            except ValueError:
                return jsonify({'error': '结束日期格式不正确，请使用YYYY-MM-DD格式'}), 400
        
        # 生成SQL查询
        try:
            sql = export_battle_sql(start_date, end_date)
            
            # 执行SQL查询
            from app import db
            result = db.session.execute(text(sql))
            
            # 获取列名
            columns = result.keys()
            
            # 转换结果为列表
            data = []
            for row in result:
                item = {}
                for idx, col in enumerate(columns):
                    item[col] = row[idx]
                    
                    # 处理可能的datetime对象
                    if isinstance(item[col], datetime):
                        item[col] = item[col].strftime('%Y-%m-%d %H:%M:%S')
                data.append(item)
                
            return jsonify(data)
        except Exception as e:
            logger.error(f"执行SQL查询时出错: {str(e)}")
            return jsonify({'error': f'执行SQL查询时出错: {str(e)}'}), 500
    except Exception as e:
        logger.error(f"获取战斗数据时出错: {str(e)}")
        return jsonify({'error': f'获取战斗数据时出错: {str(e)}'}), 500

@battle_bp.route('/leaderboard', methods=['GET'])
def leaderboard():
    """显示战斗排行榜"""
    # 获取日期范围参数
    start_date_str = request.args.get('start_date', '')
    end_date_str = request.args.get('end_date', '')
    
    # 解析日期字符串
    start_date = None
    end_date = None
    try:
        if start_date_str:
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d')
        if end_date_str:
            # 设置结束日期为当天的23:59:59，包含整天
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d')
            end_date = end_date.replace(hour=23, minute=59, second=59)
    except ValueError as e:
        logger.error(f"日期格式错误: {str(e)}")
        return render_template('error.html', message=f"日期格式错误: {str(e)}")
    
    return render_template('leaderboard.html', start_date=start_date_str, end_date=end_date_str)

@battle_bp.route('/player/<string:player_name>/kills')
def get_player_kills(player_name):
    """获取玩家的击杀详情"""
    try:
        # 查询玩家的所有击杀记录
        query = text("""
            SELECT 
                p2.name as victim,
                p2.faction as victim_faction,
                COUNT(*) as count
            FROM battle_records br
            JOIN person p1 ON br.winner_id = p1.id
            JOIN person p2 ON br.loser_id = p2.id
            WHERE p1.name = :player_name
            GROUP BY p2.name, p2.faction
            ORDER BY count DESC
        """)
        
        result = db.session.execute(query, {'player_name': player_name})
        kills = [
            {
                'victim': row.victim,
                'victim_faction': row.victim_faction,
                'count': row.count
            }
            for row in result
        ]
        
        return jsonify({'kills': kills})
    except Exception as e:
        logger.error(f"获取玩家 {player_name} 击杀详情时出错: {str(e)}", exc_info=True)
        return jsonify({'error': str(e)}), 500

def get_statistics(faction=None):
    """
    获取总统计数据
    :param faction: 势力名称
    :return: (总玩家数, 总击杀数, 总死亡数, 总得分)
    """
    logger.info("获取总统计数据")
    
    # 构建查询
    sql = """
    SELECT 
        (SELECT COUNT(DISTINCT p.id) FROM person p 
         WHERE p.deleted_at IS NULL
         AND (:faction IS NULL OR p.god = :faction)
         AND EXISTS (SELECT 1 FROM battle_record br WHERE p.name IN (br.win, br.lost))
        ) AS total_players,
        SUM(CASE WHEN br.win = p.name THEN 1 ELSE 0 END) AS total_kills,
        SUM(CASE WHEN br.lost = p.name THEN 1 ELSE 0 END) AS total_deaths
    FROM person p
    LEFT JOIN battle_record br ON p.name IN (br.win, br.lost)
    WHERE p.deleted_at IS NULL
    AND (:faction IS NULL OR p.god = :faction)
    """
    
    # 执行查询
    params = {'faction': faction}
    result = db.session.execute(text(sql), params).fetchone()
    
    total_players = result.total_players or 0
    total_kills = result.total_kills or 0
    total_deaths = result.total_deaths or 0
    
    # 计算总得分
    total_score = (total_kills * 3) - total_deaths
    
    logger.debug(f"总玩家数: {total_players}, 总击杀数: {total_kills}, 总死亡数: {total_deaths}, 总得分: {total_score}")
    
    return total_players, total_kills, total_deaths, total_score

@battle_bp.route('/rankings/stats')
@login_required
def rankings_stats():
    """获取排名统计数据"""
    logger.info("访问排名统计数据API")
    
    # 获取筛选参数
    faction = request.args.get('faction')
    logger.debug(f"统计数据筛选参数: faction={faction}")
    
    try:
        # 获取统计数据
        total_players, total_kills, total_deaths, total_score = get_statistics(faction=faction)
        
        # 返回JSON数据
        return jsonify({
            'total_count': total_players,
            'total_kills': total_kills,
            'total_deaths': total_deaths,
            'total_score': total_score
        })
        
    except Exception as e:
        logger.error(f"获取统计数据时出错: {str(e)}", exc_info=True)
        return jsonify({'error': '获取统计数据失败'}), 500

def get_faction_statistics():
    """
    获取各个势力的统计数据
    :return: 各个势力的人数、击杀数和死亡数
    """
    logger.info("获取各个势力的统计数据")
    
    # 构建查询
    sql = """
    SELECT 
        p.god AS faction,
        COUNT(DISTINCT p.id) AS player_count,
        SUM(CASE WHEN br.win = p.name THEN 1 ELSE 0 END) AS kills,
        SUM(CASE WHEN br.lost = p.name THEN 1 ELSE 0 END) AS deaths
    FROM person p
    LEFT JOIN battle_record br ON p.name IN (br.win, br.lost)
    WHERE p.deleted_at IS NULL
    AND EXISTS (SELECT 1 FROM battle_record br2 WHERE p.name IN (br2.win, br2.lost))
    AND p.god IS NOT NULL
    GROUP BY p.god
    ORDER BY p.god
    """
    
    # 执行查询
    result = db.session.execute(text(sql))
    
    # 处理结果
    faction_stats = []
    for row in result:
        faction_stats.append({
            'faction': row.faction,
            'player_count': row.player_count or 0,
            'kills': row.kills or 0,
            'deaths': row.deaths or 0,
            'score': (row.kills or 0) * 3 - (row.deaths or 0)
        })
    
    logger.debug(f"势力统计数据: {faction_stats}")
    
    return faction_stats 

@battle_bp.route('/rankings/faction_stats')
@login_required
def rankings_faction_stats():
    """获取势力统计数据"""
    logger.info("访问势力统计数据API")
    
    try:
        # 获取势力统计数据
        faction_stats = get_faction_statistics()
        
        # 返回JSON数据
        return jsonify({
            'faction_stats': faction_stats
        })
        
    except Exception as e:
        logger.error(f"获取势力统计数据时出错: {str(e)}", exc_info=True)
        return jsonify({'error': '获取势力统计数据失败'}), 500 

@battle_bp.route('/gods_ranking')
@login_required
def gods_ranking():
    """显示三个神的击杀死亡情况"""
    # 获取日期参数
    start_datetime_str = request.args.get('start_datetime')
    end_datetime_str = request.args.get('end_datetime')
    # 添加分组显示参数
    show_grouped = request.args.get('show_grouped', 'true') == 'true'
    
    # --- Default Date Logic --- 
    now = datetime.now()
    start_datetime = None
    end_datetime = None
    
    if start_datetime_str:
        try:
            start_datetime = datetime.strptime(start_datetime_str, '%Y-%m-%dT%H:%M')
        except ValueError:
            flash('开始时间格式不正确', 'error')
            # Fallback to default if format is wrong?
            start_datetime_str = None # Reset string so default logic applies
            
    if not start_datetime_str: # If not provided or format was wrong
        start_datetime = now.replace(hour=0, minute=0, second=0, microsecond=0)
        start_datetime_str = start_datetime.strftime('%Y-%m-%dT%H:%M')
        
    if end_datetime_str:
        try:
            end_datetime = datetime.strptime(end_datetime_str, '%Y-%m-%dT%H:%M')
            # 设置结束时间的秒数为59，以包含整分钟
            end_datetime = end_datetime.replace(second=59)
        except ValueError:
            flash('结束时间格式不正确', 'error')
            # Fallback to default?
            end_datetime_str = None # Reset string so default logic applies
            
    if not end_datetime_str: # If not provided or format was wrong
        end_datetime = now.replace(hour=23, minute=59, second=59, microsecond=0)
        end_datetime_str = end_datetime.strftime('%Y-%m-%dT%H:%M')
    # --- End Default Date Logic ---
    
    # 获取三个神的数据
    gods = ['梵天', '比湿奴', '湿婆']
    stats = {}
    
    try:
        for god in gods:
            # 构建日期条件
            date_condition = ""
            query_params = {'god': god}
            
            if start_datetime:
                date_condition += " AND br.publish_at >= :start_datetime"
                query_params['start_datetime'] = start_datetime
            if end_datetime:
                date_condition += " AND br.publish_at <= :end_datetime"
                query_params['end_datetime'] = end_datetime
            
            # 根据是否需要按玩家分组进行统计选择不同的查询
            if show_grouped:
                # 使用玩家分组的查询 - 修正版：先计算个人战绩再按组聚合
                query = text(f"""
                    WITH player_battle_stats AS (
                        -- 1. 计算每个玩家在时间范围内的独立战绩 (使用 win/lost 列)
                        SELECT
                            p.id, -- Include player ID
                            p.name,
                            SUM(CASE WHEN br.win = p.name THEN 1 ELSE 0 END) as kills,
                            SUM(CASE WHEN br.lost = p.name THEN 1 ELSE 0 END) as deaths,
                            SUM(CASE WHEN br.win = p.name THEN COALESCE(br.remark, 0) ELSE 0 END) as bless
                        FROM person p
                        LEFT JOIN battle_record br ON p.name IN (br.win, br.lost)
                            -- Apply date condition here if needed, but simpler outside JOIN now
                        WHERE p.god = :god
                          AND p.deleted_at IS NULL
                          {date_condition} -- Apply date condition in WHERE clause
                        GROUP BY p.id, p.name -- Group by ID and Name
                        HAVING SUM(CASE WHEN br.win = p.name THEN 1 ELSE 0 END) > 0
                            OR SUM(CASE WHEN br.lost = p.name THEN 1 ELSE 0 END) > 0
                            OR SUM(CASE WHEN br.win = p.name THEN COALESCE(br.remark, 0) ELSE 0 END) > 0
                    ),
                    player_distinct AS (
                        -- 2. 获取所有有效的玩家ID，并关联其分组信息 (与之前类似)
                        SELECT
                            p.id,
                            p.name AS original_player_name, -- Keep original name if needed
                            p.god,
                            COALESCE(p.player_group_id, p.id) AS group_key,
                            COALESCE(pg.group_name, p.name) AS player_name, -- Display name
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
                    -- 3. 简化最终聚合：直接聚合 player_distinct 和 player_battle_stats
                    SELECT
                        pd.player_name AS name, -- Display name (group or individual)
                        MAX(pd.is_group) AS is_group, -- Get the is_group flag for the group
                        SUM(COALESCE(pbs.kills, 0)) AS kills,
                        SUM(COALESCE(pbs.deaths, 0)) AS deaths,
                        SUM(COALESCE(pbs.bless, 0)) AS bless
                    FROM
                        player_distinct pd
                    LEFT JOIN
                        player_battle_stats pbs ON pd.id = pbs.id -- Join member info to their stats by ID
                    GROUP BY
                        pd.group_key, pd.player_name -- Group by the unique group key and its display name
                    HAVING
                        SUM(COALESCE(pbs.kills, 0)) > 0 OR SUM(COALESCE(pbs.deaths, 0)) > 0 OR SUM(COALESCE(pbs.bless, 0)) > 0 -- Keep filtering
                    ORDER BY
                        kills DESC, deaths ASC, bless DESC
                """)
            else:
                # 原始查询（不考虑玩家分组） - 修正版: 使用 ID 计算战绩
                query = text(f"""
                    WITH player_stats AS (
                        SELECT 
                            p.id, -- Include ID
                            p.name,
                            SUM(CASE WHEN br.win = p.name THEN 1 ELSE 0 END) as kills, -- Use p.name
                            SUM(CASE WHEN br.lost = p.name THEN 1 ELSE 0 END) as deaths, -- Use p.name
                            SUM(CASE WHEN br.win = p.name THEN COALESCE(br.remark, 0) ELSE 0 END) as bless -- Use p.name
                        FROM person p
                        LEFT JOIN battle_record br ON p.name IN (br.win, br.lost)
                            -- Apply date condition here if needed, but simpler outside JOIN now
                            # AND (1=1 {date_condition.replace('br.', 'br.')})
                        WHERE p.god = :god
                          AND p.deleted_at IS NULL
                          {date_condition} -- Apply date condition in WHERE clause
                        GROUP BY p.id, p.name -- Group by ID and Name
                        HAVING SUM(CASE WHEN br.win = p.name THEN 1 ELSE 0 END) > 0 -- Use p.name
                            OR SUM(CASE WHEN br.lost = p.name THEN 1 ELSE 0 END) > 0 -- Use p.name
                            OR SUM(CASE WHEN br.win = p.name THEN COALESCE(br.remark, 0) ELSE 0 END) > 0 -- Use p.name
                    )
                    SELECT 
                        name,
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
                # --- DEBUGGING: Print raw row data --- 
                # print(f"DEBUG ROW: {row._asdict()}") 
                # --- END DEBUGGING ---
                
                player_data = {
                    'name': row.name,
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
        
        return render_template('battle/gods.html', 
                             stats=stats,
                             start_datetime=start_datetime_str,
                             end_datetime=end_datetime_str,
                             show_grouped=show_grouped)
    except Exception as e:
        logger.error(f"获取三神战绩统计时出错: {str(e)}", exc_info=True)
        # 不再 flash 和 redirect，直接返回错误信息
        flash('获取战绩统计数据时出错', 'error')
        return redirect(url_for('battle.rankings'))

@battle_bp.route('/api/group_details')
def group_details():
    """获取玩家分组下所有游戏ID的详细战绩"""
    try:
        # 获取参数
        god = request.args.get('god')
        player_name = request.args.get('player_name')
        start_datetime_str = request.args.get('start_datetime')
        end_datetime_str = request.args.get('end_datetime')
        
        # 验证必要参数
        if not player_name:
            return jsonify({'error': '缺少必要参数：player_name'}), 400
            
        # 解析日期时间
        start_datetime = None
        end_datetime = None
        
        if start_datetime_str:
            try:
                start_datetime = datetime.strptime(start_datetime_str, '%Y-%m-%dT%H:%M')
            except ValueError:
                return jsonify({'error': '开始时间格式不正确'}), 400
                
        if end_datetime_str:
            try:
                end_datetime = datetime.strptime(end_datetime_str, '%Y-%m-%dT%H:%M')
                # 设置结束时间的秒数为59，以包含整分钟
                end_datetime = end_datetime.replace(second=59)
            except ValueError:
                return jsonify({'error': '结束时间格式不正确'}), 400
        
        # 构建日期条件
        date_condition = ""
        query_params = {
            'god': god,
            'player_name': player_name
        }
        
        if start_datetime:
            date_condition += " AND br.publish_at >= :start_datetime"
            query_params['start_datetime'] = start_datetime
        if end_datetime:
            date_condition += " AND br.publish_at <= :end_datetime"
            query_params['end_datetime'] = end_datetime
        
        # 首先查询分组信息
        group_query = text("""
            SELECT 
                pg.id as group_id,
                pg.group_name,
                pg.description
            FROM 
                player_group pg 
            WHERE 
                pg.group_name = :player_name
            LIMIT 1
        """)
        
        group_result = db.session.execute(group_query, query_params).fetchone()
        
        if not group_result:
            return jsonify({'error': '找不到指定的玩家分组'}), 404
            
        # 获取分组ID
        group_id = group_result.group_id
        
        # 查询该分组下所有玩家的战绩
        members_query = text(f"""
            SELECT 
                p.id,
                p.name,
                p.god,
                COUNT(DISTINCT CASE WHEN br.win = p.name THEN br.id END) AS kills,
                COUNT(DISTINCT CASE WHEN br.lost = p.name THEN br.id END) AS deaths,
                SUM(CASE WHEN br.win = p.name THEN COALESCE(br.remark, 0) ELSE 0 END) AS bless
            FROM 
                person p
            LEFT JOIN 
                battle_record br ON p.name IN (br.win, br.lost)
            WHERE 
                p.deleted_at IS NULL
                AND p.player_group_id = :group_id
                {'' if god is None else 'AND p.god = :god'}
                {date_condition}
            GROUP BY 
                p.id, p.name, p.god
            HAVING 
                kills > 0 OR deaths > 0
            ORDER BY 
                kills DESC, deaths ASC
        """)
        
        # 添加分组ID参数
        query_params['group_id'] = group_id
        
        # 获取成员数据
        members = []
        for row in db.session.execute(members_query, query_params):
            members.append({
                'id': row.id,
                'name': row.name,
                'god': row.god,
                'kills': int(row.kills or 0),
                'deaths': int(row.deaths or 0),
                'bless': int(row.bless or 0)
            })
        
        # 返回结果
        return jsonify({
            'group': {
                'id': group_result.group_id,
                'name': group_result.group_name,
                'description': group_result.description
            },
            'members': members
        })
        
    except Exception as e:
        logger.error(f"获取分组详情出错: {str(e)}", exc_info=True)
        return jsonify({'error': f'获取分组详情时出错: {str(e)}'}), 500 