# React Native 移动端应用 - 快速启动指南

## 前置要求

### 1. 系统环境
- **Node.js**: v14+ (推荐 v16+)
- **npm**: v6+ 或 **yarn**
- **Java Development Kit (JDK)**: 11+
- **Android Studio**: 最新版本
- **Android SDK**: API 30+

### 2. 检查环境

```bash
# 检查 Node.js 版本
node --version

# 检查 npm 版本
npm --version

# 检查 Java 版本
java -version
```

---

## 安装步骤

### 第1步：安装依赖

```bash
# 进入项目目录
cd c:\coding\kongbai\mobile

# 使用 npm 安装依赖
npm install

# 或使用 yarn
yarn install
```

**预计时间**: 5-10 分钟

### 第2步：配置 Android 环境

#### 方式 A：使用 Android Studio (推荐)

1. 打开 Android Studio
2. 点击 "AVD Manager"
3. 创建或选择一个 Android 虚拟设备
4. 启动虚拟设备

#### 方式 B：使用真实 Android 设备

1. 连接 Android 设备到电脑
2. 启用 USB 调试
3. 运行命令验证连接：
```bash
adb devices
```

### 第3步：配置 API 基础 URL

编辑文件 `src/services/api.js`，修改 API 基础 URL：

```javascript
// 开发环境 (本地后端)
const API_BASE_URL = 'http://192.168.1.100:5000';

// 或生产环境
const API_BASE_URL = 'https://api.yourdomain.com';
```

**重要**: 将 `192.168.1.100` 替换为你的后端服务器 IP 地址

### 第4步：启动应用

```bash
# 启动 Metro 服务器 (终端1)
npm start

# 在另一个终端运行 Android 应用 (终端2)
npm run android
```

**或者一步到位**:
```bash
npm run android
```

---

## 常见问题排查

### 问题 1: "command not found: npm"
**解决**: 确保 Node.js 已正确安装，重启终端

### 问题 2: "ANDROID_HOME is not set"
**解决**: 设置环境变量
```bash
# Windows (PowerShell)
$env:ANDROID_HOME = "C:\Users\YourUsername\AppData\Local\Android\Sdk"
$env:PATH += ";$env:ANDROID_HOME\platform-tools"
```

### 问题 3: "No connected devices"
**解决**: 
- 确保虚拟设备已启动
- 或连接真实设备并启用 USB 调试

### 问题 4: "Metro bundler error"
**解决**: 清除缓存并重启
```bash
npm start -- --reset-cache
```

### 问题 5: 依赖安装失败
**解决**: 清除 node_modules 并重新安装
```bash
rm -r node_modules
npm install
```

---

## 开发工作流

### 启动开发服务器

```bash
npm start
```

### 在 Android 上运行

```bash
npm run android
```

### 热重载

- 按 `R` 两次快速刷新
- 按 `M` 打开开发菜单

### 调试

1. 按 `M` 打开开发菜单
2. 选择 "Debug with Chrome"
3. 打开 Chrome DevTools

---

## 项目结构

```
mobile/
├── src/
│   ├── screens/              # 屏幕组件
│   ├── components/           # 通用组件
│   ├── services/            # API 服务
│   ├── store/               # Redux 状态管理
│   ├── styles/              # 样式系统
│   ├── navigation/          # 导航配置
│   └── App.js               # 应用入口
├── android/                 # Android 原生代码
├── package.json             # 项目配置
├── babel.config.js          # Babel 配置
├── metro.config.js          # Metro 配置
└── index.js                 # 应用入口点
```

---

## 可用命令

```bash
# 启动开发服务器
npm start

# 运行 Android 应用
npm run android

# 构建 APK
npm run build:android

# 构建 AAB (Google Play)
npm run build:android:bundle

# 运行测试
npm test

# 代码检查
npm run lint

# 清除缓存
npm start -- --reset-cache
```

---

## 首次运行检查清单

- [ ] Node.js 已安装 (v14+)
- [ ] Java JDK 已安装 (11+)
- [ ] Android SDK 已安装
- [ ] Android 虚拟设备已创建或真实设备已连接
- [ ] 依赖已安装 (`npm install`)
- [ ] API 基础 URL 已配置
- [ ] 后端服务已启动

---

## 测试登录

### 测试账户

使用你的后端系统中的任何有效账户登录。

### 测试流程

1. 启动应用
2. 输入用户名和密码
3. 点击登录
4. 应该看到首页仪表盘

---

## 性能优化建议

### 开发阶段
- 使用虚拟设备 (更快的迭代)
- 启用 Fast Refresh
- 使用 Chrome DevTools 调试

### 生产阶段
- 使用真实设备测试
- 启用 ProGuard 混淆
- 优化包大小

---

## 获取帮助

### 官方文档
- [React Native 官方文档](https://reactnative.dev/)
- [React Navigation 文档](https://reactnavigation.org/)
- [Redux 官方文档](https://redux.js.org/)

### 常见资源
- [Stack Overflow](https://stackoverflow.com/questions/tagged/react-native)
- [React Native 社区](https://github.com/react-native-community)

---

## 下一步

1. ✅ 安装依赖
2. ✅ 配置 API URL
3. ✅ 启动应用
4. ⏳ 测试登录功能
5. ⏳ 浏览首页和排名
6. ⏳ 实现剩余屏幕

---

**准备好了吗？开始运行吧！** 🚀

```bash
cd c:\coding\kongbai\mobile
npm install
npm start
```

然后在另一个终端运行：
```bash
npm run android
```
