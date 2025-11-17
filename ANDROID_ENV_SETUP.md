# Android 开发环境完整安装指南

## 第 1 步：安装 Java JDK 11

### 下载
1. 访问 [Oracle JDK 下载页面](https://www.oracle.com/java/technologies/downloads/#java11)
2. 选择 **Windows x64 Installer**
3. 下载并运行安装程序

### 安装步骤
1. 双击 `jdk-11_windows-x64_bin.exe`
2. 点击 "Next" 继续
3. 选择安装路径（默认：`C:\Program Files\Java\jdk-11`）
4. 完成安装

### 验证安装
打开 PowerShell，运行：
```powershell
java -version
```

应该显示：
```
java version "11.x.x"
```

## 第 2 步：设置 JAVA_HOME 环境变量

### Windows 10/11

1. **打开环境变量设置**
   - 右键点击 "此电脑" → 属性
   - 点击 "高级系统设置"
   - 点击 "环境变量"

2. **新建系统变量**
   - 点击 "新建"
   - 变量名：`JAVA_HOME`
   - 变量值：`C:\Program Files\Java\jdk-11`
   - 点击 "确定"

3. **编辑 PATH 变量**
   - 在系统变量中找到 `Path`
   - 点击 "编辑"
   - 点击 "新建"
   - 添加：`%JAVA_HOME%\bin`
   - 点击 "确定"

4. **验证**
   - 重启 PowerShell
   - 运行：`java -version`

## 第 3 步：安装 Android Studio

### 下载
1. 访问 [Android Studio 官网](https://developer.android.com/studio)
2. 点击 "Download Android Studio"
3. 同意条款并下载

### 安装步骤
1. 双击 `android-studio-2023.x.x-windows.exe`
2. 点击 "Next" 继续
3. 选择安装路径（默认：`C:\Program Files\Android\Android Studio`）
4. 完成安装

### 首次启动
1. 打开 Android Studio
2. 选择 "Do not import settings"
3. 点击 "Next"
4. 选择 "Standard" 安装类型
5. 接受许可证
6. 等待 SDK 下载完成（约 10-20 分钟）

## 第 4 步：安装 Android SDK

### 通过 Android Studio

1. 打开 Android Studio
2. 点击 "Tools" → "SDK Manager"
3. 在 "SDK Platforms" 标签页中：
   - ✅ 勾选 "Android 13 (API 33)" 或更高
   - ✅ 勾选 "Android 12 (API 32)"
   - 点击 "Apply" 下载

4. 在 "SDK Tools" 标签页中：
   - ✅ 勾选 "Android SDK Build-Tools 33.0.0"
   - ✅ 勾选 "Android Emulator"
   - ✅ 勾选 "Android SDK Platform-Tools"
   - 点击 "Apply" 下载

## 第 5 步：设置 ANDROID_HOME 环境变量

### Windows 10/11

1. **打开环境变量设置**（同上）

2. **新建系统变量**
   - 点击 "新建"
   - 变量名：`ANDROID_HOME`
   - 变量值：`C:\Users\YourUsername\AppData\Local\Android\Sdk`
   - 点击 "确定"

3. **编辑 PATH 变量**
   - 在系统变量中找到 `Path`
   - 点击 "编辑"
   - 点击 "新建"
   - 添加：`%ANDROID_HOME%\platform-tools`
   - 点击 "新建"
   - 添加：`%ANDROID_HOME%\tools`
   - 点击 "确定"

4. **验证**
   - 重启 PowerShell
   - 运行：`adb version`

## 第 6 步：创建 Android 虚拟设备（AVD）

### 使用 Android Studio

1. 打开 Android Studio
2. 点击 "Tools" → "Device Manager"
3. 点击 "Create Device"
4. 选择设备（例如 "Pixel 5"）
5. 点击 "Next"
6. 选择系统镜像（例如 "Android 13"）
7. 点击 "Next"
8. 配置 AVD 设置
9. 点击 "Finish"

### 启动虚拟设备

1. 在 Device Manager 中找到你的 AVD
2. 点击播放按钮启动
3. 等待虚拟设备完全启动（约 1-2 分钟）

## 第 7 步：验证环境

打开 PowerShell，运行以下命令：

```powershell
# 检查 Java
java -version

# 检查 Android SDK
adb version

# 列出虚拟设备
adb devices
```

应该都能正常输出。

## 第 8 步：运行 React Native 应用

```bash
cd c:\coding\kongbai\mobile

# 安装依赖
npm install --legacy-peer-deps

# 启动 Metro 服务器 (终端1)
npm start

# 运行应用 (终端2)
npm run android
```

## 常见问题

### Q: "java: command not found"
A: JAVA_HOME 环境变量未正确设置，重启 PowerShell 后重试

### Q: "adb: command not found"
A: ANDROID_HOME 环境变量未正确设置，重启 PowerShell 后重试

### Q: 虚拟设备启动很慢
A: 这是正常的，首次启动需要 2-5 分钟

### Q: "No devices found"
A: 
- 确保虚拟设备已启动
- 或连接真实 Android 手机并启用 USB 调试

### Q: 构建失败
A: 
- 清除缓存：`npm start -- --reset-cache`
- 重新安装依赖：`rm -r node_modules && npm install --legacy-peer-deps`

## 总结

完整安装时间：**30-60 分钟**

安装完成后，你可以：
1. ✅ 运行 React Native 应用
2. ✅ 在虚拟设备或真实手机上测试
3. ✅ 构建 APK 发布

祝你开发顺利！
