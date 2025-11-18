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
from app.models.rankings import Rankings
from app.utils.file_parser import parse_text_file, save_battle_log_to_db
from app.utils.data_service import get_player_rankings, get_battle_details_by_player, export_data_to_json, get_statistics
from app.config import Config
from app.utils.logger import get_logger
from app.utils.battle_report import generate_battle_report, export_battle_sql
from datetime import datetime, date, time, timedelta
from sqlalchemy import text, func, distinct, cast, String, DATE, TIME, Integer, or_, case
from app.utils.auth import login_required
from app.utils.jwt_auth import token_required
import json
from app.utils.web_scraper import get_rankings_by_scraper
from dateutil import parser
from app.services.battle_service import get_player_rankings as get_rankings_service, get_all_jobs

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
    
    # --- Modified Filter Logic --- 
    raw_faction = request.args.get('faction')
    raw_job = request.args.get('job')
    time_range = request.args.get('time_range', 'today')  # 默认为today
    show_grouped = request.args.get('show_grouped', 'true') == 'true'
    print("rangkings========================================\n")
    show_grouped = False
    
    # 获取自定义时间范围参数
    start_datetime = request.args.get('start_datetime')
    end_datetime = request.args.get('end_datetime')

    # Determine faction for query and template
    if raw_faction == 'all' or raw_faction == '':
        query_faction = None
        selected_faction = None # For template button state
    elif raw_faction is None: # First load or no faction specified
        query_faction = '比湿奴' # Default query to 比湿奴
        selected_faction = '比湿奴' # Default button selection to 比湿奴
    else: # Specific faction selected
        query_faction = raw_faction
        selected_faction = raw_faction

    # Determine job for query and template
    if raw_job == 'all' or raw_job == '' or raw_job is None:
        query_job = None
        selected_job = None
    else:
        query_job = raw_job
        selected_job = raw_job
        
    # 确定时间筛选条件（用于filtered_battle_records CTE，不需要br.前缀）
    date_condition = ""
    # 如果提供了具体的开始和结束日期，优先使用
    if start_datetime and end_datetime:
        date_condition = f"AND publish_at BETWEEN '{start_datetime}' AND '{end_datetime}'"
        # 在这种情况下，不使用预设时间范围
        time_range = None
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
    # 如果是'all'则不添加时间筛选
    
    # --- End Modified Filter Logic --- 

    logger.debug(f"排名筛选参数: faction={selected_faction}, job={selected_job}, time_range={time_range}, start_datetime={start_datetime}, end_datetime={end_datetime}, show_grouped={show_grouped}")
    
    try:
        # 使用服务层获取排名数据
        player_rankings = get_rankings_service(
            faction=query_faction,
            job=query_job,
            time_range=time_range,
            start_datetime=start_datetime,
            end_datetime=end_datetime
        )
        
        # 获取所有职业列表
        jobs = get_all_jobs()
        
        # 获取统计数据 (Use query_faction)
        # total_players, total_kills, total_deaths, total_score = get_statistics(faction=query_faction)
        
        # Pass selected_faction and selected_job to template
        return render_template('rankings.html', 
                              players=player_rankings, 
                              jobs=jobs,
                              selected_job=selected_job,
                              selected_faction=selected_faction,
                              show_grouped=show_grouped,
                              selected_time=time_range,
                              start_date=start_datetime,
                              end_date=end_datetime,)
    except Exception as e:
        logger.error(f"玩家排名页面渲染出错: {str(e)}", exc_info=True)
        flash('获取排名数据时出错', 'error')
        # Pass selected_faction and selected_job even on error
        return render_template('rankings.html', 
                             players=[], 
                             jobs=[],
                             selected_job=selected_job,
                             selected_faction=selected_faction,
                             show_grouped=show_grouped,
                             selected_time=time_range,
                             start_date=start_datetime,
                             end_date=end_datetime,
                             total_players=0,
                             total_kills=0,
                             total_deaths=0,
                             total_score=0)


