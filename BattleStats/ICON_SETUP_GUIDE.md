# 📱 应用图标设置指南

## 🎯 快速开始

### 方法一：使用生成器 HTML（推荐）

1. **打开生成器**
   ```bash
   # 在浏览器中打开
   c:\coding\kongbai\BattleStats\generate-icon.html
   ```

2. **截图保存**
   - 按 `Win + Shift + S` 打开截图工具
   - 截取对应的图标区域
   - 保存为 PNG 格式

3. **调整尺寸**
   使用在线工具调整到所需尺寸：
   - [TinyPNG](https://tinypng.com/) - 压缩图片
   - [ImageResizer](https://imageresizer.com/) - 调整尺寸

4. **放置文件**
   ```
   BattleStats/assets/
   ├── icon.png           (1024x1024)
   ├── adaptive-icon.png  (1024x1024)
   ├── splash-icon.png    (任意尺寸)
   └── favicon.png        (48x48)
   ```

---

### 方法二：使用在线工具（最简单）

#### 推荐工具

1. **Icon Kitchen** (https://icon.kitchen/)
   - ✅ 免费
   - ✅ 自动生成所有尺寸
   - ✅ 支持 Android/iOS
   - ✅ 可自定义颜色和图标

2. **App Icon Generator** (https://www.appicon.co/)
   - ✅ 一键生成
   - ✅ 支持多平台
   - ✅ 自动打包下载

3. **MakeAppIcon** (https://makeappicon.com/)
   - ✅ 简单易用
   - ✅ 支持拖拽上传
   - ✅ 自动生成全套图标

#### 使用步骤

1. 访问任一工具网站
2. 上传 1024x1024 的图标
3. 选择平台（Android/iOS）
4. 下载生成的图标包
5. 解压并复制到 `assets/` 文件夹

---

### 方法三：使用设计软件

#### Figma/Sketch

1. 创建 1024x1024 画布
2. 设计图标：
   - 背景：紫色渐变 (#667eea → #764ba2)
   - 图标：剑 + 图表元素
   - 文字：Battle Stats
3. 导出为 PNG
4. 生成其他尺寸

#### Canva

1. 访问 [Canva](https://www.canva.com/)
2. 选择"应用图标"模板
3. 自定义设计
4. 下载 PNG 格式

---

## 📐 图标规格要求

### icon.png
- **尺寸**: 1024x1024 px
- **格式**: PNG
- **用途**: 应用主图标
- **要求**: 
  - 圆角会自动应用
  - 避免在边缘放置重要内容
  - 保持简洁清晰

### adaptive-icon.png
- **尺寸**: 1024x1024 px
- **格式**: PNG (透明背景)
- **用途**: Android 自适应图标前景
- **要求**:
  - 必须是透明背景
  - 图标内容在安全区域内（中心 66%）
  - 避免文字过小

### splash-icon.png
- **尺寸**: 建议 512x512 或更大
- **格式**: PNG
- **用途**: 启动屏幕图标
- **要求**:
  - 可以是简化版 logo
  - 背景可透明或纯色

### favicon.png
- **尺寸**: 48x48 px
- **格式**: PNG
- **用途**: Web 版图标
- **要求**:
  - 极简设计
  - 高对比度

---

## 🎨 设计建议

### 色彩方案
```css
/* 主渐变 */
background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);

/* 图标颜色 */
icon-color: #FFFFFF;

/* 强调色 */
accent-color: #FFD700;
```

### 图标元素
- **主元素**: ⚔️ 剑（战斗）
- **辅助元素**: 📊 图表（统计）
- **可选元素**: 🛡️ 盾、🏆 奖杯、⭐ 星星

### 设计原则
1. **简洁**: 避免过多细节
2. **识别性**: 小尺寸下仍清晰
3. **一致性**: 与应用主题匹配
4. **独特性**: 区别于其他应用

---

## ✅ 验证清单

### 图标质量检查
- [ ] 1024x1024 尺寸正确
- [ ] PNG 格式
- [ ] 无背景透明问题
- [ ] 边缘无锯齿
- [ ] 颜色鲜艳清晰

### 视觉效果检查
- [ ] 小尺寸（48x48）下仍清晰
- [ ] 在不同背景下都可见
- [ ] 与应用主题一致
- [ ] 在手机上预览效果好

### 文件检查
- [ ] 所有文件已放置在 assets/ 文件夹
- [ ] 文件名正确
- [ ] app.json 中路径正确

---

## 🔧 更新 app.json

确保 `app.json` 中的图标路径正确：

```json
{
  "expo": {
    "icon": "./assets/icon.png",
    "splash": {
      "image": "./assets/splash-icon.png",
      "backgroundColor": "#667eea"
    },
    "android": {
      "adaptiveIcon": {
        "foregroundImage": "./assets/adaptive-icon.png",
        "backgroundColor": "#667eea"
      }
    },
    "web": {
      "favicon": "./assets/favicon.png"
    }
  }
}
```

---

## 🚀 测试图标

### 本地测试
```bash
# 重新启动应用
npm start

# 清除缓存
npx expo start --clear
```

### 真机测试
1. 在 Expo Go 中打开应用
2. 检查图标显示
3. 测试不同屏幕尺寸

### 构建测试
```bash
# 构建 APK
eas build --platform android --profile preview
```

---

## 💡 临时方案

如果暂时没有专业图标，可以使用：

### 纯色 + Emoji
```javascript
// 在 app.json 中
"backgroundColor": "#667eea"
// 使用系统 emoji 作为临时图标
```

### 文字 Logo
- 使用 "BS" 或 "战斗统计"
- 紫色渐变背景
- 白色粗体文字

---

## 📚 参考资源

### 设计灵感
- [Dribbble - App Icons](https://dribbble.com/tags/app_icon)
- [Behance - Mobile Icons](https://www.behance.net/search/projects?search=mobile%20app%20icon)

### 工具资源
- [Expo Icon Guidelines](https://docs.expo.dev/guides/app-icons/)
- [Android Icon Design](https://developer.android.com/guide/practices/ui_guidelines/icon_design_adaptive)
- [iOS Icon Guidelines](https://developer.apple.com/design/human-interface-guidelines/app-icons)

---

## 🐛 常见问题

### Q: 图标显示模糊？
A: 确保使用 1024x1024 高分辨率原图，不要拉伸小图。

### Q: Android 图标被裁剪？
A: 自适应图标的内容应在中心 66% 区域内。

### Q: 启动屏图标太小？
A: 增大 splash-icon.png 的尺寸。

### Q: 图标颜色不对？
A: 检查 app.json 中的 backgroundColor 设置。

---

**更新时间**: 2025-11-18  
**版本**: v1.0
