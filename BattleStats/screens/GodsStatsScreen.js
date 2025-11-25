import React, { useState, useEffect, useRef } from 'react';
import {
  View,
  Text,
  ScrollView,
  StyleSheet,
  ActivityIndicator,
  RefreshControl,
  TouchableOpacity,
  Alert,
  Modal,
  Platform,
} from 'react-native';
import DateTimePicker from '@react-native-community/datetimepicker';
import { MaterialIcons, FontAwesome5 } from '@expo/vector-icons';
import { getGodsStats, getGroupDetails, getGroupKillDetails } from '../services/api';
import { useTheme } from '../contexts/ThemeContext';
import { captureRef } from 'react-native-view-shot';
import * as Sharing from 'expo-sharing';
import PlayerDetailScreen from './PlayerDetailScreen';
import GroupDetailScreen from './GroupDetailScreen';
import GroupMembersScreen from './GroupMembersScreen';

// 格式化日期范围显示
const formatDateRange = (startDate, endDate) => {
  if (!startDate || !endDate) return '选择时间范围';
  
  const start = new Date(startDate);
  const end = new Date(endDate);
  
  const formatDate = (date) => {
    const month = String(date.getMonth() + 1).padStart(2, '0');
    const day = String(date.getDate()).padStart(2, '0');
    return `${month}-${day}`;
  };
  
  return `${formatDate(start)} ~ ${formatDate(end)}`;
};

