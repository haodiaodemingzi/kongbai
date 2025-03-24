#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import glob
from datetime import datetime, timedelta
import argparse

# 日志目录
logs_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'logs')

def parse_arguments():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(description='查看战绩统计系统日志')
    parser.add_argument('-d', '--date', help='日期 (YYYYMMDD 格式), 默认为今天', default=datetime.now().strftime('%Y%m%d'))
    parser.add_argument('-n', '--lines', type=int, help='显示的行数', default=50)
    parser.add_argument('-l', '--level', choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'], help='日志级别过滤', default=None)
    parser.add_argument('-s', '--search', help='搜索关键词', default=None)
    parser.add_argument('-f', '--follow', action='store_true', help='持续查看日志', default=False)
    parser.add_argument('-a', '--all', action='store_true', help='显示所有日志', default=False)
    return parser.parse_args()

def get_log_file(date):
    """获取指定日期的日志文件"""
    log_file = os.path.join(logs_dir, f'app_{date}.log')
    if os.path.exists(log_file):
        return log_file
    
    # 如果找不到指定日期的日志，尝试查找最近的日志
    all_logs = glob.glob(os.path.join(logs_dir, 'app_*.log'))
    if not all_logs:
        print(f"错误: 找不到任何日志文件在 {logs_dir}")
        sys.exit(1)
    
    # 按日期排序
    sorted_logs = sorted(all_logs, key=lambda x: os.path.basename(x).replace('app_', '').replace('.log', ''), reverse=True)
    latest_log = sorted_logs[0]
    latest_date = os.path.basename(latest_log).replace('app_', '').replace('.log', '')
    
    print(f"警告: 找不到日期 {date} 的日志，使用最近的日志 ({latest_date})")
    return latest_log

def colorize_log_line(line):
    """给日志行添加颜色"""
    if '[DEBUG]' in line:
        return f"\033[36m{line}\033[0m"  # 青色
    elif '[INFO]' in line:
        return f"\033[32m{line}\033[0m"  # 绿色
    elif '[WARNING]' in line:
        return f"\033[33m{line}\033[0m"  # 黄色
    elif '[ERROR]' in line:
        return f"\033[31m{line}\033[0m"  # 红色
    elif '[CRITICAL]' in line:
        return f"\033[35m{line}\033[0m"  # 紫色
    else:
        return line

def filter_log_line(line, level=None, search=None):
    """根据条件过滤日志行"""
    if level and f'[{level}]' not in line:
        return False
    
    if search and search.lower() not in line.lower():
        return False
    
    return True

def view_logs(args):
    """查看日志"""
    log_file = get_log_file(args.date)
    
    print(f"查看日志文件: {log_file}")
    print(f"过滤级别: {args.level or '全部'}")
    if args.search:
        print(f"搜索: '{args.search}'")
    print("-" * 80)
    
    if args.follow:
        # 持续查看日志
        try:
            with open(log_file, 'r', encoding='utf-8') as f:
                # 先移动到文件末尾
                f.seek(0, 2)
                
                while True:
                    line = f.readline()
                    if line:
                        if filter_log_line(line, args.level, args.search):
                            print(colorize_log_line(line.rstrip()))
                    else:
                        import time
                        time.sleep(0.1)
        except KeyboardInterrupt:
            print("\n停止查看日志")
    else:
        # 显示指定行数的日志
        try:
            with open(log_file, 'r', encoding='utf-8') as f:
                if args.all:
                    lines = f.readlines()
                else:
                    # 使用 tail 方式获取最后 N 行
                    lines = f.readlines()
                    lines = lines[-args.lines:] if args.lines < len(lines) else lines
                
                filtered_lines = [line for line in lines if filter_log_line(line, args.level, args.search)]
                
                if not filtered_lines:
                    print("没有找到符合条件的日志行")
                else:
                    for line in filtered_lines:
                        print(colorize_log_line(line.rstrip()))
                        
                print(f"\n共显示 {len(filtered_lines)} 行日志")
        except Exception as e:
            print(f"错误: 读取日志时出错: {str(e)}")

if __name__ == '__main__':
    # 确保日志目录存在
    if not os.path.exists(logs_dir):
        os.makedirs(logs_dir)
        print(f"日志目录不存在，已创建: {logs_dir}")
    
    args = parse_arguments()
    view_logs(args) 