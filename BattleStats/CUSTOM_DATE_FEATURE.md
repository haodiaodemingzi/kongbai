# 自定义时间区域查询功能

## ✨ 新增功能

战绩排名页面现在支持自定义时间区域查询，用户可以选择任意日期范围查看战绩数据。

---

## 📱 功能特性

### 1. 时间范围选项

**预设选项**:
- 今天
- 昨天
- 7天
- 30天
- 3个月
- 全部
- **自定义** ⭐ (新增)

### 2. 自定义时间选择

点击"自定义"按钮后，会弹出日期选择模态框：

- **开始日期**: 选择查询的起始日期
- **结束日期**: 选择查询的结束日期
- **日期验证**: 自动检查开始日期不能晚于结束日期

### 3. 日期显示

选择自定义时间后，按钮会显示选中的日期范围：
```
自定义
2025-01-01 ~ 2025-01-31
```

---

## 🎨 UI 设计

### 模态框设计
- 半透明黑色遮罩
- 白色圆角卡片
- 清晰的标题和标签
- 蓝色确认按钮
- 灰色取消按钮

### 日期选择器
- iOS: 滚轮式选择器
- Android: 日历式选择器
- 原生系统组件，体验流畅

---

## 🔧 技术实现

### 依赖包
```bash
npm install @react-native-community/datetimepicker
```

### API 参数

**预设时间范围**:
```javascript
{
  time_range: 'today' | 'yesterday' | 'week' | 'month' | 'three_months' | 'all',
  faction: '梵天' | '比湿奴' | '湿婆' | ''
}
```

**自定义时间范围**:
```javascript
{
  start_date: '2025-01-01',  // YYYY-MM-DD 格式
  end_date: '2025-01-31',
  faction: '梵天' | '比湿奴' | '湿婆' | ''
}
```

### 核心函数

#### 1. formatDate()
```javascript
// 格式化日期为 YYYY-MM-DD
const formatDate = (date) => {
  const year = date.getFullYear();
  const month = String(date.getMonth() + 1).padStart(2, '0');
  const day = String(date.getDate()).padStart(2, '0');
  return `${year}-${month}-${day}`;
};
```

#### 2. handleTimeSelect()
```javascript
// 处理时间选择
const handleTimeSelect = (value) => {
  if (value === 'custom') {
    setShowCustomModal(true);  // 显示自定义时间模态框
  } else {
    setSelectedTime(value);     // 直接设置预设时间
  }
};
```

#### 3. confirmCustomTime()
```javascript
// 确认自定义时间
const confirmCustomTime = () => {
  if (startDate > endDate) {
    Alert.alert('错误', '开始日期不能晚于结束日期');
    return;
  }
  setSelectedTime('custom');
  setShowCustomModal(false);
};
```

---

## 📊 数据流程

```
用户点击"自定义" 
  ↓
显示日期选择模态框
  ↓
用户选择开始日期和结束日期
  ↓
点击"确定"按钮
  ↓
验证日期有效性
  ↓
调用 API (传递 start_date 和 end_date)
  ↓
显示查询结果
```

---

## 🎯 使用场景

### 场景 1: 查看特定活动期间数据
用户想查看某次大型活动期间的战绩：
- 开始日期: 2025-01-15
- 结束日期: 2025-01-20

### 场景 2: 对比不同时期数据
用户想对比两个不同时间段的数据：
- 第一次查询: 2025-01-01 ~ 2025-01-15
- 第二次查询: 2025-01-16 ~ 2025-01-31

### 场景 3: 查看历史数据
用户想查看很久以前的数据：
- 开始日期: 2024-06-01
- 结束日期: 2024-06-30

---

## ⚠️ 注意事项

### 1. 日期验证
- 开始日期必须 ≤ 结束日期
- 如果违反，会弹出错误提示

### 2. 数据量考虑
- 时间范围过大可能导致数据量较多
- 建议合理选择时间范围

### 3. 性能优化
- API 会根据时间范围自动优化查询
- 后端有缓存机制

---

## 🔄 与 Web 端对比

### 相似功能
- ✅ 支持自定义时间范围
- ✅ 日期格式统一 (YYYY-MM-DD)
- ✅ 相同的 API 参数

### 移动端特色
- 📱 原生日期选择器
- 📱 模态框交互
- 📱 触摸友好的 UI

---

## 📝 后续优化建议

### 短期
- [ ] 添加快捷日期选项 (本周/上周/本月/上月)
- [ ] 记住用户最后选择的日期
- [ ] 添加日期范围预设模板

### 中期
- [ ] 支持日期范围拖拽选择
- [ ] 添加日期范围可视化
- [ ] 支持多个日期范围对比

### 长期
- [ ] 添加数据趋势分析
- [ ] 支持导出指定日期范围数据
- [ ] 添加日期范围分享功能

---

## 🐛 已知问题

暂无

---

## 📚 相关文档

- [React Native DateTimePicker](https://github.com/react-native-datetimepicker/datetimepicker)
- [API 文档](./API_DOCUMENTATION.md)
- [UI 优化记录](./UI_IMPROVEMENTS.md)

---

**版本**: v1.1.0  
**更新时间**: 2025-11-18  
**功能状态**: ✅ 已完成
