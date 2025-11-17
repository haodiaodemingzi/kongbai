import api from './api';

export const rankingService = {
  // 获取玩家排名
  getPlayerRankings: async (faction = null, timeRange = 'week', job = null) => {
    try {
      const params = new URLSearchParams();
      if (faction && faction !== 'all') {
        params.append('faction', faction);
      }
      if (job && job !== 'all') {
        params.append('job', job);
      }
      params.append('time_range', timeRange);

      const response = await api.get(`/battle/rankings?${params.toString()}`);
      return response;
    } catch (error) {
      throw error;
    }
  },

  // 获取玩家详情
  getPlayerDetail: async (playerName) => {
    try {
      const response = await api.get(`/battle/player/${playerName}`);
      return response;
    } catch (error) {
      throw error;
    }
  },

  // 获取首页统计数据
  getFactionStats: async (dateRange = 'week') => {
    try {
      const response = await api.get(`/?date_range=${dateRange}`);
      return response;
    } catch (error) {
      throw error;
    }
  },

  // 获取每日击杀数据
  getDailyKills: async (dateRange = 'week', limit = 5) => {
    try {
      const response = await api.get(`/daily-kills?date_range=${dateRange}&limit=${limit}`);
      return response;
    } catch (error) {
      throw error;
    }
  },

  // 获取每日死亡数据
  getDailyDeaths: async (dateRange = 'week', limit = 5) => {
    try {
      const response = await api.get(`/daily-deaths?date_range=${dateRange}&limit=${limit}`);
      return response;
    } catch (error) {
      throw error;
    }
  },

  // 获取每日得分数据
  getDailyScores: async (dateRange = 'week', limit = 5) => {
    try {
      const response = await api.get(`/daily-scores?date_range=${dateRange}&limit=${limit}`);
      return response;
    } catch (error) {
      throw error;
    }
  },

  // 获取排行榜数据
  getRankingData: async (category = '主神排行榜', refresh = false) => {
    try {
      const response = await api.get(`/ranking/data?category=${category}&refresh=${refresh}`);
      return response;
    } catch (error) {
      throw error;
    }
  },

  // 获取排行榜历史
  getRankingHistory: async (category = '主神排行榜', limit = 10) => {
    try {
      const response = await api.get(`/ranking/history?category=${category}&limit=${limit}`);
      return response;
    } catch (error) {
      throw error;
    }
  }
};
