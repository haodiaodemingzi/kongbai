# Battle Stats - 战斗统计移动应用

基于 React Native 的战斗统计移动应用，集成了 JWT Token 认证和完整的 API 调用。

## 功能特性

- ✅ **JWT Token 认证** - 安全的登录认证机制
- ✅ **自动登录** - Token 本地存储，自动恢复登录状态
- ✅ **首页仪表盘** - 实时显示战斗统计数据
- ✅ **玩家排名** - 支持多维度筛选的排名列表
- ✅ **势力统计** - 各势力数据对比展示
- ✅ **主神排行榜** - 官方排行榜数据查看

## 技术栈

- **React Native** - 跨平台移动应用框架
- **Expo** - React Native 开发工具
- **Axios** - HTTP 请求库
- **AsyncStorage** - 本地数据存储
- **JWT** - Token 认证

## 安装步骤

### 1. 安装依赖

```bash
cd BattleStats
npm install
```

### 2. 配置 API 地址

编辑 `services/api.js`，修改 API 基础 URL：

```javascript
const API_BASE_URL = 'https://your-domain.com'; // 改成你的服务器地址
```

### 3. 运行应用

#### Android
```bash
npm run android
```

#### iOS
```bash
npm run ios
```

#### Web
```bash
npm start
```

## 项目结构

```
BattleStats/
├── App.js                      # 主应用入口
├── screens/                    # 页面组件
│   ├── LoginScreen.js         # 登录页面
│   ├── BattleRankingsScreen.js # 战绩排名页面
│   └── RankingsScreen.js      # 主神排行榜页面
├── services/                   # API 服务
│   └── api.js                 # API 调用封装
├── package.json               # 项目配置
└── README.md                  # 项目说明
```

## API 集成说明

### 认证流程

1. **登录获取 Token**
```javascript
import { login } from './services/api';

const result = await login('admin', 'admin123');
if (result.success) {
  const { token, user } = result;
  // Token 会自动保存到 AsyncStorage
}
```

2. **自动添加 Token**
所有 API 请求会自动从 AsyncStorage 读取 token 并添加到请求头：
```
Authorization: Bearer <token>
```

3. **Token 过期处理**
当 token 过期（401 错误）时，会自动清除本地存储，用户需要重新登录。

### 可用的 API 方法

#### 认证相关
- `login(username, password)` - 登录
- `logout()` - 登出
- `verifyToken()` - 验证 token
- `getStoredToken()` - 获取本地 token
- `getStoredUser()` - 获取本地用户信息

#### 数据获取
- `getDashboardData(dateRange)` - 获取首页数据
- `getPlayerRankings(params)` - 获取玩家排名
- `getPlayerDetails(playerName, timeRange)` - 获取玩家详情
- `getFactionStats(dateRange)` - 获取势力统计
- `getRankingData(category, refresh)` - 获取排行榜数据
- `refreshRanking(category)` - 刷新排行榜
- `getRankingHistory(category, limit)` - 获取排行榜历史

#### 文件上传
- `uploadBattleLog(file)` - 上传战斗日志

## 使用示例

### 获取玩家排名

```javascript
import { getPlayerRankings } from './services/api';

const fetchRankings = async () => {
  const result = await getPlayerRankings({
    faction: '比湿奴',
    time_range: 'week',
  });

  if (result.success) {
    const rankings = result.data.rankings;
    // 处理排名数据
  }
};
```

### 获取首页数据

```javascript
import { getDashboardData } from './services/api';

const loadDashboard = async () => {
  const result = await getDashboardData('week');

  if (result.success) {
    const data = result.data;
    // data.summary - 总览数据
    // data.faction_stats - 势力统计
    // data.top_rankings - 排行榜
  }
};
```

## 数据格式

### 登录响应
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

### 排名数据
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

### 首页数据
```json
{
  "status": "success",
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
        "deaths": [4000, 5000, 3456]
      },
      "player_counts": {
        "梵天": 78,
        "比湿奴": 89,
        "湿婆": 67
      }
    }
  }
}
```

## 筛选参数

### 时间范围 (time_range)
- `today` - 今天
- `yesterday` - 昨天
- `week` - 最近 7 天
- `month` - 最近 30 天
- `three_months` - 最近 90 天
- `all` - 全部（最近 365 天）

### 势力 (faction)
- `梵天`
- `比湿奴`
- `湿婆`
- `''` 或 `all` - 全部

## 注意事项

1. **Token 有效期**: Token 有效期为 24 小时，过期后需要重新登录
2. **网络请求超时**: 默认超时时间为 30 秒
3. **错误处理**: 所有 API 方法都返回统一格式：`{ success: boolean, data?: any, message?: string }`
4. **本地存储**: Token 和用户信息存储在 AsyncStorage 中
5. **自动重连**: Token 过期时会自动清除本地数据，引导用户重新登录

## 测试账号

- 用户名: `admin`
- 密码: `admin123`

## 常见问题

### 1. 无法连接服务器
检查 `services/api.js` 中的 `API_BASE_URL` 是否正确。

### 2. Token 过期
Token 有效期为 24 小时，过期后会自动跳转到登录页面。

### 3. 数据加载失败
检查网络连接和服务器状态，查看控制台错误信息。

### 4. AsyncStorage 错误
确保已安装 `@react-native-async-storage/async-storage` 依赖：
```bash
npm install @react-native-async-storage/async-storage
```

## 开发调试

### 查看网络请求
在 `services/api.js` 中，axios 拦截器会打印所有请求和响应信息。

### 查看 Token
```javascript
import { getStoredToken } from './services/api';

const token = await getStoredToken();
console.log('Current token:', token);
```

### 清除本地数据
```javascript
import AsyncStorage from '@react-native-async-storage/async-storage';

await AsyncStorage.clear();
```

## 后续开发

- [ ] 添加下拉刷新功能
- [ ] 添加玩家详情页面
- [ ] 添加战斗日志上传功能
- [ ] 添加图表可视化
- [ ] 添加推送通知
- [ ] 添加离线缓存

## 许可证

MIT
