import api from './api';

export const authService = {
  // 登录
  login: async (username, password) => {
    try {
      const response = await api.post('/auth/login', {
        username,
        password
      });
      return response;
    } catch (error) {
      throw error;
    }
  },

  // 注册
  register: async (username, password, email) => {
    try {
      const response = await api.post('/auth/register', {
        username,
        password,
        email
      });
      return response;
    } catch (error) {
      throw error;
    }
  },

  // 登出
  logout: async () => {
    try {
      await api.post('/auth/logout');
    } catch (error) {
      console.error('Logout error:', error);
    }
  },

  // 刷新 token
  refreshToken: async () => {
    try {
      const response = await api.post('/auth/refresh');
      return response;
    } catch (error) {
      throw error;
    }
  }
};
