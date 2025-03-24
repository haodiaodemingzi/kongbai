#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
事务帮助工具，提供事务重试功能
"""

import time
import logging
import functools
from sqlalchemy.exc import OperationalError
from pymysql.err import OperationalError as PyMySQLOperationalError

logger = logging.getLogger(__name__)

def retry_on_deadlock(max_retries=3, retry_interval=0.5):
    """
    装饰器：在发生死锁时自动重试事务
    
    参数:
        max_retries: 最大重试次数
        retry_interval: 重试间隔(秒)
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            retries = 0
            while retries < max_retries:
                try:
                    return func(*args, **kwargs)
                except (OperationalError, PyMySQLOperationalError) as e:
                    # 检查是否为死锁异常
                    err_msg = str(e)
                    if "Deadlock found" in err_msg and retries < max_retries - 1:
                        retries += 1
                        logger.warning(f"检测到死锁，正在进行第 {retries} 次重试...")
                        time.sleep(retry_interval * (2 ** retries))  # 指数退避
                        continue
                    raise  # 非死锁异常或已达最大重试次数，重新抛出
            raise RuntimeError(f"在 {max_retries} 次尝试后仍无法解决死锁")
        return wrapper
    return decorator 