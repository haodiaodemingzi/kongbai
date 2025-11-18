# 🚀 快速打包 APK

## 📱 最简单的方法：使用 EAS Build

### 步骤 1: 登录 Expo

```bash
eas login
```

**如果没有账号**，访问 https://expo.dev/signup 注册一个免费账号。

---

### 步骤 2: 构建 APK

```bash
eas build --platform android --profile preview
```

这个命令会：
1. ✅ 上传代码到 Expo 云端
2. ✅ 自动配置构建环境
3. ✅ 编译生成 APK
4. ✅ 提供下载链接

**构建时间**: 约 10-15 分钟

---

### 步骤 3: 下载 APK

构建完成后，终端会显示下载链接，例如：
```
✔ Build finished
https://expo.dev/accounts/xxx/projects/battle-stats/builds/xxx
```

点击链接下载 APK，或在 Expo 网站查看所有构建：
https://expo.dev/

---

## 🎯 一键命令

```bash
# 安装 EAS CLI (只需一次)
npm install -g eas-cli

# 登录
eas login

# 构建 APK
eas build --platform android --profile preview
```

---

## 📦 构建配置说明

当前配置 (`eas.json`):

- **preview**: 快速构建，生成 APK，适合测试
- **production**: 完整构建，可发布到 Google Play

---

## ⚠️ 重要提示

### 1. API 地址已配置

当前使用生产环境：`https://bigmang.xyz`

如需修改，编辑 `config.js`:
```javascript
const ENV = 'production'; // 或 'local'
```

### 2. 应用信息

- **应用名**: 战斗统计
- **包名**: com.kongbai.battlestats
- **版本**: 1.0.0

### 3. 首次构建

首次运行 `eas build` 时，会提示：
- 是否创建项目？选择 **Yes**
- 是否生成签名密钥？选择 **Yes**

EAS 会自动管理所有配置。

---

## 🔄 更新版本

修改 `app.json`:

```json
{
  "expo": {
    "version": "1.0.1",
    "android": {
      "versionCode": 2
    }
  }
}
```

然后重新构建：
```bash
eas build --platform android --profile preview
```

---

## 📱 安装 APK

### 方法 1: 手机直接下载
1. 在手机浏览器打开下载链接
2. 下载 APK
3. 安装（需允许未知来源）

### 方法 2: 电脑传输
1. 下载 APK 到电脑
2. 通过 USB 或其他方式传到手机
3. 在手机上安装

---

## 🎉 完成！

现在你有了一个可以安装在任何 Android 手机上的 APK！

**文件大小**: 约 30-50 MB
**支持系统**: Android 5.0+

---

## 💡 提示

- 免费账号每月有构建额度限制
- 构建记录保存在 Expo 网站
- 可以随时重新下载之前的构建

---

**需要帮助？** 查看完整文档：`BUILD_GUIDE.md`
