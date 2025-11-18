# API 蓝图重构说明

## 📋 改动概述

将 API 接口从 `auth.py` 中分离出来，创建独立的 API 蓝图 `api_auth.py`，使代码结构更清晰。

## 🔄 改动内容

### 1. 新建文件

**`app/routes/api_auth.py`** - 独立的 API 认证蓝图

包含以下接口：
- `POST /api/auth/login` - 登录获取 token
- `POST /api/auth/logout` - 登出
- `GET /api/auth/verify` - 验证 token
- `POST /api/auth/refresh` - 刷新 token（新增）

### 2. 修改文件

#### `app/routes/auth.py`
- ✅ 移除了 API 接口部分
- ✅ 保留了 Web 页面相关的路由（login, logout, captcha）
- ✅ 添加注释说明 API 接口已移至 `api_auth.py`

#### `app/__init__.py`
- ✅ 导入新的 `api_auth_bp` 蓝图
- ✅ 注册蓝图到 `/api/auth` 路径
- ✅ 更新日志信息

#### `BattleStats/services/api.js`
- ✅ 更新登录接口路径：`/auth/api/login` → `/api/auth/login`
- ✅ 更新登出接口路径：`/auth/api/logout` → `/api/auth/logout`
- ✅ 更新验证接口路径：`/auth/api/verify` → `/api/auth/verify`

#### 文档更新
- ✅ `MOBILE_API_DOCUMENTATION.md` - 更新所有 API 路径
- ✅ `ENVIRONMENT_SETUP.md` - 更新测试命令中的路径

## 🎯 路由对比

### 改动前
```
/auth/api/login    → auth_bp.api_login()
/auth/api/logout   → auth_bp.api_logout()
/auth/api/verify   → auth_bp.api_verify()
```

### 改动后
```
/api/auth/login    → api_auth_bp.api_login()
/api/auth/logout   → api_auth_bp.api_logout()
/api/auth/verify   → api_auth_bp.api_verify()
/api/auth/refresh  → api_auth_bp.api_refresh_token() (新增)
```

## 📁 文件结构

```
app/
├── routes/
│   ├── auth.py          # Web 页面认证（/auth/login, /auth/logout）
│   ├── api_auth.py      # API 认证（/api/auth/*）⭐ 新建
│   ├── home.py          # 首页
│   ├── battle.py        # 战斗数据
│   └── ...
└── __init__.py          # 注册蓝图
```

## ✨ 优势

### 1. **职责分离**
- Web 页面认证 → `auth.py`
- API 认证 → `api_auth.py`

### 2. **路径更清晰**
- Web: `/auth/*`
- API: `/api/auth/*`

### 3. **易于维护**
- API 接口集中管理
- 不影响现有 Web 功能
- 便于后续扩展

### 4. **符合 RESTful 规范**
- API 路径统一以 `/api/` 开头
- 更容易识别和管理

## 🔧 使用方法

### 后端

#### 启动服务器
```bash
cd c:\coding\kongbai
python run.py
```

服务器会自动注册新的 API 蓝图。

#### 验证路由
```bash
python test_routes.py
```

应该能看到：
```
✅ /api/auth/login 路由已注册
   方法: POST
   端点: api_auth.api_login
```

### 移动端

#### 无需修改代码
移动端的 `services/api.js` 已自动更新路径，无需额外修改。

#### 测试登录
```bash
cd BattleStats
npm start
```

使用测试账号登录：
- 用户名: admin
- 密码: admin123

## 🧪 测试

### 1. 测试本地 API

```bash
# PowerShell
Invoke-WebRequest -Uri "http://localhost:5000/api/auth/login" -Method POST -ContentType "application/json" -Body '{"username":"admin","password":"admin123"}'
```

### 2. 测试生产 API

```bash
# PowerShell
Invoke-WebRequest -Uri "https://bigmang.xyz/api/auth/login" -Method POST -ContentType "application/json" -Body '{"username":"admin","password":"admin123"}'
```

### 3. 测试移动端

1. 启动后端服务器
2. 配置 `BattleStats/config.js` 中的 API 地址
3. 运行移动应用：`npm start`
4. 测试登录功能

## 📊 API 接口列表

### 认证接口（/api/auth）

| 方法 | 路径 | 说明 | 认证 |
|------|------|------|------|
| POST | `/api/auth/login` | 登录获取 token | ❌ |
| POST | `/api/auth/logout` | 登出 | ✅ |
| GET | `/api/auth/verify` | 验证 token | ✅ |
| POST | `/api/auth/refresh` | 刷新 token | ✅ |

### 其他 API 接口

| 方法 | 路径 | 说明 | 认证 |
|------|------|------|------|
| GET | `/api/dashboard` | 首页数据 | ✅ |
| GET | `/battle/api/rankings` | 玩家排名 | ✅ |
| GET | `/battle/api/player/<name>` | 玩家详情 | ✅ |
| POST | `/battle/api/upload` | 上传日志 | ✅ |
| GET | `/battle/api/faction_stats` | 势力统计 | ✅ |
| GET | `/ranking/api/data` | 排行榜数据 | ✅ |
| POST | `/ranking/api/refresh` | 刷新排行榜 | ✅ |
| GET | `/ranking/api/history` | 排行榜历史 | ✅ |

## 🔒 安全性

### Token 认证
所有 API 接口（除了登录）都需要在请求头中携带 token：
```
Authorization: Bearer <token>
```

### Token 刷新
新增 `/api/auth/refresh` 接口，可以在 token 即将过期时刷新：
```javascript
const result = await apiClient.post('/api/auth/refresh');
const newToken = result.data.data.token;
```

## 📝 注意事项

1. **重启服务器**
   - 修改后需要重启后端服务器才能生效

2. **清除缓存**
   - 如果遇到问题，清除移动端的 AsyncStorage 缓存

3. **检查路径**
   - 确保所有 API 调用都使用新的路径 `/api/auth/*`

4. **生产部署**
   - 部署到生产环境时，确保新的蓝图已正确注册

## 🎉 总结

✅ API 接口已成功分离到独立蓝图
✅ 路径更加清晰和规范
✅ 代码结构更易维护
✅ 移动端已自动适配新路径
✅ 所有文档已更新

现在可以重启后端服务器并测试新的 API 路径了！
