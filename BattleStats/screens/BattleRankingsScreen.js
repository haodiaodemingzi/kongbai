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
} from 'react-native';
import { MaterialIcons, FontAwesome5 } from '@expo/vector-icons';
import { getPlayerRankings } from '../services/api';
import PlayerDetailScreen from './PlayerDetailScreen';

// 时间范围选项
const TIME_RANGES = [
  { label: '今天', value: 'today' },
  { label: '昨天', value: 'yesterday' },
  { label: '7天', value: 'week' },
  { label: '30天', value: 'month' },
  { label: '3个月', value: 'three_months' },
  { label: '全部', value: 'all' },
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
  const [selectedPlayer, setSelectedPlayer] = useState(null);

  useEffect(() => {
    fetchRankings();
  }, [selectedTime, selectedFaction]);

  const fetchRankings = async () => {
    try {
      const result = await getPlayerRankings({
        time_range: selectedTime,
        faction: selectedFaction,
      });

      if (result.success) {
        // 处理返回的数据，添加 K/D 比率
        const processedData = result.data.rankings.map((player) => ({
          ...player,
          kd_ratio: player.deaths > 0 
            ? (player.kills / player.deaths).toFixed(2) 
            : player.kills.toFixed(2),
        }));
        setPlayers(processedData);
      } else {
        Alert.alert('错误', result.message || '获取排名失败');
        setPlayers([]);
      }
    } catch (error) {
      console.error('获取战绩失败:', error);
      Alert.alert('错误', '网络错误，请稍后重试');
      setPlayers([]);
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  const onRefresh = async () => {
    setRefreshing(true);
    await fetchRankings();
    setRefreshing(false);
  };

  // 如果选中了玩家，显示玩家详情
  if (selectedPlayer) {
    return (
      <PlayerDetailScreen
        playerName={selectedPlayer}
        onBack={() => setSelectedPlayer(null)}
      />
    );
  }

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
          <View style={[styles.headerCell, styles.rankCell]}>
            <MaterialIcons name="format-list-numbered" size={14} color="#7f8c8d" />
          </View>
          <Text style={[styles.headerCell, styles.nameCell]}>玩家</Text>
          <Text style={[styles.headerCell, styles.jobCell]}>职业</Text>
          <View style={[styles.headerCell, styles.killsCell]}>
            <FontAwesome5 name="skull-crossbones" size={12} color="#e74c3c" />
          </View>
          <View style={[styles.headerCell, styles.deathsCell]}>
            <MaterialIcons name="dangerous" size={14} color="#95a5a6" />
          </View>
          <View style={[styles.headerCell, styles.blessingsCell]}>
            <MaterialIcons name="wb-sunny" size={14} color="#f39c12" />
          </View>
          <Text style={[styles.headerCell, styles.kdCell]}>K/D</Text>
          <View style={[styles.headerCell, styles.scoreCell]}>
            <MaterialIcons name="stars" size={14} color="#f1c40f" />
          </View>
        </View>

        {/* 数据行 */}
        {players.map((player) => (
          <TouchableOpacity
            key={player.id}
            style={styles.tableRow}
            onPress={() => setSelectedPlayer(player.name)}
          >
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
            <Text style={[styles.cell, styles.blessingsCell, styles.blessingsText]}>
              {player.blessings || 0}
            </Text>
            <Text style={[styles.cell, styles.kdCell]}>{player.kd_ratio}</Text>
            <Text style={[styles.cell, styles.scoreCell, styles.scoreText]}>
              {player.score}
            </Text>
          </TouchableOpacity>
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
    width: 40,
  },
  deathsCell: {
    width: 40,
  },
  blessingsCell: {
    width: 40,
  },
  kdCell: {
    width: 45,
  },
  scoreCell: {
    width: 45,
  },
  killsText: {
    color: '#27ae60',
    fontWeight: '600',
  },
  deathsText: {
    color: '#e74c3c',
    fontWeight: '600',
  },
  blessingsText: {
    color: '#f39c12',
    fontWeight: '600',
  },
  scoreText: {
    color: '#3498db',
    fontWeight: 'bold',
  },
});
