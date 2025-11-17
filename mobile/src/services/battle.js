import api from './api';

export const battleService = {
  // 上传战斗日志
  uploadBattleLog: async (fileUri, fileName) => {
    try {
      const formData = new FormData();
      formData.append('file', {
        uri: fileUri,
        type: 'text/plain',
        name: fileName
      });

      const response = await api.post('/battle/upload', formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      });
      return response;
    } catch (error) {
      throw error;
    }
  },

  // 获取上传历史
  getUploadHistory: async () => {
    try {
      const response = await api.get('/battle/history');
      return response;
    } catch (error) {
      throw error;
    }
  },

  // 导出数据
  exportData: async (faction = null) => {
    try {
      const url = faction ? `/battle/export?faction=${faction}` : '/battle/export';
      const response = await api.get(url);
      return response;
    } catch (error) {
      throw error;
    }
  }
};
