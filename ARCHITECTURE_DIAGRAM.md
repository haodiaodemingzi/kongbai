# 项目架构可视化图解

## 一、系统整体架构

```
┌────────────────────────────────────────────────────────────────────────┐
│                         前端层 (Frontend)                              │
├────────────────────────────────────────────────────────────────────────┤
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌──────────┐  │
│  │  首页仪表盘  │  │  排名页面    │  │  上传页面    │  │ 其他页面 │  │
│  └──────────────┘  └──────────────┘  └──────────────┘  └──────────┘  │
└────────────────────────────────────────────────────────────────────────┘
                             ▼
┌────────────────────────────────────────────────────────────────────────┐
│                         API 层 (Routes)                                │
├────────────────────────────────────────────────────────────────────────┤
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌──────────┐  │
│  │  home.py     │  │  battle.py   │  │  ranking.py  │  │ 其他路由 │  │
│  └──────────────┘  └──────────────┘  └──────────────┘  └──────────┘  │
└────────────────────────────────────────────────────────────────────────┘
                             ▼
┌────────────────────────────────────────────────────────────────────────┐
│                      服务层 (Services)                                 │
├────────────────────────────────────────────────────────────────────────┤
│  data_service.py (核心数据服务)                                        │
│  • get_faction_stats()          - 势力统计                             │
│  • get_player_rankings()        - 玩家排名                             │
│  • get_battle_details_by_player() - 玩家详情                           │
│  • get_daily_kills_by_player()  - 每日击杀                             │
│  • get_daily_deaths_by_player() - 每日死亡                             │
│  • get_daily_scores_by_player() - 每日得分                             │
└────────────────────────────────────────────────────────────────────────┘
                             ▼
┌────────────────────────────────────────────────────────────────────────┐
│                      数据库层 (Database)                               │
├────────────────────────────────────────────────────────────────────────┤
│  MySQL 数据库 (oneapi)                                                 │
│  ├── person (玩家表)                                                   │
│  ├── battle_record (战斗记录表)                                        │
│  ├── player_group (玩家分组表)                                         │
│  └── rankings (排行榜缓存表)                                           │
└────────────────────────────────────────────────────────────────────────┘
```

## 二、数据库表关系图

```
person (玩家表)
├── id, name, god, union_name, job, level
├── player_group_id (FK)
└── deleted_at (软删除)
    ▲
    │ (1:N)
    │
player_group (分组)
├── id, group_name, description
└── created_at, updated_at

battle_record (战斗记录)
├── id, win, lost, position, remark
├── publish_at (关键字段)
├── create_by (FK → person.id)
└── deleted_at

rankings (排行榜缓存)
├── id, category, source_url
├── ranking_data (JSON)
└── update_time, create_time
```

## 三、数据查询流程

```
用户请求 → 路由处理 → 服务层函数 → SQL查询 → 结果处理 → JSON响应 → 前端渲染

关键优化:
1. 使用 CTE (Common Table Expressions) 分层查询
2. 先过滤 battle_record 表 (利用索引)
3. 分别统计 win_stats 和 lost_stats
4. 最后 JOIN person 表获取玩家信息
```

## 四、计分系统

```
击杀 (win): +3 分
祝福 (remark): +1 分
死亡 (lost): -1 分

总分 = kills * 3 + blessings - deaths

排序规则:
1. score DESC (得分降序)
2. kills DESC (击杀数降序)
3. deaths ASC (死亡数升序)
```

## 五、时间范围筛选

```
today       → DATE(publish_at) = CURDATE()
yesterday   → DATE(publish_at) = DATE_SUB(CURDATE(), INTERVAL 1 DAY)
week        → publish_at >= DATE_SUB(CURDATE(), INTERVAL 7 DAY)
month       → publish_at >= DATE_SUB(CURDATE(), INTERVAL 1 MONTH)
three_months→ publish_at >= DATE_SUB(CURDATE(), INTERVAL 3 MONTH)
all         → 最近365天
```

## 六、文件上传流程

```
用户上传文件
    ↓
POST /battle/upload
    ↓
parse_text_file() - 解析文本
    ↓
save_battle_log_to_db() - 保存数据库
    ↓
battle_record 表 + person 表
    ↓
重定向到 /battle/rankings
```

## 七、认证流程

```
用户访问受保护路由
    ↓
@login_required 检查
    ↓
检查 session['user_id']
    ↓
存在 → 继续执行
不存在 → 重定向到登录页面
```

## 八、缓存策略

```
GET /ranking/data
    ↓
检查数据库中的缓存
    ↓
存在且未过期 (< 24小时) → 返回缓存
过期或不存在 → 爬取新数据 → 保存到数据库 → 返回
    ↓
refresh=true → 强制刷新
```

## 九、关键索引

```
battle_record 表:
- idx_battle_record_deleted_at (deleted_at)
- idx_battle_record_publish_at (publish_at)
- idx_battle_record_win (win)
- idx_battle_record_lost (lost)

person 表:
- idx_person_god (god)
- idx_person_deleted_at (deleted_at)
- idx_person_name (name)
```

## 十、API 端点总览

```
GET /                           - 首页仪表盘
GET /battle/upload              - 上传页面
POST /battle/upload             - 处理上传
GET /battle/rankings            - 排名页面
GET /ranking/data               - 排行榜数据
POST /ranking/refresh           - 刷新排行榜
GET /ranking/history            - 历史数据
GET /person                     - 玩家列表
POST /auth/login                - 登录
POST /auth/logout               - 登出
```

## 十一、核心数据结构

```
玩家排名:
{
  'id': int,
  'name': str,
  'faction': str,
  'kills': int,
  'deaths': int,
  'blessings': int,
  'score': int,
  'kd_ratio': float
}

每日数据:
{
  'dates': ['2025-01-01', ...],
  'players': [
    {
      'name': str,
      'faction': str,
      'data': [10, 15, 20, ...]
    }
  ]
}

势力统计:
{
  'player_count': int,
  'total_kills': int,
  'total_deaths': int,
  'total_blessings': int,
  'top_killer': {'name': str, 'kills': int},
  'top_scorer': {'name': str, 'score': int}
}
```

---

**生成时间**: 2025-01-15  
**项目**: kongbai - 游戏战斗数据统计系统
