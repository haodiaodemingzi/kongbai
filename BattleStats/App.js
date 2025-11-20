import React, { useState, useEffect } from 'react';
import { StatusBar } from 'expo-status-bar';
import { NavigationContainer } from '@react-navigation/native';
import { createBottomTabNavigator } from '@react-navigation/bottom-tabs';
import { createNativeStackNavigator } from '@react-navigation/native-stack';
import { MaterialIcons } from '@expo/vector-icons';
import { 
  ActivityIndicator, 
  View, 
  Text, 
  StyleSheet, 
  TouchableOpacity, 
  ScrollView, 
  RefreshControl 
} from 'react-native';
import LoginScreen from './screens/LoginScreen';
import RankingsScreen from './screens/RankingsScreen';
import BattleRankingsScreen from './screens/BattleRankingsScreen';
import UploadScreen from './screens/UploadScreen';
import PersonManagementScreen from './screens/PersonManagementScreen';
import GroupManagementScreen from './screens/GroupManagementScreen';
import { getStoredToken, getStoredUser } from './services/api';

const Tab = createBottomTabNavigator();
const Stack = createNativeStackNavigator();

// 首页组件 - 战绩排名（支持时间筛选）
function HomeScreen({ navigation }) {
  return <BattleRankingsScreen />;
}

// 个人中心组件
function ProfileScreen({ onLogout, navigation }) {
  return (
    <View style={styles.container}>
      <Text style={styles.title}>配置中心</Text>
      
      <TouchableOpacity
        style={styles.menuItem}
        onPress={() => navigation.navigate('PersonManagement')}
      >
        <MaterialIcons name="people" size={24} color="#e74c3c" />
        <Text style={styles.menuItemText}>人员管理</Text>
        <MaterialIcons name="chevron-right" size={24} color="#95a5a6" />
      </TouchableOpacity>
      
      <TouchableOpacity
        style={styles.menuItem}
        onPress={() => navigation.navigate('GroupManagement')}
      >
        <MaterialIcons name="group" size={24} color="#e74c3c" />
        <Text style={styles.menuItemText}>分组管理</Text>
        <MaterialIcons name="chevron-right" size={24} color="#95a5a6" />
      </TouchableOpacity>
      
      <TouchableOpacity
        style={styles.logoutButton}
        onPress={onLogout}
      >
        <MaterialIcons name="logout" size={20} color="#fff" style={{ marginRight: 8 }} />
        <Text style={styles.logoutButtonText}>登出</Text>
      </TouchableOpacity>
    </View>
  );
}

// 底部标签导航
function TabNavigator({ onLogout }) {
  return (
    <Tab.Navigator
      screenOptions={({ route }) => ({
        tabBarIcon: ({ focused, color, size }) => {
          let iconName;
          
          if (route.name === 'Home') {
            iconName = 'home';
          } else if (route.name === 'Rankings') {
            iconName = 'leaderboard';
          } else if (route.name === 'Upload') {
            iconName = 'cloud-upload';
          } else if (route.name === 'Profile') {
            iconName = 'person';
          }
          
          return <MaterialIcons name={iconName} size={size} color={color} />;
        },
        tabBarActiveTintColor: '#ffffff',
        tabBarInactiveTintColor: 'rgba(255, 255, 255, 0.6)',
        tabBarStyle: {
          backgroundColor: '#e74c3c',
          borderTopWidth: 0,
          height: 60,
          paddingBottom: 8,
          paddingTop: 8,
        },
        tabBarLabelStyle: {
          fontSize: 12,
          fontWeight: '600',
        },
        headerStyle: {
          backgroundColor: '#e74c3c',
        },
        headerTintColor: '#fff',
        headerTitleStyle: {
          fontWeight: 'bold',
        },
      })}
    >
      <Tab.Screen 
        name="Home" 
        component={HomeScreen} 
        options={{ 
          title: '首页',
          headerTitle: '战绩排名'
        }} 
      />
      <Tab.Screen 
        name="Rankings" 
        component={RankingsScreen} 
        options={{ 
          title: '排名',
          headerTitle: '主神排名'
        }} 
      />
      <Tab.Screen 
        name="Upload" 
        component={UploadScreen} 
        options={{ 
          title: '上传',
          headerTitle: '上传日志'
        }} 
      />
      <Tab.Screen 
        name="Profile" 
        options={{ 
          title: '管理',
          headerTitle: '配置中心'
        }}
      >
        {(props) => <ProfileScreen {...props} onLogout={onLogout} />}
      </Tab.Screen>
    </Tab.Navigator>
  );
}

