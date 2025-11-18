# 移动端 API 接口文档

## 概述

本文档描述了为移动端应用提供的 RESTful API 接口。所有接口都返回 JSON 格式数据，并使用 JWT Token 进行认证。

## 基础信息

- **Base URL**: `http://your-domain.com`
- **认证方式**: JWT Token (Bearer Token)
- **响应格式**: JSON
- **字符编码**: UTF-8

## 通用响应格式

### 成功响应
```json
{
  "status": "success",
  "message": "操作成功",
  "data": {
    // 具体数据
  }
}
```

### 错误响应
```json
{
  "status": "error",
  "message": "错误描述"
}
```

## 认证相关接口

### 1. 登录

**接口**: `POST /api/auth/login`

**描述**: 用户登录，获取 JWT Token

**请求头**:
```
Content-Type: application/json
```

**请求体**:
```json
{
  "username": "admin",
  "password": "admin123"
}
```

**响应示例**:
```json
{
  "status": "success",
  "message": "登录成功",
  "data": {
    "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "user": {
      "user_id": "admin",
      "username": "admin"
    }
  }
}
```

### 2. 登出

**接口**: `POST /api/auth/logout`

**描述**: 用户登出

**请求头**:
```
Authorization: Bearer <token>
```

**响应示例**:
```json
{
  "status": "success",
  "message": "登出成功"
}
```

### 3. 验证 Token

**接口**: `GET /api/auth/verify`

**描述**: 验证 Token 是否有效

**请求头**:
```
Authorization: Bearer <token>
```

**响应示例**:
```json
{
  "status": "success",
  "message": "Token 有效",
  "data": {
    "user": {
      "user_id": "admin",
      "username": "admin"
    }
  }
}
```

## 首页数据接口

### 4. 获取首页仪表盘数据

**接口**: `GET /api/dashboard`

**描述**: 获取首页统计数据、图表数据、排行榜等

**请求头**:
```
Authorization: Bearer <token>
```

**查询参数**:
- `date_range` (可选): 时间范围，可选值: `today`, `yesterday`, `week`, `month`, `three_months`, `all`，默认 `week`

**请求示例**:
```
GET /api/dashboard?date_range=week
```

**响应示例**:
```json
{
  "status": "success",
  "message": "获取首页数据成功",
  "data": {
    "summary": {
      "total_kills": 15234,
      "total_deaths": 12456,
      "total_blessings": 3456,
      "total_players": 234
    },
    "faction_stats": {
      "chart_data": {
        "factions": ["梵天", "比湿奴", "湿婆"],
        "kills": [5000, 6000, 4234],
        "deaths": [4000, 5000, 3456],
        "blessings": [1200, 1400, 856]
      },
      "player_counts": {
        "梵天": 78,
        "比湿奴": 89,
        "湿婆": 67
      },
      "statistics": [
        {
          "faction": "梵天",
          "player_count": 78,
          "total_kills": 5000
        }
      ]
    },
    "top_rankings": {
      "top_killers": [
        {
          "name": "玩家1",
          "faction": "比湿奴",
          "kills": 234
        }
      ],
      "top_scorers": [],
      "top_deaths": []
    },
    "daily_trends": {
      "kills": {
        "dates": ["2024-01-01", "2024-01-02"],
        "players": []
      },
      "deaths": {},
      "scores": {}
    },
    "date_range": "week"
  }
}
```

## 战斗数据接口

### 5. 获取玩家排名列表

**接口**: `GET /battle/api/rankings`

**描述**: 获取玩家排名列表，支持多种筛选条件

**请求头**:
```
Authorization: Bearer <token>
```

**查询参数**:
- `faction` (可选): 势力筛选，可选值: `梵天`, `比湿奴`, `湿婆`, `all`
- `job` (可选): 职业筛选
- `time_range` (可选): 时间范围，可选值: `today`, `yesterday`, `week`, `month`, `three_months`, `all`，默认 `today`
- `start_datetime` (可选): 自定义开始时间，格式: `YYYY-MM-DD HH:MM:SS`
- `end_datetime` (可选): 自定义结束时间，格式: `YYYY-MM-DD HH:MM:SS`

