#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
初始化MySQL数据库
"""

from app import db, create_app

app = create_app()
with app.app_context():
    print("开始初始化数据库...")
    db.create_all()
    print("数据库初始化完成") 