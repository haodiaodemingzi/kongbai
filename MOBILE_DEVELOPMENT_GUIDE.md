# React Native 移动端开发指南

## 项目初始化

### 1. 创建项目

```bash
# 使用 React Native CLI
npx react-native init BattleStatsMobile --template react-native-template-typescript

# 或使用 Expo
npx create-expo-app BattleStatsMobile
```

### 2. 安装依赖

```bash
cd BattleStatsMobile
npm install

# 安装项目依赖
npm install @react-navigation/native @react-navigation/bottom-tabs @react-navigation/stack
npm install react-redux redux redux-thunk
npm install axios react-native-chart-kit
npm install react-native-gesture-handler react-native-reanimated react-native-screens react-native-safe-area-context
npm install react-native-vector-icons
npm install @react-native-async-storage/async-storage
npm install react-native-toast-message
npm install react-native-loading-spinner-overlay
npm install react-native-linear-gradient
npm install react-native-file-picker
npm install date-fns lodash
```

### 3. 链接原生模块 (仅 React Native)

```bash
npx react-native link react-native-vector-icons
npx react-native link react-native-linear-gradient
npx react-native link @react-native-async-storage/async-storage
```

### 4. 项目结构

```
mobile/
├── src/
│   ├── screens/              # 屏幕组件
│   ├── components/           # 可复用组件
│   ├── services/            # API 服务
│   ├── store/               # Redux 状态管理
│   ├── styles/              # 全局样式
│   ├── navigation/          # 导航配置
│   ├── utils/               # 工具函数
│   └── App.js               # 应用入口
├── assets/                  # 资源文件
├── android/                 # Android 原生代码
├── ios/                     # iOS 原生代码 (后续)
├── package.json
├── babel.config.js
├── metro.config.js
└── index.js
```

---

## 开发流程

### 1. 启动开发服务器

```bash
# Android
npm run android

# 或手动启动
npx react-native start
npx react-native run-android
```

### 2. 热重载

- **快速刷新**: 按 `R` 两次
- **完全重新加载**: 按 `R` 一次
- **打开开发菜单**: 按 `M` (Android)

### 3. 调试

```bash
# 打开 React Native Debugger
# 或使用 Chrome DevTools
# 在开发菜单中选择 "Debug with Chrome"
```

---

## 核心功能实现

### 1. 认证流程

```javascript
// 登录
import { useDispatch } from 'react-redux';
import { login } from '../store/reducers/authReducer';

const dispatch = useDispatch();
await dispatch(login(username, password));

// 登出
import { logout } from '../store/reducers/authReducer';
await dispatch(logout());
```

### 2. 获取排名数据

```javascript
import { rankingService } from '../services/ranking';

// 获取玩家排名
const players = await rankingService.getPlayerRankings(
  faction = '比湿奴',
  timeRange = 'week',
  job = null
);

// 获取玩家详情
const detail = await rankingService.getPlayerDetail('玩家名');

// 获取首页统计
const stats = await rankingService.getFactionStats('week');
```

### 3. 上传战斗日志

```javascript
import { battleService } from '../services/battle';
import { DocumentPicker } from 'react-native-document-picker';

// 选择文件
const result = await DocumentPicker.pick({
  type: [DocumentPicker.types.plainText]
});

// 上传
await battleService.uploadBattleLog(result.uri, result.name);
```

### 4. 状态管理

```javascript
// 使用 Redux
import { useSelector, useDispatch } from 'react-redux';

const user = useSelector(state => state.auth.user);
const players = useSelector(state => state.ranking.players);
const dispatch = useDispatch();

// 分发 action
dispatch(fetchPlayerRankings('比湿奴', 'week'));
```

---

## 屏幕开发指南

### 1. 首页屏幕 (HomeScreen)

**功能**:
- 显示总击杀、死亡、得分
- 显示势力对比图表
- 显示排行榜预览
- 支持下拉刷新

**实现步骤**:
1. 获取首页数据 (`getFactionStats`)
2. 渲染统计卡片
3. 集成图表库 (react-native-chart-kit)
4. 实现下拉刷新

### 2. 排名屏幕 (RankingScreen)

