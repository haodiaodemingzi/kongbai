import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  ScrollView,
  StyleSheet,
  ActivityIndicator,
  TouchableOpacity,
  Alert,
} from 'react-native';
import { MaterialIcons } from '@expo/vector-icons';
import { getPlayerDetail } from '../services/api';

export default function PlayerDetailScreen({ playerName, onBack }) {
  
  const [loading, setLoading] = useState(true);
  const [playerData, setPlayerData] = useState(null);

  useEffect(() => {
    fetchPlayerDetail();
  }, []);

  const fetchPlayerDetail = async () => {
    try {
      setLoading(true);
      const result = await getPlayerDetail(playerName);
      
      if (result.success) {
        setPlayerData(result.data);
      } else {
        Alert.alert('错误', result.message || '获取玩家详情失败');
      }
    } catch (error) {
      console.error('获取玩家详情失败:', error);
      Alert.alert('错误', '获取玩家详情失败');
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <View style={styles.loadingContainer}>
        <ActivityIndicator size="large" color="#3498db" />
        <Text style={styles.loadingText}>加载中...</Text>
      </View>
    );
  }

  if (!playerData) {
    return (
      <View style={styles.container}>
        <TouchableOpacity
          style={styles.backIconButton}
          onPress={onBack}
        >
          <MaterialIcons name="arrow-back" size={24} color="#2c3e50" />
        </TouchableOpacity>
        <View style={styles.errorContainer}>
          <Text style={styles.errorText}>未找到玩家信息</Text>
        </View>
      </View>
    );
  }

  return (
    <View style={styles.container}>
      {/* 返回按钮 */}
      <TouchableOpacity
        style={styles.backIconButton}
        onPress={onBack}
      >
        <MaterialIcons name="arrow-back" size={24} color="#2c3e50" />
      </TouchableOpacity>

      <ScrollView style={styles.scrollView}>
        {/* 头部信息 */}
        <View style={styles.header}>
        <Text style={styles.playerName}>{playerData.name}</Text>
        <View style={styles.infoRow}>
          <Text style={styles.infoLabel}>势力：</Text>
          <Text style={styles.infoValue}>{playerData.faction}</Text>
        </View>
        <View style={styles.infoRow}>
          <Text style={styles.infoLabel}>职业：</Text>
          <Text style={styles.infoValue}>{playerData.job}</Text>
        </View>
      </View>

      {/* 统计卡片 */}
      <View style={styles.statsContainer}>
        <View style={styles.statCard}>
          <Text style={styles.statValue}>{playerData.kills}</Text>
          <Text style={styles.statLabel}>击杀</Text>
        </View>
        <View style={styles.statCard}>
          <Text style={[styles.statValue, styles.deathValue]}>
            {playerData.deaths}
          </Text>
          <Text style={styles.statLabel}>死亡</Text>
        </View>
        <View style={styles.statCard}>
          <Text style={[styles.statValue, styles.blessingsValue]}>
            {playerData.blessings}
          </Text>
          <Text style={styles.statLabel}>爆灯</Text>
        </View>
        <View style={styles.statCard}>
          <Text style={styles.statValue}>{playerData.kd_ratio}</Text>
          <Text style={styles.statLabel}>K/D</Text>
        </View>
        <View style={styles.statCard}>
          <Text style={[styles.statValue, styles.scoreValue]}>
            {playerData.score}
          </Text>
          <Text style={styles.statLabel}>总分</Text>
        </View>
      </View>

      {/* 近期战斗记录 */}
      <View style={styles.battlesSection}>
        <Text style={styles.sectionTitle}>近期战斗记录</Text>
        {playerData.recent_battles && playerData.recent_battles.length > 0 ? (
          playerData.recent_battles.map((battle, index) => (
            <View key={battle.id || index} style={styles.battleCard}>
              <View style={styles.battleHeader}>
                <Text
                  style={[
                    styles.battleResult,
                    battle.battle_result === 'win'
                      ? styles.winText
                      : styles.lostText,
                  ]}
                >
                  {battle.battle_result === 'win' ? '胜利' : '失败'}
                </Text>
                <Text style={styles.battleTime}>{battle.publish_at}</Text>
              </View>
              <View style={styles.battleInfo}>
                <Text style={styles.battleLabel}>对手：</Text>
                <Text style={styles.battleValue}>{battle.opponent_name}</Text>
              </View>
              {battle.blessings > 0 && (
                <View style={styles.battleInfo}>
                  <Text style={styles.battleLabel}>爆灯：</Text>
                  <Text style={[styles.battleValue, styles.blessingsValue]}>
                    {battle.blessings}
                  </Text>
                </View>
              )}
              <View style={styles.battleInfo}>
                <Text style={styles.battleLabel}>位置：</Text>
                <Text style={styles.battleValue}>{battle.position}</Text>
              </View>
            </View>
          ))
        ) : (
          <Text style={styles.noDataText}>暂无战斗记录</Text>
        )}
      </View>

      </ScrollView>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f5f6fa',
  },
  backIconButton: {
    position: 'absolute',
    bottom: 20,
    left: 20,
    zIndex: 10,
    width: 40,
    height: 40,
    borderRadius: 20,
    backgroundColor: 'rgba(255, 255, 255, 0.9)',
    justifyContent: 'center',
    alignItems: 'center',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.2,
    shadowRadius: 4,
    elevation: 4,
  },
  scrollView: {
    flex: 1,
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
  errorContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    padding: 20,
  },
  errorText: {
    fontSize: 18,
    color: '#e74c3c',
  },
  header: {
    backgroundColor: '#2c3e50',
    padding: 20,
    paddingTop: 60,
  },
  playerName: {
    fontSize: 28,
    fontWeight: 'bold',
    color: '#fff',
    marginBottom: 15,
  },
  infoRow: {
    flexDirection: 'row',
    marginBottom: 8,
  },
  infoLabel: {
    fontSize: 16,
    color: '#bdc3c7',
    width: 60,
  },
  infoValue: {
    fontSize: 16,
    color: '#fff',
    fontWeight: '600',
  },
  statsContainer: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    padding: 15,
    justifyContent: 'space-between',
  },
  statCard: {
    backgroundColor: '#fff',
    width: '30%',
    padding: 15,
    borderRadius: 10,
    alignItems: 'center',
    marginBottom: 15,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  statValue: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#27ae60',
    marginBottom: 5,
  },
  deathValue: {
    color: '#e74c3c',
  },
  blessingsValue: {
    color: '#f39c12',
  },
  scoreValue: {
    color: '#3498db',
  },
  statLabel: {
    fontSize: 12,
    color: '#7f8c8d',
  },
  battlesSection: {
    padding: 15,
  },
  sectionTitle: {
    fontSize: 20,
    fontWeight: 'bold',
    color: '#2c3e50',
    marginBottom: 15,
  },
  battleCard: {
    backgroundColor: '#fff',
    padding: 15,
    borderRadius: 10,
    marginBottom: 10,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.1,
    shadowRadius: 2,
    elevation: 2,
  },
  battleHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 10,
    paddingBottom: 10,
    borderBottomWidth: 1,
    borderBottomColor: '#ecf0f1',
  },
  battleResult: {
    fontSize: 16,
    fontWeight: 'bold',
  },
  winText: {
    color: '#27ae60',
  },
  lostText: {
    color: '#e74c3c',
  },
  battleTime: {
    fontSize: 12,
    color: '#7f8c8d',
  },
  battleInfo: {
    flexDirection: 'row',
    marginBottom: 5,
  },
  battleLabel: {
    fontSize: 14,
    color: '#7f8c8d',
    width: 60,
  },
  battleValue: {
    fontSize: 14,
    color: '#2c3e50',
    fontWeight: '500',
  },
  noDataText: {
    textAlign: 'center',
    fontSize: 16,
    color: '#7f8c8d',
    marginTop: 20,
  },
});
