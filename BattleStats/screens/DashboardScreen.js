import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  ScrollView,
  StyleSheet,
  ActivityIndicator,
  RefreshControl,
  Dimensions,
  TouchableOpacity,
} from 'react-native';
import { MaterialIcons } from '@expo/vector-icons';
import { useTheme } from '../contexts/ThemeContext';
import AsyncStorage from '@react-native-async-storage/async-storage';

const API_BASE_URL = 'https://bigmang.xyz';
const TOKEN_KEY = '@battle_stats_token';

const screenWidth = Dimensions.get('window').width;

// 时间范围选项
const TIME_RANGES = [
  { label: '今天', value: 'today' },
  { label: '昨天', value: 'yesterday' },
  { label: '7天', value: 'week' },
  { label: '30天', value: 'month' },
];

export default function DashboardScreen() {
  const { colors } = useTheme();
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [dashboardData, setDashboardData] = useState(null);
  const [selectedTimeRange, setSelectedTimeRange] = useState('week');

  useEffect(() => {
    fetchDashboardData();
  }, [selectedTimeRange]);

  const fetchDashboardData = async () => {
    try {
      const token = await AsyncStorage.getItem(TOKEN_KEY);
      const response = await fetch(
        `${API_BASE_URL}/api/dashboard?date_range=${selectedTimeRange}`,
        {
          headers: {
            'Authorization': `Bearer ${token}`,
          },
        }
      );

      const result = await response.json();

      if (result.status === 'success') {
        setDashboardData(result.data);
      }
    } catch (error) {
      console.error('获取仪表盘数据失败:', error);
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  const onRefresh = () => {
    setRefreshing(true);
    fetchDashboardData();
  };

  if (loading) {
    return (
      <View style={styles.loadingContainer}>
        <ActivityIndicator size="large" color={colors.primary} />
        <Text style={styles.loadingText}>加载中...</Text>
      </View>
    );
  }

  if (!dashboardData) {
    return (
      <View style={styles.emptyContainer}>
        <MaterialIcons name="dashboard" size={64} color="#bdc3c7" />
        <Text style={styles.emptyText}>暂无数据</Text>
      </View>
    );
  }

  const { summary, faction_stats, top_rankings } = dashboardData;

  // 势力颜色映射
  const factionColors = {
    '梵天': '#f39c12',
    '比湿奴': '#e74c3c',
    '湿婆': '#3498db',
  };

  return (
    <ScrollView
      style={[styles.container, { backgroundColor: colors.background }]}
      refreshControl={
        <RefreshControl refreshing={refreshing} onRefresh={onRefresh} />
      }
    >
      {/* 时间范围选择 */}
      <View style={[styles.timeRangeContainer, { backgroundColor: colors.cardBackground }]}>
        <ScrollView horizontal showsHorizontalScrollIndicator={false}>
          {TIME_RANGES.map((range) => (
            <TouchableOpacity
              key={range.value}
              style={[
                styles.timeRangeButton,
                { borderColor: colors.border },
                selectedTimeRange === range.value && { backgroundColor: colors.primary },
              ]}
              onPress={() => setSelectedTimeRange(range.value)}
            >
              <Text
                style={[
                  styles.timeRangeText,
                  { color: colors.text },
                  selectedTimeRange === range.value && { color: colors.headerText },
                ]}
              >
                {range.label}
              </Text>
            </TouchableOpacity>
          ))}
        </ScrollView>
      </View>

      {/* 统计卡片 */}
      <View style={styles.summaryContainer}>
        <View style={[styles.statCard, { backgroundColor: colors.cardBackground }]}>
          <MaterialIcons name="flash-on" size={24} color="#f39c12" />
          <Text style={[styles.statValue, { color: colors.text }]}>{summary.total_kills}</Text>
          <Text style={[styles.statLabel, { color: colors.textSecondary }]}>总击杀</Text>
        </View>

        <View style={[styles.statCard, { backgroundColor: colors.cardBackground }]}>
          <MaterialIcons name="dangerous" size={24} color="#e74c3c" />
          <Text style={[styles.statValue, { color: colors.text }]}>{summary.total_deaths}</Text>
          <Text style={[styles.statLabel, { color: colors.textSecondary }]}>总死亡</Text>
        </View>

        <View style={[styles.statCard, { backgroundColor: colors.cardBackground }]}>
          <MaterialIcons name="lightbulb" size={24} color="#f1c40f" />
          <Text style={[styles.statValue, { color: colors.text }]}>{summary.total_blessings}</Text>
          <Text style={[styles.statLabel, { color: colors.textSecondary }]}>总爆灯</Text>
        </View>

        <View style={[styles.statCard, { backgroundColor: colors.cardBackground }]}>
          <MaterialIcons name="people" size={24} color={colors.primary} />
          <Text style={[styles.statValue, { color: colors.text }]}>{summary.total_players}</Text>
          <Text style={[styles.statLabel, { color: colors.textSecondary }]}>玩家数</Text>
        </View>
      </View>

      {/* 势力数据统计 */}
      <View style={[styles.factionSection, { backgroundColor: colors.cardBackground }]}>
        <Text style={[styles.sectionTitle, { color: colors.text }]}>势力数据统计</Text>
        {faction_stats.chart_data.factions.map((faction, index) => {
          const kills = faction_stats.chart_data.kills[index];
          const deaths = faction_stats.chart_data.deaths[index];
          const blessings = faction_stats.chart_data.blessings[index];
          const playerCount = faction_stats.player_counts[faction] || 0;
          const factionColor = factionColors[faction];

          return (
            <View key={faction} style={[styles.factionCard, { borderLeftColor: factionColor }]}>
              <View style={styles.factionHeader}>
                <Text style={[styles.factionName, { color: factionColor }]}>{faction}</Text>
                <View style={[styles.playerCountBadge, { backgroundColor: factionColor }]}>
                  <MaterialIcons name="people" size={14} color="#fff" />
                  <Text style={styles.playerCountText}>{playerCount}</Text>
                </View>
              </View>
              <View style={styles.factionStats}>
                <View style={styles.factionStatItem}>
                  <Text style={[styles.factionStatLabel, { color: colors.textSecondary }]}>击杀</Text>
                  <Text style={[styles.factionStatValue, { color: colors.text }]}>{kills}</Text>
                </View>
                <View style={styles.factionStatItem}>
                  <Text style={[styles.factionStatLabel, { color: colors.textSecondary }]}>死亡</Text>
                  <Text style={[styles.factionStatValue, { color: colors.text }]}>{deaths}</Text>
                </View>
                <View style={styles.factionStatItem}>
                  <Text style={[styles.factionStatLabel, { color: colors.textSecondary }]}>爆灯</Text>
                  <Text style={[styles.factionStatValue, { color: colors.text }]}>{blessings}</Text>
                </View>
              </View>
            </View>
          );
        })}
      </View>

      {/* Top 排行榜 */}
      <View style={[styles.rankingSection, { backgroundColor: colors.cardBackground }]}>
        <Text style={[styles.sectionTitle, { color: colors.text }]}>击杀榜 Top 5</Text>
        {top_rankings.top_killers.map((player, index) => (
          <View key={index} style={[styles.rankingItem, { borderBottomColor: colors.border }]}>
            <View style={styles.rankingLeft}>
              <Text style={[styles.rankNumber, { color: colors.primary }]}>#{index + 1}</Text>
              <Text style={[styles.playerName, { color: colors.text }]}>{player.name}</Text>
            </View>
            <Text style={[styles.scoreValue, { color: colors.primary }]}>{player.kills}</Text>
          </View>
        ))}
      </View>

      <View style={[styles.rankingSection, { backgroundColor: colors.cardBackground }]}>
        <Text style={[styles.sectionTitle, { color: colors.text }]}>得分榜 Top 5</Text>
        {top_rankings.top_scorers.map((player, index) => (
          <View key={index} style={[styles.rankingItem, { borderBottomColor: colors.border }]}>
            <View style={styles.rankingLeft}>
              <Text style={[styles.rankNumber, { color: colors.primary }]}>#{index + 1}</Text>
              <Text style={[styles.playerName, { color: colors.text }]}>{player.name}</Text>
            </View>
            <Text style={[styles.scoreValue, { color: colors.primary }]}>{player.score}</Text>
          </View>
        ))}
      </View>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
  },
  loadingContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
  },
  loadingText: {
    marginTop: 10,
    fontSize: 16,
    color: '#7f8c8d',
  },
  emptyContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    padding: 40,
  },
  emptyText: {
    marginTop: 12,
    fontSize: 16,
    color: '#95a5a6',
  },
  timeRangeContainer: {
    padding: 12,
    borderBottomWidth: 1,
    borderBottomColor: '#ecf0f1',
  },
  timeRangeButton: {
    paddingHorizontal: 16,
    paddingVertical: 8,
    borderRadius: 20,
    borderWidth: 1,
    marginRight: 8,
  },
  timeRangeText: {
    fontSize: 14,
    fontWeight: '500',
  },
  summaryContainer: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    padding: 15,
    gap: 10,
  },
  statCard: {
    width: (screenWidth - 50) / 2,
    padding: 15,
    borderRadius: 12,
    alignItems: 'center',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  statValue: {
    fontSize: 28,
    fontWeight: 'bold',
    marginTop: 8,
  },
  statLabel: {
    fontSize: 12,
    marginTop: 4,
  },
  factionSection: {
    margin: 15,
    marginTop: 0,
    padding: 15,
    borderRadius: 12,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  factionCard: {
    borderLeftWidth: 4,
    backgroundColor: '#f8f9fa',
    padding: 12,
    borderRadius: 8,
    marginBottom: 12,
  },
  factionHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 12,
  },
  factionName: {
    fontSize: 18,
    fontWeight: 'bold',
  },
  playerCountBadge: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingHorizontal: 8,
    paddingVertical: 4,
    borderRadius: 12,
    gap: 4,
  },
  playerCountText: {
    color: '#fff',
    fontSize: 12,
    fontWeight: '600',
  },
  factionStats: {
    flexDirection: 'row',
    justifyContent: 'space-around',
  },
  factionStatItem: {
    alignItems: 'center',
  },
  factionStatLabel: {
    fontSize: 12,
    marginBottom: 4,
  },
  factionStatValue: {
    fontSize: 20,
    fontWeight: 'bold',
  },
  rankingSection: {
    margin: 15,
    marginTop: 0,
    padding: 15,
    borderRadius: 12,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  sectionTitle: {
    fontSize: 16,
    fontWeight: '600',
    marginBottom: 15,
  },
  rankingItem: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingVertical: 12,
    borderBottomWidth: 1,
  },
  rankingLeft: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  rankNumber: {
    fontSize: 16,
    fontWeight: 'bold',
    width: 40,
  },
  playerName: {
    fontSize: 15,
    fontWeight: '500',
  },
  scoreValue: {
    fontSize: 16,
    fontWeight: 'bold',
  },
});
