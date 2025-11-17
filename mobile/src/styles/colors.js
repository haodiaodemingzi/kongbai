export const colors = {
  // 主色调
  primary: '#2563EB',        // 蓝色 (主要操作)
  secondary: '#7C3AED',      // 紫色 (次要操作)
  
  // 势力颜色
  faction: {
    brahma: '#FF6B6B',       // 梵天 - 红色
    vishnu: '#4ECDC4',       // 比湿奴 - 青色
    shiva: '#9B59B6'         // 湿婆 - 紫色
  },
  
  // 状态颜色
  success: '#10B981',        // 成功 - 绿色
  warning: '#F59E0B',        // 警告 - 橙色
  error: '#EF4444',          // 错误 - 红色
  info: '#3B82F6',           // 信息 - 蓝色
  
  // 中性色
  neutral: {
    50: '#F9FAFB',
    100: '#F3F4F6',
    200: '#E5E7EB',
    300: '#D1D5DB',
    400: '#9CA3AF',
    500: '#6B7280',
    600: '#4B5563',
    700: '#374151',
    800: '#1F2937',
    900: '#111827'
  },
  
  // 背景
  background: '#FFFFFF',
  surface: '#F9FAFB',
  border: '#E5E7EB',
  
  // 透明度
  transparent: 'transparent'
};

export const getFactionColor = (faction) => {
  const factionMap = {
    '梵天': colors.faction.brahma,
    '比湿奴': colors.faction.vishnu,
    '湿婆': colors.faction.shiva
  };
  return factionMap[faction] || colors.primary;
};
