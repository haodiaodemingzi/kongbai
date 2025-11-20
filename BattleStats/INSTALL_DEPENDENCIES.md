# 安装新依赖包

为了支持截图和分享功能，需要安装以下依赖包：

## 安装命令

在 `BattleStats` 目录下运行：

```bash
npm install
```

或者单独安装：

```bash
npm install expo-sharing@~13.0.2
npm install react-native-view-shot@4.1.0
```

## 依赖说明

- **expo-sharing**: Expo 官方分享组件，用于分享文件到其他应用
- **react-native-view-shot**: 截图组件，可以将 React Native 视图转换为图片

## 使用后重启

安装完成后，请重启开发服务器：

```bash
# 停止当前服务器 (Ctrl+C)
# 然后重新启动
npm start
```

## 功能说明

安装完成后，三神统计页面将支持：
- 点击"分享截图"按钮
- 自动截取整个页面内容（包括所有三神的战绩数据）
- 生成长截图
- 通过系统分享功能分享到其他应用（微信、QQ、保存到相册等）
