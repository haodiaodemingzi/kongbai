# API 文档

## 基础信息

- **基础URL**: `http://localhost:5000` (开发环境)
- **认证**: 基于 Session (需要登录)
- **响应格式**: JSON / HTML

---

## 认证相关

### 登录
```
POST /auth/login
Content-Type: application/x-www-form-urlencoded

参数:
  username: string (必需)
  password: string (必需)

响应:
  成功: 重定向到首页
  失败: 返回登录页面，显示错误信息
```

### 登出
```
POST /auth/logout

响应:
  重定向到登录页面
```

---

## 首页相关

### 获取首页仪表盘
```
GET /
Query Parameters:
  date_range: string (可选)
    - week (默认)
    - today
    - yesterday
    - month
    - three_months
    - all

响应:
  HTML 页面，包含:
  - 势力统计图表
  - 每日击杀/死亡/得分趋势
  - 排行榜展示
  - 总体统计数据

示例:
  GET /?date_range=week
```

---

## 战斗相关

### 获取上传页面
```
GET /battle/upload

响应:
  HTML 上传表单页面
```

### 上传战斗日志
```
POST /battle/upload
Content-Type: multipart/form-data

参数:
  file: file (必需)
    - 格式: .txt
    - 最大大小: 16MB

响应:
  成功: 重定向到 /battle/rankings
        flash 消息: "文件解析成功，数据已保存"
  失败: 重定向到上传页面
        flash 消息: 错误信息

示例:
  curl -F "file=@battle_log.txt" http://localhost:5000/battle/upload
```

### 获取排名页面
```
GET /battle/rankings
Query Parameters:
  faction: string (可选)
    - 梵天
    - 比湿奴
    - 湿婆
    - all (默认: 比湿奴)
  
  job: string (可选)
    - 职业名称
    - all
  
  time_range: string (可选)
    - today
    - yesterday
    - week (默认)
    - month
    - three_months
    - all
  
  start_datetime: string (可选)
    - 格式: YYYY-MM-DD HH:MM:SS
    - 与 end_datetime 配合使用
  
  end_datetime: string (可选)
    - 格式: YYYY-MM-DD HH:MM:SS
  
  show_grouped: boolean (可选)
    - true: 按玩家分组显示
    - false (默认): 按单个ID显示

响应:
  HTML 排名页面，包含:
  - 玩家排名表格
  - 筛选器
  - 统计数据

示例:
  GET /battle/rankings?faction=比湿奴&time_range=week
  GET /battle/rankings?faction=梵天&job=法师&time_range=today
  GET /battle/rankings?start_datetime=2025-01-01%2000:00:00&end_datetime=2025-01-15%2023:59:59
```

### 获取玩家详情
```
GET /battle/player/<player_name>

路径参数:
  player_name: string (必需)
    - 玩家游戏ID

响应:
  HTML 玩家详情页面，包含:
  - 基本信息 (击杀、死亡、得分等)
  - 击杀详情 (被击杀的对手)
  - 死亡详情 (击杀自己的对手)

示例:
  GET /battle/player/玩家名
```

---

## 排行榜相关

### 获取排行榜数据
```
GET /ranking/data
Query Parameters:
  category: string (可选)
    - 主神排行榜 (默认)
  
  refresh: boolean (可选)
    - true: 强制刷新
    - false (默认): 使用缓存

响应:
  JSON
  {
    "category": "主神排行榜",
    "update_time": "2025-01-15 10:30:00",
    "data": [...]  // 排行榜数据
  }

缓存策略:
  - 24小时内返回缓存数据
  - 超过24小时自动刷新
  - refresh=true 强制刷新

示例:
  GET /ranking/data?category=主神排行榜
  GET /ranking/data?category=主神排行榜&refresh=true
```

### 手动刷新排行榜
```
POST /ranking/refresh
Content-Type: application/x-www-form-urlencoded

参数:
  category: string (可选)
    - 主神排行榜 (默认)

响应:
  JSON
  {
    "status": "success",
    "message": "排行榜数据已成功刷新",
    "ranking_id": 123,
    "data": [...]
  }
  
  或
  
  {
    "status": "error",
    "message": "错误信息"
  }

示例:
  curl -X POST -d "category=主神排行榜" http://localhost:5000/ranking/refresh
```

### 获取排行榜历史
```
GET /ranking/history
Query Parameters:
  category: string (可选)
    - 主神排行榜 (默认)
  
  limit: integer (可选)
    - 返回记录数 (默认: 10, 最大: 100)

响应:
  JSON
  {
    "status": "success",
    "message": "成功获取'主神排行榜'分类的历史数据",
    "data": [
      {
        "id": 1,
        "category": "主神排行榜",
        "update_time": "2025-01-15 10:30:00",
        "create_time": "2025-01-15 10:30:00",
        "data": {...}
      },
      ...
    ]
  }

示例:
  GET /ranking/history?category=主神排行榜&limit=10
```

