#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
从MySQL导出Person表数据到CSV文件
"""

import os
import sys
import csv
import logging
import pymysql
from dotenv import load_dotenv

# 配置日志
logging.basicConfig(
    level=logging.DEBUG,
    format='[%(asctime)s] [%(levelname)s] [%(name)s] - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger("export_mysql")

# 加载环境变量
load_dotenv()

# MySQL连接配置
MYSQL_CONFIG = {
    'host': '192.168.123.144',
    'user': 'cheetah',
    'password': 'cheetah',
    'database': 'oneapi',
    'charset': 'utf8mb4',
}

def export_person_to_csv(csv_file):
    """从MySQL导出person表数据到CSV文件"""
    logger.info(f"导出MySQL中的person表数据到CSV: {csv_file}")
    
    try:
        # 连接数据库
        logger.debug("连接MySQL数据库...")
        conn = pymysql.connect(**MYSQL_CONFIG)
        cursor = conn.cursor(pymysql.cursors.DictCursor)  # 使用字典游标
        
        # 查询person表数据
        logger.debug("查询person表数据...")
        query = """
        SELECT id, name, job, god, status, 
               DATE_FORMAT(create_at, '%Y-%m-%d %H:%i:%s') as create_at, 
               DATE_FORMAT(update_at, '%Y-%m-%d %H:%i:%s') as update_at
        FROM person
        """
        cursor.execute(query)
        rows = cursor.fetchall()
        
        if not rows:
            logger.warning("MySQL中person表数据为空")
            return False
            
        logger.info(f"查询到 {len(rows)} 条person记录")
        
        # 写入CSV文件
        logger.debug(f"写入数据到CSV文件: {csv_file}")
        with open(csv_file, 'w', newline='', encoding='utf-8') as f:
            # 获取字段名
            fieldnames = rows[0].keys()
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            
            # 写入表头
            writer.writeheader()
            
            # 写入数据行
            writer.writerows(rows)
        
        logger.info(f"成功导出 {len(rows)} 条记录到CSV文件")
        return True
        
    except Exception as e:
        logger.error(f"导出数据时出错: {str(e)}")
        return False
    finally:
        if 'conn' in locals():
            conn.close()

def main():
    """主函数"""
    try:
        # 设置CSV文件路径
        if len(sys.argv) > 1:
            csv_file = sys.argv[1]
        else:
            csv_file = "person_data.csv"
            
        # 导出数据
        success = export_person_to_csv(csv_file)
        
        if success:
            logger.info(f"数据成功导出到: {csv_file}")
            return 0
        else:
            logger.error("数据导出失败")
            return 1
            
    except Exception as e:
        logger.error(f"程序执行出错: {str(e)}")
        return 1
        
if __name__ == "__main__":
    sys.exit(main()) 