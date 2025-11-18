import React, { useState, useEffect } from 'react';
import { StatusBar } from 'expo-status-bar';
import { StyleSheet, Text, View, ScrollView, TouchableOpacity, ActivityIndicator, Alert } from 'react-native';
import { MaterialIcons } from '@expo/vector-icons';
import LoginScreen from './screens/LoginScreen';
import RankingsScreen from './screens/RankingsScreen';
import BattleRankingsScreen from './screens/BattleRankingsScreen';
import { getDashboardData, logout, getStoredToken, getStoredUser } from './services/api';

export default function App() {
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [username, setUsername] = useState('');
  const [token, setToken] = useState(null);
  const [currentScreen, setCurrentScreen] = useState('home'); // 'home', 'rankings', 'battle'
  const [loading, setLoading] = useState(true);
  const [dashboardData, setDashboardData] = useState(null);
  const [selectedDateRange, setSelectedDateRange] = useState('week');

  // 检查本地是否有保存的 token
  useEffect(() => {
    checkStoredToken();
  }, []);

  // 登录成功后加载首页数据
  useEffect(() => {
    if (isLoggedIn && currentScreen === 'home') {
      loadDashboardData();
    }
  }, [isLoggedIn, currentScreen, selectedDateRange]);

  const checkStoredToken = async () => {
    try {
      const storedToken = await getStoredToken();
      const storedUser = await getStoredUser();
      
      if (storedToken && storedUser) {
        setToken(storedToken);
        setUsername(storedUser.username);
        setIsLoggedIn(true);
      }
    } catch (error) {
      console.error('检查 token 失败:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleLoginSuccess = (user, userToken) => {
    setUsername(user.username);
    setToken(userToken);
    setIsLoggedIn(true);
    setLoading(false);
  };

  const handleLogout = async () => {
    try {
      await logout();
      setIsLoggedIn(false);
      setUsername('');
      setToken(null);
      setCurrentScreen('home');
      setDashboardData(null);
    } catch (error) {
      console.error('登出失败:', error);
    }
  };

  const loadDashboardData = async () => {
    try {
      const result = await getDashboardData(selectedDateRange);
      if (result.success) {
        setDashboardData(result.data);
      } else {
        Alert.alert('错误', result.message || '加载数据失败');
      }
    } catch (error) {
      console.error('加载首页数据失败:', error);
    }
  };

  // 初始加载中
  if (loading) {
    return (
      <View style={styles.loadingContainer}>
        <ActivityIndicator size="large" color="#3498db" />
        <Text style={styles.loadingText}>加载中...</Text>
      </View>
    );
  }

  // 如果未登录，显示登录界面
  if (!isLoggedIn) {
    return <LoginScreen onLoginSuccess={handleLoginSuccess} />;
  }

  // 如果在排名页面
  if (currentScreen === 'rankings') {
    return (
      <View style={styles.container}>
        <TouchableOpacity
          style={styles.backIconButton}
          onPress={() => setCurrentScreen('home')}
        >
          <MaterialIcons name="arrow-back" size={24} color="#2c3e50" />
        </TouchableOpacity>
        <RankingsScreen />
      </View>
    );
  }

  // 如果在战绩页面
  if (currentScreen === 'battle') {
    return (
      <View style={styles.container}>
        <TouchableOpacity
          style={styles.backIconButton}
          onPress={() => setCurrentScreen('home')}
        >
          <MaterialIcons name="arrow-back" size={24} color="#2c3e50" />
        </TouchableOpacity>
        <BattleRankingsScreen />
      </View>
    );
  }

  // 已登录，显示主界面
  return (
    <View style={styles.container}>
      <StatusBar style="light" />
      
      {/* 顶部标题 */}
      <View style={styles.header}>
        <View>
          <Text style={styles.headerTitle}>战斗统计</Text>
          <Text style={styles.headerSubtitle}>欢迎, {username}</Text>
        </View>
        <TouchableOpacity onPress={handleLogout} style={styles.logoutButton}>
          <Text style={styles.logoutText}>登出</Text>
        </TouchableOpacity>
      </View>

      {/* 主要内容 */}
      <ScrollView style={styles.content}>
        {dashboardData ? (
          <>
            {/* 统计卡片 */}
            <View style={styles.statsRow}>
              <View style={styles.statCard}>
                <Text style={styles.statNumber}>{dashboardData.summary.total_kills.toLocaleString()}</Text>
                <Text style={styles.statLabel}>总击杀</Text>
              </View>
              <View style={styles.statCard}>
                <Text style={styles.statNumber}>{dashboardData.summary.total_deaths.toLocaleString()}</Text>
                <Text style={styles.statLabel}>总死亡</Text>
              </View>
            </View>

            <View style={styles.statsRow}>
              <View style={styles.statCard}>
                <Text style={styles.statNumber}>{(dashboardData.summary.total_kills * 3 + dashboardData.summary.total_blessings - dashboardData.summary.total_deaths).toLocaleString()}</Text>
                <Text style={styles.statLabel}>总得分</Text>
              </View>
              <View style={styles.statCard}>
                <Text style={styles.statNumber}>{dashboardData.summary.total_players}</Text>
                <Text style={styles.statLabel}>玩家数</Text>
              </View>
            </View>

            {/* 势力统计 */}
            <View style={styles.section}>
              <Text style={styles.sectionTitle}>势力统计</Text>
              
              {dashboardData.faction_stats.chart_data.factions.map((faction, index) => (
                <View key={faction} style={styles.factionCard}>
                  <View style={[styles.factionBar, { backgroundColor: getFactionColor(faction) }]} />
                  <View style={{ flex: 1 }}>
                    <Text style={styles.factionName}>{faction}</Text>
                    <Text style={styles.factionSubtext}>
                      玩家: {dashboardData.faction_stats.player_counts[faction]}
                    </Text>
                  </View>
                  <View style={{ alignItems: 'flex-end' }}>
                    <Text style={styles.factionScore}>
                      {dashboardData.faction_stats.chart_data.kills[index]}
                    </Text>
                    <Text style={styles.factionSubtext}>击杀</Text>
                  </View>
                </View>
              ))}
            </View>
          </>
        ) : (
          <View style={styles.loadingContainer}>
            <ActivityIndicator size="large" color="#3498db" />
            <Text style={styles.loadingText}>加载数据中...</Text>
          </View>
        )}

        {/* 操作按钮 */}
        <TouchableOpacity
          style={styles.button}
          onPress={() => setCurrentScreen('rankings')}
        >
          <Text style={styles.buttonText}>查看主神排名</Text>
        </TouchableOpacity>

        <TouchableOpacity
          style={[styles.button, styles.buttonSecondary]}
          onPress={() => setCurrentScreen('battle')}
        >
          <Text style={styles.buttonTextSecondary}>查看战绩排名</Text>
        </TouchableOpacity>
      </ScrollView>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f5f6fa',
  },
  header: {
    backgroundColor: '#2c3e50',
    paddingTop: 50,
    paddingBottom: 20,
    paddingHorizontal: 20,
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  logoutButton: {
    backgroundColor: '#e74c3c',
    paddingHorizontal: 16,
    paddingVertical: 8,
    borderRadius: 8,
  },
  logoutText: {
    color: '#fff',
    fontSize: 14,
    fontWeight: '600',
  },
  headerTitle: {
    fontSize: 28,
    fontWeight: 'bold',
    color: '#fff',
  },
  headerSubtitle: {
    fontSize: 14,
    color: '#bdc3c7',
    marginTop: 5,
  },
  content: {
    flex: 1,
    padding: 15,
  },
  statsRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginBottom: 15,
  },
  statCard: {
    flex: 1,
    backgroundColor: '#fff',
    borderRadius: 12,
    padding: 20,
    marginHorizontal: 5,
    alignItems: 'center',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  statNumber: {
    fontSize: 32,
    fontWeight: 'bold',
    color: '#2c3e50',
  },
  statLabel: {
    fontSize: 14,
    color: '#7f8c8d',
    marginTop: 5,
  },
  section: {
    marginTop: 10,
    marginBottom: 20,
  },
  sectionTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#2c3e50',
    marginBottom: 15,
  },
  factionCard: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#fff',
    borderRadius: 12,
    padding: 15,
    marginBottom: 10,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  factionBar: {
    width: 4,
    height: 40,
    borderRadius: 2,
    marginRight: 15,
  },
  factionName: {
    flex: 1,
    fontSize: 16,
    fontWeight: '600',
    color: '#2c3e50',
  },
  factionScore: {
    fontSize: 20,
    fontWeight: 'bold',
    color: '#3498db',
  },
  button: {
    backgroundColor: '#3498db',
    borderRadius: 12,
    padding: 16,
    alignItems: 'center',
    marginBottom: 10,
  },
  buttonText: {
    color: '#fff',
    fontSize: 16,
    fontWeight: '600',
  },
  buttonSecondary: {
    backgroundColor: '#fff',
    borderWidth: 2,
    borderColor: '#3498db',
  },
  buttonTextSecondary: {
    color: '#3498db',
    fontSize: 16,
    fontWeight: '600',
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
  factionSubtext: {
    fontSize: 12,
    color: '#7f8c8d',
    marginTop: 2,
  },
});

// 势力颜色映射
function getFactionColor(faction) {
  const colors = {
    '梵天': '#f39c12',  // 橘黄色
    '比湿奴': '#e74c3c',  // 鲜红色
    '湿婆': '#3498db',  // 蓝色
  };
  return colors[faction] || '#95a5a6';
}