---

## 玩家管理相关

### 获取玩家列表
```
GET /person
Query Parameters:
  page: integer (可选)
    - 页码 (默认: 1)
  
  per_page: integer (可选)
    - 每页数量 (默认: 20)

响应:
  HTML 玩家列表页面
```

### 创建玩家
```
POST /person
Content-Type: application/json

参数:
  {
    "name": "玩家名",
    "god": "梵天|比湿奴|湿婆",
    "union_name": "战盟名",
    "job": "职业",
    "level": "等级"
  }

响应:
  JSON
  {
    "status": "success",
    "message": "玩家创建成功",
    "player_id": 123
  }
```

### 更新玩家
```
PUT /person/<player_id>
Content-Type: application/json

参数:
  {
    "name": "新名字",
    "god": "新势力",
    "union_name": "新战盟",
    "job": "新职业",
    "level": "新等级"
  }

响应:
  JSON
  {
    "status": "success",
    "message": "玩家信息已更新"
  }
```

### 删除玩家
```
DELETE /person/<player_id>

响应:
  JSON
  {
    "status": "success",
    "message": "玩家已删除"
  }
```

---

## 玩家分组相关

### 获取分组列表
```
GET /player_group

响应:
  HTML 分组列表页面
```

### 创建分组
```
POST /player_group
Content-Type: application/json

参数:
  {
    "group_name": "分组名称",
    "description": "分组描述"
  }

响应:
  JSON
  {
    "status": "success",
    "message": "分组创建成功",
    "group_id": 123
  }
```

### 关联玩家到分组
```
POST /player_group/<group_id>/add_player
Content-Type: application/json

参数:
  {
    "player_id": 123
  }

响应:
  JSON
  {
    "status": "success",
    "message": "玩家已关联到分组"
  }
```

---

## 数据导出相关

### 导出排名数据为 JSON
```
GET /battle/export
Query Parameters:
  faction: string (可选)
    - 梵天
    - 比湿奴
    - 湿婆
    - 不指定则导出所有

响应:
  JSON 文件下载
  {
    "export_time": "2025-01-15 10:30:00",
    "faction_filter": "比湿奴",
    "players": [
      {
        "id": 1,
        "name": "玩家名",
        "faction": "比湿奴",
        "kills": 100,
        "deaths": 50,
        "blessings": 10,
        "score": 260,
        "kd_ratio": 2.0
      },
      ...
    ]
  }

示例:
  GET /battle/export?faction=比湿奴
```

---

## 错误响应

### 404 Not Found
```
GET /nonexistent

响应:
  HTML 404 页面
```

### 500 Internal Server Error
```
响应:
  HTML 500 页面
```

### 未授权 (401)
```
访问受保护路由但未登录

响应:
  重定向到登录页面
```

---

## 数据模型

### 玩家对象
```json
{
  "id": 1,
  "name": "玩家名",
  "god": "梵天",
  "union_name": "战盟名",
  "job": "职业",
  "level": "等级",
  "created_at": "2025-01-15 10:30:00",
  "updated_at": "2025-01-15 10:30:00"
}
```

### 战斗记录对象
```json
{
  "id": 1,
  "win": "胜者名",
  "lost": "败者名",
  "position": "X,Y",
  "remark": 1,
  "publish_at": "2025-01-15 10:30:00",
  "created_at": "2025-01-15 10:30:00"
}
```

### 排名对象
```json
{
  "id": 1,
  "name": "玩家名",
  "faction": "梵天",
  "kills": 100,
  "deaths": 50,
  "blessings": 10,
  "score": 260,
  "kd_ratio": 2.0
}
```

### 势力统计对象
```json
{
  "faction": "梵天",
  "player_count": 50,
  "total_kills": 1000,
  "total_deaths": 800,
  "total_blessings": 100,
  "top_killer": {
    "name": "玩家名",
    "kills": 100
  },
  "top_scorer": {
    "name": "玩家名",
    "score": 260
  }
}
```

---

## 速率限制

当前无速率限制。

---

## 版本历史

### v1.0 (2025-01-15)
- 初始版本
- 支持战斗记录上传
- 支持玩家排名查询
- 支持势力统计
- 支持排行榜缓存

---

## 常见问题

### Q: 如何获取某玩家的详细信息?
A: 使用 `GET /battle/player/<player_name>` 端点

### Q: 如何导出排名数据?
A: 使用 `GET /battle/export?faction=比湿奴` 端点

### Q: 排行榜数据多久更新一次?
A: 24小时自动更新，或使用 `refresh=true` 参数强制刷新

### Q: 支持哪些时间范围?
A: today, yesterday, week, month, three_months, all

### Q: 如何计算玩家得分?
A: score = kills * 3 + blessings - deaths

---

**文档版本**: 1.0  
**最后更新**: 2025-01-15  
**项目**: kongbai
