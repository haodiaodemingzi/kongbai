#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
排行榜数据模型
"""

import datetime
import json
import logging
from sqlalchemy import Column, Integer, String, DateTime, Text, desc
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()
logger = logging.getLogger(__name__)

class Ranking(Base):
    """排行榜数据模型"""
    __tablename__ = 'rankings'

    id = Column(Integer, primary_key=True, autoincrement=True)
    category = Column(String(50), nullable=False, comment='排行榜类别')
    source_url = Column(String(255), nullable=False, comment='数据来源URL')
    update_time = Column(DateTime, default=datetime.datetime.now, comment='数据更新时间')
    create_time = Column(DateTime, default=datetime.datetime.now, comment='记录创建时间')
    ranking_data = Column(Text, nullable=False, comment='排行榜数据JSON')

    def __init__(self, category, source_url, ranking_data):
        """
        初始化排行榜数据模型
        
        Args:
            category (str): 排行榜类别
            source_url (str): 数据来源URL
            ranking_data (dict): 排行榜数据字典
        """
        self.category = category
        self.source_url = source_url
        
        # 确保ranking_data是字典类型，并转为JSON字符串
        if isinstance(ranking_data, dict):
            self.ranking_data = json.dumps(ranking_data, ensure_ascii=False)
        else:
            # 如果不是字典，尝试将其解析为字典
            try:
                json_data = json.loads(ranking_data) if isinstance(ranking_data, str) else ranking_data
                self.ranking_data = json.dumps(json_data, ensure_ascii=False)
            except (TypeError, json.JSONDecodeError) as e:
                logger.error(f"排行榜数据格式不正确: {e}")
                self.ranking_data = json.dumps({"error": "数据格式不正确"}, ensure_ascii=False)
        
        # 如果数据中有更新时间，使用数据中的更新时间
        if isinstance(ranking_data, dict) and 'update_time' in ranking_data:
            try:
                # 尝试解析数据中的更新时间字符串
                update_time_str = ranking_data['update_time']
                # 检查更新时间格式
                if ' ' in update_time_str:  # 包含时间部分
                    self.update_time = datetime.datetime.strptime(
                        update_time_str, 
                        '%Y-%m-%d %H:%M:%S'
                    )
                else:  # 只有日期部分
                    self.update_time = datetime.datetime.strptime(
                        update_time_str, 
                        '%Y-%m-%d'
                    )
            except (ValueError, TypeError) as e:
                # 如果解析失败，使用当前时间
                logger.warning(f"更新时间格式解析失败: {e}, 使用当前时间")
                self.update_time = datetime.datetime.now()
        else:
            self.update_time = datetime.datetime.now()

    @property
    def ranking_data_dict(self):
        """获取排行榜数据字典"""
        try:
            if not self.ranking_data:
                logger.warning("排行榜数据为空")
                return {}
            
            # 尝试解析JSON字符串为字典
            data = json.loads(self.ranking_data)
            logger.debug(f"成功解析排行榜数据，类别: {self.category}")
            return data
        except json.JSONDecodeError as e:
            logger.error(f"解析排行榜数据失败: {e}, 原始数据: {self.ranking_data[:100]}...")
            return {
                "error": "数据解析失败",
                "category": self.category,
                "update_time": self.update_time.strftime('%Y-%m-%d %H:%M:%S')
            }
        except Exception as e:
            logger.error(f"获取排行榜数据时发生未知错误: {e}")
            return {
                "error": f"获取数据时发生错误: {str(e)}",
                "category": self.category,
                "update_time": self.update_time.strftime('%Y-%m-%d %H:%M:%S')
            }

    @staticmethod
    def create(session, category, source_url, ranking_data):
        """
        创建新的排行榜数据记录
        
        Args:
            session: 数据库会话
            category (str): 排行榜类别
            source_url (str): 数据来源URL
            ranking_data (dict): 排行榜数据字典
            
        Returns:
            Ranking: 创建的排行榜数据模型实例
        """
        try:
            ranking = Ranking(category, source_url, ranking_data)
            session.add(ranking)
            session.commit()
            logger.info(f"成功创建排行榜数据，ID: {ranking.id}, 类别: {category}")
            return ranking
        except Exception as e:
            session.rollback()
            logger.error(f"创建排行榜数据失败: {e}")
            raise

    @staticmethod
    def get_latest_by_category(session, category):
        """
        获取指定类别的最新排行榜数据
        
        Args:
            session: 数据库会话
            category (str): 排行榜类别
            
        Returns:
            Ranking: 排行榜数据模型实例，如果没有找到则返回None
        """
        try:
            return session.query(Ranking)\
                .filter(Ranking.category == category)\
                .order_by(desc(Ranking.update_time))\
                .first()
        except Exception as e:
            logger.error(f"获取最新排行榜数据失败: {e}")
            return None

    @staticmethod
    def get_by_id(session, ranking_id):
        """
        根据ID获取排行榜数据
        
        Args:
            session: 数据库会话
            ranking_id (int): 排行榜数据ID
            
        Returns:
            Ranking: 排行榜数据模型实例，如果没有找到则返回None
        """
        try:
            return session.query(Ranking).filter(Ranking.id == ranking_id).first()
        except Exception as e:
            logger.error(f"根据ID获取排行榜数据失败: {e}")
            return None

    @staticmethod
    def get_history(session, category, limit=10):
        """
        获取指定类别的历史排行榜数据
        
        Args:
            session: 数据库会话
            category (str): 排行榜类别
            limit (int): 返回的记录数量限制
            
        Returns:
            list: 排行榜数据模型实例列表
        """
        try:
            return session.query(Ranking)\
                .filter(Ranking.category == category)\
                .order_by(desc(Ranking.update_time))\
                .limit(limit)\
                .all()
        except Exception as e:
            logger.error(f"获取历史排行榜数据失败: {e}")
            return []

    def __repr__(self):
        return f"<Ranking(id={self.id}, category='{self.category}', update_time='{self.update_time}')>" 