**请求示例**:
```
GET /battle/api/rankings?faction=比湿奴&time_range=week
```

**响应示例**:
```json
{
  "status": "success",
  "message": "获取排名成功",
  "data": {
    "rankings": [
      {
        "rank": 1,
        "id": 123,
        "name": "玩家1",
        "faction": "比湿奴",
        "job": "战士",
        "kills": 234,
        "deaths": 45,
        "blessings": 56,
        "score": 713
      }
    ],
    "filters": {
      "faction": "比湿奴",
      "job": null,
      "time_range": "week"
    }
  }
}
```

### 6. 获取玩家详细信息

**接口**: `GET /battle/api/player/<player_name>`

**描述**: 获取指定玩家的详细战斗信息

**请求头**:
```
Authorization: Bearer <token>
```

**路径参数**:
- `player_name`: 玩家名称

**查询参数**:
- `time_range` (可选): 时间范围
- `start_datetime` (可选): 自定义开始时间
- `end_datetime` (可选): 自定义结束时间

**请求示例**:
```
GET /battle/api/player/玩家1?time_range=week
```

**响应示例**:
```json
{
  "status": "success",
  "message": "获取玩家详情成功",
  "data": {
    "id": 123,
    "name": "玩家1",
    "faction": "比湿奴",
    "job": "战士",
    "kills": 234,
    "deaths": 45,
    "blessings": 56,
    "score": 713,
    "kill_details": [],
    "death_details": []
  }
}
```

### 7. 上传战斗日志

**接口**: `POST /battle/api/upload`

**描述**: 上传战斗日志文件（.txt 格式）

**请求头**:
```
Authorization: Bearer <token>
Content-Type: multipart/form-data
```

**请求体**:
- `file`: 文件对象（.txt 格式）

**响应示例**:
```json
{
  "status": "success",
  "message": "文件解析成功，数据已保存",
  "data": {
    "battle_count": 150,
    "blessing_count": 30
  }
}
```

### 8. 获取势力统计数据

**接口**: `GET /battle/api/faction_stats`

**描述**: 获取各势力的统计数据

**请求头**:
```
Authorization: Bearer <token>
```

**查询参数**:
- `date_range` (可选): 时间范围，默认 `week`

**请求示例**:
```
GET /battle/api/faction_stats?date_range=week
```

**响应示例**:
```json
{
  "status": "success",
  "message": "获取势力统计成功",
  "data": {
    "faction_stats": [
      {
        "faction": "梵天",
        "player_count": 78,
        "total_kills": 5000,
        "total_deaths": 4000
      }
    ],
    "date_range": "week"
  }
}
```

## 排行榜接口

### 9. 获取排行榜数据

**接口**: `GET /ranking/api/data`

**描述**: 获取官方排行榜数据（从游戏官网抓取）

**请求头**:
```
Authorization: Bearer <token>
```

**查询参数**:
- `category` (可选): 排行榜分类，默认 `主神排行榜`
- `refresh` (可选): 是否强制刷新，`true` 或 `false`，默认 `false`

**请求示例**:
```
GET /ranking/api/data?category=主神排行榜&refresh=false
```

**响应示例**:
```json
{
  "status": "success",
  "message": "获取排行榜数据成功",
  "data": {
    "category": "主神排行榜",
    "update_time": "2024-01-15 10:30:00",
    "rankings": []
  }
}
```

### 10. 刷新排行榜数据

**接口**: `POST /ranking/api/refresh`

**描述**: 手动刷新排行榜数据

**请求头**:
```
Authorization: Bearer <token>
Content-Type: application/json
```

**请求体**:
```json
{
  "category": "主神排行榜"
}
```

