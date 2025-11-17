# React Native 移动端应用 - 安装和运行指南

## 📋 目录

1. [系统要求](#系统要求)
2. [安装步骤](#安装步骤)
3. [配置](#配置)
4. [运行应用](#运行应用)
5. [常见问题](#常见问题)
6. [开发工作流](#开发工作流)

---

## 系统要求

### 最低配置

| 软件 | 版本 | 说明 |
|------|------|------|
| Node.js | v14+ | 推荐 v16 LTS |
| npm | v6+ | 或使用 yarn |
| Java JDK | 11+ | 必需 |
| Android Studio | 最新 | 用于 Android SDK |
| Android SDK | API 30+ | 最低 API 级别 |

### 磁盘空间

- Node.js + npm: ~500MB
- Android SDK: ~10GB
- 项目 + node_modules: ~2GB
- **总计**: 至少 15GB 可用空间

---

## 安装步骤

### 第 1 步：检查系统环境

#### Windows (PowerShell)

```powershell
# 检查 Node.js
node --version
npm --version

# 检查 Java
java -version

# 检查 Android SDK (如果已安装)
$env:ANDROID_HOME
```

#### macOS / Linux

```bash
# 检查 Node.js
node --version
npm --version

# 检查 Java
java -version

# 检查 Android SDK
echo $ANDROID_HOME
```

### 第 2 步：安装 Node.js

如果未安装，请从 [nodejs.org](https://nodejs.org/) 下载安装。

**验证安装**:
```bash
node --version  # 应显示 v14+ 或更高
npm --version   # 应显示 v6+ 或更高
```

### 第 3 步：安装 Java JDK

从 [Oracle](https://www.oracle.com/java/technologies/downloads/) 或 [OpenJDK](https://openjdk.java.net/) 下载安装。

**验证安装**:
```bash
java -version
```

### 第 4 步：安装 Android Studio

从 [Android Studio 官网](https://developer.android.com/studio) 下载安装。

**安装后配置**:
1. 打开 Android Studio
2. 点击 "SDK Manager"
3. 安装 Android SDK (API 30+)
4. 记下 Android SDK 路径

### 第 5 步：设置 Android SDK 环境变量

#### Windows (PowerShell)

```powershell
# 临时设置 (当前会话)
$env:ANDROID_HOME = "C:\Users\YourUsername\AppData\Local\Android\Sdk"
$env:PATH += ";$env:ANDROID_HOME\platform-tools;$env:ANDROID_HOME\tools"

# 永久设置 (编辑系统环境变量)
# 1. 右键点击 "此电脑" → 属性
# 2. 点击 "高级系统设置"
# 3. 点击 "环境变量"
# 4. 新建变量 ANDROID_HOME，值为 Android SDK 路径
# 5. 编辑 PATH，添加 %ANDROID_HOME%\platform-tools 和 %ANDROID_HOME%\tools
```

#### macOS / Linux

```bash
# 添加到 ~/.bash_profile 或 ~/.zshrc
export ANDROID_HOME=$HOME/Library/Android/sdk  # macOS
# 或
export ANDROID_HOME=$HOME/Android/Sdk  # Linux

export PATH=$PATH:$ANDROID_HOME/platform-tools:$ANDROID_HOME/tools
```

### 第 6 步：安装项目依赖

#### 方式 A：使用自动化脚本 (推荐)

**Windows**:
```bash
cd c:\coding\kongbai\mobile
.\setup.bat
```

**macOS / Linux**:
```bash
cd ~/coding/kongbai/mobile
chmod +x setup.sh
./setup.sh
```

#### 方式 B：手动安装

```bash
# 进入项目目录
cd c:\coding\kongbai\mobile

# 清除旧的依赖 (如果存在)
rm -r node_modules
npm cache clean --force

# 安装依赖
npm install --legacy-peer-deps
```

**预计时间**: 5-10 分钟

### 第 7 步：配置 API 基础 URL

编辑文件 `mobile/src/services/api.js`:

```javascript
// 修改这一行
const API_BASE_URL = 'http://192.168.1.100:5000';

// 替换为你的后端服务器 IP 地址
// 例如:
// const API_BASE_URL = 'http://192.168.1.50:5000';  // 本地网络
// const API_BASE_URL = 'http://10.0.2.2:5000';      // Android 模拟器
// const API_BASE_URL = 'https://api.example.com';   // 生产环境
```

**重要**: 
- 开发环境使用 `http://` (不是 `https://`)
- 如果使用 Android 模拟器，使用 `10.0.2.2` 代替 `localhost`
- 如果使用真实设备，使用你的电脑在局域网中的 IP 地址

### 第 8 步：创建 Android 虚拟设备 (可选)

如果没有真实 Android 设备，需要创建虚拟设备：

1. 打开 Android Studio
2. 点击 "AVD Manager"
3. 点击 "Create Virtual Device"
4. 选择设备 (例如 Pixel 4)
5. 选择 API 级别 (30+)
6. 完成创建

---

## 配置

### 环境变量

复制 `.env.example` 为 `.env`:

```bash
cd mobile
cp .env.example .env
```

编辑 `.env` 文件:

```
API_BASE_URL=http://192.168.1.100:5000
APP_NAME=BattleStats
APP_VERSION=1.0.0
DEBUG=true
```

### API 配置

编辑 `src/services/api.js`:

```javascript
// 开发环境
const API_BASE_URL = 'http://192.168.1.100:5000';

// 生产环境
// const API_BASE_URL = 'https://api.yourdomain.com';
```

---

## 运行应用

### 前置条件

- ✅ 所有依赖已安装
- ✅ API 基础 URL 已配置
- ✅ Android 虚拟设备已创建或真实设备已连接
- ✅ 后端服务已启动 (Flask 应用)

### 方式 1：一步启动 (推荐)

```bash
cd c:\coding\kongbai\mobile
npm run android
```

这会自动启动 Metro 服务器并运行应用。

### 方式 2：分步启动

**终端 1 - 启动 Metro 服务器**:
```bash
cd c:\coding\kongbai\mobile
npm start
```

**终端 2 - 运行应用**:
```bash
cd c:\coding\kongbai\mobile
npm run android
```

### 首次运行

首次运行可能需要 2-5 分钟来编译和构建应用。

**预期结果**:
1. Metro 服务器启动
2. Android 虚拟设备启动
3. 应用编译和安装
4. 应用在设备上启动
5. 看到登录屏幕

### 验证安装

1. **看到登录屏幕** ✓
2. **输入用户名和密码** ✓
3. **点击登录** ✓
4. **看到首页仪表盘** ✓

---

## 常见问题

### 问题 1: "command not found: npm"

**原因**: Node.js 未正确安装或 PATH 未配置

**解决**:
```bash
# 重新安装 Node.js
# 或重启终端/电脑
# 验证安装
node --version
npm --version
```

### 问题 2: "ANDROID_HOME is not set"

**原因**: Android SDK 环境变量未设置

**解决**:
```powershell
# Windows PowerShell
$env:ANDROID_HOME = "C:\Users\YourUsername\AppData\Local\Android\Sdk"

# 验证
echo $env:ANDROID_HOME
```

### 问题 3: "No connected devices"

**原因**: 没有可用的 Android 设备或虚拟设备

**解决**:
```bash
# 列出可用设备
adb devices

# 启动虚拟设备
# 1. 打开 Android Studio
# 2. 点击 AVD Manager
# 3. 启动虚拟设备

# 或连接真实设备
# 1. 用 USB 连接 Android 手机
# 2. 启用 USB 调试
# 3. 运行 adb devices 验证
```

### 问题 4: "Metro bundler error"

**原因**: Metro 服务器出错或缓存问题

**解决**:
```bash
# 清除缓存并重启
npm start -- --reset-cache

# 或完全清除
npm cache clean --force
rm -r node_modules
npm install --legacy-peer-deps
npm start
```

### 问题 5: "API 连接失败"

**原因**: API 基础 URL 配置错误或后端未启动

**解决**:
1. 检查 `src/services/api.js` 中的 API URL
2. 确保后端服务已启动
3. 检查防火墙设置
4. 使用正确的 IP 地址:
   - 本地网络: `192.168.x.x`
   - Android 模拟器: `10.0.2.2`
   - 生产环境: 域名或公网 IP

### 问题 6: "依赖安装失败"

**原因**: npm 源问题或网络问题

**解决**:
```bash
# 清除缓存
npm cache clean --force

# 使用国内源 (如果在中国)
npm config set registry https://registry.npmmirror.com

# 重新安装
npm install --legacy-peer-deps

# 恢复默认源
npm config set registry https://registry.npmjs.org/
```

### 问题 7: "应用闪退"

**原因**: 运行时错误或依赖问题

**解决**:
1. 查看 Android 日志:
```bash
adb logcat
```

2. 重新构建应用:
```bash
npm start -- --reset-cache
npm run android
```

3. 清除应用数据:
```bash
adb shell pm clear com.battlstats  # 包名可能不同
```

---

## 开发工作流

### 热重载

在应用运行时修改代码，按以下快捷键：

- **快速刷新**: 按 `R` 两次
- **完全重新加载**: 按 `R` 一次
- **打开开发菜单**: 按 `M`

### 调试

```bash
# 打开开发菜单 (按 M)
# 选择 "Debug with Chrome"
# 打开 Chrome DevTools (F12)
```

### 查看日志

```bash
# 实时日志
adb logcat

# 过滤日志
adb logcat | grep "BattleStats"

# 清除日志
adb logcat -c
```

### 构建 APK

```bash
# 开发 APK
npm run build:android

# 生产 APK (需要签名)
npm run build:android:bundle
```

---

## 下一步

1. ✅ 安装依赖
2. ✅ 配置 API URL
3. ✅ 启动应用
4. ⏳ 测试登录功能
5. ⏳ 浏览首页和排名
6. ⏳ 实现剩余屏幕

---

## 获取帮助

### 官方文档
- [React Native 官方文档](https://reactnative.dev/)
- [Android 开发者文档](https://developer.android.com/docs)
- [React Navigation 文档](https://reactnavigation.org/)

### 常见资源
- [Stack Overflow](https://stackoverflow.com/questions/tagged/react-native)
- [React Native 社区](https://github.com/react-native-community)

---

**准备好了吗？开始运行吧！** 🚀

```bash
cd c:\coding\kongbai\mobile
npm install --legacy-peer-deps
npm start
```

然后在另一个终端：
```bash
npm run android
```