**功能**:
- 显示玩家排名列表
- 筛选器 (势力、职业、时间)
- 点击进入玩家详情
- 支持下拉刷新

**实现步骤**:
1. 创建筛选器组件
2. 获取排名数据 (`getPlayerRankings`)
3. 渲染排名列表 (FlatList)
4. 实现导航到玩家详情

### 3. 玩家详情屏幕 (PlayerDetailScreen)

**功能**:
- 显示玩家基本信息
- 显示统计数据
- 显示击杀/死亡详情
- 标签页切换

**实现步骤**:
1. 获取玩家详情 (`getPlayerDetail`)
2. 渲染玩家头部信息
3. 创建标签页组件
4. 显示击杀/死亡列表

### 4. 上传屏幕 (UploadScreen)

**功能**:
- 文件选择
- 上传进度显示
- 上传历史

**实现步骤**:
1. 集成文件选择器
2. 显示选择的文件
3. 上传文件并显示进度
4. 显示上传结果

### 5. 个人资料屏幕 (ProfileScreen)

**功能**:
- 显示用户信息
- 显示统计数据
- 账号设置
- 登出

**实现步骤**:
1. 从 Redux 获取用户信息
2. 渲染用户头部
3. 显示统计数据
4. 创建设置菜单

---

## 组件开发指南

### 1. 通用组件

#### Button 组件
```javascript
<Button
  title="登录"
  onPress={handleLogin}
  variant="primary"      // primary | secondary | outline
  size="large"           // small | medium | large
  loading={isLoading}
  disabled={isDisabled}
/>
```

#### Input 组件
```javascript
<Input
  placeholder="输入用户名"
  value={username}
  onChangeText={setUsername}
  icon="user"
  label="用户名"
  error={error}
/>
```

#### Card 组件
```javascript
<Card
  title="统计数据"
  subtitle="最近7天"
>
  {children}
</Card>
```

### 2. 排名组件

#### RankingCard 组件
```javascript
<RankingCard
  rank={1}
  playerName="玩家A"
  faction="梵天"
  kills={100}
  deaths={50}
  score={260}
  kd={2.0}
  onPress={handlePress}
/>
```

#### FactionCard 组件
```javascript
<FactionCard
  faction="梵天"
  playerCount={50}
  totalKills={1000}
  totalDeaths={800}
  color={colors.faction.brahma}
/>
```

### 3. 图表组件

#### 柱状图
```javascript
import { BarChart } from 'react-native-chart-kit';

<BarChart
  data={{
    labels: ['梵天', '比湿奴', '湿婆'],
    datasets: [{
      data: [100, 150, 120]
    }]
  }}
  width={screenWidth}
  height={220}
/>
```

#### 折线图
```javascript
import { LineChart } from 'react-native-chart-kit';

<LineChart
  data={{
    labels: ['周一', '周二', '周三', '周四', '周五'],
    datasets: [{
      data: [10, 15, 20, 18, 25]
    }]
  }}
  width={screenWidth}
  height={220}
/>
```

---

## API 集成

### 1. 配置 API 基础 URL

```javascript
// services/api.js
const API_BASE_URL = 'http://your-backend-url.com';

// 开发环境
const API_BASE_URL = 'http://192.168.1.100:5000';

// 生产环境
const API_BASE_URL = 'https://api.yourdomain.com';
```

### 2. 请求拦截器

```javascript
// 自动添加 token
api.interceptors.request.use(
  async (config) => {
    const token = await AsyncStorage.getItem('authToken');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  }
);
```

### 3. 响应拦截器

```javascript
// 处理 401 错误
api.interceptors.response.use(
  response => response.data,
  error => {
    if (error.response?.status === 401) {
      // 清除 token 并重定向到登录
      AsyncStorage.removeItem('authToken');
    }
    return Promise.reject(error);
  }
);
```

---

## 性能优化

### 1. 列表优化

```javascript
import { FlatList } from 'react-native';

<FlatList
  data={players}
  renderItem={({ item }) => <PlayerCard player={item} />}
  keyExtractor={item => item.id.toString()}
  removeClippedSubviews={true}
  maxToRenderPerBatch={10}
  updateCellsBatchingPeriod={50}
  initialNumToRender={10}
/>
```

