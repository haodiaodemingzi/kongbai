import axios from 'axios';
import AsyncStorage from '@react-native-async-storage/async-storage';

// API 配置
const API_BASE_URL = 'http://your-backend-url.com'; // 替换为实际的后端 URL

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json'
  }
});

// 请求拦截器
api.interceptors.request.use(
  async (config) => {
    try {
      const token = await AsyncStorage.getItem('authToken');
      if (token) {
        config.headers.Authorization = `Bearer ${token}`;
      }
    } catch (error) {
      console.error('Error getting token:', error);
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// 响应拦截器
api.interceptors.response.use(
  (response) => {
    return response.data;
  },
  (error) => {
    if (error.response?.status === 401) {
      // 处理未授权 - 清除 token 并重定向到登录
      AsyncStorage.removeItem('authToken');
      // 触发登出事件
    }
    
    const errorMessage = error.response?.data?.message || error.message || '请求失败';
    return Promise.reject({
      status: error.response?.status,
      message: errorMessage,
      data: error.response?.data
    });
  }
);

export default api;