export default function GodsStatsScreen({ navigation }) {
  const { colors } = useTheme();
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [stats, setStats] = useState({});
  const [showGrouped, setShowGrouped] = useState(false);
  const [isCapturing, setIsCapturing] = useState(false); // 截图中状态
  const scrollViewRef = useRef(null); // ScrollView 引用
  const contentRef = useRef(null); // 内容引用，用于截图
  
  // 自定义时间相关状态
  const [showDatePicker, setShowDatePicker] = useState(false);
  const [showTimePicker, setShowTimePicker] = useState(false);
  const [datePickerMode, setDatePickerMode] = useState('start'); // 'start' or 'end'
  const [tempDate, setTempDate] = useState(new Date()); // 临时存储选择的日期
  const [startDate, setStartDate] = useState(() => {
    const date = new Date();
    date.setHours(0, 0, 0, 0);
    return date;
  });
  const [endDate, setEndDate] = useState(() => {
    const date = new Date();
    date.setHours(23, 59, 59, 999);
    return date;
  });
  const [showCustomModal, setShowCustomModal] = useState(false);
  const [selectedPlayer, setSelectedPlayer] = useState(null);
  const [selectedGroup, setSelectedGroup] = useState(null);
  const [selectedGroupForMembers, setSelectedGroupForMembers] = useState(null);

  useEffect(() => {
    fetchGodsStats();
  }, [showGrouped, startDate, endDate]);

  const fetchGodsStats = async () => {
    try {
      const params = {
        show_grouped: showGrouped,
        start_datetime: formatDateTime(startDate),
        end_datetime: formatDateTime(endDate),
      };
      
      const result = await getGodsStats(params);

      if (result.success) {
        setStats(result.data.stats || {});
      } else {
        Alert.alert('错误', result.message || '获取三神统计失败');
        setStats({});
      }
    } catch (error) {
      console.error('获取三神统计失败:', error);
      Alert.alert('错误', '网络错误，请稍后重试');
      setStats({});
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };
  
  // 格式化日期时间为 YYYY-MM-DDTHH:MM
  const formatDateTime = (date) => {
    const year = date.getFullYear();
    const month = String(date.getMonth() + 1).padStart(2, '0');
    const day = String(date.getDate()).padStart(2, '0');
    const hours = String(date.getHours()).padStart(2, '0');
    const minutes = String(date.getMinutes()).padStart(2, '0');
    return `${year}-${month}-${day}T${hours}:${minutes}`;
  };
  
  // 格式化显示日期时间
  const formatDisplayDateTime = (date) => {
    const year = date.getFullYear();
    const month = String(date.getMonth() + 1).padStart(2, '0');
    const day = String(date.getDate()).padStart(2, '0');
    const hours = String(date.getHours()).padStart(2, '0');
    const minutes = String(date.getMinutes()).padStart(2, '0');
    return `${year}-${month}-${day} ${hours}:${minutes}`;
  };

  const onRefresh = () => {
    setRefreshing(true);
    fetchGodsStats();
  };

  // 处理日期选择
  const onDateChange = (event, selectedDate) => {
    if (Platform.OS === 'android') {
      setShowDatePicker(false);
      if (event.type === 'set' && selectedDate) {
        // Android: 选择日期后,打开时间选择器
        setTempDate(selectedDate);
        setShowTimePicker(true);
      }
    } else {
      // iOS: 直接更新日期
      if (selectedDate) {
        if (datePickerMode === 'start') {
          setStartDate(selectedDate);
        } else {
          setEndDate(selectedDate);
        }
      }
    }
  };

  // 处理时间选择
  const onTimeChange = (event, selectedTime) => {
    setShowTimePicker(false);
    
    if (event.type === 'set' && selectedTime) {
      // 合并日期和时间
      const finalDate = new Date(tempDate);
      finalDate.setHours(selectedTime.getHours());
      finalDate.setMinutes(selectedTime.getMinutes());
      finalDate.setSeconds(0);
      finalDate.setMilliseconds(0);
      
      if (datePickerMode === 'start') {
        setStartDate(finalDate);
      } else {
        setEndDate(finalDate);
      }
    }
  };

  // 打开日期选择器
  const openDatePicker = (mode) => {
    setDatePickerMode(mode);
    setTempDate(mode === 'start' ? startDate : endDate);
    setShowDatePicker(true);
  };

  // 生成并分享截图
  const handleShareScreenshot = async () => {
    try {
      setIsCapturing(true);
      
      // 检查分享功能是否可用
      const isAvailable = await Sharing.isAvailableAsync();
      if (!isAvailable) {
        Alert.alert('提示', '当前设备不支持分享功能');
        setIsCapturing(false);
        return;
      }

      // 等待一小段时间确保UI渲染完成
      await new Promise(resolve => setTimeout(resolve, 100));

      // 截取整个内容区域
      const uri = await captureRef(contentRef, {
        format: 'png',
        quality: 1,
        result: 'tmpfile',
      });

      // 分享截图
      await Sharing.shareAsync(uri, {
        mimeType: 'image/png',
        dialogTitle: '分享三神统计',
      });

    } catch (error) {
      console.error('截图分享失败:', error);
      Alert.alert('错误', '截图失败，请稍后重试');
    } finally {
      setIsCapturing(false);
    }
  };

  // 渲染统计卡片
  const renderStatsCard = (godName, godData) => {
    const godColors = {
      '梵天': '#e74c3c',
      '比湿奴': '#3498db',
      '湿婆': '#9b59b6',
    };

    return (
      <View key={godName} style={styles.godCard}>
        {/* 势力头部 - 参考PlayerDetailScreen的深色头部 */}
        <View style={[styles.godHeader, { backgroundColor: godColors[godName] || colors.primary }]}>
          <Text style={styles.godName}>{godName}</Text>
          <Text style={styles.godSubtitle}>势力统计</Text>
        </View>

        {/* 玩家卡片列表 */}
        <View style={styles.playersContainer}>
          {godData.players && godData.players.map((player, index) => (
            <View key={index} style={styles.playerCardContainer}>
              {/* 玩家卡片 - 参考PlayerDetailScreen的detailCard样式 */}
              <TouchableOpacity
                onPress={() => {
                  if (!showGrouped || !player.is_group) {
                    setSelectedPlayer(player.name);
                  }
                }}
                disabled={showGrouped && player.is_group}
                style={[
                  styles.playerCard,
                  player.is_group && styles.groupCard
                ]}
              >
                {/* 玩家信息头部 */}
                <View style={styles.playerCardHeader}>
                  <View style={styles.playerNameSection}>
                    {showGrouped && player.is_group && (
                      <MaterialIcons 
                        name="group" 
                        size={20} 
                        color={colors.primary} 
                        style={styles.groupIcon}
                      />
                    )}
                    <Text style={styles.playerName}>
                      {showGrouped ? player.name : `${player.name}（${player.job || '未知'}）`}
                    </Text>
                  </View>

                  {/* 操作按钮 */}
                  {showGrouped && player.is_group && (
                    <View style={styles.groupActionsContainer}>
                      <TouchableOpacity
                        style={styles.groupActionButton}
                        onPress={() => setSelectedGroup(player.name)}
                      >
                        <MaterialIcons 
                          name="trending-up" 
                          size={18} 
                          color={colors.primary} 
                        />
                      </TouchableOpacity>
                      <TouchableOpacity
                        style={styles.groupActionButton}
                        onPress={() => setSelectedGroupForMembers(player.name)}
                      >
                        <MaterialIcons 
                          name="people" 
                          size={18} 
                          color={colors.primary} 
                        />
                      </TouchableOpacity>
                    </View>
                  )}
                </View>

                {/* 统计数据 - 参考PlayerDetailScreen的infoRow样式 */}
                <View style={styles.playerStatsRow}>
                  <View style={styles.statItem}>
                    <Text style={styles.statLabel}>击杀</Text>
                    <Text style={[styles.statValue, { color: '#27ae60' }]}>{player.kills}</Text>
                  </View>
                  <View style={styles.statItem}>
                    <Text style={styles.statLabel}>死亡</Text>
                    <Text style={[styles.statValue, { color: '#e74c3c' }]}>{player.deaths}</Text>
                  </View>
                  <View style={styles.statItem}>
                    <Text style={styles.statLabel}>爆灯</Text>
                    <Text style={[
                      styles.statValue, 
                      { color: player.bless > 0 ? '#f39c12' : colors.textSecondary }
                    ]}>
                      {player.bless > 0 ? `🏮${player.bless}` : '0'}
                    </Text>
                  </View>
                </View>
              </TouchableOpacity>
            </View>
          ))}
        </View>
      </View>
    );
  };

  // 如果选中了分组成员，显示分组成员战绩
  if (selectedGroupForMembers) {
    return (
      <GroupMembersScreen
        groupName={selectedGroupForMembers}
        timeRange={{ startDate, endDate }}
        onBack={() => setSelectedGroupForMembers(null)}
      />
    );
  }

  // 如果选中了分组，显示分组详情
  if (selectedGroup) {
    return (
      <GroupDetailScreen
        groupName={selectedGroup}
        timeRange={{ startDate, endDate }}
        onBack={() => setSelectedGroup(null)}
      />
    );
  }

  // 如果选中了玩家，显示玩家详情
  if (selectedPlayer) {
    return (
      <PlayerDetailScreen
        playerName={selectedPlayer}
        timeRange={{ startDate, endDate }}
        onBack={() => setSelectedPlayer(null)}
      />
    );
  }

  if (loading) {
    return (
      <View style={[styles.container, styles.centerContent, { backgroundColor: colors.background }]}>
        <ActivityIndicator size="large" color={colors.primary} />
        <Text style={[styles.loadingText, { color: colors.textSecondary }]}>加载中...</Text>
      </View>
    );
  }

  return (
    <View style={[styles.container, { backgroundColor: colors.background }]}>
      {/* 筛选器 */}
      <View style={[styles.filterContainer, { backgroundColor: colors.cardBackground }]}>
        {/* 分享按钮 */}
        <View style={styles.shareButtonContainer}>
          <TouchableOpacity
            style={[styles.shareButton, { backgroundColor: colors.primary }]}
            onPress={handleShareScreenshot}
            disabled={isCapturing || loading}
          >
            {isCapturing ? (
              <ActivityIndicator size="small" color="#fff" />
            ) : (
              <MaterialIcons name="share" size={18} color="#fff" />
            )}
            <Text style={styles.shareButtonText}>分享统计</Text>
          </TouchableOpacity>
        </View>

        {/* 日期选择 */}
        <View style={styles.dateRow}>
          <TouchableOpacity
            style={[styles.dateButton, { borderColor: colors.border }]}
            onPress={() => setShowCustomModal(true)}
          >
            <MaterialIcons name="date-range" size={18} color={colors.text} />
            <Text style={[styles.dateButtonText, { color: colors.text }]}>
              {formatDateRange(startDate, endDate)}
            </Text>
          </TouchableOpacity>
        </View>

        {/* 切换按钮 */}
        <View style={styles.toggleRow}>
          <TouchableOpacity
            style={[
              styles.toggleButton,
              !showGrouped && { backgroundColor: colors.primary },
              { borderColor: colors.border }
            ]}
            onPress={() => setShowGrouped(false)}
          >
            <FontAwesome5 
              name="user" 
              size={14} 
              color={!showGrouped ? '#fff' : colors.textSecondary} 
            />
            <Text style={[
              styles.toggleButtonText,
              { color: !showGrouped ? '#fff' : colors.textSecondary }
            ]}>
              按游戏ID
            </Text>
          </TouchableOpacity>

          <TouchableOpacity
            style={[
              styles.toggleButton,
              showGrouped && { backgroundColor: colors.primary },
              { borderColor: colors.border }
            ]}
            onPress={() => setShowGrouped(true)}
          >
            <FontAwesome5 
              name="users" 
              size={14} 
              color={showGrouped ? '#fff' : colors.textSecondary} 
            />
            <Text style={[
              styles.toggleButtonText,
              { color: showGrouped ? '#fff' : colors.textSecondary }
            ]}>
              按玩家分组
            </Text>
          </TouchableOpacity>
        </View>
      </View>

      {/* 三神统计卡片 */}
      <ScrollView
        ref={scrollViewRef}
        style={styles.scrollView}
        refreshControl={
          <RefreshControl
            refreshing={refreshing}
            onRefresh={onRefresh}
            colors={[colors.primary]}
            tintColor={colors.primary}
          />
        }
      >
        <View ref={contentRef} collapsable={false} style={{ backgroundColor: colors.background }}>
          {Object.keys(stats).length > 0 ? (
            Object.entries(stats).map(([godName, godData]) => 
              renderStatsCard(godName, godData)
            )
          ) : (
            <View style={styles.emptyContainer}>
              <MaterialIcons name="inbox" size={64} color={colors.textSecondary} />
              <Text style={[styles.emptyText, { color: colors.textSecondary }]}>
                暂无数据
              </Text>
            </View>
          )}
        </View>
      </ScrollView>

      {/* 日期选择器 */}
      {showDatePicker && (
        <DateTimePicker
          value={tempDate}
          mode={Platform.OS === 'ios' ? 'datetime' : 'date'}
          display={Platform.OS === 'ios' ? 'spinner' : 'default'}
          onChange={onDateChange}
        />
      )}

      {/* 时间选择器 (仅 Android) */}
      {showTimePicker && Platform.OS === 'android' && (
        <DateTimePicker
          value={tempDate}
          mode="time"
          is24Hour={true}
          display="default"
          onChange={onTimeChange}
        />
      )}
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
  },
  centerContent: {
    justifyContent: 'center',
    alignItems: 'center',
  },
  loadingText: {
    marginTop: 12,
    fontSize: 16,
  },
  header: {
    padding: 16,
    borderBottomWidth: 1,
    borderBottomColor: '#e0e0e0',
  },
  navBar: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  backButton: {
    padding: 8,
    borderRadius: 8,
  },
  title: {
    fontSize: 20,
    fontWeight: 'bold',
  },
  headerButtons: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 8,
  },
  groupButton: {
    paddingHorizontal: 12,
    paddingVertical: 6,
    borderRadius: 6,
    borderWidth: 1,
  },
  groupButtonText: {
    fontSize: 12,
    fontWeight: '600',
  },
  dateButton: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingHorizontal: 8,
    paddingVertical: 4,
    borderRadius: 6,
    borderWidth: 1,
  },
  dateButtonText: {
    fontSize: 12,
  },
  filterContainer: {
    padding: 12,
    borderBottomWidth: 1,
    borderBottomColor: '#e0e0e0',
  },
  shareButtonContainer: {
    marginBottom: 12,
  },
  shareButton: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    padding: 12,
    borderRadius: 8,
    gap: 8,
  },
  shareButtonText: {
    color: '#fff',
    fontSize: 14,
    fontWeight: '600',
  },
  dateRow: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 12,
  },
  dateButtonText: {
    marginLeft: 8,
    fontSize: 12,
    flex: 1,
  },
  dateSeparator: {
    marginHorizontal: 8,
    fontSize: 12,
  },
  toggleRow: {
    flexDirection: 'row',
    gap: 8,
  },
  toggleButton: {
    flex: 1,
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    padding: 10,
    borderRadius: 8,
    borderWidth: 1,
    gap: 6,
  },
  toggleButtonText: {
    fontSize: 13,
    fontWeight: '500',
  },
  scrollView: {
    flex: 1,
  },
  godCard: {
    marginBottom: 20,
    backgroundColor: '#fff',
    borderRadius: 0,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  godHeader: {
    padding: 20,
    paddingTop: 30,
    alignItems: 'center',
  },
  godName: {
    fontSize: 28,
    fontWeight: 'bold',
    color: '#fff',
    marginBottom: 5,
  },
  godSubtitle: {
    fontSize: 16,
    color: 'rgba(255, 255, 255, 0.8)',
  },
  playersContainer: {
    padding: 6,
    backgroundColor: '#f8f9fa',
  },
  playerCardContainer: {
    marginBottom: 6,
  },
  playerCard: {
    backgroundColor: '#ffffff',
    padding: 8,
    borderRadius: 8,
    marginBottom: 0,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.08,
    shadowRadius: 2,
    elevation: 1,
    borderWidth: 1,
    borderColor: '#e9ecef',
  },
  groupCard: {
    backgroundColor: '#ffffff',
    borderWidth: 1,
    borderColor: '#e9ecef',
  },
  playerCardHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 6,
    paddingBottom: 6,
    borderBottomWidth: 1,
    borderBottomColor: '#ecf0f1',
  },
  playerNameSection: {
    flex: 1,
    flexDirection: 'row',
    alignItems: 'center',
    gap: 8,
  },
  groupIcon: {
    marginRight: 4,
  },
  playerName: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#2c3e50',
  },
  groupActionsContainer: {
    flexDirection: 'row',
    gap: 8,
  },
  groupActionButton: {
    padding: 8,
    borderRadius: 6,
    backgroundColor: 'rgba(52, 152, 219, 0.1)',
    justifyContent: 'center',
    alignItems: 'center',
  },
  playerStatsRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
  },
  statItem: {
    alignItems: 'center',
    flex: 1,
  },
  statValue: {
    fontSize: 24,
    fontWeight: 'bold',
    marginBottom: 5,
  },
  statLabel: {
    fontSize: 12,
    color: '#7f8c8d',
  },
  emptyContainer: {
    alignItems: 'center',
    justifyContent: 'center',
    paddingVertical: 60,
  },
  emptyText: {
    marginTop: 16,
    fontSize: 16,
  },
});
