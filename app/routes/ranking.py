#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
排行榜路由模块
"""

from flask import Blueprint, render_template, jsonify, request, current_app
from sqlalchemy.exc import SQLAlchemyError
from app.services.scraper_service import ScraperService
from app.models.ranking import Ranking
from app.utils.logger import get_logger
from app.utils.decorators import login_required
from app.utils.jwt_auth import token_required
import datetime

logger = get_logger()

# 创建蓝图
ranking_bp = Blueprint('ranking', __name__, url_prefix='/ranking')

@ranking_bp.route('/', methods=['GET'])
@login_required
def index():
    """排行榜页面"""
    try:
        logger.info("访问排行榜页面")
        return render_template('ranking/index.html')
    except Exception as e:
        logger.error(f"访问排行榜页面时出错: {str(e)}", exc_info=True)
        return render_template('error.html', message="加载排行榜页面时出错")

@ranking_bp.route('/data', methods=['GET'])
def get_ranking_data():
    """获取排行榜数据API"""
    try:
        logger.info("请求获取排行榜数据")
        
        # 获取请求参数
        category = request.args.get('category', '主神排行榜')
        force_refresh = request.args.get('refresh', 'false').lower() == 'true'
        
        logger.info(f"数据请求参数: 分类={category}, 强制刷新={force_refresh}")
        
        # 优先从数据库获取最新数据
        if not force_refresh:
            latest_ranking = Ranking.get_latest_by_category(category)
            
            if latest_ranking:
                # 检查数据是否最近更新过（24小时内）
                now = datetime.datetime.now()
                update_time = latest_ranking.update_time
                
                if isinstance(update_time, str):
                    try:
                        # 尝试解析日期字符串
                        if len(update_time) <= 10:  # 只有日期部分 (YYYY-MM-DD)
                            update_time = datetime.datetime.strptime(update_time, "%Y-%m-%d")
                        else:  # 带有时间部分 (YYYY-MM-DD HH:MM:SS)
                            update_time = datetime.datetime.strptime(update_time, "%Y-%m-%d %H:%M:%S")
                    except ValueError:
                        logger.warning(f"无法解析日期字符串: {update_time}，将其视为过期")
                        update_time = now - datetime.timedelta(days=2)  # 将其视为过期
                
                if isinstance(update_time, datetime.datetime):
                    time_diff = now - update_time
                    
                    # 如果数据更新时间在24小时内，直接返回
                    if time_diff.total_seconds() < 24 * 3600:
                        logger.info(f"返回缓存的排行榜数据，最后更新时间: {update_time}")
                        return jsonify(latest_ranking.ranking_data_dict)
                    else:
                        logger.info(f"缓存数据已过期({time_diff.total_seconds() / 3600:.1f}小时)，将刷新数据")
                else:
                    logger.warning(f"数据库中的更新时间格式无效: {update_time}，将刷新数据")
            else:
                logger.info("数据库中没有该类别的排行榜数据，将抓取最新数据")
        else:
            logger.info("强制刷新参数已设置，将抓取最新数据")
        
        # 从网络抓取最新数据
        url = current_app.config.get('RANKING_URL', 'http://bbs.3gsc.com.cn/misc/gsm20/data/paiming.htm')
        
        # 使用requests抓取数据
        logger.info(f"使用requests抓取数据: {url}")
        data = ScraperService.scrape_ranking_data(url)
        
        # 保存到数据库
        try:
            # 设置分类
            data['category'] = category
            
            # 创建新的排行榜记录
            new_ranking = Ranking.create(
                category=category,
                source_url=url,
                ranking_data=data
            )
            
            if new_ranking:
                logger.info(f"成功保存排行榜数据，ID: {new_ranking.id}")
            else:
                logger.error("保存排行榜数据失败")
                
        except Exception as e:
            logger.error(f"保存排行榜数据时出错: {str(e)}", exc_info=True)
            # 虽然保存失败，但仍然返回抓取到的数据
        
        return jsonify(data)
    
    except Exception as e:
        logger.error(f"获取排行榜数据时出错: {str(e)}", exc_info=True)
        return jsonify({
            "error": str(e),
            "category": request.args.get('category', '主神排行榜'),
            "update_time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }), 500

@ranking_bp.route('/refresh', methods=['POST'])
def refresh_ranking():
    """手动刷新排行榜数据"""
    try:
        logger.info("手动刷新排行榜数据")
        
        # 获取分类参数
        category = request.form.get('category', '主神排行榜')
        
        # 获取排行榜URL
        url = current_app.config.get('RANKING_URL', 'http://bbs.3gsc.com.cn/misc/gsm20/data/paiming.htm')
        
        # 使用requests抓取数据
        logger.info(f"使用requests抓取数据: {url}")
        data = ScraperService.scrape_ranking_data(url)
        
        # 设置分类
        data['category'] = category
        
        # 保存到数据库
        try:
            new_ranking = Ranking.create(
                category=category,
                source_url=url,
                ranking_data=data
            )
            
            if new_ranking:
                logger.info(f"成功刷新并保存排行榜数据，ID: {new_ranking.id}")
                return jsonify({
                    "status": "success",
                    "message": "排行榜数据已成功刷新",
                    "ranking_id": new_ranking.id,
                    "data": data
                })
            else:
                logger.error("刷新排行榜数据失败：无法创建新记录")
                return jsonify({
                    "status": "error",
                    "message": "无法创建新的排行榜记录",
                    "data": data
                }), 500
                
        except Exception as e:
            logger.error(f"保存刷新的排行榜数据时出错: {str(e)}", exc_info=True)
            return jsonify({
                "status": "error",
                "message": f"保存数据时出错: {str(e)}",
                "data": data
            }), 500
    
    except Exception as e:
        logger.error(f"刷新排行榜数据时出错: {str(e)}", exc_info=True)
        return jsonify({
            "status": "error",
            "message": f"刷新数据时出错: {str(e)}"
        }), 500

@ranking_bp.route('/history', methods=['GET'])
def get_ranking_history():
    """获取排行榜历史数据"""
    try:
        logger.info("请求获取排行榜历史数据")
        
        # 获取参数
        category = request.args.get('category', '主神排行榜')
        limit = int(request.args.get('limit', 10))
        
        # 限制最大查询数量
        if limit > 100:
            limit = 100
            
        logger.info(f"历史数据请求参数: 分类={category}, 数量限制={limit}")
        
        # 获取历史数据
        history_list = Ranking.get_history(category, limit)
        
        if not history_list:
            logger.warning(f"未找到'{category}'分类的历史数据")
            return jsonify({
                "status": "error", 
                "message": f"未找到'{category}'分类的历史数据",
                "data": []
            })
        
        # 构建响应数据
        history_data = []
        for record in history_list:
            try:
                history_data.append({
                    "id": record.id,
                    "category": record.category,
                    "update_time": record.update_time,
                    "create_time": record.create_time,
                    "data": record.ranking_data_dict
                })
            except Exception as e:
                logger.error(f"处理排行榜历史记录时出错 (ID: {record.id}): {str(e)}")
                # 继续处理下一条记录
        
        logger.info(f"成功获取排行榜历史数据，共{len(history_data)}条记录")
        return jsonify({
            "status": "success",
            "message": f"成功获取'{category}'分类的历史数据",
            "data": history_data
        })
    
    except Exception as e:
        logger.error(f"获取排行榜历史数据时出错: {str(e)}", exc_info=True)
        return jsonify({
            "status": "error",
            "message": f"获取历史数据时出错: {str(e)}"
        }), 500

# ==================== 移动端 API 接口 ====================

@ranking_bp.route('/api/data', methods=['GET'])
@token_required
def api_get_ranking_data():
    """API 获取排行榜数据"""
    try:
        logger.info("API 请求获取排行榜数据")
        
        # 获取请求参数
        category = request.args.get('category', '主神排行榜')
        force_refresh = request.args.get('refresh', 'false').lower() == 'true'
        
        logger.info(f"API 数据请求参数: 分类={category}, 强制刷新={force_refresh}")
        
        # 优先从数据库获取最新数据
        if not force_refresh:
            latest_ranking = Ranking.get_latest_by_category(category)
            
            if latest_ranking:
                # 检查数据是否最近更新过（24小时内）
                now = datetime.datetime.now()
                update_time = latest_ranking.update_time
                
                if isinstance(update_time, str):
                    try:
                        if len(update_time) <= 10:
                            update_time = datetime.datetime.strptime(update_time, "%Y-%m-%d")
                        else:
                            update_time = datetime.datetime.strptime(update_time, "%Y-%m-%d %H:%M:%S")
                    except ValueError:
                        logger.warning(f"无法解析日期字符串: {update_time}")
                        update_time = now - datetime.timedelta(days=2)
                
                if isinstance(update_time, datetime.datetime):
                    time_diff = now - update_time
                    
                    if time_diff.total_seconds() < 24 * 3600:
                        logger.info(f"API 返回缓存的排行榜数据，最后更新时间: {update_time}")
                        return jsonify({
                            'status': 'success',
                            'message': '获取排行榜数据成功',
                            'data': latest_ranking.ranking_data_dict
                        }), 200
        
        # 从网络抓取最新数据
        url = current_app.config.get('RANKING_URL', 'http://bbs.3gsc.com.cn/misc/gsm20/data/paiming.htm')
        
        logger.info(f"API 使用requests抓取数据: {url}")
        data = ScraperService.scrape_ranking_data(url)
        
        # 保存到数据库
        try:
            data['category'] = category
            
            new_ranking = Ranking.create(
                category=category,
                source_url=url,
                ranking_data=data
            )
            
            if new_ranking:
                logger.info(f"API 成功保存排行榜数据，ID: {new_ranking.id}")
                
        except Exception as e:
            logger.error(f"API 保存排行榜数据时出错: {str(e)}", exc_info=True)
        
        return jsonify({
            'status': 'success',
            'message': '获取排行榜数据成功',
            'data': data
        }), 200
    
    except Exception as e:
        logger.error(f"API 获取排行榜数据时出错: {str(e)}", exc_info=True)
        return jsonify({
            'status': 'error',
            'message': f'获取排行榜数据失败: {str(e)}'
        }), 500

@ranking_bp.route('/api/refresh', methods=['POST'])
@token_required
def api_refresh_ranking():
    """API 手动刷新排行榜数据"""
    try:
        logger.info("API 手动刷新排行榜数据")
        
        # 获取分类参数
        data = request.get_json() or {}
        category = data.get('category', '主神排行榜')
        
        # 获取排行榜URL
        url = current_app.config.get('RANKING_URL', 'http://bbs.3gsc.com.cn/misc/gsm20/data/paiming.htm')
        
        logger.info(f"API 使用requests抓取数据: {url}")
        ranking_data = ScraperService.scrape_ranking_data(url)
        
        ranking_data['category'] = category
        
        # 保存到数据库
        try:
            new_ranking = Ranking.create(
                category=category,
                source_url=url,
                ranking_data=ranking_data
            )
            
            if new_ranking:
                logger.info(f"API 成功刷新并保存排行榜数据，ID: {new_ranking.id}")
                return jsonify({
                    'status': 'success',
                    'message': '排行榜数据已成功刷新',
                    'data': {
                        'ranking_id': new_ranking.id,
                        'ranking_data': ranking_data
                    }
                }), 200
            else:
                logger.error("API 刷新排行榜数据失败：无法创建新记录")
                return jsonify({
                    'status': 'error',
                    'message': '无法创建新的排行榜记录',
                    'data': ranking_data
                }), 500
                
        except Exception as e:
            logger.error(f"API 保存刷新的排行榜数据时出错: {str(e)}", exc_info=True)
            return jsonify({
                'status': 'error',
                'message': f'保存数据时出错: {str(e)}',
                'data': ranking_data
            }), 500
    
    except Exception as e:
        logger.error(f"API 刷新排行榜数据时出错: {str(e)}", exc_info=True)
        return jsonify({
            'status': 'error',
            'message': f'刷新数据时出错: {str(e)}'
        }), 500

@ranking_bp.route('/api/history', methods=['GET'])
@token_required
def api_get_ranking_history():
    """API 获取排行榜历史数据"""
    try:
        logger.info("API 请求获取排行榜历史数据")
        
        # 获取参数
        category = request.args.get('category', '主神排行榜')
        limit = int(request.args.get('limit', 10))
        
        # 限制最大查询数量
        if limit > 100:
            limit = 100
            
        logger.info(f"API 历史数据请求参数: 分类={category}, 数量限制={limit}")
        
        # 获取历史数据
        history_list = Ranking.get_history(category, limit)
        
        if not history_list:
            logger.warning(f"API 未找到'{category}'分类的历史数据")
            return jsonify({
                'status': 'error', 
                'message': f"未找到'{category}'分类的历史数据",
                'data': []
            }), 404
        
        # 构建响应数据
        history_data = []
        for record in history_list:
            try:
                history_data.append({
                    'id': record.id,
                    'category': record.category,
                    'update_time': record.update_time,
                    'create_time': record.create_time,
                    'data': record.ranking_data_dict
                })
            except Exception as e:
                logger.error(f"API 处理排行榜历史记录时出错 (ID: {record.id}): {str(e)}")
        
        logger.info(f"API 成功获取排行榜历史数据，共{len(history_data)}条记录")
        return jsonify({
            'status': 'success',
            'message': f"成功获取'{category}'分类的历史数据",
            'data': history_data
        }), 200
    
    except Exception as e:
        logger.error(f"API 获取排行榜历史数据时出错: {str(e)}", exc_info=True)
        return jsonify({
            'status': 'error',
            'message': f'获取历史数据时出错: {str(e)}'
        }), 500 