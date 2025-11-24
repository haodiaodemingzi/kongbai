# 快速启动指南

## 🚀 5 分钟快速上手

### 步骤 1: 安装依赖

```bash
cd BattleStats
npm install
```

### 步骤 2: 配置 API 地址

编辑 `services/api.js` 第 6 行：

```javascript
const API_BASE_URL = 'https://bigmang.top'; // 改成你的服务器地址
```

### 步骤 3: 运行应用

```bash
npm start
```

然后按 `a` 运行 Android 模拟器，或按 `i` 运行 iOS 模拟器。

### 步骤 4: 登录测试

- 用户名: `admin`
- 密码: `admin123`

## ✅ 功能验证清单

登录后，你应该能看到：

- ✅ 首页显示实时统计数据（总击杀、总死亡、玩家数）
- ✅ 势力统计卡片（梵天、比湿奴、湿婆）
- ✅ 点击"查看战绩排名"可以查看玩家排名
- ✅ 支持按时间范围和势力筛选
- ✅ 下拉刷新数据
- ✅ 登出功能

## 🔧 常见问题

### 问题 1: 无法连接服务器

**解决方案**: 
1. 检查 `services/api.js` 中的 API 地址是否正确
2. 确保服务器正在运行
3. 检查网络连接

### 问题 2: 登录失败

**解决方案**:
1. 检查用户名和密码是否正确（admin/admin123）
2. 查看控制台错误信息
3. 确认后端 API 接口正常工作

### 问题 3: 数据不显示

**解决方案**:
1. 检查 token 是否有效（有效期 24 小时）
2. 尝试重新登录
3. 查看控制台网络请求日志

## 📱 测试流程

### 1. 测试登录
```
1. 打开应用
2. 输入用户名: admin
3. 输入密码: admin123
4. 点击登录
5. 应该看到"登录成功"提示
```

### 2. 测试首页数据
```
1. 登录成功后自动进入首页
2. 应该看到统计卡片显示数字
3. 应该看到势力统计列表
4. 数据应该是从服务器获取的真实数据
```

### 3. 测试排名功能
```
1. 点击"查看战绩排名"按钮
2. 应该看到玩家排名列表
3. 点击时间范围筛选（今天、7天、30天等）
4. 点击势力筛选（梵天、比湿奴、湿婆）
5. 下拉刷新列表
```

### 4. 测试登出
```
1. 点击右上角"登出"按钮
2. 应该返回登录页面
3. 本地 token 应该被清除
```

### 5. 测试自动登录
```
1. 登录成功后
2. 关闭应用
3. 重新打开应用
4. 应该自动恢复登录状态，直接进入首页
```

## 🎯 API 测试

### 使用 Postman 测试后端 API

#### 1. 测试登录
```
POST https://bigmang.top/auth/api/login
Content-Type: application/json

{
  "username": "admin",
  "password": "admin123"
}
```

**期望响应**:
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

#### 2. 测试获取排名（需要 token）
```
GET https://bigmang.top/battle/api/rankings?time_range=week&faction=比湿奴
Authorization: Bearer <your_token>
```

**期望响应**:
```json
{
  "status": "success",
  "message": "获取排名成功",
  "data": {
    "rankings": [
      {
        "rank": 1,
        "name": "玩家1",
        "faction": "比湿奴",
        "kills": 100,
        "deaths": 20,
        "score": 280
      }
    ]
  }
}
```

#### 3. 测试获取首页数据（需要 token）
```
GET https://bigmang.top/api/dashboard?date_range=week
Authorization: Bearer <your_token>
```

## 🐛 调试技巧

### 1. 查看控制台日志
```javascript
// 在代码中添加日志
console.log('Token:', token);
console.log('API Response:', response.data);
```

### 2. 查看网络请求
打开 React Native Debugger，在 Network 标签页查看所有网络请求。

### 3. 查看本地存储
```javascript
import AsyncStorage from '@react-native-async-storage/async-storage';

// 查看所有存储的数据
const keys = await AsyncStorage.getAllKeys();
const items = await AsyncStorage.multiGet(keys);
console.log('AsyncStorage:', items);
```

### 4. 清除本地数据
```javascript
import AsyncStorage from '@react-native-async-storage/async-storage';

// 清除所有数据
await AsyncStorage.clear();
```

## 📊 数据流程图

```
用户输入账号密码
    ↓
调用 login() API
    ↓
服务器验证并返回 token
    ↓
保存 token 到 AsyncStorage
    ↓
设置 isLoggedIn = true
    ↓
自动调用 getDashboardData()
    ↓
axios 自动添加 token 到请求头
    ↓
服务器验证 token 并返回数据
    ↓
渲染首页界面
```

## 🔄 Token 生命周期

```
登录成功
    ↓
生成 token (有效期 24 小时)
    ↓
保存到 AsyncStorage
    ↓
每次 API 请求自动添加 token
    ↓
token 过期 (24 小时后)
    ↓
服务器返回 401 错误
    ↓
axios 拦截器清除本地 token
    ↓
用户需要重新登录
```

## 📝 下一步

1. ✅ 确认所有功能正常工作
2. ✅ 根据需求修改 UI 样式
3. ✅ 添加更多功能（玩家详情、数据导出等）
4. ✅ 优化性能和用户体验
5. ✅ 准备发布到应用商店

## 💡 提示

- Token 会自动保存，下次打开应用会自动登录
- 所有 API 请求都会自动添加 token，无需手动处理
- 网络错误会自动显示提示信息
- 数据加载时会显示加载动画

## 📞 需要帮助？

如果遇到问题，请检查：
1. 控制台错误信息
2. 网络请求日志
3. 服务器状态
4. API 地址配置

祝你使用愉快！🎉