**响应示例**:
```json
{
  "status": "success",
  "message": "排行榜数据已成功刷新",
  "data": {
    "ranking_id": 456,
    "ranking_data": {}
  }
}
```

### 11. 获取排行榜历史数据

**接口**: `GET /ranking/api/history`

**描述**: 获取排行榜的历史记录

**请求头**:
```
Authorization: Bearer <token>
```

**查询参数**:
- `category` (可选): 排行榜分类，默认 `主神排行榜`
- `limit` (可选): 返回记录数量，默认 10，最大 100

**请求示例**:
```
GET /ranking/api/history?category=主神排行榜&limit=10
```

**响应示例**:
```json
{
  "status": "success",
  "message": "成功获取'主神排行榜'分类的历史数据",
  "data": [
    {
      "id": 456,
      "category": "主神排行榜",
      "update_time": "2024-01-15 10:30:00",
      "create_time": "2024-01-15 10:30:00",
      "data": {}
    }
  ]
}
```

## 认证说明

### Token 使用方式

所有需要认证的接口都支持两种方式传递 Token：

#### 方式 1: Authorization Header（推荐）
```
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

#### 方式 2: Query Parameter
```
GET /api/dashboard?token=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

### Token 有效期

- Token 有效期为 **24 小时**
- Token 过期后需要重新登录获取新的 Token

### 错误码说明

| HTTP 状态码 | 说明 |
|------------|------|
| 200 | 请求成功 |
| 400 | 请求参数错误 |
| 401 | 未认证或 Token 无效 |
| 404 | 资源不存在 |
| 500 | 服务器内部错误 |

## 时间范围参数说明

`time_range` 参数可选值：

| 值 | 说明 |
|----|------|
| `today` | 今天 |
| `yesterday` | 昨天 |
| `week` | 最近 7 天 |
| `month` | 最近 30 天 |
| `three_months` | 最近 90 天 |
| `all` | 最近 365 天 |

## 势力列表

| 势力名称 | 说明 |
|---------|------|
| `梵天` | 梵天势力 |
| `比湿奴` | 比湿奴势力 |
| `湿婆` | 湿婆势力 |

## 计分规则

玩家得分计算公式：
```
score = kills × 3 + blessings - deaths
```

- `kills`: 击杀数
- `blessings`: 祝福数
- `deaths`: 死亡数

## 使用示例

### JavaScript (Axios)

```javascript
// 登录
const loginResponse = await axios.post('http://your-domain.com/api/auth/login', {
  username: 'admin',
  password: 'admin123'
});

const token = loginResponse.data.data.token;

// 获取排名
const rankingsResponse = await axios.get('http://your-domain.com/battle/api/rankings', {
  headers: {
    'Authorization': `Bearer ${token}`
  },
  params: {
    faction: '比湿奴',
    time_range: 'week'
  }
});

console.log(rankingsResponse.data);
```

### React Native (Fetch)

```javascript
// 登录
const loginResponse = await fetch('http://your-domain.com/api/auth/login', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    username: 'admin',
    password: 'admin123'
  })
});

const loginData = await loginResponse.json();
const token = loginData.data.token;

// 获取首页数据
const dashboardResponse = await fetch('http://your-domain.com/api/dashboard?date_range=week', {
  headers: {
    'Authorization': `Bearer ${token}`
  }
});

const dashboardData = await dashboardResponse.json();
console.log(dashboardData);
```

## 注意事项

1. **所有接口都需要认证**（除了登录接口）
2. **Token 需要妥善保存**，建议使用 AsyncStorage 或 SecureStore
3. **请求失败时检查 message 字段**获取错误详情
4. **上传文件时使用 multipart/form-data**
5. **日期时间格式统一使用 ISO 8601 格式**

## 更新日志

### v1.0.0 (2024-01-15)
- 初始版本
- 支持用户认证
- 支持首页数据获取
- 支持玩家排名查询
- 支持战斗日志上传
- 支持排行榜数据获取