@battle_bp.route('/player/<int:person_id>')
def player_details(person_id):
    """玩家详细信息页面"""
    logger.info(f"访问玩家ID={person_id}的详细信息页面")
    
    # 获取日期参数
    time_range = request.args.get('time_range')
    start_date = request.args.get('start_datetime')
    end_date = request.args.get('end_datetime')
    
    date_condition = ""
    # 如果提供了具体的开始和结束日期，优先使用
    if start_date and end_date:
        try:
            # 格式化日期字符串以防SQL注入并确保格式正确
            start_datetime = parser.parse(start_date)
            end_datetime = parser.parse(end_date)
            date_condition = f"AND br.publish_at BETWEEN '{start_datetime:%Y-%m-%d %H:%M:%S}' AND '{end_datetime:%Y-%m-%d %H:%M:%S}'"
            # 为模板保存格式化后的日期字符串
            start_date = start_datetime.strftime('%Y-%m-%dT%H:%M')
            end_date = end_datetime.strftime('%Y-%m-%dT%H:%M')
        except (ValueError, TypeError) as e:
            logger.error(f"日期解析错误: {str(e)}")
            # 重置为默认值
            start_date = None
            end_date = None
            date_condition = ""
    # 如果没有明确的日期参数但有时间范围，根据时间范围设置日期条件
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
    
    try:
        # 获取玩家战斗明细，传递时间参数
        player_details = get_battle_details_by_player(person_id, date_condition=date_condition)
        
        if not player_details:
            flash('未找到该玩家的详细信息', 'warning')
            return redirect(url_for('battle.rankings'))
        
        return render_template('player_details.html', 
                             player=player_details,
                             start_date=start_date,
                             end_date=end_date,
                             time_range=time_range)
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
    
    # 构建查询 - 优化版：先过滤battle_record并聚合，充分利用索引
    sql = """
    WITH filtered_battle_records AS (
        -- 1. 先过滤battle_record表（利用 deleted_at 索引）
        SELECT win, lost
        FROM battle_record
        WHERE deleted_at IS NULL
    ),
    win_stats AS (
        -- 2. 统计每个玩家的击杀记录（利用 win 索引）
        SELECT 
            win as player_name,
            COUNT(*) as kills
        FROM filtered_battle_records
        WHERE win IS NOT NULL
        GROUP BY win
    ),
    lost_stats AS (
        -- 3. 统计每个玩家的死亡记录（利用 lost 索引）
        SELECT 
            lost as player_name,
            COUNT(*) as deaths
        FROM filtered_battle_records
        WHERE lost IS NOT NULL
        GROUP BY lost
    ),
    player_stats AS (
        -- 4. 将统计数据与玩家表JOIN（只保留有战斗记录的玩家）
        SELECT
            p.id,
            p.god,
            COALESCE(ws.kills, 0) as kills,
            COALESCE(ls.deaths, 0) as deaths
        FROM person p
        LEFT JOIN win_stats ws ON p.name = ws.player_name
        LEFT JOIN lost_stats ls ON p.name = ls.player_name
        WHERE p.deleted_at IS NULL
          AND p.god IS NOT NULL
          AND (COALESCE(ws.kills, 0) > 0 OR COALESCE(ls.deaths, 0) > 0)
    )
    SELECT 
        god AS faction,
        COUNT(DISTINCT id) AS player_count,
        SUM(kills) AS kills,
        SUM(deaths) AS deaths
    FROM player_stats
    GROUP BY god
    ORDER BY god
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
            # 构建日期条件（用于CTE中的battle_record表）
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
                # 使用玩家分组的查询 - 优化版：先过滤battle_record并聚合，充分利用索引
                query = text(f"""
                    WITH filtered_battle_records AS (
                        -- 1. 先过滤battle_record表（利用 publish_at 和 deleted_at 索引）
                        SELECT win, lost, remark
                        FROM battle_record
                        WHERE deleted_at IS NULL
                          {date_condition}
                    ),
                    win_stats AS (
                        -- 2. 统计每个玩家的击杀记录（利用 win 索引）
                        SELECT 
                            win as player_name,
                            COUNT(*) as kills,
                            SUM(COALESCE(remark, 0)) as bless
                        FROM filtered_battle_records
                        WHERE win IS NOT NULL
                        GROUP BY win
                    ),
                    lost_stats AS (
                        -- 3. 统计每个玩家的死亡记录（利用 lost 索引）
                        SELECT 
                            lost as player_name,
                            COUNT(*) as deaths
                        FROM filtered_battle_records
                        WHERE lost IS NOT NULL
                        GROUP BY lost
                    ),
                    player_battle_stats AS (
                        -- 4. 将统计数据与玩家表JOIN（使用等值JOIN，可以走索引）
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
                # 原始查询（不考虑玩家分组） - 优化版: 先过滤battle_record并聚合，充分利用索引
                query = text(f"""
                    WITH filtered_battle_records AS (
                        -- 1. 先过滤battle_record表（利用 publish_at 和 deleted_at 索引）
                        SELECT win, lost, remark
                        FROM battle_record
                        WHERE deleted_at IS NULL
                          {date_condition}
                    ),
                    win_stats AS (
                        -- 2. 统计每个玩家的击杀记录（利用 win 索引）
                        SELECT 
                            win as player_name,
                            COUNT(*) as kills,
                            SUM(COALESCE(remark, 0)) as bless
                        FROM filtered_battle_records
                        WHERE win IS NOT NULL
                        GROUP BY win
                    ),
                    lost_stats AS (
                        -- 3. 统计每个玩家的死亡记录（利用 lost 索引）
                        SELECT 
                            lost as player_name,
                            COUNT(*) as deaths
                        FROM filtered_battle_records
                        WHERE lost IS NOT NULL
                        GROUP BY lost
                    ),
                    player_stats AS (
                        -- 4. 将统计数据与玩家表JOIN（使用等值JOIN，可以走索引）
                        SELECT 
                            p.id,
                            CONCAT(p.name, '(', IFNULL(p.job, '无'), ')') AS name,
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

@battle_bp.route('/pk_participation')
@login_required
def pk_participation():
    """显示玩家晚间PK参与次数和奖励"""
    # 添加分组显示参数
    show_grouped = request.args.get("show_grouped", "true") == "true"
    logger.info("访问晚间PK参与统计页面")

    start_date_str = request.args.get('start_date')
    end_date_str = request.args.get('end_date')

    # --- Default Date Logic ---
    now = datetime.now()
    start_date = None
    end_date = None

    if start_date_str:
        try:
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
        except ValueError:
            flash('开始日期格式不正确', 'error')
            start_date_str = None
    if not start_date_str:
        start_date = now.date()
        start_date_str = start_date.strftime('%Y-%m-%d')

    if end_date_str:
        try:
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
        except ValueError:
            flash('结束日期格式不正确', 'error')
            end_date_str = None
    if not end_date_str:
        end_date = now.date()
        end_date_str = end_date.strftime('%Y-%m-%d')
    # --- End Default Date Logic ---

    # 使用确切的时间范围
    start_datetime = datetime.combine(start_date, time(20, 0, 0))
    end_datetime = datetime.combine(end_date, time(21, 59, 59))

    summary_data = []
    try:
        # --- 1. Database Query for Raw Participation Data (No blessing info needed here) ---
        # 查询参与PK的比湿奴玩家的基本信息和不重复的参与日期
        query_participation = text("""
            SELECT DISTINCT
                p.id AS person_id,
                p.name AS person_name,
                p.god,
                p.job,
                p.player_group_id,
                pg.group_name,
                DATE(br.publish_at) as participation_date
            FROM person p
            JOIN battle_record br ON p.name IN (br.win, br.lost)
            LEFT JOIN player_group pg ON p.player_group_id = pg.id
            WHERE p.deleted_at IS NULL
              AND p.god = '比湿奴'
              AND br.publish_at >= :start_datetime
              AND br.publish_at <= :end_datetime
              -- 时间范围已由 start_datetime 和 end_datetime 控制
            ORDER BY p.player_group_id, p.id, participation_date
        """)

        results = db.session.execute(query_participation, {
            'start_datetime': start_datetime,
            'end_datetime': end_datetime
        }).fetchall()

        # --- 2. Process Results and Aggregate basic info (No blessing count here) ---
        group_aggregates = {}
        individual_aggregates = {}

        for row in results:
            person_id, person_name, god, job, player_group_id, group_name, participation_date = row
            # logger.debug(f"Processing participation: {person_name}, Date: {participation_date}") # Optional debug

            if player_group_id:
                group_key = player_group_id
                if group_key not in group_aggregates:
                    group_aggregates[group_key] = {
                        'name': group_name or f'分组 {group_key}',
                        'god': god,
                        'members': [], # Store member details {id, name, job}
                        'jobs': set(),
                        'participation_dates': set()
                    }
                group_aggregates[group_key]['participation_dates'].add(participation_date)
                # Store unique members and their jobs
                member_ids = {m['id'] for m in group_aggregates[group_key]['members']}
                if person_id not in member_ids:
                     group_aggregates[group_key]['members'].append({'id': person_id, 'name': person_name, 'job': job})
                     group_aggregates[group_key]['jobs'].add(job)
            else:
                # Individual players
                if person_id not in individual_aggregates:
                    individual_aggregates[person_id] = {
                        'id': person_id,
                        'name': person_name,
                        'god': god,
                        'job': job,
                        'participation_dates': set()
                    }
                individual_aggregates[person_id]['participation_dates'].add(participation_date)


        # --- 3. Calculate Statistics and Prepare Final Summary Data (Query blessing count here) ---
        final_summary_data = []
        total_reward_all = 0
        period_total_days = (end_date - start_date).days + 1
        full_attendance_list = []

        # Base SQL for counting blessings in the time range where remark='1'
        query_blessing_count_base = """
            SELECT COUNT(*)
            FROM battle_record br
            WHERE br.remark = '1'
              AND br.publish_at >= :start_datetime
              AND br.publish_at <= :end_datetime
              AND {win_condition}
        """
        query_params_blessing = {
            'start_datetime': start_datetime,
            'end_datetime': end_datetime
        }


        # Process aggregated groups
        for group_key, data in group_aggregates.items():
            participation_days = len(data['participation_dates'])
            group_job = '奶' if '奶' in data['jobs'] else (list(data['jobs'])[0] if data['jobs'] else '未知')
            member_names = [m['name'] for m in data['members']]

            # Get blessing count for the group
            blessing_count = 0
            if member_names: # Only query if group has members
                win_condition = "br.win IN :member_names"
                query_blessing_sql = query_blessing_count_base.format(win_condition=win_condition)
                # Create a copy of params for this specific query to avoid modification issues
                current_params = query_params_blessing.copy()
                current_params['member_names'] = tuple(member_names) # Use tuple for IN clause
                blessing_count = db.session.execute(text(query_blessing_sql), current_params).scalar() or 0
                logger.debug(f"Group '{data['name']}' blessing count: {blessing_count} for members: {member_names}") # Debug log

            base_reward_per_day = 20_000_000_000 if group_job == '奶' else 10_000_000_000
            total_base_reward = base_reward_per_day * participation_days
            blessing_bonus = 10_000_000_000 if blessing_count > 0 else 0
            total_reward = total_base_reward + blessing_bonus
            total_reward_all += total_reward

            if participation_days == period_total_days:
                full_attendance_list.append(data['name'] + " (组)")

            final_summary_data.append({
                'id': group_key,
                'name': data['name'],
                'god': data['god'],
                'job': group_job,
                'participation_days': participation_days,
                'total_blessings': blessing_count, # Use the queried count
                'reward': total_reward,
                'is_group': True
            })

        # Process individual players
        for player_id, data in individual_aggregates.items():
            participation_days = len(data['participation_dates'])
            job = data['job'] or '未知'
            player_name = data['name']

            # Get blessing count for the individual
            win_condition = "br.win = :player_name"
            query_blessing_sql = query_blessing_count_base.format(win_condition=win_condition)
            # Create a copy of params
            current_params = query_params_blessing.copy()
            current_params['player_name'] = player_name
            blessing_count = db.session.execute(text(query_blessing_sql), current_params).scalar() or 0
            logger.debug(f"Individual '{player_name}' blessing count: {blessing_count}") # Debug log

            base_reward_per_day = 20_000_000_000 if job == '奶' else 10_000_000_000
            total_base_reward = base_reward_per_day * participation_days
            blessing_bonus = 10_000_000_000 if blessing_count > 0 else 0
            total_reward = total_base_reward + blessing_bonus
            total_reward_all += total_reward

            if participation_days == period_total_days:
                full_attendance_list.append(data['name'])

            final_summary_data.append({
                'id': player_id,
                'name': data['name'],
                'god': data['god'],
                'job': job,
                'participation_days': participation_days,
                'total_blessings': blessing_count, # Use the queried count
                'reward': total_reward,
                'is_group': False
            })

        # --- Sort the final list by reward (desc), then participation days (desc), then name (asc) ---
        final_summary_data.sort(key=lambda x: (-x['reward'], -x['participation_days'], x['name']))
        summary_data = final_summary_data

    except Exception as e:
        logger.error(f"获取PK参与统计时出错: {str(e)}", exc_info=True)
        flash('获取PK参与统计数据时出错', 'error')
        summary_data = [] # Ensure it's empty on error
        total_reward_all = 0 # Reset on error
        period_total_days = 0 # Reset on error
        full_attendance_list = [] # Reset on error

    # 渲染模板时传递所有需要的数据
    return render_template('battle/pk_participation.html',
                           summary_data=summary_data,
                           start_date=start_date_str,
                           end_date=end_date_str,
                           show_grouped=show_grouped,
                           total_reward_all=total_reward_all, # 添加总奖励
                           period_total_days=period_total_days, # 添加周期天数
                           full_attendance_list=full_attendance_list) # 添加全勤列表

@battle_bp.route('/api/pk_participation_details')
@login_required # Assuming details also require login
def pk_participation_details_api():
    player_id = request.args.get('player_id', type=int)
    god = request.args.get('god')
    start_date_str = request.args.get('start_date')
    end_date_str = request.args.get('end_date')

    if not all([player_id, god, start_date_str, end_date_str]):
        return jsonify({"error": "Missing required parameters"}), 400

    try:
        start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
        end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
        start_datetime = datetime.combine(start_date, datetime.min.time())
        end_datetime_next_day = datetime.combine(end_date + timedelta(days=1), datetime.min.time())

        # Query distinct participation dates
        participation_dates = (
            db.session.query(
                distinct(cast(BattleRecord.publish_at, DATE)).label('participation_date')
            )
            .join(Person, or_(Person.name == BattleRecord.win, Person.name == BattleRecord.lost))
            .filter(
                Person.id == player_id,
                Person.god == god, # Also filter by god for consistency?
                BattleRecord.publish_at >= start_datetime,
                BattleRecord.publish_at < end_datetime_next_day,
                cast(BattleRecord.publish_at, TIME) >= time(20, 0, 0),
                cast(BattleRecord.publish_at, TIME) <= time(21, 59, 59)
            )
            .order_by(cast(BattleRecord.publish_at, DATE).desc())
            .all()
        )

        # Convert date objects to strings
        details = [d.participation_date.strftime('%Y-%m-%d') for d in participation_dates]

        return jsonify({"details": details})

    except ValueError:
        return jsonify({"error": "Invalid date format"}), 400
    except Exception as e:
        logger.error(f"获取PK参与详情API出错: {str(e)}", exc_info=True)
        return jsonify({"error": "Failed to fetch participation details"}), 500 

@battle_bp.route('/rankings_card')
@login_required
def rankings_card():
    """排行榜数据卡片查询页面"""
    logger.info("访问排行榜数据卡片查询页面")
    
    # 获取URL参数
    url = request.args.get('url', 'http://fqa.173mz.com/a/a.asp?b=100&id=12')
    category = request.args.get('category', '虎威主神排行榜')
    
    # 使用爬虫获取数据
    logger.debug(f"使用爬虫从 {url} 获取排行榜数据")
    try:
        # 获取爬虫数据
        ranking_data = get_rankings_by_scraper(url=url, category=category)
        
        # 确保数据包含所需的字段
        if ranking_data and 'brahma_players' not in ranking_data and 'players' in ranking_data:
            # 如果爬虫返回的数据没有按神分类，手动分类
            players = ranking_data.get('players', [])
            
            # 按神分类玩家
            brahma_players = []
            vishnu_players = []
            shiva_players = []
            
            for player in players:
                if player.get('god') == "梵天":
                    brahma_players.append(player)
                elif player.get('god') == "比湿奴":
                    vishnu_players.append(player)
                elif player.get('god') == "湿婆":
                    shiva_players.append(player)
            
            # 添加到结果中
            ranking_data['brahma_players'] = brahma_players
            ranking_data['vishnu_players'] = vishnu_players
            ranking_data['shiva_players'] = shiva_players
        
        # 检查是否有错误且没有数据
        if "error" in ranking_data and not (ranking_data.get('all_players') or ranking_data.get('brahma_players')):
            flash(f"获取排行榜数据失败: {ranking_data['error']}", 'error')
            ranking_data = None
    except Exception as e:
        logger.error(f"获取排行榜数据时出错: {str(e)}", exc_info=True)
        flash(f"获取排行榜数据时出错: {str(e)}", 'error')
        ranking_data = None
    
    # 固定类别选项，因为我们现在使用爬虫
    categories = ['虎威主神排行榜', '积分排行榜', '杀人排行榜', '死亡排行榜']
    
    return render_template('battle/rankings_card.html', 
                           categories=categories,
                           category=category,
                           url=url,
                           ranking_data=ranking_data)

@battle_bp.route('/api/rankings')
@login_required
def get_rankings():
    """获取排行榜数据API"""
    url = request.args.get('url', 'http://fqa.173mz.com/a/a.asp?b=100&id=12')
    category = request.args.get('category', '虎威主神排行榜')
    
    try:
        # 使用爬虫获取数据，同时会查询数据库获取职业信息
        ranking_data = get_rankings_by_scraper(url=url, category=category)
        
        # 检查是否有错误
        if "error" in ranking_data:
            return jsonify({'error': ranking_data['error']}), 500
        
        # 返回排行榜数据
        return jsonify(ranking_data)
    except Exception as e:
        logger.error(f"获取排行榜数据时出错: {str(e)}", exc_info=True)
        return jsonify({'error': f'获取排行榜数据失败: {str(e)}'}), 500

@battle_bp.route('/api/rankings/categories')
@login_required
def get_ranking_categories():
    """获取所有排行榜类别API"""
    try:
        # 获取所有排行榜类别
        categories = db.session.query(Rankings.category).distinct().all()
        categories = [c[0] for c in categories]
        
        return jsonify({'categories': categories})
    except Exception as e:
        logger.error(f"获取排行榜类别时出错: {str(e)}", exc_info=True)
        return jsonify({'error': f'获取排行榜类别失败: {str(e)}'}), 500

@battle_bp.route('/rankings_admin', methods=['GET', 'POST'])
@login_required
def rankings_admin():
    """排行榜数据管理页面"""
    if request.method == 'POST':
        try:
            # 从请求中获取数据
            category = request.form.get('category')
            update_time = request.form.get('update_time')
            players_data = request.form.get('players_data')
            
            if not category or not players_data:
                flash('类别和玩家数据不能为空', 'error')
                return redirect(url_for('battle.rankings_admin'))
            
            # 尝试解析 players_data
            try:
                players_json = json.loads(players_data)
            except json.JSONDecodeError:
                flash('玩家数据格式错误，必须是有效的 JSON 格式', 'error')
                return redirect(url_for('battle.rankings_admin'))
            
            # 创建或更新排行榜数据
            ranking = Rankings.create_or_update(
                category=category,
                players_data=players_json,
                update_time=update_time
            )
            
            flash(f'排行榜数据已成功保存，ID: {ranking.id}', 'success')
            return redirect(url_for('battle.rankings_admin'))
        except Exception as e:
            logger.error(f"保存排行榜数据时出错: {str(e)}", exc_info=True)
            flash(f'保存排行榜数据时出错: {str(e)}', 'error')
            return redirect(url_for('battle.rankings_admin'))
    
    # GET 请求，显示管理页面
    # 获取所有排行榜记录
    rankings = Rankings.query.order_by(Rankings.updated_at.desc()).all()
    rankings = [r.to_dict() for r in rankings]
    
    return render_template('battle/rankings_admin.html', 
                          rankings=rankings,
                          now=datetime.now())

@battle_bp.route('/api/rankings/<int:ranking_id>', methods=['DELETE'])
@login_required
def delete_ranking(ranking_id):
    """删除排行榜数据API"""
    try:
        ranking = Rankings.query.get(ranking_id)
        if not ranking:
            return jsonify({'error': f'未找到 ID 为 {ranking_id} 的排行榜数据'}), 404
        
        db.session.delete(ranking)
        db.session.commit()
        
        return jsonify({'message': f'ID 为 {ranking_id} 的排行榜数据已成功删除'})
    except Exception as e:
        logger.error(f"删除排行榜数据时出错: {str(e)}", exc_info=True)
        return jsonify({'error': f'删除排行榜数据失败: {str(e)}'}), 500

# 移动端 API 接口已移至 app/routes/api_battle.py
