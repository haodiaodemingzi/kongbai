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
import DashboardScreen from './screens/DashboardScreen';
import UploadScreen from './screens/UploadScreen';
import PersonManagementScreen from './screens/PersonManagementScreen';
import GroupManagementScreen from './screens/GroupManagementScreen';
import ThemeSettingsScreen from './screens/ThemeSettingsScreen';
import GodsStatsScreen from './screens/GodsStatsScreen';
import { getStoredToken, getStoredUser, logout } from './services/api';
import { ThemeProvider, useTheme } from './contexts/ThemeContext';

const Tab = createBottomTabNavigator();
const Stack = createNativeStackNavigator();

// 首页组件 - 战绩排名（支持时间筛选）
function HomeScreen({ navigation }) {
  return <BattleRankingsScreen />;
}

// 个人中心组件
function ProfileScreen({ onLogout, navigation }) {
  const { colors } = useTheme();

  return (
    <ScrollView style={[styles.scrollContainer, { backgroundColor: colors.background }]}>
      <Text style={[styles.title, { color: colors.text }]}>配置中心</Text>
      
      {/* 系统设置 */}
      <View style={styles.section}>
        <Text style={[styles.sectionTitle, { color: colors.text }]}>系统设置</Text>
        
        <TouchableOpacity
          style={[styles.menuItem, { backgroundColor: colors.cardBackground, borderColor: colors.border }]}
          onPress={() => navigation.navigate('ThemeSettings')}
        >
          <MaterialIcons name="palette" size={24} color={colors.primary} />
          <Text style={[styles.menuItemText, { color: colors.text }]}>主题颜色</Text>
          <MaterialIcons name="chevron-right" size={24} color={colors.textLight} />
        </TouchableOpacity>
      </View>

      {/* 系统管理 */}
      <View style={styles.section}>
        <Text style={[styles.sectionTitle, { color: colors.text }]}>系统管理</Text>
        
        <TouchableOpacity
          style={[styles.menuItem, { backgroundColor: colors.cardBackground, borderColor: colors.border }]}
          onPress={() => navigation.navigate('PersonManagement')}
        >
          <MaterialIcons name="people" size={24} color={colors.primary} />
          <Text style={[styles.menuItemText, { color: colors.text }]}>人员管理</Text>
          <MaterialIcons name="chevron-right" size={24} color={colors.textLight} />
        </TouchableOpacity>
        
        <TouchableOpacity
          style={[styles.menuItem, { backgroundColor: colors.cardBackground, borderColor: colors.border }]}
          onPress={() => navigation.navigate('GroupManagement')}
        >
          <MaterialIcons name="group" size={24} color={colors.primary} />
          <Text style={[styles.menuItemText, { color: colors.text }]}>分组管理</Text>
          <MaterialIcons name="chevron-right" size={24} color={colors.textLight} />
        </TouchableOpacity>
      </View>
      
      {/* 登出按钮 */}
      <TouchableOpacity
        style={[styles.logoutButton, { backgroundColor: colors.primary }]}
        onPress={onLogout}
      >
        <MaterialIcons name="logout" size={20} color={colors.headerText} style={{ marginRight: 8 }} />
        <Text style={[styles.logoutButtonText, { color: colors.headerText }]}>登出</Text>
      </TouchableOpacity>
    </ScrollView>
  );
}

