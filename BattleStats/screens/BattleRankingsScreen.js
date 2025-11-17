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
import axios from 'axios';

const API_URL = 'https://bigmang.xyz';

// 时间范围选项
const TIME_RANGES = [
  { label: '全部', value: 'all' },
  { label: '今天', value: 'today' },
  { label: '昨天', value: 'yesterday' },
  { label: '7天', value: 'week' },
  { label: '30天', value: 'month' },
  { label: '1年', value: 'all' },
];

// 势力选项
const FACTIONS = [
  { label: '全部', value: '' },
  { label: '梵天', value: '梵天' },
  { label: '比湿奴', value: '比湿奴' },
  { label: '湿婆', value: '湿婆' },
];

export default function BattleRankingsScreen() {
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [players, setPlayers] = useState([]);
  const [selectedTime, setSelectedTime] = useState('today');
  const [selectedFaction, setSelectedFaction] = useState('');

  useEffect(() => {
    fetchRankings();
  }, [selectedTime, selectedFaction]);

  const fetchRankings = async () => {
    try {
      const response = await axios.get(`${API_URL}/battle/rankings`, {
        params: {
          time_range: selectedTime,
          faction: selectedFaction,
          show_grouped: 'false',
        },
      });

      // 解析 HTML 响应（实际应该有 JSON API）
      // 这里暂时使用模拟数据
      setPlayers(generateMockData());
    } catch (error) {
      console.error('获取战绩失败:', error);
      setPlayers(generateMockData());
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  const onRefresh = () => {
    setRefreshing(true);
    fetchRankings();
  };

  // 生成模拟数据
  const generateMockData = () => {
    const factions = ['梵天', '比湿奴', '湿婆'];
    const jobs = ['法师', '刺客', '金刚', '奶', '弓', '狂'];
    const data = [];

    for (let i = 1; i <= 20; i++) {
      const kills = Math.floor(Math.random() * 20);
      const deaths = Math.floor(Math.random() * 20);
      const blessings = Math.floor(Math.random() * 5);
      
      data.push({
        id: i,
        rank: i,
        name: `玩家${i}`,
        job: jobs[Math.floor(Math.random() * jobs.length)],
        faction: selectedFaction || factions[Math.floor(Math.random() * factions.length)],
        kills,
        deaths,
        kd_ratio: deaths > 0 ? (kills / deaths).toFixed(2) : kills.toFixed(2),
        blessings,
        score: kills * 3 + blessings - deaths,
      });
    }

    return data.sort((a, b) => b.score - a.score);
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
        <Text style={styles.headerTitle}>战绩排名</Text>
      </View>

      {/* 筛选器 */}
      <View style={styles.filterContainer}>
        {/* 时间筛选 */}
        <View style={styles.filterSection}>
          <Text style={styles.filterLabel}>时间范围</Text>
          <ScrollView horizontal showsHorizontalScrollIndicator={false}>
            <View style={styles.filterButtons}>
              {TIME_RANGES.map((item) => (
                <TouchableOpacity
                  key={item.value}
                  style={[
                    styles.filterButton,
                    selectedTime === item.value && styles.filterButtonActive,
                  ]}
                  onPress={() => setSelectedTime(item.value)}
                >
                  <Text
                    style={[
                      styles.filterButtonText,
                      selectedTime === item.value && styles.filterButtonTextActive,
                    ]}
                  >
                    {item.label}
                  </Text>
                </TouchableOpacity>
              ))}
            </View>
          </ScrollView>
        </View>

        {/* 势力筛选 */}
        <View style={styles.filterSection}>
          <Text style={styles.filterLabel}>势力筛选</Text>
          <View style={styles.filterButtons}>
            {FACTIONS.map((item) => (
              <TouchableOpacity
                key={item.value}
                style={[
                  styles.filterButton,
                  selectedFaction === item.value && styles.filterButtonActive,
                ]}
                onPress={() => setSelectedFaction(item.value)}
              >
                <Text
                  style={[
                    styles.filterButtonText,
                    selectedFaction === item.value && styles.filterButtonTextActive,
                  ]}
                >
                  {item.label}
                </Text>
              </TouchableOpacity>
            ))}
          </View>
        </View>
      </View>

      {/* 排名列表 */}
      <ScrollView
        style={styles.content}
        refreshControl={
          <RefreshControl refreshing={refreshing} onRefresh={onRefresh} />
        }
      >
        {/* 表头 */}
        <View style={styles.tableHeader}>
          <Text style={[styles.headerCell, styles.rankCell]}>排名</Text>
          <Text style={[styles.headerCell, styles.nameCell]}>玩家</Text>
          <Text style={[styles.headerCell, styles.jobCell]}>职业</Text>
          <Text style={[styles.headerCell, styles.killsCell]}>击杀</Text>
          <Text style={[styles.headerCell, styles.deathsCell]}>死亡</Text>
          <Text style={[styles.headerCell, styles.kdCell]}>K/D</Text>
          <Text style={[styles.headerCell, styles.scoreCell]}>总分</Text>
        </View>

        {/* 数据行 */}
        {players.map((player) => (
          <View key={player.id} style={styles.tableRow}>
            <Text style={[styles.cell, styles.rankCell]}>{player.rank}</Text>
            <View style={[styles.cell, styles.nameCell]}>
              <Text style={styles.playerName} numberOfLines={1}>
                {player.name}
              </Text>
              <Text style={styles.factionText}>{player.faction}</Text>
            </View>
            <Text style={[styles.cell, styles.jobCell]}>{player.job}</Text>
            <Text style={[styles.cell, styles.killsCell, styles.killsText]}>
              {player.kills}
            </Text>
            <Text style={[styles.cell, styles.deathsCell, styles.deathsText]}>
              {player.deaths}
            </Text>
            <Text style={[styles.cell, styles.kdCell]}>{player.kd_ratio}</Text>
            <Text style={[styles.cell, styles.scoreCell, styles.scoreText]}>
              {player.score}
            </Text>
          </View>
        ))}
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
  filterContainer: {
    backgroundColor: '#fff',
    padding: 15,
    borderBottomWidth: 1,
    borderBottomColor: '#ecf0f1',
  },
  filterSection: {
    marginBottom: 15,
  },
  filterLabel: {
    fontSize: 14,
    fontWeight: '600',
    color: '#2c3e50',
    marginBottom: 8,
  },
  filterButtons: {
    flexDirection: 'row',
    flexWrap: 'wrap',
  },
  filterButton: {
    paddingHorizontal: 16,
    paddingVertical: 8,
    borderRadius: 20,
    backgroundColor: '#ecf0f1',
    marginRight: 8,
    marginBottom: 8,
  },
  filterButtonActive: {
    backgroundColor: '#3498db',
  },
  filterButtonText: {
    fontSize: 14,
    color: '#7f8c8d',
    fontWeight: '500',
  },
  filterButtonTextActive: {
    color: '#fff',
  },
  content: {
    flex: 1,
    padding: 15,
  },
  tableHeader: {
    flexDirection: 'row',
    backgroundColor: '#2c3e50',
    padding: 12,
    borderRadius: 8,
    marginBottom: 10,
  },
  headerCell: {
    fontSize: 12,
    fontWeight: 'bold',
    color: '#fff',
    textAlign: 'center',
  },
  tableRow: {
    flexDirection: 'row',
    backgroundColor: '#fff',
    padding: 12,
    borderRadius: 8,
    marginBottom: 8,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.1,
    shadowRadius: 2,
    elevation: 2,
  },
  cell: {
    fontSize: 14,
    color: '#2c3e50',
    textAlign: 'center',
  },
  rankCell: {
    width: 40,
  },
  nameCell: {
    flex: 1,
    paddingHorizontal: 5,
  },
  playerName: {
    fontSize: 14,
    fontWeight: '600',
    color: '#2c3e50',
  },
  factionText: {
    fontSize: 11,
    color: '#7f8c8d',
    marginTop: 2,
  },
  jobCell: {
    width: 50,
  },
  killsCell: {
    width: 45,
  },
  deathsCell: {
    width: 45,
  },
  kdCell: {
    width: 50,
  },
  scoreCell: {
    width: 50,
  },
  killsText: {
    color: '#27ae60',
    fontWeight: '600',
  },
  deathsText: {
    color: '#e74c3c',
    fontWeight: '600',
  },
  scoreText: {
    color: '#3498db',
    fontWeight: 'bold',
  },
});
