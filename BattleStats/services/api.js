// API 服务模块
import axios from 'axios';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { API_BASE_URL, CONFIG } from '../config';

console.log('API Base URL:', API_BASE_URL);

// Token 存储键
const TOKEN_KEY = '@battle_stats_token';
const USER_KEY = '@battle_stats_user';

// 创建 axios 实例
const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// 请求拦截器 - 自动添加 token
apiClient.interceptors.request.use(
  async (config) => {
    const token = await AsyncStorage.getItem(TOKEN_KEY);
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// 响应拦截器 - 处理错误
apiClient.interceptors.response.use(
  (response) => {
    return response;
  },
  async (error) => {
    if (error.response?.status === 401) {
      // Token 过期或无效，清除本地存储
      await AsyncStorage.removeItem(TOKEN_KEY);
      await AsyncStorage.removeItem(USER_KEY);
    }
    return Promise.reject(error);
  }
);

// ==================== 认证相关 API ====================

/**
 * 登录
 * @param {string} username 用户名
 * @param {string} password 密码
 * @returns {Promise} 返回 token 和用户信息
 */
export const login = async (username, password) => {
  try {
    const response = await apiClient.post('/api/auth/login', {
      username,
      password,
    });

    if (response.data.status === 'success') {
      const { token, user } = response.data.data;
      
      // 保存 token 和用户信息到本地
      await AsyncStorage.setItem(TOKEN_KEY, token);
      await AsyncStorage.setItem(USER_KEY, JSON.stringify(user));
      
      return { success: true, token, user };
    } else {
      return { success: false, message: response.data.message };
    }
  } catch (error) {
    console.error('登录失败:', error);
    return {
      success: false,
      message: error.response?.data?.message || '登录失败，请检查网络连接',
    };
  }
};

/**
 * 登出
 */
export const logout = async () => {
  try {
    await apiClient.post('/api/auth/logout');
  } catch (error) {
    console.error('登出失败:', error);
  } finally {
    // 清除本地存储
    await AsyncStorage.removeItem(TOKEN_KEY);
    await AsyncStorage.removeItem(USER_KEY);
  }
};

/**
 * 验证 token 是否有效
 */
export const verifyToken = async () => {
  try {
    const response = await apiClient.get('/api/auth/verify');
    return response.data.status === 'success';
  } catch (error) {
    return false;
  }
};

/**
 * 获取本地保存的 token
 */
export const getStoredToken = async () => {
  return await AsyncStorage.getItem(TOKEN_KEY);
};

/**
 * 获取本地保存的用户信息
 */
export const getStoredUser = async () => {
  const userStr = await AsyncStorage.getItem(USER_KEY);
  return userStr ? JSON.parse(userStr) : null;
};

// ==================== 首页数据 API ====================

/**
 * 获取首页仪表盘数据
 * @param {string} dateRange 时间范围 (today, yesterday, week, month, three_months, all)
 */
export const getDashboardData = async (dateRange = 'week') => {
  try {
    const response = await apiClient.get('/api/dashboard', {
      params: { date_range: dateRange },
    });

    if (response.data.status === 'success') {
      return { success: true, data: response.data.data };
    } else {
      return { success: false, message: response.data.message };
    }
  } catch (error) {
    console.error('获取首页数据失败:', error);
    return {
      success: false,
      message: error.response?.data?.message || '获取数据失败',
    };
  }
};

// ==================== 战斗数据 API ====================

/**
 * 获取玩家排名列表
 * @param {Object} params 筛选参数
 * @param {string} params.faction 势力 (梵天, 比湿奴, 湿婆, all)
 * @param {string} params.job 职业
 * @param {string} params.time_range 时间范围 (today, yesterday, week, month, three_months, all)
 * @param {string} params.start_date 自定义开始日期 (YYYY-MM-DD)
 * @param {string} params.end_date 自定义结束日期 (YYYY-MM-DD)
 */
export const getPlayerRankings = async (params = {}) => {
  try {
    const requestParams = {
      faction: params.faction || '',
      job: params.job || '',
    };
    
    // 如果有自定义日期，使用自定义日期；否则使用时间范围
    if (params.start_date && params.end_date) {
      requestParams.start_datetime = params.start_date;
      requestParams.end_datetime = params.end_date;
    } else {
      requestParams.time_range = params.time_range || 'today';
    }
    
    const response = await apiClient.get('/api/battle/rankings', {
      params: requestParams,
    });

    if (response.data.status === 'success') {
      return { success: true, data: response.data.data };
    } else {
      return { success: false, message: response.data.message };
    }
  } catch (error) {
    console.error('获取排名失败:', error);
    return {
      success: false,
      message: error.response?.data?.message || '获取排名失败',
    };
  }
};

/**
 * 获取玩家详细信息
 * @param {string} playerName 玩家名称
 * @param {string} timeRange 时间范围
 */
export const getPlayerDetails = async (playerName, timeRange = 'week') => {
  try {
    const response = await apiClient.get(`/api/battle/player/${playerName}`, {
      params: { time_range: timeRange },
    });

    if (response.data.status === 'success') {
      return { success: true, data: response.data.data };
    } else {
      return { success: false, message: response.data.message };
    }
  } catch (error) {
    console.error('获取玩家详情失败:', error);
    return {
      success: false,
      message: error.response?.data?.message || '获取玩家详情失败',
    };
  }
};

/**
 * 获取玩家详细信息
 * @param {string} playerName 玩家名称
 * @param {string} timeRange 时间范围
 */
export const getPlayerDetail = async (playerName, timeRange = 'week') => {
  try {
    const response = await apiClient.get(`/api/battle/player/${encodeURIComponent(playerName)}`, {
      params: { time_range: timeRange },
    });

    if (response.data.status === 'success') {
      return { success: true, data: response.data.data };
    } else {
      return { success: false, message: response.data.message };
    }
  } catch (error) {
    console.error('获取玩家详情失败:', error);
    return {
      success: false,
      message: error.response?.data?.message || '获取玩家详情失败',
    };
  }
};

/**
 * 获取主神排名数据
 */
export const getGodRankings = async () => {
  try {
    const response = await apiClient.get('/api/battle/god_rankings');

    if (response.data.status === 'success') {
      return { success: true, data: response.data.data };
    } else {
      return { success: false, message: response.data.message, data: response.data.data };
    }
  } catch (error) {
    console.error('获取主神排名失败:', error);
    return {
      success: false,
      message: error.response?.data?.message || '获取主神排名失败',
    };
  }
};

/**
 * 获取三神统计数据
 * @param {Object} params 筛选参数
 * @param {string} params.start_datetime 开始时间
 * @param {string} params.end_datetime 结束时间
 * @param {boolean} params.show_grouped 是否按玩家分组显示
 */
export const getGodsStats = async (params = {}) => {
  try {
    const requestParams = {
      show_grouped: params.show_grouped ? 'true' : 'false',
    };
    
    if (params.start_datetime) {
      requestParams.start_datetime = params.start_datetime;
    }
    if (params.end_datetime) {
      requestParams.end_datetime = params.end_datetime;
    }
    
    const response = await apiClient.get('/api/battle/gods_stats', {
      params: requestParams,
    });

    if (response.data.status === 'success') {
      return { success: true, data: response.data.data };
    } else {
      return { success: false, message: response.data.message };
    }
  } catch (error) {
    console.error('获取三神统计失败:', error);
    return {
      success: false,
      message: error.response?.data?.message || '获取三神统计失败',
    };
  }
};

/**
 * 获取玩家分组成员详情
 * @param {Object} params 参数
 * @param {string} params.god 神族
 * @param {string} params.player_name 玩家分组名称
 * @param {string} params.start_datetime 开始时间
 * @param {string} params.end_datetime 结束时间
 */
export const getGroupDetails = async (params = {}) => {
  try {
    const requestParams = {
      player_name: params.player_name,
    };
    
    if (params.god) {
      requestParams.god = params.god;
    }
    if (params.start_datetime) {
      requestParams.start_datetime = params.start_datetime;
    }
    if (params.end_datetime) {
      requestParams.end_datetime = params.end_datetime;
    }
    
    const response = await apiClient.get('/api/battle/group_details', {
      params: requestParams,
    });

    if (response.data.status === 'success') {
      return { success: true, data: response.data.data };
    } else {
      return { success: false, message: response.data.message };
    }
  } catch (error) {
    console.error('获取分组详情失败:', error);
    return {
      success: false,
      message: error.response?.data?.message || '获取分组详情失败',
    };
  }
};

/**
 * 获取势力统计数据
 * @param {string} dateRange 时间范围
 */
export const getFactionStats = async (dateRange = 'week') => {
  try {
    const response = await apiClient.get('/api/battle/faction_stats', {
      params: { date_range: dateRange },
    });

    if (response.data.status === 'success') {
      return { success: true, data: response.data.data };
    } else {
      return { success: false, message: response.data.message };
    }
  } catch (error) {
    console.error('获取势力统计失败:', error);
    return {
      success: false,
      message: error.response?.data?.message || '获取势力统计失败',
    };
  }
};

/**
 * 上传战斗日志文件
 * @param {Object} file 文件对象
 */
export const uploadBattleLog = async (file) => {
  try {
    const formData = new FormData();
    
    // 创建文件对象
    formData.append('file', {
      uri: file.uri,
      type: 'text/plain',
      name: file.name,
    });

    const response = await apiClient.post('/api/battle/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
      timeout: 60000, // 上传文件超时时间设置为60秒
    });

    if (response.data.status === 'success') {
      return { 
        success: true, 
        message: response.data.message,
        data: response.data.data 
      };
    } else {
      return { 
        success: false, 
        message: response.data.message 
      };
    }
  } catch (error) {
    console.error('上传战斗日志失败:', error);
    return {
      success: false,
      message: error.response?.data?.message || '上传失败，请检查网络连接',
    };
  }
};

// ==================== 排行榜 API ====================

/**
 * 获取排行榜数据
 * @param {string} category 排行榜分类
 * @param {boolean} refresh 是否强制刷新
 */
export const getRankingData = async (category = '主神排行榜', refresh = false) => {
  try {
    const response = await apiClient.get('/ranking/api/data', {
      params: {
        category,
        refresh: refresh ? 'true' : 'false',
      },
    });

    if (response.data.status === 'success') {
      return { success: true, data: response.data.data };
    } else {
      return { success: false, message: response.data.message };
    }
  } catch (error) {
    console.error('获取排行榜失败:', error);
    return {
      success: false,
      message: error.response?.data?.message || '获取排行榜失败',
    };
  }
};

/**
 * 刷新排行榜数据
 * @param {string} category 排行榜分类
 */
export const refreshRanking = async (category = '主神排行榜') => {
  try {
    const response = await apiClient.post('/ranking/api/refresh', {
      category,
    });

    if (response.data.status === 'success') {
      return { success: true, data: response.data.data };
    } else {
      return { success: false, message: response.data.message };
    }
  } catch (error) {
    console.error('刷新排行榜失败:', error);
    return {
      success: false,
      message: error.response?.data?.message || '刷新排行榜失败',
    };
  }
};

/**
 * 获取排行榜历史数据
 * @param {string} category 排行榜分类
 * @param {number} limit 返回记录数量
 */
export const getRankingHistory = async (category = '主神排行榜', limit = 10) => {
  try {
    const response = await apiClient.get('/ranking/api/history', {
      params: {
        category,
        limit,
      },
    });

    if (response.data.status === 'success') {
      return { success: true, data: response.data.data };
    } else {
      return { success: false, message: response.data.message };
    }
  } catch (error) {
    console.error('获取排行榜历史失败:', error);
    return {
      success: false,
      message: error.response?.data?.message || '获取排行榜历史失败',
    };
  }
};

export default {
  login,
  logout,
  verifyToken,
  getStoredToken,
  getStoredUser,
  getDashboardData,
  getPlayerRankings,
  getPlayerDetails,
  uploadBattleLog,
  getFactionStats,
  getGodRankings,
  getGodsStats,
  getGroupDetails,
  getRankingData,
  refreshRanking,
  getRankingHistory,
};
