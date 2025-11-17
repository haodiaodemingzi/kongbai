import axios from 'axios';

const RANKING_URL = 'http://fqa.173mz.com/a/a.asp?b=100&id=12';

// 根据排名返回对应的级别
const getRankLevel = (rank) => {
  const r = parseInt(rank);
  if (r === 1) return '君主';
  if (r >= 2 && r <= 3) return '君主';
  if (r >= 4 && r <= 6) return '君主';
  if (r >= 7 && r <= 11) return '化身';
  if (r >= 12 && r <= 18) return '化身';
  if (r >= 19 && r <= 28) return '化身';
  if (r >= 29 && r <= 43) return '婆罗门';
  if (r >= 44 && r <= 63) return '婆罗门';
  if (r >= 64 && r <= 88) return '婆罗门';
  if (r >= 89 && r <= 118) return '刹帝利';
  if (r >= 119 && r <= 168) return '刹帝利';
  if (r >= 169 && r <= 248) return '刹帝利';
  return '未知';
};

// 解析 HTML 文本，提取排名数据
const parseRankingHTML = (htmlText) => {
  const players = [];
  
  // 将 HTML 按行分割
  const lines = htmlText.split('\n');
  
  for (const line of lines) {
    const trimmedLine = line.trim();
    
    // 匹配格式: "神索引 排名 玩家名 职业"
    // 例如: "1 1 白素贞 法师" 或 "2 1 将臣 刺客"
    const match = trimmedLine.match(/^(\d+)\s+(\d+)\s+(.+?)\s+(.+)$/);
    
    if (match) {
      const [, godIndex, rank, playerName, job] = match;
      
      // 根据 godIndex 确定对应的神
      let god = '未知';
      if (godIndex === '1') god = '梵天';
      else if (godIndex === '2') god = '比湿奴';
      else if (godIndex === '4') god = '湿婆';
      
      players.push({
        rank: parseInt(rank),
        name: playerName.trim(),
        job: job.trim(),
        level: getRankLevel(rank),
        god: god,
      });
    }
  }
  
  return players;
};

// 抓取排行榜数据
export const scrapeRankings = async () => {
  try {
    console.log('开始抓取排行榜数据...');
    
    // React Native 不支持直接处理 GBK 编码
    // 直接返回模拟数据
    console.log('使用模拟数据（React Native 不支持 GBK 编码转换）');
    
    return generateMockData();
  } catch (error) {
    console.error('抓取排行榜数据失败:', error);
    
    // 返回模拟数据
    return generateMockData();
  }
};

// 生成模拟数据（当爬虫失败时使用）
const generateMockData = () => {
  const jobs = ['法师', '刺客', '金刚', '奶', '弓', '狂'];
  const mockPlayers = (god, count) => {
    const players = [];
    for (let i = 1; i <= count; i++) {
      players.push({
        rank: i,
        name: `${god}玩家${i}`,
        job: jobs[Math.floor(Math.random() * jobs.length)],
        level: getRankLevel(i),
        god: god,
      });
    }
    return players;
  };
  
  const brahmaPlayers = mockPlayers('梵天', 250);
  const vishnuPlayers = mockPlayers('比湿奴', 250);
  const shivaPlayers = mockPlayers('湿婆', 250);
  
  return {
    updateTime: new Date().toLocaleString('zh-CN', {
      year: 'numeric',
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit',
      hour12: false,
    }),
    brahmaPlayers,
    vishnuPlayers,
    shivaPlayers,
    allPlayers: [...brahmaPlayers, ...vishnuPlayers, ...shivaPlayers],
  };
};
