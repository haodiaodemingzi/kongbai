# 快速参考指南

## 项目结构速查

```
kongbai/
├── app/
│   ├── __init__.py              # Flask应用初始化
│   ├── config.py                # 配置文件
│   ├── extensions.py            # SQLAlchemy扩展
│   ├── models.py                # 旧模型定义
│   ├── models/
│   │   ├── player.py            # Person, BattleRecord, PlayerGroup 模型
│   │   ├── ranking.py           # Ranking 模型 (SQLAlchemy)
│   │   └── rankings.py          # Rankings 模型
│   ├── routes/
│   │   ├── home.py              # 首页路由 (/)
│   │   ├── battle.py            # 战斗路由 (/battle/*)
│   │   ├── ranking.py           # 排行榜路由 (/ranking/*)
│   │   ├── person.py            # 玩家管理路由
│   │   ├── reward.py            # 奖励路由
│   │   ├── player_group.py      # 玩家分组路由
│   │   └── auth.py              # 认证路由
│   ├── services/
│   │   └── data_service.py      # 核心数据服务 (994行)
│   ├── templates/               # HTML模板
│   ├── static/                  # 静态文件
│   └── utils/                   # 工具函数
├── run.py                       # 启动脚本
├── requirements.txt             # 依赖
└── CODE_ANALYSIS.md            # 详细分析文档
```

## 数据库表速查

| 表名 | 主要字段 | 用途 |
|------|--------|------|
| `person` | id, name, god, job, level | 玩家信息 |
| `battle_record` | id, win, lost, publish_at, remark | 战斗记录 |
| `player_group` | id, group_name | 玩家分组 |
| `rankings` | id, category, ranking_data, update_time | 排行榜缓存 |

## 关键函数速查

### data_service.py

```python
# 获取势力统计
get_faction_stats(date_range=None)
→ (faction_stats, top_deaths, top_killers, top_scorers)

# 获取玩家排名
get_player_rankings(faction=None, time_range=None)
→ [{'id', 'name', 'faction', 'kills', 'deaths', 'blessings', 'score', 'kd_ratio'}, ...]

# 获取玩家详情
get_battle_details_by_player(player_name)
→ {'id', 'name', 'kills_details', 'deaths_details', ...}

# 每日数据
get_daily_kills_by_player(date_range, limit=5)
get_daily_deaths_by_player(date_range, limit=5)
get_daily_scores_by_player(date_range, limit=5)
→ {'dates': [...], 'players': [...]}

# 数据导出
export_data_to_json(faction=None)
→ (json_string, filename)
```

## API 端点速查

### 首页
```
GET /
Query: date_range (week|today|yesterday|month|three_months)
返回: 首页仪表盘 (HTML)
```

### 战斗相关
```
GET /battle/upload
POST /battle/upload
Query: file (txt文件)
返回: 重定向到 /battle/rankings

GET /battle/rankings
Query: faction, job, time_range, start_datetime, end_datetime
返回: 排名页面 (HTML)
```

### 排行榜
```
GET /ranking/data
Query: category, refresh (true|false)
返回: JSON 排行榜数据

POST /ranking/refresh
Form: category
返回: JSON 刷新结果

GET /ranking/history
Query: category, limit
返回: JSON 历史数据
```

## 计分公式

```
score = kills * 3 + blessings - deaths

排序: score DESC, kills DESC, deaths ASC

K/D比: kills / deaths (deaths=0时返回kills)
```

## 时间范围参数

```
today        → 当天
yesterday    → 昨天
week         → 最近7天
month        → 最近30天
three_months → 最近90天
all          → 最近365天
```

## 势力列表

```
梵天
比湿奴
湿婆
```

## 常见查询模式

### 1. 获取某势力的排名
```python
from app.services.data_service import get_player_rankings
players = get_player_rankings(faction='比湿奴', time_range='week')
```

### 2. 获取玩家详情
```python
from app.services.data_service import get_battle_details_by_player
details = get_battle_details_by_player('玩家名')
```

### 3. 获取首页数据
```python
from app.services.data_service import (
    get_faction_stats,
    get_daily_kills_by_player,
    get_daily_deaths_by_player,
    get_daily_scores_by_player
)

faction_stats, top_deaths, top_killers, top_scorers = get_faction_stats('week')
daily_kills = get_daily_kills_by_player('week', limit=5)
daily_deaths = get_daily_deaths_by_player('week', limit=5)
daily_scores = get_daily_scores_by_player('week', limit=5)
```

## SQL 查询优化技巧