### 2. 图片优化

```javascript
import { Image } from 'react-native';

<Image
  source={{ uri: imageUrl }}
  style={{ width: 100, height: 100 }}
  resizeMode="cover"
/>
```

### 3. 组件优化

```javascript
import { memo } from 'react';

const PlayerCard = memo(({ player, onPress }) => (
  // 组件内容
), (prevProps, nextProps) => {
  return prevProps.player.id === nextProps.player.id;
});
```

### 4. 状态优化

```javascript
// 使用 useCallback 避免不必要的重新创建函数
const handlePress = useCallback(() => {
  navigation.navigate('PlayerDetail', { playerName });
}, [playerName]);

// 使用 useMemo 缓存计算结果
const sortedPlayers = useMemo(() => {
  return players.sort((a, b) => b.score - a.score);
}, [players]);
```

---

## 测试

### 1. 单元测试

```javascript
// __tests__/utils.test.js
import { calculateScore } from '../utils/helpers';

describe('calculateScore', () => {
  it('should calculate score correctly', () => {
    const score = calculateScore(100, 50, 10);
    expect(score).toBe(260);
  });
});
```

### 2. 集成测试

```javascript
// __tests__/auth.test.js
import { authService } from '../services/auth';

describe('authService', () => {
  it('should login successfully', async () => {
    const result = await authService.login('user', 'pass');
    expect(result.token).toBeDefined();
  });
});
```

### 3. 运行测试

```bash
npm test
npm test -- --coverage
```

---

## 打包和发布

### 1. Android 打包

```bash
# 生成签名密钥
keytool -genkey -v -keystore my-release-key.keystore -keyalg RSA -keysize 2048 -validity 10000 -alias my-key-alias

# 构建 APK
npm run build:android

# 构建 AAB (Google Play)
npm run build:android:bundle
```

### 2. 版本管理

```json
// package.json
{
  "version": "1.0.0",
  "versionCode": 1
}
```

### 3. 发布到 Google Play

1. 创建 Google Play 开发者账户
2. 创建应用
3. 填写应用信息
4. 上传 AAB 文件
5. 提交审核

---

## 常见问题

### Q: 如何处理网络错误?
A: 在 API 响应拦截器中处理，显示 Toast 提示用户。

### Q: 如何实现离线支持?
A: 使用 AsyncStorage 缓存数据，检查网络连接状态。

### Q: 如何优化应用大小?
A: 使用代码分割、移除未使用的依赖、优化图片。

### Q: 如何调试 Redux?
A: 使用 Redux DevTools 或 React Native Debugger。

### Q: 如何处理深层链接?
A: 在导航配置中设置 linking 配置。

---

## 开发工具

### 1. 必需工具

- **Node.js**: v14+
- **Android Studio**: 最新版本
- **Android SDK**: API 30+
- **Java Development Kit (JDK)**: 11+

### 2. 推荐工具

- **Visual Studio Code**: 代码编辑器
- **React Native Debugger**: 调试工具
- **Redux DevTools**: 状态管理调试
- **Flipper**: Facebook 开发工具

### 3. 浏览器扩展

- **React Developer Tools**
- **Redux DevTools**

---

## 资源链接

- [React Native 官方文档](https://reactnative.dev/)
- [React Navigation 文档](https://reactnavigation.org/)
- [Redux 官方文档](https://redux.js.org/)
- [Axios 文档](https://axios-http.com/)
- [React Native Chart Kit](https://github.com/indiespirit/react-native-chart-kit)

---

## 下一步

1. ✅ 完成项目初始化
2. ✅ 实现认证模块
3. ✅ 实现首页屏幕
4. ✅ 实现排名屏幕
5. ✅ 实现玩家详情屏幕
6. ✅ 实现上传屏幕
7. ✅ 实现个人资料屏幕
8. ✅ 集成图表库
9. ✅ 性能优化
10. ✅ 测试和调试
11. ✅ 打包发布

---

**文档完成时间**: 2025-01-15  
**应用名称**: Battle Stats (战斗统计)  
**平台**: Android (React Native)