// 底部标签导航
function TabNavigator({ onLogout }) {
  const { colors } = useTheme();
  
  return (
    <Tab.Navigator
      screenOptions={({ route }) => ({
        tabBarIcon: ({ focused, color, size }) => {
          let iconName;
          
          if (route.name === 'Dashboard') {
            iconName = 'assessment'; // 数据分析图标
          } else if (route.name === 'Home') {
            iconName = 'military-tech'; // 勋章/战绩图标
          } else if (route.name === 'GodsStats') {
            iconName = 'auto-awesome'; // 三神统计图标
          } else if (route.name === 'Rankings') {
            iconName = 'emoji-events'; // 奖杯/排名图标
          } else if (route.name === 'Upload') {
            iconName = 'cloud-upload'; // 上传图标
          } else if (route.name === 'Profile') {
            iconName = 'settings'; // 设置/管理图标
          }
          
          return <MaterialIcons name={iconName} size={32} color={color} />;
        },
        tabBarShowLabel: false, // 隐藏文字标签
        tabBarActiveTintColor: colors.tabBarActive,
        tabBarInactiveTintColor: colors.tabBarInactive,
        tabBarStyle: {
          backgroundColor: colors.tabBarBackground,
          borderTopWidth: 0,
          height: 60,
          paddingBottom: 8,
          paddingTop: 8,
        },
        headerStyle: {
          backgroundColor: colors.headerBackground,
        },
        headerTintColor: colors.headerText,
        headerTitleStyle: {
          fontWeight: 'bold',
        },
      })}
    >
      <Tab.Screen 
        name="Dashboard" 
        component={DashboardScreen} 
        options={{ 
          title: '仪表盘',
          headerTitle: '数据仪表盘'
        }} 
      />
      <Tab.Screen 
        name="Home" 
        component={HomeScreen} 
        options={{ 
          title: '战绩',
          headerTitle: '战绩详情'
        }} 
      />
      <Tab.Screen 
        name="GodsStats" 
        component={GodsStatsScreen} 
        options={{ 
          title: '三神',
          headerTitle: '三神统计'
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
  const { colors } = useTheme();
  
  return (
    <Stack.Navigator
      screenOptions={{
        headerStyle: {
          backgroundColor: colors.headerBackground,
        },
        headerTintColor: colors.headerText,
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
      <Stack.Screen 
        name="ThemeSettings" 
        component={ThemeSettingsScreen} 
        options={{ 
          title: '主题颜色',
          presentation: 'card',
        }} 
      />
    </Stack.Navigator>
  );
}

// 主应用内容组件
function AppContent() {
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [loading, setLoading] = useState(true);

  // 检查本地是否有保存的 token
  useEffect(() => {
    checkStoredToken();
  }, []);

  const checkStoredToken = async () => {
    try {
      // 检查本地是否有保存的 token
      const token = await getStoredToken();
      const user = await getStoredUser();
      
      if (token && user) {
        // 有保存的 token,自动登录
        console.log('发现保存的 token,自动登录');
        setIsLoggedIn(true);
      } else {
        // 没有保存的 token,显示登录界面
        console.log('没有保存的 token,显示登录界面');
        setIsLoggedIn(false);
      }
    } catch (error) {
      console.error('检查 token 失败:', error);
      setIsLoggedIn(false);
    } finally {
      setLoading(false);
    }
  };

  const handleLoginSuccess = (user, userToken) => {
    setIsLoggedIn(true);
    setLoading(false);
  };

  const handleLogout = async () => {
    try {
      // 调用 logout API 清除 token 和用户信息
      // 但保留记住的用户名
      await logout();
    } catch (error) {
      console.error('登出失败:', error);
    }
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

// 主 App 组件，包装 ThemeProvider
export default function App() {
  return (
    <ThemeProvider>
      <AppContent />
    </ThemeProvider>
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
  scrollContainer: {
    flex: 1,
  },
  title: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#2c3e50',
    marginBottom: 20,
    marginTop: 20,
    paddingHorizontal: 20,
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
    marginHorizontal: 20,
    borderWidth: 1,
    borderColor: '#ecf0f1',
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
    marginHorizontal: 20,
    marginBottom: 20,
  },
  logoutButtonText: {
    color: '#fff',
    fontSize: 16,
    fontWeight: '600',
  },
  section: {
    marginBottom: 24,
  },
  sectionTitle: {
    fontSize: 18,
    fontWeight: '600',
    marginBottom: 16,
    paddingHorizontal: 20,
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
