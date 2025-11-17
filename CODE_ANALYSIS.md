# 项目代码架构详细分析

## 一、项目概述

**项目名称**: kongbai - 游戏战斗数据统计系统  
**技术栈**: Flask + MySQL + SQLAlchemy + Jinja2  
**主要功能**: 战斗记录管理、玩家排名、势力统计、数据可视化

---

## 二、数据库架构

### 2.1 核心表结构

```
┌─────────────────────────────────────────────────────────────┐
│                    数据库表关系图                             │
└─────────────────────────────────────────────────────────────┘

person (玩家表)
├── id (PK)
├── name (玩家名称) - UNIQUE
├── god (势力: 梵天/比湿奴/湿婆)
├── union_name (战盟)
├── job (职业)
├── level (等级)
├── player_group_id (FK → player_group.id)
├── created_at, updated_at, deleted_at (软删除)
└── create_by, update_by

battle_record (战斗记录表)
├── id (PK)
├── win (胜者名称) - 关键字段，存储player name而非ID
├── lost (败者名称) - 关键字段，存储player name而非ID
├── position (位置坐标)
├── remark (祝福次数)
├── publish_at (战斗时间) - 关键索引字段
├── created_at, updated_at, deleted_at
├── create_by (FK → person.id)
└── update_by

player_group (玩家分组表)
├── id (PK)
├── group_name (分组名称)
├── description (描述)
├── created_at, updated_at
└── create_by, update_by

rankings (排行榜缓存表)
├── id (PK)
├── category (分类)
├── source_url (数据来源)
├── ranking_data (JSON格式数据)
├── update_time (更新时间)
└── create_time (创建时间)
```

### 2.2 关键设计特点

| 特点 | 说明 |
|------|------|
| **软删除** | 所有表都有 `deleted_at` 字段，支持逻辑删除 |
| **审计字段** | `created_at`, `updated_at`, `create_by`, `update_by` |
| **name存储** | battle_record 中 win/lost 存储玩家名称而非ID |
| **JSON存储** | rankings 表中 ranking_data 存储为JSON文本 |
| **时间戳** | publish_at 用于战斗时间，是查询的关键字段 |

---

## 三、后端服务层架构

### 3.1 数据服务流程图

```
┌──────────────────────────────────────────────────────────────┐
│                    数据查询流程                               │
└──────────────────────────────────────────────────────────────┘

用户请求
    ↓
路由处理 (routes/*.py)
    ↓
服务层 (services/data_service.py)
    ├── get_faction_stats()          ← 势力统计
    ├── get_player_rankings()        ← 玩家排名
    ├── get_battle_details_by_player() ← 玩家详情
    ├── get_daily_kills_by_player()  ← 每日击杀
    ├── get_daily_deaths_by_player() ← 每日死亡
    └── get_daily_scores_by_player() ← 每日得分
    ↓
数据库查询 (SQL + CTE)
    ├── filtered_battle_records (过滤战斗记录)
    ├── win_stats (击杀统计)
    ├── lost_stats (死亡统计)
    ├── player_stats (玩家统计)
    └── 最终聚合
    ↓
结果转换 (Python dict/list)
    ↓
JSON响应
    ↓
前端渲染
```

### 3.2 核心服务函数详解

#### 3.2.1 `get_faction_stats(date_range=None)`

**功能**: 获取各势力的统计数据

**返回值**:
```python
(
    faction_stats,  # [(势力名, {统计数据}), ...]
    top_deaths,     # [{name, faction, deaths}, ...]
    top_killers,    # [{name, faction, kills}, ...]
    top_scorers     # [{name, faction, score}, ...]
)
```

**SQL优化策略**:
- 使用 CTE 分层查询
- 先过滤 battle_record (利用 deleted_at, publish_at 索引)
- 分别统计 win_stats 和 lost_stats
- 最后 JOIN person 表获取玩家信息