// 主堆栈导航（包含二级页面）
function MainStackNavigator({ onLogout }) {
  return (
    <Stack.Navigator
      screenOptions={{
        headerStyle: {
          backgroundColor: '#e74c3c',
        },
        headerTintColor: '#fff',
        headerTitleStyle: {
          fontWeight: 'bold',
        },
        gestureEnabled: true, // 启用手势返回
        gestureDirection: 'horizontal',
      }}
    >
      <Stack.Screen 
        name="MainTabs" 
        options={{ headerShown: false }}
      >
        {(props) => <TabNavigator {...props} onLogout={onLogout} />}
      </Stack.Screen>
      <Stack.Screen 
        name="PersonManagement" 
        component={PersonManagementScreen} 
        options={{ 
          title: '人员管理',
          presentation: 'card',
        }} 
      />
      <Stack.Screen 
        name="GroupManagement" 
        component={GroupManagementScreen} 
        options={{ 
          title: '分组管理',
          presentation: 'card',
        }} 
      />
    </Stack.Navigator>
  );
}

export default function App() {
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [loading, setLoading] = useState(true);

  // 检查本地是否有保存的 token
  useEffect(() => {
    checkStoredToken();
  }, []);

  const checkStoredToken = async () => {
    try {
      // 清除旧的 token，强制用户重新登录
      const AsyncStorage = require('@react-native-async-storage/async-storage').default;
      await AsyncStorage.removeItem('@battle_stats_token');
      await AsyncStorage.removeItem('@battle_stats_user');
      
      // 不自动登录，让用户手动登录
      setIsLoggedIn(false);
    } catch (error) {
      console.error('检查 token 失败:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleLoginSuccess = (user, userToken) => {
    setIsLoggedIn(true);
    setLoading(false);
  };

  const handleLogout = () => {
    setIsLoggedIn(false);
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

  // 已登录，显示主导航
  return (
    <NavigationContainer>
      <StatusBar style="light" />
      <MainStackNavigator onLogout={handleLogout} />
    </NavigationContainer>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f5f6fa',
    justifyContent: 'center',
    alignItems: 'center',
    padding: 20,
  },
  title: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#2c3e50',
    marginBottom: 10,
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
  menuItem: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#fff',
    padding: 16,
    borderRadius: 12,
    marginBottom: 12,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  menuItemText: {
    flex: 1,
    fontSize: 16,
    fontWeight: '600',
    color: '#2c3e50',
    marginLeft: 12,
  },
  logoutButton: {
    backgroundColor: '#e74c3c',
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    paddingVertical: 12,
    paddingHorizontal: 24,
    borderRadius: 8,
    marginTop: 20,
  },
  logoutButtonText: {
    color: '#fff',
    fontSize: 16,
    fontWeight: '600',
  },
  scrollView: {
    flex: 1,
    backgroundColor: '#f5f6fa',
  },
  header: {
    backgroundColor: '#3498db',
    padding: 20,
    paddingTop: 10,
  },
  headerTitle: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#fff',
    marginBottom: 5,
  },
  updateTime: {
    fontSize: 12,
    color: '#ecf0f1',
  },
  tabContainer: {
    flexDirection: 'row',
    backgroundColor: '#fff',
    padding: 10,
    justifyContent: 'space-around',
  },
  tab: {
    flex: 1,
    paddingVertical: 10,
    paddingHorizontal: 15,
    marginHorizontal: 5,
    borderRadius: 8,
    backgroundColor: '#ecf0f1',
    alignItems: 'center',
  },
  tabText: {
    fontSize: 14,
    fontWeight: '600',
    color: '#7f8c8d',
  },
  tabTextActive: {
    color: '#fff',
  },
  playerList: {
    padding: 15,
  },
  playerCard: {
    flexDirection: 'row',
    backgroundColor: '#fff',
    borderRadius: 12,
    padding: 15,
    marginBottom: 10,
    alignItems: 'center',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  rankBadge: {
    width: 40,
    height: 40,
    borderRadius: 20,
    backgroundColor: '#3498db',
    justifyContent: 'center',
    alignItems: 'center',
    marginRight: 15,
  },
  rankText: {
    color: '#fff',
    fontWeight: 'bold',
    fontSize: 14,
  },
  playerInfo: {
    flex: 1,
  },
  playerName: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#2c3e50',
    marginBottom: 4,
  },
  playerLevel: {
    fontSize: 12,
    color: '#7f8c8d',
  },
  statsContainer: {
    flexDirection: 'row',
    gap: 10,
  },
  statItem: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 4,
  },
  statText: {
    fontSize: 14,
    fontWeight: '600',
    color: '#2c3e50',
  },
  emptyText: {
    textAlign: 'center',
    color: '#7f8c8d',
    fontSize: 16,
    marginTop: 50,
  },
  battleRankingsButton: {
    backgroundColor: '#3498db',
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    paddingVertical: 15,
    paddingHorizontal: 20,
    borderRadius: 12,
    margin: 15,
    marginTop: 10,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.2,
    shadowRadius: 4,
    elevation: 4,
  },
  battleRankingsButtonText: {
    color: '#fff',
    fontSize: 16,
    fontWeight: 'bold',
    marginLeft: 10,
  },
});
