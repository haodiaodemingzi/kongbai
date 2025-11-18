#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""测试路由是否正确注册"""

from app import create_app

app = create_app()

print("\n=== 已注册的路由 ===\n")

# 获取所有路由
routes = []
for rule in app.url_map.iter_rules():
    routes.append({
        'endpoint': rule.endpoint,
        'methods': ','.join(rule.methods - {'HEAD', 'OPTIONS'}),
        'path': rule.rule
    })

# 按路径排序
routes.sort(key=lambda x: x['path'])

# 筛选 API 路由
api_routes = [r for r in routes if '/api/' in r['path']]

print("API 路由:")
for route in api_routes:
    print("  {:<10s} {:<50s} -> {}".format(route['methods'], route['path'], route['endpoint']))

print(f"\n总共 {len(api_routes)} 个 API 路由")

# 检查特定路由
auth_api_login = [r for r in routes if r['path'] == '/auth/api/login']
if auth_api_login:
    print("\n✅ /auth/api/login 路由已注册")
    print(f"   方法: {auth_api_login[0]['methods']}")
    print(f"   端点: {auth_api_login[0]['endpoint']}")
else:
    print("\n❌ /auth/api/login 路由未找到")
    
    # 查找相似路由
    auth_routes = [r for r in routes if '/auth/' in r['path']]
    if auth_routes:
        print("\n找到的 /auth/ 相关路由:")
        for route in auth_routes:
            print(f"  {route['methods']:10s} {route['path']}")
