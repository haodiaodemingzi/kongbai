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
from app.utils.data_service import get_player_rankings, get_battle_details_by_player, export_data_to_json
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
    """玩家排名页面"""
    logger.info("访问玩家排名页面")
    
    # 获取筛选参数
    faction = request.args.get('faction')
    logger.debug(f"排名筛选参数: faction={faction}")
    
    try:
        # 获取玩家排名数据
        player_rankings = get_player_rankings(faction=faction)
        logger.debug(f"获取到 {len(player_rankings)} 名玩家排名数据")
        
        # 获取所有势力
        factions = ['梵天', '比湿奴', '湿婆']
        
        logger.debug("渲染排名页面")
        return render_template('rankings.html', 
                              players=player_rankings, 
                              factions=factions, 
                              current_faction=faction)
    except Exception as e:
        logger.error(f"玩家排名页面渲染出错: {str(e)}", exc_info=True)
        flash('获取排名数据时出错', 'error')
        return render_template('rankings.html', 
                              players=[], 
                              factions=['梵天', '比湿奴', '湿婆'], 
                              current_faction=faction)


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