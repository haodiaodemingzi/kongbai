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
  TextInput,
} from 'react-native';
import { MaterialIcons, FontAwesome5 } from '@expo/vector-icons';
import { getGodsStats, getGroupDetails, getGroupKillDetails } from '../services/api';
import { useTheme } from '../contexts/ThemeContext';
import { captureRef } from 'react-native-view-shot';
import * as Sharing from 'expo-sharing';
import PlayerDetailScreen from './PlayerDetailScreen';
import GroupDetailScreen from './GroupDetailScreen';

// 格式化日期范围显示
const formatDateRange = (startDate, endDate) => {
  if (!startDate || !endDate) return '选择时间范围';
  
  const start = new Date(startDate);
  const end = new Date(endDate);
  
  const formatDateTime = (date) => {
    const month = String(date.getMonth() + 1).padStart(2, '0');
    const day = String(date.getDate()).padStart(2, '0');
    const hours = String(date.getHours()).padStart(2, '0');
    const minutes = String(date.getMinutes()).padStart(2, '0');
    return `${month}-${day} ${hours}:${minutes}`;
  };
  
  return `${formatDateTime(start)} ~ ${formatDateTime(end)}`;
};

// 获取势力配置
const getGodConfig = (godName) => {
  const configs = {
    '梵天': { backgroundColor: '#FFD700', textColor: '#000000' }, // 黄色浅色背景用黑字
    '湿婆': { backgroundColor: '#4169E1', textColor: '#FFFFFF' }, // 蓝色深色背景用白字
    '比湿奴': { backgroundColor: '#DC143C', textColor: '#FFFFFF' }, // 红色深色背景用白字
  };
  return configs[godName] || { backgroundColor: '#6c757d', textColor: '#FFFFFF' }; // 默认深色背景用白字
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
  
  // 日期输入状态
  const [startDateText, setStartDateText] = useState('');
  const [endDateText, setEndDateText] = useState('');
  
  // 初始化日期文本
  useEffect(() => {
    setStartDateText(formatDisplayDateTime(startDate));
    setEndDateText(formatDisplayDateTime(endDate));
  }, [startDate, endDate]);
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
  
  // 格式化日期时间为 YYYY-MM-DD HH:MM:SS
  const formatDateTime = (date) => {
    const year = date.getFullYear();
    const month = String(date.getMonth() + 1).padStart(2, '0');
    const day = String(date.getDate()).padStart(2, '0');
    const hours = String(date.getHours()).padStart(2, '0');
    const minutes = String(date.getMinutes()).padStart(2, '0');
    const seconds = String(date.getSeconds()).padStart(2, '0');
    return `${year}-${month}-${day} ${hours}:${minutes}:${seconds}`;
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

  // 解析日期文本
  const parseDateText = (dateText) => {
    try {
      // 支持格式：2025-01-15 14:30 或 2025-01-15
      const parts = dateText.trim().split(' ');
      const datePart = parts[0];
      const timePart = parts[1] || '00:00';
      
      const [year, month, day] = datePart.split('-').map(Number);
      const [hour, minute] = timePart.split(':').map(Number);
      
      if (year && month && day) {
        return new Date(year, month - 1, day, hour || 0, minute || 0);
      }
    } catch (error) {
      console.log('日期解析错误:', error);
    }
    return null;
  };

  // 应用自定义日期
  const applyCustomDates = () => {
    const newStartDate = parseDateText(startDateText);
    const newEndDate = parseDateText(endDateText);
    
    if (newStartDate && newEndDate) {
      if (newStartDate <= newEndDate) {
        setStartDate(newStartDate);
        setEndDate(newEndDate);
        setShowCustomModal(false);
        fetchGodsStats();
      } else {
        Alert.alert('错误', '开始时间不能晚于结束时间');
      }
    } else {
      Alert.alert('错误', '请输入正确的日期格式\n格式：2025-01-15 14:30 或 2025-01-15');
    }
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
    const godConfig = getGodConfig(godName);
    
    // 统计分组/玩家数量
    let totalPlayers;
    let displayPlayers;
    
    if (showGrouped) {
      // 分组模式：统计分组数量（包括单独的游戏ID）
      const groups = new Set();
      godData.players.forEach(player => {
        if (player.is_group) {
          groups.add(player.name); // 分组名
        } else {
          groups.add(player.name); // 单独的游戏ID也算一组
        }
      });
      totalPlayers = groups.size;
      
      // 只显示分组汇总数据，累加所有成员的战绩
      const groupMap = new Map();
      godData.players.forEach(player => {
        if (player.is_group) {
          // 如果是分组，累加所有成员的战绩
          if (!groupMap.has(player.name)) {
            groupMap.set(player.name, {
              ...player,
              kills: 0,
              deaths: 0,
              bless: 0
            });
          }
          const groupData = groupMap.get(player.name);
          groupData.kills += player.kills || 0;
          groupData.deaths += player.deaths || 0;
          groupData.bless += player.bless || 0;
        } else {
          // 非分组玩家直接添加
          groupMap.set(player.name, player);
        }
      });
      displayPlayers = Array.from(groupMap.values());
    } else {
      // 普通模式：显示所有玩家
      totalPlayers = godData.players.length;
      displayPlayers = godData.players;
    }

    return (
      <View key={godName} style={styles.godCard}>
        {/* 势力头部 - 单行显示 */}
        <View style={[styles.godHeaderInline, { backgroundColor: godConfig.backgroundColor }]}>
          {/* 左侧：势力名称、时间范围和人数 */}
          <View style={styles.godInfoSection}>
            <Text style={[styles.godNameInline, { color: godConfig.textColor }]}>{godName}</Text>
            <Text style={[styles.godTimeRange, { color: godConfig.textColor }]}>
              {formatDateRange(startDate, endDate)}
            </Text>
            <Text style={[styles.godSubtitleInline, { color: godConfig.textColor }]}>
              {showGrouped ? `${totalPlayers}组` : `${totalPlayers}人`}
            </Text>
          </View>
          
          {/* 右侧：统计数据 */}
          <View style={styles.godStatsInline}>
            <View style={styles.godStatInlineItem}>
              <Text style={[styles.godStatValueInline, { color: godConfig.textColor }]}>{godData.kills}</Text>
              <Text style={[styles.godStatLabelInline, { color: godConfig.textColor }]}>击杀</Text>
            </View>
            <View style={styles.godStatInlineItem}>
              <Text style={[styles.godStatValueInline, { color: godConfig.textColor }]}>{godData.deaths}</Text>
              <Text style={[styles.godStatLabelInline, { color: godConfig.textColor }]}>死亡</Text>
            </View>
            <View style={styles.godStatInlineItem}>
              <Text style={[styles.godStatValueInline, { color: godConfig.textColor }]}>
                {godData.bless > 0 ? `🏮${godData.bless}` : '🏮0'}
              </Text>
            </View>
          </View>
        </View>

        {/* 玩家卡片列表 */}
        <View style={styles.playersContainer}>
          {displayPlayers && displayPlayers.map((player, index) => (
            <View key={index} style={styles.playerCardContainer}>
              {/* 玩家卡片 - 参考PlayerDetailScreen的detailCard样式 */}
              <TouchableOpacity
                onPress={() => {
                  if (showGrouped && player.is_group) {
                    // 分组模式下点击分组卡片,跳转到分组详情页
                    setSelectedGroup(player.name);
                  } else {
                    // 非分组或普通玩家,跳转到玩家详情页
                    setSelectedPlayer(player.name);
                  }
                }}
                style={[
                  styles.playerCard,
                  player.is_group && styles.groupCard
                ]}
              >
                {/* 玩家信息 + 统计数据 */}
                <View style={styles.playerInfoRow}>
                  {/* 左侧：玩家信息 */}
                  <View style={styles.playerInfoSection}>
                    {showGrouped && player.is_group && (
                      <MaterialIcons 
                        name="group" 
                        size={16} 
                        color="#2c3e50"
                        style={styles.groupIcon}
                      />
                    )}
                    <Text style={styles.playerName}>
                      {showGrouped ? player.name : `${player.name}（${player.job || '未知'}）`}
                    </Text>
                  </View>

                  {/* 右侧：统计数据 */}
                  <View style={styles.statsSection}>
                    <View style={styles.statInline}>
                      <Text style={[styles.statValue, { color: '#2196F3' }]}>{player.kills}</Text>
                    </View>
                    <View style={styles.statInline}>
                      <Text style={[styles.statValue, { color: '#F44336' }]}>{player.deaths}</Text>
                    </View>
                    <View style={styles.statInline}>
                      <Text style={[
                        styles.statValue, 
                        { color: player.bless > 0 ? '#FF9800' : colors.textSecondary }
                      ]}>
                        {player.bless > 0 ? `🏮${player.bless}` : '🏮0'}
                      </Text>
                    </View>
                  </View>
                </View>
              </TouchableOpacity>
            </View>
          ))}
        </View>
      </View>
    );
  };

  // 如果选中了分组，显示分组详情
  if (selectedGroup) {
    return (
      <GroupDetailScreen
        groupName={selectedGroup}
        timeRange={{ 
          startDate: formatDateTime(startDate), 
          endDate: formatDateTime(endDate) 
        }}
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
      {/* 紧凑筛选器 - 单行布局 */}
      <View style={[styles.compactFilterContainer, { backgroundColor: colors.cardBackground }]}>
        {/* 日期选择 */}
        <TouchableOpacity
          style={[styles.compactButton, { borderColor: colors.border }]}
          onPress={() => setShowCustomModal(true)}
        >
          <MaterialIcons name="date-range" size={20} color={colors.primary} />
        </TouchableOpacity>

        {/* 模式切换 */}
        <View style={styles.compactToggleContainer}>
          <TouchableOpacity
            style={[
              styles.compactToggleButton,
              !showGrouped && [styles.compactToggleActive, { backgroundColor: colors.primary }],
              { borderColor: colors.border }
            ]}
            onPress={() => setShowGrouped(false)}
          >
            <Text style={[
              styles.compactToggleText,
              { color: !showGrouped ? '#fff' : colors.textSecondary }
            ]}>
              ID
            </Text>
          </TouchableOpacity>

          <TouchableOpacity
            style={[
              styles.compactToggleButton,
              showGrouped && [styles.compactToggleActive, { backgroundColor: colors.primary }],
              { borderColor: colors.border }
            ]}
            onPress={() => setShowGrouped(true)}
          >
            <Text style={[
              styles.compactToggleText,
              { color: showGrouped ? '#fff' : colors.textSecondary }
            ]}>
              分组
            </Text>
          </TouchableOpacity>
        </View>

        {/* 分享按钮 */}
        <TouchableOpacity
          style={[styles.compactButton, { backgroundColor: colors.primary }]}
          onPress={handleShareScreenshot}
          disabled={isCapturing || loading}
        >
          {isCapturing ? (
            <ActivityIndicator size="small" color="#fff" />
          ) : (
            <MaterialIcons name="share" size={20} color="#fff" />
          )}
        </TouchableOpacity>
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

      
      {/* 自定义日期范围选择模态框 */}
      <Modal
        visible={showCustomModal}
        transparent={true}
        animationType="slide"
        onRequestClose={() => setShowCustomModal(false)}
      >
        <View style={styles.modalOverlay}>
          <View style={[styles.modalContent, { backgroundColor: colors.cardBackground }]}>
            <View style={styles.modalHeader}>
              <Text style={[styles.modalTitle, { color: colors.text }]}>选择时间范围</Text>
              <TouchableOpacity
                style={styles.closeButton}
                onPress={() => setShowCustomModal(false)}
              >
                <MaterialIcons name="close" size={24} color={colors.text} />
              </TouchableOpacity>
            </View>
            
            <View style={styles.modalBody}>
              {/* 快速选择 */}
              <View style={styles.quickSelectSection}>
                <Text style={[styles.sectionTitle, { color: colors.text }]}>快速选择</Text>
                <View style={styles.presetRow}>
                  <TouchableOpacity
                    style={[styles.presetButtonSmall, { borderColor: colors.border }]}
                    onPress={() => {
                      const now = new Date();
                      const start = new Date(now.getFullYear(), now.getMonth(), now.getDate(), 0, 0, 0);
                      const end = new Date(now.getFullYear(), now.getMonth(), now.getDate(), 23, 59, 59);
                      setStartDate(start);
                      setEndDate(end);
                      setShowCustomModal(false);
                      fetchGodsStats();
                    }}
                  >
                    <Text style={[styles.presetButtonTextSmall, { color: colors.text }]}>今天</Text>
                  </TouchableOpacity>
                  
                  <TouchableOpacity
                    style={[styles.presetButtonSmall, { borderColor: colors.border }]}
                    onPress={() => {
                      const now = new Date();
                      const start = new Date(now.getTime() - 3 * 24 * 60 * 60 * 1000);
                      setStartDate(start);
                      setEndDate(now);
                      setShowCustomModal(false);
                      fetchGodsStats();
                    }}
                  >
                    <Text style={[styles.presetButtonTextSmall, { color: colors.text }]}>3天</Text>
                  </TouchableOpacity>
                  
                  <TouchableOpacity
                    style={[styles.presetButtonSmall, { borderColor: colors.border }]}
                    onPress={() => {
                      const now = new Date();
                      const start = new Date(now.getTime() - 7 * 24 * 60 * 60 * 1000);
                      setStartDate(start);
                      setEndDate(now);
                      setShowCustomModal(false);
                      fetchGodsStats();
                    }}
                  >
                    <Text style={[styles.presetButtonTextSmall, { color: colors.text }]}>7天</Text>
                  </TouchableOpacity>
                  
                  <TouchableOpacity
                    style={[styles.presetButtonSmall, { borderColor: colors.border }]}
                    onPress={() => {
                      const now = new Date();
                      const start = new Date(now.getTime() - 30 * 24 * 60 * 60 * 1000);
                      setStartDate(start);
                      setEndDate(now);
                      setShowCustomModal(false);
                      fetchGodsStats();
                    }}
                  >
                    <Text style={[styles.presetButtonTextSmall, { color: colors.text }]}>30天</Text>
                  </TouchableOpacity>
                </View>
              </View>

              {/* 自定义时间选择 */}
              <View style={styles.customSelectSection}>
                <Text style={[styles.sectionTitle, { color: colors.text }]}>自定义时间</Text>
                <Text style={[styles.formatHint, { color: colors.textSecondary }]}>
                  格式：2025-01-15 14:30 或 2025-01-15
                </Text>
                
                <View style={styles.dateInputContainer}>
                  <Text style={[styles.inputLabel, { color: colors.text }]}>开始时间</Text>
                  <TextInput
                    style={[styles.dateInput, { 
                      borderColor: colors.border, 
                      color: colors.text,
                      backgroundColor: colors.background 
                    }]}
                    value={startDateText}
                    onChangeText={setStartDateText}
                    placeholder="2025-01-15 00:00"
                    placeholderTextColor={colors.textSecondary}
                  />
                </View>
                
                <View style={styles.dateInputContainer}>
                  <Text style={[styles.inputLabel, { color: colors.text }]}>结束时间</Text>
                  <TextInput
                    style={[styles.dateInput, { 
                      borderColor: colors.border, 
                      color: colors.text,
                      backgroundColor: colors.background 
                    }]}
                    value={endDateText}
                    onChangeText={setEndDateText}
                    placeholder="2025-01-15 23:59"
                    placeholderTextColor={colors.textSecondary}
                  />
                </View>
              </View>

              {/* 应用按钮 */}
              <TouchableOpacity
                style={[styles.applyButton, { backgroundColor: colors.primary }]}
                onPress={applyCustomDates}
              >
                <Text style={styles.applyButtonText}>应用</Text>
              </TouchableOpacity>
            </View>
          </View>
        </View>
      </Modal>
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
  compactFilterContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    padding: 12,
    borderBottomWidth: 1,
    borderBottomColor: '#e0e0e0',
  },
  compactButton: {
    width: 44,
    height: 44,
    borderRadius: 22,
    borderWidth: 1,
    justifyContent: 'center',
    alignItems: 'center',
  },
  compactToggleContainer: {
    flexDirection: 'row',
    borderRadius: 22,
    borderWidth: 1,
    borderColor: '#e0e0e0',
    overflow: 'hidden',
  },
  compactToggleButton: {
    paddingHorizontal: 16,
    paddingVertical: 10,
    minWidth: 50,
    justifyContent: 'center',
    alignItems: 'center',
  },
  compactToggleActive: {
    // 激活状态样式在组件中动态设置
  },
  compactToggleText: {
    fontSize: 14,
    fontWeight: '600',
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
    marginBottom: 7,
    backgroundColor: '#fff',
    borderRadius: 0,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  godHeader: {
    padding: 12,
    paddingTop: 16,
    alignItems: 'center',
  },
  godName: {
    fontSize: 22,
    fontWeight: 'bold',
    color: '#fff',
    marginBottom: 3,
  },
  godSubtitle: {
    fontSize: 13,
    color: 'rgba(255, 255, 255, 0.8)',
  },
  godHeaderTop: {
    alignItems: 'center',
    marginBottom: 10,
  },
  godStatsRow: {
    flexDirection: 'row',
    justifyContent: 'space-around',
    width: '100%',
  },
  godStatItem: {
    alignItems: 'center',
  },
  godStatValue: {
    fontSize: 16,
    fontWeight: 'bold',
    marginBottom: 1,
  },
  godStatLabel: {
    fontSize: 10,
    opacity: 0.9,
  },
  // 单行势力头部样式
  godHeaderInline: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    padding: 12,
    paddingVertical: 10,
  },
  godInfoSection: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 8,
  },
  godNameInline: {
    fontSize: 18,
    fontWeight: 'bold',
  },
  godTimeRange: {
    fontSize: 11,
    opacity: 0.7,
    fontStyle: 'italic',
  },
  godSubtitleInline: {
    fontSize: 12,
    opacity: 0.8,
  },
  godStatsInline: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 12,
  },
  godStatInlineItem: {
    alignItems: 'center',
  },
  godStatValueInline: {
    fontSize: 14,
    fontWeight: 'bold',
    marginBottom: 1,
  },
  godStatLabelInline: {
    fontSize: 9,
    opacity: 0.8,
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
    padding: 6,
    borderRadius: 6,
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
    backgroundColor: '#e3f2fd', // 淡蓝色背景
    borderWidth: 1,
    borderColor: '#bbdefb',
  },
  playerInfoRow: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
  },
  playerInfoSection: {
    flex: 1,
    flexDirection: 'row',
    alignItems: 'center',
    gap: 6,
  },
  groupIcon: {
    marginRight: 2,
  },
  playerName: {
    fontSize: 14,
    fontWeight: 'bold',
    color: '#2c3e50',
  },
  statsSection: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'flex-end',
    flex: 1,
    gap: 20,
  },
  statInline: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 2,
    minWidth: 60,
    justifyContent: 'flex-end',
  },
  statValue: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#2c3e50',
    minWidth: 20,
    textAlign: 'right',
  },
  statLabel: {
    fontSize: 11,
    color: '#7f8c8d',
    minWidth: 22,
  },
  iconSpacer: {
    fontSize: 8,
    lineHeight: 14,
  },
  inlineActionButton: {
    padding: 2,
    borderRadius: 2,
    backgroundColor: 'rgba(44, 62, 80, 0.1)',
    justifyContent: 'center',
    alignItems: 'center',
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
  modalOverlay: {
    flex: 1,
    backgroundColor: 'rgba(0, 0, 0, 0.5)',
    justifyContent: 'center',
    alignItems: 'center',
  },
  modalContent: {
    borderRadius: 12,
    padding: 20,
    width: '80%',
    maxWidth: 300,
  },
  modalHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 20,
  },
  modalTitle: {
    fontSize: 18,
    fontWeight: 'bold',
  },
  closeButton: {
    padding: 4,
  },
  modalBody: {
    gap: 12,
  },
  presetButton: {
    padding: 15,
    borderRadius: 8,
    borderWidth: 1,
    alignItems: 'center',
  },
  presetButtonText: {
    fontSize: 16,
    fontWeight: '500',
  },
  quickSelectSection: {
    marginBottom: 20,
  },
  customSelectSection: {
    marginBottom: 20,
  },
  sectionTitle: {
    fontSize: 16,
    fontWeight: 'bold',
    marginBottom: 12,
  },
  presetRow: {
    flexDirection: 'row',
    gap: 8,
    justifyContent: 'space-between',
  },
  presetButtonSmall: {
    flex: 1,
    padding: 12,
    borderRadius: 8,
    borderWidth: 1,
    alignItems: 'center',
  },
  presetButtonTextSmall: {
    fontSize: 14,
    fontWeight: '500',
  },
  dateTimeButton: {
    flexDirection: 'row',
    alignItems: 'center',
    padding: 12,
    borderRadius: 8,
    borderWidth: 1,
    marginBottom: 8,
    gap: 8,
  },
  dateTimeButtonText: {
    fontSize: 14,
    flex: 1,
  },
  applyButton: {
    padding: 15,
    borderRadius: 8,
    alignItems: 'center',
  },
  applyButtonText: {
    color: '#fff',
    fontSize: 16,
    fontWeight: 'bold',
  },
  formatHint: {
    fontSize: 12,
    marginBottom: 12,
    fontStyle: 'italic',
  },
  dateInputContainer: {
    marginBottom: 12,
  },
  inputLabel: {
    fontSize: 14,
    fontWeight: '500',
    marginBottom: 6,
  },
  dateInput: {
    borderWidth: 1,
    borderRadius: 8,
    padding: 12,
    fontSize: 14,
  },
});
