# React Native 导航设置指南

## 🎯 新导航结构

已成功重构应用为底部标签导航 + 堆栈导航的结构，支持手势返回。

### 📋 导航层级

```
App (登录检查)
├── LoginScreen (未登录)
└── NavigationContainer (已登录)
    └── MainStackNavigator
        ├── MainTabs (底部标签导航)
        │   ├── Home (首页)
        │   ├── Rankings (排名)
        │   ├── Upload (上传)
        │   └── Profile (个人中心)
        └── BattleRankings (二级页面，支持手势返回)
```

## 🛠️ 安装步骤

### 1. 安装依赖
```bash
npm install @react-navigation/native @react-navigation/bottom-tabs @react-navigation/native-stack react-native-screens react-native-safe-area-context
```

### 2. 对于 Expo 项目
```bash
expo install react-native-screens react-native-safe-area-context
```

### 3. 启动应用
```bash
npm start
# 或
expo start
```

## 🎨 功能特性

### ✅ 底部导航栏
- **首页**：战斗统计数据
- **排名**：玩家排名列表
- **上传**：上传战斗日志
- **个人中心**：用户设置

### ✅ 手势返回
- **右滑返回**：从二级页面返回主页面
- **系统返回键**：Android 返回键支持
- **导航栏返回**：标准返回按钮

### ✅ 导航按钮
- 在排名页面添加了"查看战绩排名"按钮
- 点击可导航到战绩排名页面
- 支持右滑手势返回

## 📱 使用方法

### 主要导航
1. 使用底部标签在主要页面间切换
2. 点击"查看战绩排名"进入二级页面
3. 右滑或点击返回按钮返回

### 手势返回
- **从左边缘右滑**：返回上一页面
- **Android 返回键**：返回上一页面
- **导航栏返回按钮**：返回上一页面

## 🔧 配置说明

### 手势返回配置
```javascript
<Stack.Navigator
  screenOptions={{
    gestureEnabled: true, // 启用手势返回
    gestureDirection: 'horizontal', // 水平滑动
    presentation: 'card', // 卡片模式
  }}
>
```

### 底部标签配置
```javascript
<Tab.Navigator
  screenOptions={{
    tabBarActiveTintColor: '#3498db', // 激活颜色
    tabBarInactiveTintColor: 'gray', // 非激活颜色
    tabBarStyle: {
      height: 60, // 标签栏高度
      paddingBottom: 8,
      paddingTop: 8,
    },
  }}
>
```

## 🎯 页面说明

### 主页面（底部标签）
- **Home**：显示战斗统计概览
- **Rankings**：显示玩家排名，包含导航按钮
- **Upload**：上传功能（待实现）
- **Profile**：个人设置（待实现）

### 二级页面（堆栈导航）
- **BattleRankings**：战绩排名详情
- 支持手势返回到上一页面
- 自动显示返回按钮

## 🚀 下一步开发

### 立即实现
1. 完善首页数据展示
2. 实现上传功能
3. 添加个人中心页面
4. 优化页面样式

### 功能扩展
1. 添加更多二级页面
2. 实现深度链接
3. 添加页面转场动画
4. 优化手势体验

## 💡 使用建议

### 导航最佳实践
1. 主要功能放在底部标签
2. 详情页面使用堆栈导航
3. 保持导航层级简单
4. 确保手势返回正常工作

### 用户体验
1. 底部标签提供快速切换
2. 手势返回提供直观操作
3. 返回按钮作为备选方案
4. 保持导航一致性

## 🔍 故障排查

### 常见问题
1. **手势返回不工作**：检查 `gestureEnabled: true`
2. **导航错误**：确保所有依赖已安装
3. **样式问题**：检查 `react-native-screens` 配置
4. **性能问题**：启用原生屏幕优化

### 调试方法
```javascript
// 检查导航状态
console.log('Navigation state:', navigation.getState());

// 检查是否可以返回
console.log('Can go back:', navigation.canGoBack());
```

## ✨ 总结

新的导航结构提供了：
- 🎯 清晰的页面层级
- 📱 原生的导航体验
- 👆 直观的手势操作
- 🔄 灵活的页面切换

现在你可以享受流畅的导航体验，右滑返回功能完美工作！
