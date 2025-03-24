#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
从API获取人员信息并生成INSERT SQL语句到文件
共21页，每页50条记录
"""

import sys
import json
import logging
import time
import requests
from datetime import datetime
from dotenv import load_dotenv
import os

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] [%(levelname)s] [%(name)s] - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger("import_api")

# 加载环境变量
load_dotenv()

# 输出文件名
SQL_OUTPUT_FILE = "person_data.sql"

# API配置
API_BASE_URL = 'https://bigmang.xyz/api/api/v1/person'
TOTAL_PAGES = 3
PAGE_SIZE = 500
AUTH_TOKEN = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJkYXRhc2NvcGUiOiIxIiwiZXhwIjoxNzQyNjQyOTc4LCJpZGVudGl0eSI6MSwibmljZSI6ImFkbWluIiwib3JpZ19pYXQiOjE3NDI2MzkzNzgsInJvbGVpZCI6MSwicm9sZWtleSI6ImFkbWluIiwicm9sZW5hbWUiOiLns7vnu5_nrqHnkIblkZgifQ.ZAOBc-rMmyRwMOjMGb6_0QkG6zxvvVaDo7ANPcYnJI0'

# 请求头
HEADERS = {
    'authority': 'bigmang.xyz',
    'accept': 'application/json, text/plain, */*',
    'accept-language': 'zh-CN,zh;q=0.9',
    'authorization': f'Bearer {AUTH_TOKEN}',
    'referer': 'https://bigmang.xyz/admin/person',
    'sec-ch-ua': '"Not A(Brand";v="99", "Google Chrome";v="121", "Chromium";v="121"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'same-origin',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36'
}

def fetch_data_from_api(page_index):
    """从API获取指定页的数据"""
    url = f"{API_BASE_URL}?pageIndex={page_index}&pageSize={PAGE_SIZE}&beginTime=&endTime="
    logger.info(f"获取第 {page_index} 页数据...")
    
    try:
        response = requests.get(url, headers=HEADERS)
        if response.status_code != 200:
            logger.error(f"API请求失败: HTTP {response.status_code} - {response.text}")
            return None
        
        data = response.json()
        if not data.get('code') == 200:
            logger.error(f"API返回错误: {data.get('message')}")
            return None
            
        items = data.get('data', {}).get('list', [])
        logger.info(f"成功获取 {len(items)} 条记录")
        return items
        
    except Exception as e:
        logger.error(f"获取API数据出错: {str(e)}")
        return None

def generate_create_table_sql():
    """生成创建表的SQL语句"""
    sql = """-- 创建person表
CREATE TABLE IF NOT EXISTS person (
    id INT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    job VARCHAR(50),
    god VARCHAR(50),
    status INT DEFAULT 1,
    create_at DATETIME,
    update_at DATETIME
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 清空表数据
TRUNCATE TABLE person;
"""
    return sql

def map_api_data_to_person(item):
    """将API返回的数据转换为person表结构"""
    # 根据实际API返回的字段调整
    try:
        person = {
            'id': item.get('id'),
            'name': item.get('name', ''),
            'job': item.get('job', ''),
            'god': item.get('god', ''),
            'status': item.get('status', 1),
            'create_at': item.get('createTime') or datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'update_at': item.get('updateTime') or datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        return person
    except Exception as e:
        logger.error(f"转换数据出错: {str(e)}")
        return None

def generate_insert_sql(persons):
    """生成插入数据的SQL语句"""
    if not persons:
        logger.warning("没有数据需要生成SQL")
        return ""
    
    # 生成批量插入SQL
    fields = "id, name, job, god, status, create_at, update_at"
    values_list = []
    
    for person in persons:
        if person:
            # 处理单引号，防止SQL注入
            name = person['name'].replace("'", "''") if person['name'] else ''
            job = person['job'].replace("'", "''") if person['job'] else ''
            god = person['god'].replace("'", "''") if person['god'] else ''
            
            value = f"({person['id']}, '{name}', '{job}', '{god}', {person['status']}, '{person['create_at']}', '{person['update_at']}')"
            values_list.append(value)
    
    # 生成单个INSERT语句，包含所有数据
    insert_sql = f"""-- 批量插入所有数据 (共{len(values_list)}条记录)
INSERT INTO person ({fields})
VALUES 
{',\n'.join(values_list)};"""
    
    logger.info(f"生成了SQL语句，共 {len(values_list)} 条记录")
    return insert_sql

def write_sql_to_file(sql_content):
    """将SQL语句写入文件"""
    try:
        with open(SQL_OUTPUT_FILE, 'w', encoding='utf-8') as f:
            f.write(sql_content)
        
        file_size = os.path.getsize(SQL_OUTPUT_FILE)
        logger.info(f"SQL已保存到文件: {SQL_OUTPUT_FILE}")
        logger.info(f"SQL文件大小: {file_size} 字节")
        return True
    except Exception as e:
        logger.error(f"写入SQL文件时出错: {str(e)}")
        return False

def main():
    """主函数"""
    all_persons = []
    
    try:
        # 遍历所有页，获取数据
        for page in range(1, TOTAL_PAGES + 1):
            # 获取API数据
            items = fetch_data_from_api(page)
            if items is None:
                logger.error(f"无法获取第 {page} 页数据，跳过")
                continue
                
            # 转换数据格式
            persons = [map_api_data_to_person(item) for item in items]
            all_persons.extend([p for p in persons if p])
            
            # 防止请求过于频繁
            if page < TOTAL_PAGES:
                logger.info(f"已获取 {len(all_persons)} 条记录，等待1秒后继续...")
                time.sleep(1)
        
        # 生成SQL语句
        logger.info(f"数据获取完成，共获取 {len(all_persons)} 条记录")
        
        # 生成建表SQL
        create_table_sql = generate_create_table_sql()
        
        # 生成插入数据SQL
        insert_sql = generate_insert_sql(all_persons)
        if insert_sql:
            # 将SQL写入文件
            full_sql = create_table_sql + "\n\n" + insert_sql
            success = write_sql_to_file(full_sql)
            
            if success:
                logger.info("SQL文件生成成功")
                # 生成样本SQL文件，最多包含5条记录
                if all_persons:
                    with open("sample_person.sql", "w", encoding="utf-8") as f:
                        sample_sql = create_table_sql + "\n\n"
                        # 为样本数据准备值列表
                        sample_values = []
                        for i, person in enumerate(all_persons):
                            if person:
                                name = person['name'].replace("'", "''") if person['name'] else ''
                                job = person['job'].replace("'", "''") if person['job'] else ''
                                god = person['god'].replace("'", "''") if person['god'] else ''
                                
                                value = f"({person['id']}, '{name}', '{job}', '{god}', '{person['create_at']}', '{person['update_at']}')"
                                sample_values.append(value)
                        
                        if sample_values:
                            sample_sql += f"""-- 样本数据插入
INSERT INTO person (id, name, job, god, created_at, updated_at)
VALUES 
{',\n'.join(sample_values)};"""
                            f.write(sample_sql)
                            logger.info("样本SQL文件也已生成: sample_person.sql")
            else:
                logger.error("SQL文件生成失败")
                return 1
            
        return 0
        
    except Exception as e:
        logger.error(f"程序执行出错: {str(e)}")
        return 1
        
if __name__ == "__main__":
    sys.exit(main()) 