**时间范围支持**:
```python
'today'       → DATE(publish_at) = CURDATE()
'yesterday'   → DATE(publish_at) = DATE_SUB(CURDATE(), INTERVAL 1 DAY)
'week'        → publish_at >= DATE_SUB(CURDATE(), INTERVAL 7 DAY)
'month'       → publish_at >= DATE_SUB(CURDATE(), INTERVAL 1 MONTH)
'three_months'→ publish_at >= DATE_SUB(CURDATE(), INTERVAL 3 MONTH)
```

#### 3.2.2 `get_player_rankings(faction=None, time_range=None)`

**功能**: 获取玩家排名列表

**计分公式**:
```
score = kills * 3 + blessings - deaths
```

**排序规则**:
```
ORDER BY score DESC, kills DESC, deaths ASC
```

**返回数据结构**:
```python
[
    {
        'id': int,
        'name': str,
        'faction': str,
        'kills': int,
        'deaths': int,
        'blessings': int,
        'score': int,
        'kd_ratio': float  # kills/deaths
    },
    ...
]
```

#### 3.2.3 `get_battle_details_by_player(player_name)`

**功能**: 获取玩家的详细战斗信息

**返回数据**:
```python
{
    'id': int,
    'name': str,
    'faction': str,
    'kills': int,
    'deaths': int,
    'blessings': int,
    'score': int,
    'kd_ratio': float,
    'kills_details': [  # 击杀详情
        {
            'victim_name': str,
            'victim_faction': str,
            'kill_count': int,
            'last_kill_time': datetime
        }
    ],
    'deaths_details': [  # 死亡详情
        {
            'killer_name': str,
            'killer_faction': str,
            'death_count': int,
            'last_death_time': datetime
        }
    ]
}
```

#### 3.2.4 每日数据函数

**`get_daily_kills_by_player(date_range, limit=5)`**
**`get_daily_deaths_by_player(date_range, limit=5)`**
**`get_daily_scores_by_player(date_range, limit=5)`**

**返回数据结构**:
```python
{
    'dates': ['2025-01-01', '2025-01-02', ...],
    'players': [
        {
            'name': str,
            'faction': str,
            'data': [10, 15, 20, ...]  # 对应dates的数据
        },
        ...
    ]
}
```

**用途**: 前端绘制时间序列图表

---

## 四、API路由架构

### 4.1 路由结构

```
/
├── / (home.py)
│   └── GET / → 首页仪表盘
│
├── /auth (auth.py)
│   ├── POST /login → 登录
│   ├── POST /logout → 登出
│   └── GET /register → 注册
│
├── /battle (battle.py)
│   ├── GET /upload → 上传页面
│   ├── POST /upload → 处理文件上传
│   ├── GET /rankings → 排名页面
│   ├── GET /rankings/api → 排名数据API
│   └── GET /player/<name> → 玩家详情
│
├── /ranking (ranking.py)
│   ├── GET /data → 获取排行榜数据
│   ├── POST /refresh → 刷新排行榜
│   └── GET /history → 历史数据
│
├── /person (person.py)
│   ├── GET / → 玩家列表
│   ├── POST / → 创建玩家
│   └── PUT /<id> → 更新玩家
│
├── /reward (reward.py)
│   └── ...
│
└── /player_group (player_group.py)
    └── ...
```

### 4.2 关键路由详解

#### 4.2.1 首页路由 (`/`)

```python
# home.py - index()
GET / 
Query Params: date_range (week|today|yesterday|month|three_months)

Response:
{
    'chart_data': {
        'factions': ['梵天', '比湿奴', '湿婆'],
        'kills': [100, 150, 120],
        'deaths': [80, 90, 100],
        'blessings': [10, 15, 12]
    },
    'total_kills': 370,
    'total_deaths': 270,
    'total_blessings': 37,
    'top_killers': [...],
    'top_scorers': [...],
    'top_deaths': [...],
    'daily_kills_data': {...},
    'daily_deaths_data': {...},
    'daily_scores_data': {...}
}
```

#### 4.2.2 排名页面路由 (`/battle/rankings`)

