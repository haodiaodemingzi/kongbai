#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
排行榜数据服务
"""

import logging
import json
import traceback
import datetime
import requests
from requests.exceptions import RequestException
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright

from app.models.ranking import Ranking

logger = logging.getLogger(__name__)

class RankingService:
    """排行榜数据服务类"""

    @staticmethod
    def get_latest_ranking(session, category):
        """
        获取最新的排行榜数据
        
        Args:
            session: 数据库会话
            category (str): 排行榜类别
            
        Returns:
            dict: 排行榜数据字典，如果没有数据则返回空字典
        """
        ranking = Ranking.get_latest_by_category(session, category)
        if ranking:
            return ranking.ranking_data_dict
        return {}

    @staticmethod
    def save_ranking_data(session, category, source_url, data):
        """
        保存排行榜数据
        
        Args:
            session: 数据库会话
            category (str): 排行榜类别
            source_url (str): 数据来源URL
            data (dict): 排行榜数据字典
            
        Returns:
            Ranking: 创建的排行榜数据模型实例
        """
        try:
            # 确保data中包含更新时间
            if 'update_time' not in data:
                data['update_time'] = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                
            ranking = Ranking.create(session, category, source_url, data)
            logger.info(f"已保存排行榜数据，类别: {category}, ID: {ranking.id}")
            return ranking
        except Exception as e:
            logger.error(f"保存排行榜数据失败: {str(e)}")
            logger.error(traceback.format_exc())
            raise

    @staticmethod
    def fetch_ranking_data(url, category, use_playwright=True):
        """
        从指定URL获取排行榜数据
        
        Args:
            url (str): 数据源URL
            category (str): 排行榜类别
            use_playwright (bool): 是否使用Playwright获取数据
            
        Returns:
            dict: 解析后的排行榜数据字典
        """
        logger.info(f"开始获取排行榜数据，类别: {category}, URL: {url}")
        
        try:
            if use_playwright:
                data = RankingService._fetch_with_playwright(url, category)
            else:
                data = RankingService._fetch_with_requests(url, category)
                
            if data:
                # 添加元数据
                data['meta'] = {
                    'source_url': url,
                    'fetch_time': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    'category': category
                }
                logger.info(f"成功获取排行榜数据，类别: {category}, 数据项数: {len(data.get('items', []))}")
                return data
            else:
                logger.error(f"获取排行榜数据失败，类别: {category}, URL: {url}")
                return {}
        except Exception as e:
            logger.error(f"获取排行榜数据异常: {str(e)}")
            logger.error(traceback.format_exc())
            return {}

    @staticmethod
    def _fetch_with_playwright(url, category):
        """
        使用Playwright获取排行榜数据
        
        Args:
            url (str): 数据源URL
            category (str): 排行榜类别
            
        Returns:
            dict: 解析后的排行榜数据字典
        """
        logger.info(f"使用Playwright获取数据，类别: {category}")
        
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            
            try:
                page.goto(url, timeout=30000)
                # 等待页面加载
                page.wait_for_load_state("networkidle")
                
                # 根据不同的类别解析页面
                if category == 'github_trending':
                    return RankingService._parse_github_trending(page)
                elif category == 'hacker_news':
                    return RankingService._parse_hacker_news(page)
                # 可以添加更多类别的解析方法
                else:
                    logger.warning(f"未实现的排行榜类别解析: {category}")
                    # 返回通用的页面内容
                    return {'html': page.content(), 'items': []}
            except Exception as e:
                logger.error(f"Playwright获取数据失败: {str(e)}")
                logger.error(traceback.format_exc())
                return {}
            finally:
                browser.close()

    @staticmethod
    def _fetch_with_requests(url, category):
        """
        使用Requests获取排行榜数据
        
        Args:
            url (str): 数据源URL
            category (str): 排行榜类别
            
        Returns:
            dict: 解析后的排行榜数据字典
        """
        logger.info(f"使用Requests获取数据，类别: {category}")
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        try:
            response = requests.get(url, headers=headers, timeout=30)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # 根据不同的类别解析页面
            if category == 'github_trending':
                return RankingService._parse_github_trending_html(soup)
            elif category == 'hacker_news':
                return RankingService._parse_hacker_news_html(soup)
            # 可以添加更多类别的解析方法
            else:
                logger.warning(f"未实现的排行榜类别解析: {category}")
                # 返回通用的页面内容
                return {'html': response.text, 'items': []}
        except RequestException as e:
            logger.error(f"Requests获取数据失败: {str(e)}")
            return {}
        except Exception as e:
            logger.error(f"解析数据失败: {str(e)}")
            logger.error(traceback.format_exc())
            return {}

    @staticmethod
    def _parse_github_trending(page):
        """
        解析GitHub Trending页面
        
        Args:
            page: Playwright页面对象
            
        Returns:
            dict: 解析后的GitHub Trending数据
        """
        result = {
            'title': 'GitHub Trending',
            'update_time': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'items': []
        }
        
        # 获取所有仓库项
        repos = page.query_selector_all('article.Box-row')
        
        for i, repo in enumerate(repos):
            try:
                # 仓库名称和链接
                name_element = repo.query_selector('h2 a')
                if not name_element:
                    continue
                    
                repo_path = name_element.get_attribute('href').strip('/')
                repo_name = repo_path.split('/')[-2] + '/' + repo_path.split('/')[-1]
                repo_url = f"https://github.com/{repo_path}"
                
                # 仓库描述
                description_element = repo.query_selector('p')
                description = description_element.text_content().strip() if description_element else ""
                
                # 编程语言
                language_element = repo.query_selector('span[itemprop="programmingLanguage"]')
                language = language_element.text_content().strip() if language_element else "Unknown"
                
                # 星标数
                stars_element = repo.query_selector('a[href*="stargazers"]')
                stars = stars_element.text_content().strip() if stars_element else "0"
                
                # 今日新增星标
                stars_today_element = repo.query_selector('span.d-inline-block.float-sm-right')
                stars_today = stars_today_element.text_content().strip() if stars_today_element else "0"
                
                result['items'].append({
                    'rank': i + 1,
                    'name': repo_name,
                    'url': repo_url,
                    'description': description,
                    'language': language,
                    'stars': stars,
                    'stars_today': stars_today
                })
            except Exception as e:
                logger.error(f"解析GitHub仓库项失败: {str(e)}")
                continue
        
        return result

    @staticmethod
    def _parse_github_trending_html(soup):
        """
        使用BeautifulSoup解析GitHub Trending页面
        
        Args:
            soup: BeautifulSoup对象
            
        Returns:
            dict: 解析后的GitHub Trending数据
        """
        result = {
            'title': 'GitHub Trending',
            'update_time': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'items': []
        }
        
        # 获取所有仓库项
        repos = soup.select('article.Box-row')
        
        for i, repo in enumerate(repos):
            try:
                # 仓库名称和链接
                name_element = repo.select_one('h2 a')
                if not name_element:
                    continue
                    
                repo_path = name_element.get('href').strip('/')
                repo_name = repo_path.split('/')[-2] + '/' + repo_path.split('/')[-1]
                repo_url = f"https://github.com/{repo_path}"
                
                # 仓库描述
                description_element = repo.select_one('p')
                description = description_element.text.strip() if description_element else ""
                
                # 编程语言
                language_element = repo.select_one('span[itemprop="programmingLanguage"]')
                language = language_element.text.strip() if language_element else "Unknown"
                
                # 星标数
                stars_element = repo.select_one('a[href*="stargazers"]')
                stars = stars_element.text.strip() if stars_element else "0"
                
                # 今日新增星标
                stars_today_element = repo.select_one('span.d-inline-block.float-sm-right')
                stars_today = stars_today_element.text.strip() if stars_today_element else "0"
                
                result['items'].append({
                    'rank': i + 1,
                    'name': repo_name,
                    'url': repo_url,
                    'description': description,
                    'language': language,
                    'stars': stars,
                    'stars_today': stars_today
                })
            except Exception as e:
                logger.error(f"解析GitHub仓库项失败: {str(e)}")
                continue
        
        return result

    @staticmethod
    def _parse_hacker_news(page):
        """
        解析Hacker News页面
        
        Args:
            page: Playwright页面对象
            
        Returns:
            dict: 解析后的Hacker News数据
        """
        result = {
            'title': 'Hacker News',
            'update_time': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'items': []
        }
        
        # 获取所有新闻项
        stories = page.query_selector_all('tr.athing')
        
        for i, story in enumerate(stories):
            try:
                # 新闻ID
                story_id = story.get_attribute('id')
                
                # 新闻标题和链接
                title_element = story.query_selector('td.title > span.titleline > a')
                if not title_element:
                    continue
                    
                title = title_element.text_content()
                url = title_element.get_attribute('href')
                
                # 获取网站域名
                site_element = story.query_selector('span.sitestr')
                site = site_element.text_content() if site_element else ""
                
                # 获取下一个行，包含分数、评论等信息
                subtext = page.query_selector(f'#score_{story_id}')
                score = subtext.text_content().split()[0] if subtext else "0"
                
                # 获取评论数
                comments_element = page.query_selector(f'tr:has(#score_{story_id}) a:has-text("comment")')
                comments = comments_element.text_content().split()[0] if comments_element else "0"
                
                result['items'].append({
                    'rank': i + 1,
                    'id': story_id,
                    'title': title,
                    'url': url,
                    'site': site,
                    'score': score,
                    'comments': comments
                })
            except Exception as e:
                logger.error(f"解析Hacker News项失败: {str(e)}")
                continue
        
        return result

    @staticmethod
    def _parse_hacker_news_html(soup):
        """
        使用BeautifulSoup解析Hacker News页面
        
        Args:
            soup: BeautifulSoup对象
            
        Returns:
            dict: 解析后的Hacker News数据
        """
        result = {
            'title': 'Hacker News',
            'update_time': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'items': []
        }
        
        # 获取所有新闻项
        stories = soup.select('tr.athing')
        
        for i, story in enumerate(stories):
            try:
                # 新闻ID
                story_id = story.get('id')
                
                # 新闻标题和链接
                title_element = story.select_one('td.title > span.titleline > a')
                if not title_element:
                    continue
                    
                title = title_element.text
                url = title_element.get('href')
                
                # 获取网站域名
                site_element = story.select_one('span.sitestr')
                site = site_element.text if site_element else ""
                
                # 获取下一个行，包含分数、评论等信息
                subtext = soup.select_one(f'#score_{story_id}')
                score = subtext.text.split()[0] if subtext else "0"
                
                # 获取评论数
                comments_element = soup.select_one(f'tr:has(#score_{story_id}) a:contains("comment")')
                comments = comments_element.text.split()[0] if comments_element else "0"
                
                result['items'].append({
                    'rank': i + 1,
                    'id': story_id,
                    'title': title,
                    'url': url,
                    'site': site,
                    'score': score,
                    'comments': comments
                })
            except Exception as e:
                logger.error(f"解析Hacker News项失败: {str(e)}")
                continue
        
        return result 