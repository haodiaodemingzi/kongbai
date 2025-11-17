# Battle Stats - React Native Mobile App

游戏战斗数据统计系统的 Android 移动应用

## 📱 项目信息

- **应用名称**: Battle Stats (战斗统计)
- **平台**: Android (React Native)
- **版本**: 1.0.0
- **状态**: 开发中

## 🚀 快速开始

### 前置要求

- Node.js v14+
- npm v6+ 或 yarn
- Java JDK 11+
- Android Studio 最新版本
- Android SDK API 30+

### 安装和运行

```bash
# 1. 进入项目目录
cd mobile

# 2. 安装依赖
npm install

# 3. 启动 Metro 服务器 (终端1)
npm start

# 4. 运行应用 (终端2)
npm run android
```

详细步骤请查看 [QUICK_START.md](./QUICK_START.md)

## 📁 项目结构

```
mobile/
├── src/
│   ├── screens/              # 屏幕组件
│   │   ├── auth/            # 认证屏幕
│   │   ├── home/            # 首页屏幕
│   │   ├── ranking/         # 排名屏幕
│   │   ├── upload/          # 上传屏幕
│   │   └── profile/         # 个人资料屏幕
│   ├── components/           # 通用组件
│   │   └── common/          # 基础组件
│   ├── services/            # API 服务
│   │   ├── api.js
│   │   ├── auth.js
│   │   ├── ranking.js
│   │   └── battle.js
│   ├── store/               # Redux 状态管理
│   │   ├── store.js
│   │   └── reducers/
│   ├── styles/              # 样式系统
│   │   ├── colors.js
│   │   └── spacing.js
│   ├── navigation/          # 导航配置
│   │   ├── RootNavigator.js
│   │   ├── AuthNavigator.js
│   │   └── MainNavigator.js
│   └── App.js               # 应用入口
├── android/                 # Android 原生代码
├── package.json             # 项目配置
├── babel.config.js          # Babel 配置
├── metro.config.js          # Metro 配置
├── app.json                 # 应用配置
├── index.js                 # 应用入口点
└── README.md                # 本文件
```

## 🎨 设计特点

### 色彩系统
- **主色**: 蓝色 (#2563EB)
- **势力色**: 梵天(红)、比湿奴(青)、湿婆(紫)
- **状态色**: 成功(绿)、警告(橙)、错误(红)

### 功能特性
- 用户认证
- 实时数据展示
- 图表可视化
- 多条件筛选
- 下拉刷新

## 📚 可用命令

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

## 🔧 配置

### API 基础 URL

编辑 `src/services/api.js`:

```javascript
const API_BASE_URL = 'http://192.168.1.100:5000';
```

将 IP 地址替换为你的后端服务器地址。

### 环境变量

复制 `.env.example` 为 `.env`:

```bash
cp .env.example .env
```

然后编辑 `.env` 文件配置你的环境变量。

## 📖 文档

- [快速启动指南](./QUICK_START.md) - 详细的安装和运行步骤
- [应用设计方案](../MOBILE_APP_DESIGN.md) - 完整的设计文档
- [开发指南](../MOBILE_DEVELOPMENT_GUIDE.md) - 详细的开发指南
- [项目总结](../MOBILE_PROJECT_SUMMARY.md) - 项目统计和进度

## 🐛 常见问题

### Q: "command not found: npm"
A: 确保 Node.js 已正确安装，重启终端

### Q: "ANDROID_HOME is not set"
A: 设置 ANDROID_HOME 环境变量指向 Android SDK 目录

### Q: "No connected devices"
A: 启动 Android 虚拟设备或连接真实设备

### Q: Metro bundler error
A: 运行 `npm start -- --reset-cache` 清除缓存

更多问题请查看 [QUICK_START.md](./QUICK_START.md)

## 🚀 下一步

- [ ] 完成玩家详情屏幕
- [ ] 完成上传屏幕
- [ ] 完成个人资料屏幕
- [ ] 完成注册屏幕
- [ ] 性能优化
- [ ] 单元测试
- [ ] 打包发布

## 📦 技术栈

- **React Native** 0.71.0
- **React** 18.2.0
- **React Navigation** 6.1.0
- **Redux** 4.2.0
- **Axios** 1.3.0
- **React Native Chart Kit** 6.12.0

## 📝 许可证

MIT License

## 👥 贡献者

开发团队

## 📞 联系方式

如有问题或建议，请联系开发团队。

---

**准备好了吗？** 🚀

```bash
npm install && npm start
```
