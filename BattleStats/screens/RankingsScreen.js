import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  ScrollView,
  StyleSheet,
  ActivityIndicator,
  RefreshControl,
  TouchableOpacity,
  Alert,
  Animated,
} from 'react-native';
import { MaterialIcons, Ionicons } from '@expo/vector-icons';
import { LinearGradient } from 'expo-linear-gradient';
import { getGodRankings } from '../services/api';

// 势力颜色映射
const GOD_COLORS = {
  '梵天': '#f39c12',  // 橘黄色
  '比湿奴': '#e74c3c',  // 鲜红色
  '湿婆': '#3498db',  // 蓝色
};

// 等级颜色映射
const LEVEL_COLORS = {
  '君主': '#FFD700',
  '化身': '#9C27B0',
  '婆罗门': '#4CAF50',
  '刹帝利': '#2196F3',
};

// 标签选项
const TABS = [
  { label: '梵天', value: 'brahma', key: 'brahma_players' },
  { label: '比湿奴', value: 'vishnu', key: 'vishnu_players' },
  { label: '湿婆', value: 'shiva', key: 'shiva_players' },
];

export default function RankingsScreen() {
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [rankingData, setRankingData] = useState(null);
  const [updateTime, setUpdateTime] = useState('');
  const [selectedTab, setSelectedTab] = useState('brahma');

  useEffect(() => {
    fetchRankings();
  }, []);

  const fetchRankings = async () => {
    try {
      const result = await getGodRankings();
      
      if (result.success) {
        setRankingData(result.data);
        setUpdateTime(result.data.update_time || '未知');
      } else {
        Alert.alert('提示', result.message || '获取排名失败');
        setRankingData({
          brahma_players: [],
          vishnu_players: [],
          shiva_players: [],
        });
      }
    } catch (error) {
      console.error('获取排名失败:', error);
      Alert.alert('错误', '网络错误，请稍后重试');
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  const onRefresh = () => {
    setRefreshing(true);
    fetchRankings();
  };

  const getCurrentPlayers = () => {
    if (!rankingData) return [];
    const tab = TABS.find(t => t.value === selectedTab);
    return rankingData[tab.key] || [];
  };

  const getCurrentGodName = () => {
    const tab = TABS.find(t => t.value === selectedTab);
    return tab ? tab.label : '';
  };

  if (loading) {
    return (
      <View style={styles.loadingContainer}>
        <ActivityIndicator size="large" color="#3498db" />
        <Text style={styles.loadingText}>加载中...</Text>
      </View>
    );
  }

  const currentPlayers = getCurrentPlayers();
  const currentGodName = getCurrentGodName();

  return (
    <View style={styles.container}>
      {/* 顶部标题 */}
      <View style={styles.header}>
        <Text style={styles.headerTitle}>虎威主神排行榜</Text>
        <Text style={styles.updateTime}>更新时间: {updateTime}</Text>
      </View>

      {/* 标签切换 */}
      <View style={styles.tabContainer}>
        {TABS.map((tab) => {
          const isActive = selectedTab === tab.value;
          return (
            <TouchableOpacity
              key={tab.value}
              style={[
                styles.tab,
                isActive && styles.tabActive,
              ]}
              onPress={() => setSelectedTab(tab.value)}
            >
              {isActive && (
                <LinearGradient
                  colors={[GOD_COLORS[tab.label], GOD_COLORS[tab.label] + 'CC']}
                  style={styles.tabGradient}
                />
              )}
              <View style={[styles.tabIcon, { backgroundColor: GOD_COLORS[tab.label] }]}>
                <MaterialIcons name="military-tech" size={12} color="#fff" />
              </View>
              <Text
                style={[
                  styles.tabText,
                  isActive && styles.tabTextActive,
                ]}
              >
                {tab.label}
              </Text>
              <View style={[styles.tabBadge, isActive && styles.tabBadgeActive]}>
                <Text style={[styles.tabBadgeText, isActive && styles.tabBadgeTextActive]}>
                  {rankingData ? (rankingData[tab.key] || []).length : 0}
                </Text>
              </View>
            </TouchableOpacity>
          );
        })}
      </View>

      {/* 排名列表 */}
      <ScrollView
        style={styles.content}
        refreshControl={
          <RefreshControl refreshing={refreshing} onRefresh={onRefresh} />
        }
      >
        {currentPlayers.length > 0 ? (
          <View style={styles.rankingCard}>
            {/* 表头 */}
            <View style={styles.tableHeader}>
              <Text style={[styles.headerCell, styles.rankCell]}>#</Text>
              <Text style={[styles.headerCell, styles.nameCell]}>玩家名</Text>
              <Text style={[styles.headerCell, styles.jobCell]}>职业</Text>
              <Text style={[styles.headerCell, styles.levelCell]}>级别</Text>
            </View>

            {/* 数据行 */}
            {currentPlayers.map((player, index) => {
              const rank = player.rank || index + 1;
              const isTopThree = rank <= 3;
              return (
                <View key={`${player.god}-${rank}`} style={[styles.tableRow, isTopThree && styles.tableRowHighlight]}>
                  <View style={[styles.cell, styles.rankCell]}>
                    {isTopThree ? (
                      <View style={styles.medalContainer}>
                        <Ionicons 
                          name="medal" 
                          size={24} 
                          color={rank === 1 ? '#FFD700' : rank === 2 ? '#C0C0C0' : '#CD7F32'} 
                        />
                        <Text style={styles.medalText}>{rank}</Text>
                      </View>
                    ) : (
                      <Text style={styles.rankText}>{rank}</Text>
                    )}
                  </View>
                  <Text style={[styles.cell, styles.nameCell]} numberOfLines={1}>
                    {player.name}
                  </Text>
                  <View style={[styles.cell, styles.jobCell]}>
                    <View style={styles.jobBadge}>
                      <Text style={styles.jobText}>{player.job || '未知'}</Text>
                    </View>
                  </View>
                  <View style={[styles.cell, styles.levelCell]}>
                    <View
                      style={[
                        styles.levelBadge,
                        { backgroundColor: LEVEL_COLORS[player.level] || '#999' },
                      ]}
                    >
                      <Text style={styles.levelText}>{player.level || '未知'}</Text>
                    </View>
                  </View>
                </View>
              );
            })}
          </View>
        ) : (
          <View style={styles.emptyContainer}>
            <Text style={styles.emptyText}>暂无{currentGodName}排名数据</Text>
          </View>
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
  tabContainer: {
    flexDirection: 'row',
    backgroundColor: '#fff',
    borderBottomWidth: 1,
    borderBottomColor: '#ecf0f1',
  },
  tab: {
    flex: 1,
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    paddingVertical: 15,
    position: 'relative',
    overflow: 'hidden',
  },
  tabActive: {
    backgroundColor: 'rgba(0, 0, 0, 0.05)',
  },
  tabGradient: {
    position: 'absolute',
    bottom: 0,
    left: 0,
    right: 0,
    height: 3,
  },
  tabIcon: {
    width: 20,
    height: 20,
    borderRadius: 10,
    marginRight: 6,
    justifyContent: 'center',
    alignItems: 'center',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.2,
    shadowRadius: 2,
    elevation: 2,
  },
  tabText: {
    fontSize: 14,
    color: '#7f8c8d',
    fontWeight: '500',
  },
  tabTextActive: {
    color: '#2c3e50',
    fontWeight: 'bold',
  },
  tabBadge: {
    backgroundColor: '#ecf0f1',
    paddingHorizontal: 8,
    paddingVertical: 3,
    borderRadius: 12,
    marginLeft: 6,
    minWidth: 24,
    alignItems: 'center',
  },
  tabBadgeActive: {
    backgroundColor: '#667eea',
  },
  tabBadgeText: {
    fontSize: 11,
    color: '#7f8c8d',
    fontWeight: 'bold',
  },
  tabBadgeTextActive: {
    color: '#fff',
  },
  rankingCard: {
    backgroundColor: '#fff',
    borderRadius: 12,
    padding: 15,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  emptyContainer: {
    backgroundColor: '#fff',
    borderRadius: 12,
    padding: 40,
    alignItems: 'center',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  emptyText: {
    fontSize: 16,
    color: '#7f8c8d',
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
    alignItems: 'center',
  },
  tableRowHighlight: {
    backgroundColor: 'rgba(255, 215, 0, 0.05)',
  },
  cell: {
    fontSize: 14,
    color: '#2c3e50',
  },
  rankCell: {
    width: 50,
    alignItems: 'center',
    justifyContent: 'center',
  },
  medalContainer: {
    position: 'relative',
    alignItems: 'center',
    justifyContent: 'center',
  },
  medalText: {
    position: 'absolute',
    fontSize: 10,
    fontWeight: 'bold',
    color: '#fff',
    textShadowColor: 'rgba(0, 0, 0, 0.5)',
    textShadowOffset: { width: 0, height: 1 },
    textShadowRadius: 2,
  },
  rankText: {
    fontSize: 16,
    fontWeight: '600',
    color: '#7f8c8d',
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
