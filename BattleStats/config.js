// API 配置文件

// 根据运行环境选择 API 地址
const ENV = 'production'; // 'local' | 'production'

const API_URLS = {
  // 本地开发环境
  local: {
    // Android 模拟器访问本地服务器
    android: 'http://10.0.2.2:5000',
    // iOS 模拟器或真机访问本地服务器（需要在同一网络）
    ios: 'http://localhost:5000',
    // Web 开发
    web: 'http://localhost:5000',
  },
  // 生产环境
  production: {
    android: 'https://bigmang.top',
    ios: 'https://bigmang.top',
    web: 'https://bigmang.top',
  },
};

// 获取当前平台
import { Platform } from 'react-native';

// 根据平台和环境获取 API URL
export const getApiUrl = () => {
  const platform = Platform.OS === 'web' ? 'web' : Platform.OS;
  return API_URLS[ENV][platform] || API_URLS[ENV].android;
};

// 导出当前配置
export const API_BASE_URL = getApiUrl();

// 其他配置
export const CONFIG = {
  // Token 有效期（小时）
  TOKEN_EXPIRY_HOURS: 24,
  
  // 请求超时时间（毫秒）
  REQUEST_TIMEOUT: 30000,
  
  // 是否启用日志
  ENABLE_LOGGING: ENV === 'local',
};

export default {
  API_BASE_URL,
  CONFIG,
  getApiUrl,
};
