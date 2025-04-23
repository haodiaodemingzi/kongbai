#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
导入虎威密传排行榜样例数据
根据提供的排行榜图片数据
"""

import sys
import os
import json
from datetime import datetime
from app import create_app
from app.models.rankings import Rankings
from app.utils.logger import get_logger

logger = get_logger()
app = create_app()

# 根据排行榜图片生成的示例数据
SAMPLE_RANKINGS_DATA = {
    "category": "虎威主神排行榜",
    "update_time": "2025年02月18日",
    "players": [
        # 梵天
        {"rank": 1, "name": "白素贞", "god": "梵天"},
        {"rank": 2, "name": "∽小红绳", "god": "梵天"},
        {"rank": 3, "name": "悟爱", "god": "梵天"},
        {"rank": 4, "name": "曲终人散_10", "god": "梵天"},
        {"rank": 5, "name": "天若有情天又老", "god": "梵天"},
        {"rank": 6, "name": "紫の鳝", "god": "梵天"},
        {"rank": 7, "name": "特警J", "god": "梵天"},
        {"rank": 8, "name": "雪牛战仙仙", "god": "梵天"},
        {"rank": 9, "name": "quanwang", "god": "梵天"},
        {"rank": 10, "name": "◆祐见◆肘ℂ", "god": "梵天"},
        {"rank": 11, "name": "天堤有情天义老", "god": "梵天"},
        {"rank": 12, "name": "96166", "god": "梵天"},
        {"rank": 13, "name": "小爷头版头条", "god": "梵天"},
        {"rank": 14, "name": "丑黑雨丫", "god": "梵天"},
        {"rank": 15, "name": "PPA521", "god": "梵天"},
        {"rank": 16, "name": "笔歌有独幽", "god": "梵天"},
        {"rank": 17, "name": "z中华龙", "god": "梵天"},
        {"rank": 18, "name": "Only●飞鸡", "god": "梵天"},
        {"rank": 19, "name": "秋雨", "god": "梵天"},
        {"rank": 20, "name": "提提奶", "god": "梵天"},
        {"rank": 21, "name": "隐月天", "god": "梵天"},
        {"rank": 22, "name": "来也", "god": "梵天"},
        {"rank": 23, "name": "十里✘清风", "god": "梵天"},
        {"rank": 24, "name": "问剑孤鸣", "god": "梵天"},
        {"rank": 25, "name": "ブブ小器パパ19H", "god": "梵天"},
        {"rank": 26, "name": "惜灵素语", "god": "梵天"},
        {"rank": 27, "name": "叶青霜", "god": "梵天"},
        {"rank": 28, "name": "相思只因恋红杏", "god": "梵天"},
        {"rank": 29, "name": "再骧江姮", "god": "梵天"},

        # 比湿奴
        {"rank": 1, "name": "将臣", "god": "比湿奴"},
        {"rank": 2, "name": "薇风", "god": "比湿奴"},
        {"rank": 3, "name": "Angel✘焦熏", "god": "比湿奴"},
        {"rank": 4, "name": "lacer", "god": "比湿奴"},
        {"rank": 5, "name": "avax", "god": "比湿奴"},
        {"rank": 6, "name": "青帝法师", "god": "比湿奴"},
        {"rank": 7, "name": "胜利", "god": "比湿奴"},
        {"rank": 8, "name": "五星密林迷火", "god": "比湿奴"},
        {"rank": 9, "name": "香蕉个巴拉", "god": "比湿奴"},
        {"rank": 10, "name": "0o心之所向o0", "god": "比湿奴"},
        {"rank": 11, "name": "我是✘唯学军", "god": "比湿奴"},
        {"rank": 12, "name": "伊人问花语", "god": "比湿奴"},
        {"rank": 13, "name": "宛若不系之舟", "god": "比湿奴"},
        {"rank": 14, "name": "一把火烧瓜你", "god": "比湿奴"},
        {"rank": 15, "name": "恼J城恋$", "god": "比湿奴"},
        {"rank": 16, "name": "夕颜为谁舞", "god": "比湿奴"},
        {"rank": 17, "name": "【纽扣杀手】", "god": "比湿奴"},
        {"rank": 18, "name": "ZH虎嘿狂力", "god": "比湿奴"},
        {"rank": 19, "name": "时光ど流逝", "god": "比湿奴"},
        {"rank": 20, "name": "肉博士", "god": "比湿奴"},
        {"rank": 21, "name": "问花解语", "god": "比湿奴"},
        {"rank": 22, "name": "~张伟丽~", "god": "比湿奴"},
        {"rank": 23, "name": "守护时光守护你", "god": "比湿奴"},
        {"rank": 24, "name": "周bufu", "god": "比湿奴"},
        {"rank": 25, "name": "薇っ风", "god": "比湿奴"},
        {"rank": 26, "name": "fddfgdfh", "god": "比湿奴"},
        {"rank": 27, "name": "Quamx", "god": "比湿奴"},
        {"rank": 28, "name": "色彩斑斓", "god": "比湿奴"},
        {"rank": 29, "name": "一路走一路溜", "god": "比湿奴"},

        # 湿婆
        {"rank": 1, "name": "龙小小", "god": "湿婆"},
        {"rank": 2, "name": "醉人梦绕沁心逝去", "god": "湿婆"},
        {"rank": 3, "name": "好弹", "god": "湿婆"},
        {"rank": 4, "name": "水之灵灵", "god": "湿婆"},
        {"rank": 5, "name": "情非得已321", "god": "湿婆"},
        {"rank": 6, "name": "lostinfall", "god": "湿婆"},
        {"rank": 7, "name": "泳者", "god": "湿婆"},
        {"rank": 8, "name": "帅气✘被龙壤", "god": "湿婆"},
        {"rank": 9, "name": "谁这么∽牛逼", "god": "湿婆"},
        {"rank": 10, "name": "定风波", "god": "湿婆"},
        {"rank": 11, "name": "0ॐ ma瑞亚", "god": "湿婆"},
        {"rank": 12, "name": "随意飘荡", "god": "湿婆"},
        {"rank": 13, "name": "べ亦✘公子", "god": "湿婆"},
        {"rank": 14, "name": "逝水中天涯", "god": "湿婆"},
        {"rank": 15, "name": "『青棋』浮梦』", "god": "湿婆"},
        {"rank": 16, "name": "宸是ℂ捅有", "god": "湿婆"},
        {"rank": 17, "name": "乔纳森", "god": "湿婆"},
        {"rank": 18, "name": "绚烂神兽", "god": "湿婆"},
        {"rank": 19, "name": "_happy_", "god": "湿婆"},
        {"rank": 20, "name": "月下映唱", "god": "湿婆"},
        {"rank": 21, "name": "一人独身_,,天涯", "god": "湿婆"},
        {"rank": 22, "name": "女泳幻舞", "god": "湿婆"},
        {"rank": 23, "name": "陌上烟云✘心凉", "god": "湿婆"},
        {"rank": 24, "name": "o幻魂o使者", "god": "湿婆"},
        {"rank": 25, "name": "夕辉生梦死☆", "god": "湿婆"},
        {"rank": 26, "name": "养肥肥1", "god": "湿婆"},
        {"rank": 27, "name": "※宝宝爱姐姐※", "god": "湿婆"},
        {"rank": 28, "name": "№轻鸿一点№", "god": "湿婆"},
        {"rank": 29, "name": "湘江水逝楚云飞", "god": "湿婆"}
    ]
}

def import_sample_data():
    """
    导入示例排行榜数据
    """
    with app.app_context():
        try:
            # 检查是否已存在相同类别的数据
            existing = Rankings.query.filter_by(category=SAMPLE_RANKINGS_DATA['category']).first()
            if existing:
                logger.info(f"类别 '{SAMPLE_RANKINGS_DATA['category']}' 的排行榜数据已存在，将更新")
            
            # 创建或更新排行榜数据
            ranking = Rankings.create_or_update(
                category=SAMPLE_RANKINGS_DATA['category'],
                players_data=SAMPLE_RANKINGS_DATA['players'],
                update_time=SAMPLE_RANKINGS_DATA['update_time']
            )
            
            logger.info(f"已成功导入样例排行榜数据: ID={ranking.id}")
            return True
            
        except Exception as e:
            logger.error(f"导入样例排行榜数据时出错: {str(e)}")
            return False

if __name__ == "__main__":
    print("开始导入虎威密传排行榜样例数据...")
    success = import_sample_data()
    
    if success:
        print("样例排行榜数据已成功导入！")
    else:
        print("导入样例排行榜数据失败，请查看日志获取详细信息。")
        sys.exit(1) 