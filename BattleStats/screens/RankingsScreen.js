import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  ScrollView,
  StyleSheet,
  ActivityIndicator,
  RefreshControl,
  TouchableOpacity,
} from 'react-native';
import { scrapeRankings } from '../services/rankingScraper';

// 势力颜色映射
const GOD_COLORS = {
  '梵天': '#FFD700',
  '比湿奴': '#FF6347',
  '湿婆': '#4169E1',
};

// 等级颜色映射
const LEVEL_COLORS = {
  '君主': '#FFD700',
  '化身': '#9C27B0',
  '婆罗门': '#4CAF50',
  '刹帝利': '#2196F3',
};

export default function RankingsScreen() {
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [rankingData, setRankingData] = useState(null);
  const [updateTime, setUpdateTime] = useState('');

  useEffect(() => {
    fetchRankings();
  }, []);

  const fetchRankings = async () => {
    try {
      // 使用爬虫服务获取排名数据
      const data = await scrapeRankings();
      
      setRankingData({
        brahma_players: data.brahmaPlayers,
        vishnu_players: data.vishnuPlayers,
        shiva_players: data.shivaPlayers,
      });
      setUpdateTime(data.updateTime);
    } catch (error) {
      console.error('获取排名失败:', error);
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  const onRefresh = () => {
    setRefreshing(true);
    fetchRankings();
  };

  const renderGodRanking = (title, players, color) => {
    if (!players || players.length === 0) return null;

    return (
      <View style={styles.godCard}>
        <View style={styles.godHeader}>
          <View style={[styles.godIcon, { backgroundColor: color }]} />
          <Text style={styles.godTitle}>{title}</Text>
          <View style={styles.countBadge}>
            <Text style={styles.countText}>{players.length}</Text>
          </View>
        </View>

        <View style={styles.tableHeader}>
          <Text style={[styles.headerCell, styles.rankCell]}>#</Text>
          <Text style={[styles.headerCell, styles.nameCell]}>玩家名</Text>
          <Text style={[styles.headerCell, styles.jobCell]}>职业</Text>
          <Text style={[styles.headerCell, styles.levelCell]}>级别</Text>
        </View>

        {players.map((player) => (
          <View key={`${player.god}-${player.rank}`} style={styles.tableRow}>
            <Text style={[styles.cell, styles.rankCell]}>{player.rank}</Text>
            <Text style={[styles.cell, styles.nameCell]} numberOfLines={1}>
              {player.name}
            </Text>
            <View style={[styles.cell, styles.jobCell]}>
              <View style={styles.jobBadge}>
                <Text style={styles.jobText}>{player.job}</Text>
              </View>
            </View>
            <View style={[styles.cell, styles.levelCell]}>
              <View
                style={[
                  styles.levelBadge,
                  { backgroundColor: LEVEL_COLORS[player.level] || '#999' },
                ]}
              >
                <Text style={styles.levelText}>{player.level}</Text>
              </View>
            </View>
          </View>
        ))}
      </View>
    );
  };

  if (loading) {
    return (
      <View style={styles.loadingContainer}>
        <ActivityIndicator size="large" color="#3498db" />
        <Text style={styles.loadingText}>加载中...</Text>
      </View>
    );
  }

  return (
    <View style={styles.container}>
      {/* 顶部标题 */}
      <View style={styles.header}>
        <Text style={styles.headerTitle}>虎威主神排行榜</Text>
        <Text style={styles.updateTime}>更新时间: {updateTime}</Text>
      </View>

      <ScrollView
        style={styles.content}
        refreshControl={
          <RefreshControl refreshing={refreshing} onRefresh={onRefresh} />
        }
      >
        {rankingData && (
          <>
            {renderGodRanking('梵天', rankingData.brahma_players, GOD_COLORS['梵天'])}
            {renderGodRanking('比湿奴', rankingData.vishnu_players, GOD_COLORS['比湿奴'])}
            {renderGodRanking('湿婆', rankingData.shiva_players, GOD_COLORS['湿婆'])}
          </>
        )}
      </ScrollView>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f5f6fa',
  },
  loadingContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: '#f5f6fa',
  },
  loadingText: {
    marginTop: 10,
    fontSize: 16,
    color: '#7f8c8d',
  },
  header: {
    backgroundColor: '#2c3e50',
    paddingTop: 50,
    paddingBottom: 20,
    paddingHorizontal: 20,
    alignItems: 'center',
  },
  headerTitle: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#fff',
  },
  updateTime: {
    fontSize: 12,
    color: '#bdc3c7',
    marginTop: 5,
  },
  content: {
    flex: 1,
    padding: 15,
  },
  godCard: {
    backgroundColor: '#fff',
    borderRadius: 12,
    padding: 15,
    marginBottom: 15,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  godHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 15,
    paddingBottom: 10,
    borderBottomWidth: 1,
    borderBottomColor: '#ecf0f1',
  },
  godIcon: {
    width: 24,
    height: 24,
    borderRadius: 12,
    marginRight: 10,
  },
  godTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#2c3e50',
    flex: 1,
  },
  countBadge: {
    backgroundColor: '#3498db',
    paddingHorizontal: 10,
    paddingVertical: 4,
    borderRadius: 12,
  },
  countText: {
    color: '#fff',
    fontSize: 12,
    fontWeight: 'bold',
  },
  tableHeader: {
    flexDirection: 'row',
    paddingVertical: 10,
    borderBottomWidth: 2,
    borderBottomColor: '#ecf0f1',
  },
  headerCell: {
    fontSize: 14,
    fontWeight: 'bold',
    color: '#7f8c8d',
  },
  tableRow: {
    flexDirection: 'row',
    paddingVertical: 12,
    borderBottomWidth: 1,
    borderBottomColor: '#f8f9fa',
  },
  cell: {
    fontSize: 14,
    color: '#2c3e50',
  },
  rankCell: {
    width: 40,
    textAlign: 'center',
  },
  nameCell: {
    flex: 1,
    paddingHorizontal: 5,
  },
  jobCell: {
    width: 60,
    alignItems: 'center',
  },
  levelCell: {
    width: 70,
    alignItems: 'center',
  },
  jobBadge: {
    backgroundColor: '#3498db',
    paddingHorizontal: 8,
    paddingVertical: 4,
    borderRadius: 4,
  },
  jobText: {
    color: '#fff',
    fontSize: 12,
    fontWeight: '600',
  },
  levelBadge: {
    paddingHorizontal: 8,
    paddingVertical: 4,
    borderRadius: 4,
  },
  levelText: {
    color: '#fff',
    fontSize: 12,
    fontWeight: '600',
  },
});