```python
# battle.py - rankings()
GET /battle/rankings
Query Params:
  - faction: 比湿奴|梵天|湿婆|all (default: 比湿奴)
  - job: 职业名称|all
  - time_range: today|yesterday|week|month|three_months|all (default: today)
  - start_datetime: YYYY-MM-DD HH:MM:SS (可选)
  - end_datetime: YYYY-MM-DD HH:MM:SS (可选)
  - show_grouped: true|false (是否按分组显示)

Response:
Template: rankings.html
Data:
{
    'players': [
        {
            'id': 1,
            'name': '玩家名',
            'job': '职业',
            'faction': '势力',
            'kills': 100,
            'deaths': 50,
            'blessings': 10,
            'kd_ratio': 2.0,
            'score': 260
        },
        ...
    ],
    'jobs': ['职业1', '职业2', ...],
    'selected_faction': '比湿奴',
    'selected_job': None,
    'time_range': 'today'
}
```

#### 4.2.3 排行榜数据API (`/ranking/data`)

```python
# ranking.py - get_ranking_data()
GET /ranking/data
Query Params:
  - category: 主神排行榜 (default)
  - refresh: true|false (强制刷新)

Response:
{
    'category': '主神排行榜',
    'update_time': '2025-01-15 10:30:00',
    'data': [...]  # 排行榜数据
}

缓存策略:
- 24小时内返回缓存数据
- 超过24小时自动刷新
- refresh=true 强制刷新
```

---

## 五、前端架构

### 5.1 页面结构

```
templates/
├── base.html              # 基础模板
├── home/
│   └── index.html         # 首页仪表盘
├── battle/
│   ├── rankings.html      # 排名页面
│   ├── upload.html        # 上传页面
│   └── player_details.html # 玩家详情
├── person/
│   └── ...
├── player_group/
│   └── ...
└── auth/
    └── ...
```

### 5.2 前端数据流

```
┌─────────────────────────────────────────────────────────┐
│              前端数据交互流程                            │
└─────────────────────────────────────────────────────────┘

用户操作 (点击、选择)
    ↓
JavaScript 事件处理
    ↓
AJAX 请求 (fetch/jQuery)
    ↓
后端 API 路由
    ↓
JSON 响应
    ↓
JavaScript 处理数据
    ↓
Chart.js 绘制图表
    ↓
HTML 表格更新
    ↓
页面展示
```

### 5.3 关键前端功能

| 功能 | 页面 | 技术 |
|------|------|------|
| 势力统计图表 | home/index.html | Chart.js (柱状图) |
| 每日趋势图 | home/index.html | Chart.js (折线图) |
| 排名表格 | rankings.html | DataTables |
| 筛选器 | rankings.html | 下拉菜单 + AJAX |
| 文件上传 | upload.html | FormData + 进度条 |
| 玩家详情 | player_details.html | 表格展示 |

---

## 六、关键业务逻辑

### 6.1 计分系统

```
基础计分:
  - 击杀 (win): +3 分
  - 祝福 (remark): +1 分
  - 死亡 (lost): -1 分

总分计算:
  score = kills * 3 + blessings - deaths

排序规则:
  1. 按得分降序 (score DESC)
  2. 按击杀数降序 (kills DESC)
  3. 按死亡数升序 (deaths ASC)

K/D 比率:
  kd_ratio = kills / deaths (如果 deaths=0，则 kd_ratio=kills)
```

### 6.2 时间范围处理

```python
# 统一的时间条件构建
base_date_condition = ""
if date_range == 'today':
    base_date_condition = "AND DATE(publish_at) = CURDATE()"
elif date_range == 'yesterday':
    base_date_condition = "AND DATE(publish_at) = DATE_SUB(CURDATE(), INTERVAL 1 DAY)"
elif date_range == 'week':
    base_date_condition = "AND publish_at >= DATE_SUB(CURDATE(), INTERVAL 7 DAY)"
elif date_range == 'month':
    base_date_condition = "AND publish_at >= DATE_SUB(CURDATE(), INTERVAL 1 MONTH)"
elif date_range == 'three_months':
    base_date_condition = "AND publish_at >= DATE_SUB(CURDATE(), INTERVAL 3 MONTH)"

# 在 CTE 中使用
WITH filtered_battle_records AS (
    SELECT win, lost, remark
    FROM battle_record
    WHERE deleted_at IS NULL
      {base_date_condition}
)
```