### CTE 分层查询模式
```sql
WITH filtered_battle_records AS (
    -- 第1层: 过滤
    SELECT win, lost, remark
    FROM battle_record
    WHERE deleted_at IS NULL
),
win_stats AS (
    -- 第2层: 统计击杀
    SELECT win, COUNT(*) as kills
    FROM filtered_battle_records
    GROUP BY win
),
lost_stats AS (
    -- 第3层: 统计死亡
    SELECT lost, COUNT(*) as deaths
    FROM filtered_battle_records
    GROUP BY lost
),
player_stats AS (
    -- 第4层: 合并
    SELECT p.*, ws.kills, ls.deaths
    FROM person p
    LEFT JOIN win_stats ws ON p.name = ws.win
    LEFT JOIN lost_stats ls ON p.name = ls.lost
)
SELECT * FROM player_stats
```

## 索引建议

```sql
-- battle_record 表
CREATE INDEX idx_br_deleted_at ON battle_record(deleted_at);
CREATE INDEX idx_br_publish_at ON battle_record(publish_at);
CREATE INDEX idx_br_win ON battle_record(win);
CREATE INDEX idx_br_lost ON battle_record(lost);

-- person 表
CREATE INDEX idx_p_god ON person(god);
CREATE INDEX idx_p_deleted_at ON person(deleted_at);
CREATE INDEX idx_p_name ON person(name);
```

## 常见错误排查

| 问题 | 原因 | 解决方案 |
|------|------|--------|
| 查询返回空 | 玩家不存在或被软删除 | 检查 deleted_at 字段 |
| 排名不对 | 计分公式错误 | 验证 score = kills*3 + blessings - deaths |
| 时间范围不对 | 日期条件构建错误 | 检查 date_condition 变量 |
| 性能慢 | 缺少索引或查询不优化 | 添加索引或使用CTE |
| 数据重复 | 战斗记录重复导入 | 检查 battle_record 表中是否有重复 |

## 环境配置

### 开发环境
```python
# app/__init__.py
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:root123@localhost:3308/oneapi?charset=utf8mb4'
```

### 生产环境
```python
# 优先级:
# 1. 环境变量 SQLALCHEMY_DATABASE_URI
# 2. 环境变量 DATABASE_URL
# 3. 默认: mysql+pymysql://admin:admin123@db:3306/oneapi?charset=utf8mb4
```

## 调试技巧

### 启用日志
```python
import logging
from app.utils.logger import get_logger

logger = get_logger()
logger.debug("调试信息")
logger.info("信息")
logger.warning("警告")
logger.error("错误")
```

### 查看SQL查询
```python
# app/__init__.py 中已配置
logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)
```

### 测试数据库连接
```python
from app import db
from sqlalchemy import text

with app.app_context():
    result = db.session.execute(text('SELECT 1'))
    print(result.fetchone())
```

## 性能优化建议

1. **查询优化**
   - 使用 CTE 代替子查询
   - 添加必要的索引
   - 避免 SELECT * 

2. **缓存策略**
   - 排行榜数据 24 小时缓存
   - 考虑使用 Redis 缓存热数据

3. **前端优化**
   - 实现分页加载
   - 减少 AJAX 请求
   - 使用前端缓存

## 部署检查清单

- [ ] 数据库连接配置正确
- [ ] 所有必要的索引已创建
- [ ] 环境变量已设置
- [ ] 日志目录可写
- [ ] 上传目录可写
- [ ] SECRET_KEY 已设置
- [ ] 数据库备份已完成

## 常用命令

```bash
# 启动应用
python run.py

# 创建数据库表
python create_db_with_sqlalchemy.py

# 导入示例数据
python create_sample_data.py

# 查看日志
tail -f logs/app.log

# 数据库备份
mysqldump -u root -p oneapi > backup.sql

# 数据库恢复
mysql -u root -p oneapi < backup.sql
```

## 文件上传处理

```python
# 支持的文件类型: .txt
# 上传目录: UPLOAD_FOLDER (config.py)
# 最大文件大小: MAX_CONTENT_LENGTH (config.py)

# 处理流程:
# 1. 检查文件类型
# 2. 保存文件
# 3. 解析文本
# 4. 保存到数据库
```

## 玩家分组功能

```python
# 创建分组
player_group = PlayerGroup(group_name='玩家真名', description='描述')

# 关联玩家
person.player_group_id = player_group.id

# 查询时可选择:
# show_grouped=true  → 按分组聚合
# show_grouped=false → 按单个ID统计
```

## 常见 SQL 查询

### 获取某玩家的击杀数
```sql
SELECT COUNT(*) as kills
FROM battle_record
WHERE win = '玩家名' AND deleted_at IS NULL
```

### 获取某玩家的死亡数
```sql
SELECT COUNT(*) as deaths
FROM battle_record
WHERE lost = '玩家名' AND deleted_at IS NULL
```

### 获取某势力的玩家数
```sql
SELECT COUNT(*) as player_count
FROM person
WHERE god = '梵天' AND deleted_at IS NULL
```

### 获取最近7天的战斗数
```sql
SELECT COUNT(*) as battles
FROM battle_record
WHERE deleted_at IS NULL
  AND publish_at >= DATE_SUB(CURDATE(), INTERVAL 7 DAY)
```

---

**最后更新**: 2025-01-15  
**项目**: kongbai
