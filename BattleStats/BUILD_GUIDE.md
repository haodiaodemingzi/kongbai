# 📦 Android APK 打包指南

## 🎯 打包方式

### 方式一：使用 EAS Build (推荐)

EAS Build 是 Expo 官方的云构建服务，无需本地配置 Android 开发环境。

#### 1. 安装 EAS CLI

```bash
npm install -g eas-cli
```

#### 2. 登录 Expo 账号

```bash
eas login
```

如果没有账号，先注册：https://expo.dev/signup

#### 3. 配置项目

```bash
eas build:configure
```

#### 4. 构建 APK

```bash
# 构建预览版 APK (推荐，速度快)
eas build --platform android --profile preview

# 或构建生产版 APK
eas build --platform android --profile production
```

#### 5. 下载 APK

构建完成后，会提供下载链接，或者在 Expo 网站查看：
https://expo.dev/accounts/[your-account]/projects/battle-stats/builds

---

### 方式二：本地构建 (需要 Android Studio)

如果你有 Android 开发环境，可以本地构建。

#### 1. 安装 Android Studio

下载并安装：https://developer.android.com/studio

#### 2. 配置环境变量

```bash
# Windows
ANDROID_HOME=C:\Users\[你的用户名]\AppData\Local\Android\Sdk
```

#### 3. 预构建项目

```bash
npx expo prebuild --platform android
```

#### 4. 构建 APK

```bash
cd android
./gradlew assembleRelease
```

APK 位置：`android/app/build/outputs/apk/release/app-release.apk`

---

### 方式三：Expo Go 扫码运行 (开发测试)

最简单的方式，不需要打包：

```bash
npx expo start
```

使用 Expo Go App 扫描二维码即可运行。

---

## 📋 当前配置

### 应用信息
- **应用名称**: 战斗统计
- **包名**: com.kongbai.battlestats
- **版本**: 1.0.0
- **版本号**: 1

### 权限
- INTERNET (网络访问)

### 图标和启动屏
- 图标: `./assets/icon.png`
- 启动屏: `./assets/splash-icon.png`
- 主题色: `#667eea` (紫色)

---

## 🚀 推荐流程

### 首次打包

1. **使用 EAS Build** (最简单)
   ```bash
   npm install -g eas-cli
   eas login
   eas build --platform android --profile preview
   ```

2. **等待构建** (约 10-15 分钟)

3. **下载 APK** 并安装到手机

### 后续更新

1. 修改 `app.json` 中的版本号：
   ```json
   "version": "1.0.1",
   "versionCode": 2
   ```

2. 重新构建：
   ```bash
   eas build --platform android --profile preview
   ```

---

## ⚠️ 注意事项

### 1. API 地址配置

打包前确保 API 地址正确：

```javascript
// services/api.js
const API_BASE_URL = 'http://你的服务器IP:5000';
```

**重要**: 不能使用 `localhost` 或 `127.0.0.1`，必须使用实际的服务器 IP 或域名！

### 2. 网络权限

已在 `app.json` 中配置 INTERNET 权限，无需额外操作。

### 3. 图标资源

确保以下文件存在：
- `assets/icon.png` (1024x1024)
- `assets/splash-icon.png` (1284x2778)
- `assets/adaptive-icon.png` (1024x1024)

如果缺失，可以使用默认图标或自己制作。

### 4. 签名密钥

EAS Build 会自动管理签名密钥，无需手动配置。

---

## 🔧 常见问题

### Q: EAS Build 需要付费吗？
A: 免费账号每月有一定的构建额度，足够个人使用。

### Q: 构建失败怎么办？
A: 查看构建日志，通常是依赖问题或配置错误。可以运行：
```bash
eas build --platform android --profile preview --clear-cache
```

### Q: APK 太大怎么办？
A: 
- 使用 AAB 格式（Google Play）
- 移除未使用的依赖
- 启用代码压缩

### Q: 如何生成签名的 APK？
A: EAS Build 自动签名。如果需要自己的密钥：
```bash
eas credentials
```

---

## 📱 安装 APK

### 方法一：直接安装
1. 将 APK 传输到手机
2. 打开文件管理器
3. 点击 APK 文件安装
4. 允许"未知来源"安装

### 方法二：ADB 安装
```bash
adb install app-release.apk
```

---

## 🎉 完成

打包完成后，你将获得一个可以在任何 Android 手机上安装的 APK 文件！

**APK 文件名**: `battle-stats-v1.0.0.apk`

---

## 📚 参考资料

- [Expo EAS Build 文档](https://docs.expo.dev/build/introduction/)
- [Android 打包指南](https://docs.expo.dev/build-reference/apk/)
- [应用签名](https://docs.expo.dev/app-signing/app-credentials/)

---

**更新时间**: 2025-11-18
**版本**: v1.0.0
