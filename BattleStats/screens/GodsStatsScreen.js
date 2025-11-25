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

export default function GodsStatsScreen() {
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
      <View key={godName} style={[styles.godCard, { borderLeftColor: godColors[godName] || colors.primary }]}>
        <View style={[styles.godHeader, { backgroundColor: godColors[godName] || colors.primary }]}>
          <Text style={styles.godName}>{godName}</Text>
        </View>
        
        <View style={styles.statsContainer}>
          <View style={styles.statItem}>
            <Text style={[styles.statValue, { color: colors.primary }]}>{godData.player_count}</Text>
            <Text style={[styles.statLabel, { color: colors.textSecondary }]}>玩家</Text>
          </View>
          <View style={styles.statItem}>
            <Text style={[styles.statValue, { color: colors.primary }]}>{godData.kills}</Text>
            <Text style={[styles.statLabel, { color: colors.textSecondary }]}>击杀</Text>
          </View>
          <View style={styles.statItem}>
            <Text style={[styles.statValue, { color: '#e74c3c' }]}>{godData.deaths}</Text>
            <Text style={[styles.statLabel, { color: colors.textSecondary }]}>死亡</Text>
          </View>
          <View style={styles.statItem}>
            <Text style={[styles.statValue, { color: '#27ae60' }]}>{godData.bless}</Text>
            <Text style={[styles.statLabel, { color: colors.textSecondary }]}>爆灯</Text>
          </View>
        </View>

        {/* 玩家列表 */}
        <View style={styles.playersContainer}>
          {/* 玩家战绩标题已移除 */}
          {/* 表头 */}
          <View style={styles.tableHeader}>
            <Text style={[styles.tableHeaderText, { flex: 2, color: colors.text }]}>
              {showGrouped ? '玩家' : '游戏ID'}
            </Text>
            <Text style={[styles.tableHeaderText, { flex: 1, color: colors.text }]}>击杀</Text>
            <Text style={[styles.tableHeaderText, { flex: 1, color: colors.text }]}>死亡</Text>
            <Text style={[styles.tableHeaderText, { flex: 1, color: colors.text }]}>爆灯</Text>
          </View>

          {/* 玩家数据 */}
          {godData.players && godData.players.map((player, index) => (
              <View key={index}>
                {/* 主行 - 可点击查看详情或展开成员 */}
                <TouchableOpacity
                  onPress={() => {
                    if (showGrouped && player.is_group) {
                      // 分组模式下点击分组 -> 显示分组详情
                      setSelectedGroup(player.name);
                    } else {
                      // 非分组或普通玩家 -> 显示玩家详情
                      setSelectedPlayer(player.name);
                    }
                  }}
                  style={[
                    styles.playerRow,
                    { backgroundColor: index % 2 === 0 ? colors.cardBackground : colors.background },
                    player.is_group && { backgroundColor: colors.primary + '10' }
                  ]}
                >
                  <View style={styles.playerNameContainer}>
                    <Text 
                      style={[
                        styles.playerName, 
                        { color: player.is_group ? colors.primary : colors.text }
                      ]}
                      numberOfLines={1}
                    >
                      {player.name}
                    </Text>
                    {showGrouped && player.is_group && (
                      <MaterialIcons 
                        name="info" 
                        size={18} 
                        color={colors.primary} 
                      />
                    )}
                  </View>
                  <Text style={[styles.playerStat, { color: colors.primary }]}>{player.kills}</Text>
                  <Text style={[styles.playerStat, { color: '#e74c3c' }]}>{player.deaths}</Text>
                  <Text style={[styles.playerStat, { color: player.bless > 0 ? '#27ae60' : colors.textSecondary }]}>
                    {player.bless > 0 ? `🏮${player.bless}` : '0'}
                  </Text>
                </TouchableOpacity>
              </View>
            )
          )}
        </View>
      </View>
    );
  };

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
              <>
                <MaterialIcons name="share" size={20} color="#fff" />
                <Text style={styles.shareButtonText}>分享截图</Text>
              </>
            )}
          </TouchableOpacity>
        </View>

        {/* 时间选择 */}
        <View style={styles.dateRow}>
          <TouchableOpacity
            style={[styles.dateButton, { backgroundColor: colors.background, borderColor: colors.border }]}
            onPress={() => openDatePicker('start')}
          >
            <MaterialIcons name="event" size={18} color={colors.primary} />
            <Text style={[styles.dateButtonText, { color: colors.text }]} numberOfLines={1}>
              {formatDisplayDateTime(startDate)}
            </Text>
          </TouchableOpacity>

          <Text style={[styles.dateSeparator, { color: colors.textSecondary }]}>至</Text>

          <TouchableOpacity
            style={[styles.dateButton, { backgroundColor: colors.background, borderColor: colors.border }]}
            onPress={() => openDatePicker('end')}
          >
            <MaterialIcons name="event" size={18} color={colors.primary} />
            <Text style={[styles.dateButtonText, { color: colors.text }]} numberOfLines={1}>
              {formatDisplayDateTime(endDate)}
            </Text>
          </TouchableOpacity>
        </View>

        {/* 显示模式切换 */}
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
    fontSize: 14,
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
  dateButton: {
    flex: 1,
    flexDirection: 'row',
    alignItems: 'center',
    padding: 10,
    borderRadius: 8,
    borderWidth: 1,
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
    margin: 12,
    borderRadius: 12,
    backgroundColor: '#fff',
    borderLeftWidth: 4,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  godHeader: {
    padding: 12,
    borderTopLeftRadius: 12,
    borderTopRightRadius: 12,
  },
  godName: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#fff',
    textAlign: 'center',
  },
  statsContainer: {
    flexDirection: 'row',
    padding: 12,
    backgroundColor: '#f8f9fa',
  },
  statItem: {
    flex: 1,
    alignItems: 'center',
  },
  statValue: {
    fontSize: 18,
    fontWeight: 'bold',
  },
  statLabel: {
    fontSize: 12,
    marginTop: 4,
  },
  playersContainer: {
    padding: 12,
  },
  playersTitle: {
    fontSize: 14,
    fontWeight: '600',
    marginBottom: 8,
  },
  tableHeader: {
    flexDirection: 'row',
    paddingVertical: 8,
    borderBottomWidth: 2,
    borderBottomColor: '#e0e0e0',
  },
  tableHeaderText: {
    fontSize: 12,
    fontWeight: '600',
    textAlign: 'center',
  },
  playerRow: {
    flexDirection: 'row',
    paddingVertical: 8,
    paddingHorizontal: 4,
    borderBottomWidth: 1,
    borderBottomColor: '#f0f0f0',
    alignItems: 'center',
  },
  playerNameContainer: {
    flex: 2,
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
  },
  playerName: {
    flex: 1,
    fontSize: 13,
    fontWeight: '500',
  },
  playerStat: {
    flex: 1,
    fontSize: 13,
    fontWeight: '600',
    textAlign: 'center',
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
