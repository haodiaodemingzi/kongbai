#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
爬虫服务 - 用于抓取网页数据
"""

import re
import json
import logging
import datetime
import requests
from bs4 import BeautifulSoup
from app.utils.logger import get_logger

logger = get_logger()

class ScraperService:
    """抓取网页数据的服务类"""
    
    @staticmethod
    def scrape_ranking_data(url):
        """
        使用requests抓取排行榜数据
        
        Args:
            url: 要抓取的URL
            
        Returns:
            dict: 解析后的排行榜数据
        """
        try:
            logger.info(f"开始使用requests抓取排行榜数据: {url}")
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1',
                'Cache-Control': 'max-age=0'
            }
            
            response = requests.get(url, headers=headers, timeout=30)
            
            # 尝试多种编码
            encodings = ['gbk', 'gb2312', 'utf-8']
            content = None
            
            for encoding in encodings:
                try:
                    response.encoding = encoding
                    content = response.text
                    if content and ('排名' in content or '排行' in content):
                        logger.info(f"成功使用编码 {encoding} 解析页面")
                        break
                except Exception as e:
                    logger.warning(f"使用编码 {encoding} 解析页面失败: {e}")
            
            if not content:
                logger.error("无法解析页面内容")
                return {
                    "category": "主神排行榜",
                    "update_time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "error_info": "无法解析页面内容",
                    "brahma_players": [],
                    "vishnu_players": [],
                    "shiva_players": []
                }
            
            logger.info(f"成功获取页面内容，内容长度: {len(content)}")
            
            if response.status_code == 200:
                return ScraperService._parse_content(content)
            else:
                logger.error(f"抓取排行榜失败，状态码: {response.status_code}")
                return {
                    "category": "主神排行榜",
                    "update_time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "error_info": f"抓取失败，状态码: {response.status_code}",
                    "brahma_players": [],
                    "vishnu_players": [],
                    "shiva_players": []
                }
        except Exception as e:
            logger.error(f"抓取排行榜数据时出错: {str(e)}", exc_info=True)
            return {
                "category": "主神排行榜",
                "update_time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "error_info": str(e),
                "brahma_players": [],
                "vishnu_players": [],
                "shiva_players": []
            }
    
    @staticmethod
    def _parse_content(content):
        """
        解析HTML内容，提取排行榜数据
        
        Args:
            content: HTML内容
            
        Returns:
            dict: 解析后的排行榜数据
        """
        try:
            logger.info(f"开始解析HTML内容，内容长度: {len(content)}")
            soup = BeautifulSoup(content, 'html.parser')
            
            # 获取更新时间
            update_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            update_time_match = re.search(r'(\d{4})年(\d{2})月(\d{2})日', content)
            if update_time_match:
                y, m, d = update_time_match.groups()
                logger.info(f"找到更新时间信息: {y}年{m}月{d}日")
                update_time = f"{y}-{m}-{d}"
            else:
                logger.warning("未找到页面中的更新时间信息，使用当前时间")
            
            # 初始化三个门派的玩家数据列表
            brahma_players = []  # 梵天 (1)
            vishnu_players = []  # 比湿奴 (2)
            shiva_players = []   # 湿婆 (4)
            
            # 查找表格内容
            tables = soup.select("table")
            logger.info(f"页面中找到 {len(tables)} 个表格")
            
            # 遍历所有表格，寻找包含排名数据的表格
            for table_idx, table in enumerate(tables):
                table_rows = table.select("tr")
                logger.info(f"表格 #{table_idx+1} 包含 {len(table_rows)} 行")
                
                # 遍历所有表格行，寻找包含玩家排名数据的行
                for row_idx, row in enumerate(table_rows):
                    tds = row.select("td")
                    if len(tds) >= 3:  # 至少有3列的行可能包含排名数据
                        for i, td in enumerate(tds):
                            text = td.get_text(strip=True)
                            
                            # 使用正则表达式匹配排名格式
                            match = re.match(r'^([124])\s+(\d+)\s+(.+)$', text)
                            if match:
                                faction_id = match.group(1)
                                rank = match.group(2)
                                name = match.group(3).strip()
                                
                                player_data = {
                                    "rank": rank,
                                    "name": name
                                }
                                
                                if faction_id == "1":  # 梵天
                                    brahma_players.append(player_data)
                                elif faction_id == "2":  # 比湿奴
                                    vishnu_players.append(player_data)
                                elif faction_id == "4":  # 湿婆
                                    shiva_players.append(player_data)
            
            logger.info(f"第一次解析找到: 梵天{len(brahma_players)}名，比湿奴{len(vishnu_players)}名，湿婆{len(shiva_players)}名")
            
            # 如果上面的方法没有找到数据，尝试另一种查找方式
            if not brahma_players and not vishnu_players and not shiva_players:
                logger.info("使用备用方法解析排行榜数据")
                
                # 按照颜色分类查找三列数据
                brahma_cells = soup.select("td[style*='color: rgb(151, 72, 7)'], td[style*='color:#974807']")
                vishnu_cells = soup.select("td[style*='color: red'], td[style*='color:red']")
                shiva_cells = soup.select("td[style*='color: rgb(0, 32, 96)'], td[style*='color:#002060']")
                
                logger.info(f"找到颜色单元格: 梵天{len(brahma_cells)}个，比湿奴{len(vishnu_cells)}个，湿婆{len(shiva_cells)}个")
                
                # 解析梵天玩家
                for cell in brahma_cells:
                    text = cell.get_text(strip=True)
                    match = re.match(r'^1\s+(\d+)\s+(.+)$', text)
                    if match:
                        brahma_players.append({
                            "rank": match.group(1),
                            "name": match.group(2).strip()
                        })
                
                # 解析比湿奴玩家
                for cell in vishnu_cells:
                    text = cell.get_text(strip=True)
                    match = re.match(r'^2\s+(\d+)\s+(.+)$', text)
                    if match:
                        vishnu_players.append({
                            "rank": match.group(1),
                            "name": match.group(2).strip()
                        })
                
                # 解析湿婆玩家
                for cell in shiva_cells:
                    text = cell.get_text(strip=True)
                    match = re.match(r'^4\s+(\d+)\s+(.+)$', text)
                    if match:
                        shiva_players.append({
                            "rank": match.group(1),
                            "name": match.group(2).strip()
                        })
                        
                logger.info(f"第二次解析找到: 梵天{len(brahma_players)}名，比湿奴{len(vishnu_players)}名，湿婆{len(shiva_players)}名")
                
            # 如果仍然没有解析到数据，尝试第三种方法
            if not brahma_players and not vishnu_players and not shiva_players:
                logger.info("使用第三种方法解析排行榜数据")
                
                # 使用更加宽松的查找条件
                all_tds = soup.select("td")
                logger.info(f"页面中找到 {len(all_tds)} 个单元格，尝试解析")
                
                for td in all_tds:
                    text = td.get_text(strip=True)
                    
                    # 匹配任何可能的排名格式
                    brahma_match = re.match(r'^1[\s\.]+(\d+)[\s\.]+(.+)$', text)
                    vishnu_match = re.match(r'^2[\s\.]+(\d+)[\s\.]+(.+)$', text)
                    shiva_match = re.match(r'^4[\s\.]+(\d+)[\s\.]+(.+)$', text)
                    
                    if brahma_match:
                        brahma_players.append({
                            "rank": brahma_match.group(1),
                            "name": brahma_match.group(2).strip()
                        })
                    elif vishnu_match:
                        vishnu_players.append({
                            "rank": vishnu_match.group(1),
                            "name": vishnu_match.group(2).strip()
                        })
                    elif shiva_match:
                        shiva_players.append({
                            "rank": shiva_match.group(1),
                            "name": shiva_match.group(2).strip()
                        })
                
                logger.info(f"第三次解析找到: 梵天{len(brahma_players)}名，比湿奴{len(vishnu_players)}名，湿婆{len(shiva_players)}名")
                
            # 如果还是没有解析到数据，尝试第四种方法 - 提取所有可能看起来像排名的数据
            if not brahma_players and not vishnu_players and not shiva_players:
                logger.info("使用第四种方法解析排行榜数据（强制提取）")
                
                # 收集所有的文本内容
                all_text = soup.get_text()
                
                # 尝试使用更宽松的正则表达式提取数据
                brahma_matches = re.findall(r'梵天.*?(\d+)[^\d]+([^123456789\s][^\n\r]*)', all_text)
                vishnu_matches = re.findall(r'比湿奴.*?(\d+)[^\d]+([^123456789\s][^\n\r]*)', all_text)
                shiva_matches = re.findall(r'湿婆.*?(\d+)[^\d]+([^123456789\s][^\n\r]*)', all_text)
                
                # 创建玩家数据
                for rank, name in brahma_matches:
                    brahma_players.append({
                        "rank": rank.strip(),
                        "name": name.strip()
                    })
                
                for rank, name in vishnu_matches:
                    vishnu_players.append({
                        "rank": rank.strip(),
                        "name": name.strip()
                    })
                
                for rank, name in shiva_matches:
                    shiva_players.append({
                        "rank": rank.strip(),
                        "name": name.strip()
                    })
                
                logger.info(f"第四次解析找到: 梵天{len(brahma_players)}名，比湿奴{len(vishnu_players)}名，湿婆{len(shiva_players)}名")
                        
            # 返回结构化数据
            result = {
                "category": "主神排行榜",
                "update_time": update_time,
                "brahma_players": brahma_players,
                "vishnu_players": vishnu_players,
                "shiva_players": shiva_players,
                "source": "requests"
            }
            
            # 添加总结数据
            total_players = len(brahma_players) + len(vishnu_players) + len(shiva_players)
            if total_players > 0:
                logger.info(f"成功解析排行榜数据，共找到{total_players}名玩家 - 梵天{len(brahma_players)}名，比湿奴{len(vishnu_players)}名，湿婆{len(shiva_players)}名")
                return result
            else:
                logger.warning("未能解析到任何排行榜数据")
                
                # 记录页面源码的一部分用于调试
                logger.debug(f"页面部分内容: {content[:500]}...{content[-500:] if len(content) > 1000 else ''}")
                
                return {
                    "category": "主神排行榜",
                    "update_time": update_time,
                    "error_info": "未能解析到任何排行榜数据",
                    "brahma_players": [],
                    "vishnu_players": [],
                    "shiva_players": [],
                    "source": "requests"
                }
            
        except Exception as e:
            logger.error(f"解析排行榜数据时出错: {str(e)}", exc_info=True)
            return {
                "category": "主神排行榜",
                "update_time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "error_info": str(e),
                "brahma_players": [],
                "vishnu_players": [],
                "shiva_players": [],
                "source": "requests"
            }
    
    @staticmethod
    def scrape_with_requests(url):
        """
        使用requests库抓取页面（与scrape_ranking_data相同，保留此方法以兼容现有代码）
        
        Args:
            url: 要抓取的URL
            
        Returns:
            dict: 解析后的排行榜数据
        """
        return ScraperService.scrape_ranking_data(url) 