### 6.3 玩家分组逻辑

```
场景: 一个玩家有多个游戏ID

实现:
1. 创建 PlayerGroup 记录
2. 将多个 Person 关联到同一 PlayerGroup
3. 查询时可选择:
   - show_grouped=true: 按分组聚合统计
   - show_grouped=false: 按单个ID统计

优势:
- 支持多账号玩家统计
- 灵活的数据视图
```

---

## 七、SQL查询优化

### 7.1 CTE 查询模式

```sql
-- 标准的多层 CTE 查询模式
WITH filtered_battle_records AS (
    -- 第1层: 过滤战斗记录 (利用索引)
    SELECT win, lost, remark
    FROM battle_record
    WHERE deleted_at IS NULL
      AND publish_at >= DATE_SUB(CURDATE(), INTERVAL 7 DAY)
),
win_stats AS (
    -- 第2层: 统计击杀
    SELECT 
        win as player_name,
        COUNT(*) as kills,
        SUM(CASE WHEN remark = '1' THEN 1 ELSE 0 END) as blessings
    FROM filtered_battle_records
    WHERE win IS NOT NULL
    GROUP BY win
),
lost_stats AS (
    -- 第3层: 统计死亡
    SELECT 
        lost as player_name,
        COUNT(*) as deaths
    FROM filtered_battle_records
    WHERE lost IS NOT NULL
    GROUP BY lost
),
player_stats AS (
    -- 第4层: 合并统计
    SELECT 
        p.id, p.name, p.god,
        COALESCE(ws.kills, 0) as kills,
        COALESCE(ls.deaths, 0) as deaths,
        COALESCE(ws.blessings, 0) as blessings,
        COALESCE(ws.kills, 0) * 3 + COALESCE(ws.blessings, 0) - COALESCE(ls.deaths, 0) as score
    FROM person p
    LEFT JOIN win_stats ws ON p.name = ws.player_name
    LEFT JOIN lost_stats ls ON p.name = ls.player_name
    WHERE p.god = :faction AND p.deleted_at IS NULL
)
-- 第5层: 最终查询
SELECT * FROM player_stats
ORDER BY score DESC, kills DESC, deaths ASC
```

### 7.2 索引建议

```sql
-- 关键索引
CREATE INDEX idx_battle_record_deleted_at ON battle_record(deleted_at);
CREATE INDEX idx_battle_record_publish_at ON battle_record(publish_at);
CREATE INDEX idx_battle_record_win ON battle_record(win);
CREATE INDEX idx_battle_record_lost ON battle_record(lost);
CREATE INDEX idx_person_god ON person(god);
CREATE INDEX idx_person_deleted_at ON person(deleted_at);
CREATE INDEX idx_person_name ON person(name);

-- 复合索引
CREATE INDEX idx_battle_record_composite ON battle_record(deleted_at, publish_at);
```

### 7.3 查询性能对比

```
优化前 (子查询):
- 每个玩家执行一次子查询
- N个玩家 = N次查询
- 性能: O(N)

优化后 (CTE + 聚合):
- 一次查询完成所有统计
- 充分利用索引
- 性能: O(1) 相对于玩家数量
```

---

## 八、认证和权限

### 8.1 认证流程

```python
# auth.py
@login_required
def protected_route():
    # 只有登录用户才能访问
    pass

# 实现原理:
# 1. 检查 session 中是否有 user_id
# 2. 如果没有，重定向到登录页面
# 3. 如果有，继续执行路由函数
```

### 8.2 受保护的路由

```python
# 需要登录的路由
@home_bp.route('/')
@login_required
def index():
    pass

@battle_bp.route('/upload')
@login_required
def upload_file():
    pass

@battle_bp.route('/rankings')
@login_required
def rankings():
    pass
```

---

## 九、配置管理

### 9.1 环境配置

