#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
网页爬虫工具，用于从外部网站抓取数据
"""

import requests
from bs4 import BeautifulSoup
import re
import json
from datetime import datetime
from app.utils.logger import get_logger

logger = get_logger()

def scrape_tantra_rankings(url="http://fqa.173mz.com/a/a.asp?b=100&id=12"):
    """
    从虎威密传网页抓取排行榜数据
    
    Args:
        url (str): 要抓取的网页URL
        
    Returns:
        dict: 包含排行榜数据的字典
    """
    try:
        logger.info(f"开始从 {url} 抓取排行榜数据")
        # 设置请求头，模拟浏览器
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        }
        
        # 发送请求获取页面内容
        response = requests.get(url, headers=headers, timeout=10)
        # 使用 GB2312 解码，因为虎威密传网站使用的是 GB2312 编码
        response.encoding = 'gbk'
        
        if response.status_code != 200:
            logger.error(f"请求失败，状态码: {response.status_code}")
            return {"error": f"请求失败，状态码: {response.status_code}"}
        
        # 使用Beautiful Soup解析HTML
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 提取更新时间
        update_time = None
        content_text = soup.get_text()
        
        # 尝试多种更新时间格式
        time_patterns = [
            r'\[(\d{4})年式版\]',  # [2025年式版]
            r'更新时间[：:]\s*(\d{4}年\d{2}月\d{2}日)',  # 更新时间: 2025年02月18日
            r'(\d{4}[\-/年]\d{1,2}[\-/月]\d{1,2}[日]?)'  # 2025年02月18日 或 2025-02-18
        ]
        
        update_time = None
        if not update_time:
            update_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        # 尝试提取各神的排名数据
        players_data = []
        
        # === 方法1: 查找表格格式 ===
        # 查找所有表格
        tables = soup.find_all('table')
        
        # === 方法2: 查找特定文本格式 ===
        if not players_data:
            text_blocks = soup.get_text().split('\n')
            for line in text_blocks:
                line = line.strip()
                # 尝试匹配图片中的格式，如 "1 1 白素贞" 或 "2 1 将臣"
                match = re.match(r'^\s*(\d+)\s+(\d+)\s+(.+)$', line)
                if match:
                    god_index, rank, player_name = match.groups()
                    # 根据 god_index 确定对应的神
                    if god_index == '1':
                        god = "梵天"
                    elif god_index == '2':
                        god = "比湿奴"
                    elif god_index == '4':
                        god = "湿婆"
                    else:
                        god = "未知"
                    
                    players_data.append({
                        "rank": int(rank),
                        "name": player_name.strip(),
                        "god": god
                    })
        

        
        # 将梵天、比湿奴、湿婆的数据分开
        brahma_players = [p for p in players_data if p['god'] == "梵天"]
        vishnu_players = [p for p in players_data if p['god'] == "比湿奴"]
        shiva_players = [p for p in players_data if p['god'] == "湿婆"]
        
        # 创建结果数据
        result = {
            "update_time": update_time,
            "brahma_players": brahma_players,
            "vishnu_players": vishnu_players,
            "shiva_players": shiva_players,
            "all_players": players_data
        }
        
        logger.info(f"成功抓取排行榜数据，共 {len(players_data)} 条记录")
        return result
    
    except Exception as e:
        logger.error(f"抓取排行榜数据时出错: {str(e)}", exc_info=True)
        
        # 出错时返回样例数据
        try:
            from import_sample_rankings import SAMPLE_RANKINGS_DATA
            return {
                "update_time": SAMPLE_RANKINGS_DATA["update_time"],
                "all_players": SAMPLE_RANKINGS_DATA["players"],
                "brahma_players": [p for p in SAMPLE_RANKINGS_DATA["players"] if p['god'] == "梵天"],
                "vishnu_players": [p for p in SAMPLE_RANKINGS_DATA["players"] if p['god'] == "比湿奴"],
                "shiva_players": [p for p in SAMPLE_RANKINGS_DATA["players"] if p['god'] == "湿婆"],
                "error_info": f"抓取数据出错，使用样例数据: {str(e)}"
            }
        except:
            return {"error": f"抓取排行榜数据时出错: {str(e)}"}

def scrape_tantra_rankings_from_image(image_url):
    """
    从图片URL抓取排行榜数据（需要OCR服务）
    
    Args:
        image_url (str): 图片的URL
        
    Returns:
        dict: 包含排行榜数据的字典
    """
    # 这个功能需要OCR服务，暂时返回一个错误信息
    logger.error("从图片抓取排行榜数据需要OCR服务，暂未实现")
    return {"error": "从图片抓取排行榜数据需要OCR服务，暂未实现"}

def get_rank_level(rank):
    """
    根据排名返回对应的级别
    
    Args:
        rank (int): 玩家排名
        
    Returns:
        str: 级别名称
    """
    try:
        rank = int(rank)
        if rank == 1:
            return "马哈拉迦 1 级"
        elif 2 <= rank <= 3:
            return "马哈拉迦 2 级"
        elif 4 <= rank <= 6:
            return "马哈拉迦 3 级"
        elif 7 <= rank <= 11:
            return "阿瓦塔尔 1 级"
        elif 12 <= rank <= 18:
            return "阿瓦塔尔 2 级"
        elif 19 <= rank <= 28:
            return "阿瓦塔尔 3 级"
        elif 29 <= rank <= 43:
            return "婆罗门 1 级"
        elif 44 <= rank <= 63:
            return "婆罗门 2 级"
        elif 64 <= rank <= 88:
            return "婆罗门 3 级"
        elif 89 <= rank <= 118:
            return "刹帝利 1 级"
        elif 119 <= rank <= 168:
            return "刹帝利 2 级"
        elif 169 <= rank <= 248:
            return "刹帝利 3 级"
        else:
            return "未知级别"
    except (ValueError, TypeError):
        return "未知级别"

def get_rankings_by_scraper(url=None, category="虎威主神排行榜"):
    """
    获取排行榜数据，优先使用爬虫，失败时返回默认数据
    
    Args:
        url (str, optional): 要抓取的网页URL
        category (str): 排行榜类别
        
    Returns:
        dict: 包含排行榜数据的字典
    """
    if not url:
        url = "http://fqa.173mz.com/a/a.asp?b=100&id=12"
    
    # 尝试抓取数据
    result = scrape_tantra_rankings(url)
    
    # 如果抓取失败，返回带有错误信息的数据
    if "error" in result:
        return {
            "category": category,
            "update_time": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            "error": result["error"],
            "players": []
        }
    
    # 从数据库获取玩家职业信息
    try:
        from app.models.player import Person
        from app import db
        
        # 获取所有玩家的名字列表
        player_names = [p["name"] for p in result["all_players"]]
        
        # 查询数据库获取这些玩家的信息
        players_in_db = Person.query.filter(Person.name.in_(player_names)).all()
        
        # 创建一个玩家名到职业的映射
        player_job_map = {p.name: p.job for p in players_in_db}
        
        # 更新爬虫返回的玩家数据，添加职业信息
        for player in result["all_players"]:
            # 添加级别信息
            player["level"] = get_rank_level(player["rank"])
            
            # 添加职业信息 - 如果数据库中存在该玩家
            player["job"] = player_job_map.get(player["name"], "未知")
            
        # 为各神分类的玩家同样添加职业和级别信息
        for player in result["brahma_players"]:
            player["level"] = get_rank_level(player["rank"])
            player["job"] = player_job_map.get(player["name"], "未知")
        
        for player in result["vishnu_players"]:
            player["level"] = get_rank_level(player["rank"])
            player["job"] = player_job_map.get(player["name"], "未知")
        
        for player in result["shiva_players"]:
            player["level"] = get_rank_level(player["rank"])
            player["job"] = player_job_map.get(player["name"], "未知")
        
        logger.info(f"成功从数据库匹配了 {len(player_job_map)} 名玩家的职业信息")
    except Exception as e:
        logger.error(f"获取玩家职业信息时出错: {str(e)}", exc_info=True)
        # 发生错误时，仍然添加级别信息但不添加职业信息
        for player in result["all_players"]:
            player["level"] = get_rank_level(player["rank"])
        
        for player in result["brahma_players"]:
            player["level"] = get_rank_level(player["rank"])
        
        for player in result["vishnu_players"]:
            player["level"] = get_rank_level(player["rank"])
        
        for player in result["shiva_players"]:
            player["level"] = get_rank_level(player["rank"])
    
    # 构建最终数据
    return {
        "category": category,
        "update_time": result["update_time"],
        "players": result["all_players"],
        "brahma_players": result["brahma_players"],
        "vishnu_players": result["vishnu_players"],
        "shiva_players": result["shiva_players"]
    } 