```python
# app/__init__.py
if app.debug:
    # 开发环境
    app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:root123@localhost:3308/oneapi?charset=utf8mb4'
else:
    # 生产环境 - 优先级
    # 1. 环境变量 SQLALCHEMY_DATABASE_URI
    # 2. 环境变量 DATABASE_URL
    # 3. 默认配置
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('SQLALCHEMY_DATABASE_URI', 
        'mysql+pymysql://admin:admin123@db:3306/oneapi?charset=utf8mb4')
```

### 9.2 配置类

```python
# config.py
class Config:
    UPLOAD_FOLDER = 'uploads'
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB
    RANKING_URL = 'http://bbs.3gsc.com.cn/misc/gsm20/data/paiming.htm'
```

---

## 十、数据流向总结

### 10.1 完整的数据流

```
┌─────────────────────────────────────────────────────────────┐
│                  完整数据流向图                              │
└─────────────────────────────────────────────────────────────┘

用户上传战斗日志 (TXT文件)
    ↓
/battle/upload (POST)
    ↓
parse_text_file() - 解析文本
    ↓
save_battle_log_to_db() - 保存到数据库
    ↓
battle_record 表 (存储战斗记录)
    ↓
用户访问首页 (/)
    ↓
get_faction_stats() - 查询势力统计
get_daily_kills_by_player() - 查询每日击杀
get_daily_deaths_by_player() - 查询每日死亡
get_daily_scores_by_player() - 查询每日得分
    ↓
SQL 查询 (CTE优化)
    ↓
JSON 响应
    ↓
前端 JavaScript 处理
    ↓
Chart.js 绘制图表
    ↓
用户看到仪表盘
```

### 10.2 查询路径

```
用户访问 /battle/rankings?faction=比湿奴&time_range=week
    ↓
battle.py - rankings() 路由
    ↓
构建 SQL 查询 (带时间和势力筛选)
    ↓
db.session.execute(query, params)
    ↓
MySQL 执行 CTE 查询
    ↓
返回 player_rankings 列表
    ↓
render_template('rankings.html', players=player_rankings)
    ↓
前端展示排名表格
```

---

## 十一、关键文件清单

| 文件 | 行数 | 功能 |
|------|------|------|
| `app/services/data_service.py` | 994 | 核心数据查询服务 |
| `app/routes/battle.py` | 1665 | 战斗相关路由 |
| `app/routes/home.py` | 128 | 首页路由 |
| `app/routes/ranking.py` | 233 | 排行榜路由 |
| `app/models/player.py` | 90 | 玩家数据模型 |
| `app/__init__.py` | 229 | Flask应用初始化 |
| `app/templates/rankings.html` | - | 排名页面模板 |
| `app/templates/home/index.html` | - | 首页模板 |

---

## 十二、性能优化建议

### 12.1 数据库优化

1. **索引优化**
   - 为 `battle_record` 表的 `deleted_at`, `publish_at`, `win`, `lost` 字段建立索引
   - 为 `person` 表的 `god`, `deleted_at`, `name` 字段建立索引

2. **查询优化**
   - 继续使用 CTE 模式进行多层聚合
   - 避免在应用层进行数据聚合

3. **缓存策略**
   - 排行榜数据已有 24 小时缓存
   - 考虑为首页统计数据添加 Redis 缓存

### 12.2 应用层优化

1. **连接池**
   - 配置 SQLAlchemy 连接池大小
   - 设置合理的超时时间

2. **异步处理**
   - 考虑使用 Celery 处理耗时的数据导出
   - 后台任务处理排行榜爬取

3. **前端优化**
   - 使用分页加载大数据集
   - 实现前端数据缓存

---

## 十三、扩展建议

1. **功能扩展**
   - 添加数据导出功能 (CSV, Excel)
   - 实现玩家对比功能
   - 添加战斗回放功能

2. **性能扩展**
   - 实现数据分片 (按日期分表)
   - 添加读写分离
   - 实现数据预聚合

3. **可视化扩展**
   - 添加更多图表类型
   - 实现实时数据更新 (WebSocket)
   - 添加地图展示功能

---

**文档生成时间**: 2025-01-15  
**项目路径**: `c:\coding\kongbai`  
**维护者**: 开发团队
